from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import time
from .models import User
from .serializers import PhoneAuthSerializer, VerifyCodeSerializer, UserProfileSerializer
from .services import AuthService, ProfileService


class AuthView(APIView):
    """Обработка запросов авторизации по номеру телефона"""
    permission_classes = [AllowAny]
    def post(self, request) -> Response:
        serializer = PhoneAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone']
        code, debug_info = AuthService.generate_and_store_code(phone)

        request.session['auth_code'] = code
        request.session['auth_phone'] = phone
        print(f"\n=== {debug_info} ===\n")  # Для логов в разработке

        time.sleep(random.uniform(1, 2))  # Имитация задержки SMS
        return Response({
            "status": "Код отправлен",
            "debug_code": code  # Только для разработки!
        })


class VerifyView(APIView):
    """Подтверждение кода авторизации"""
    permission_classes = [AllowAny]
    def post(self, request) -> Response:
        serializer = VerifyCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        if not AuthService.verify_code(
                request.session.get('auth_code'),
                request.session.get('auth_phone'),
                code,
                phone
        ):
            return Response(
                {"error": "Неверный код подтверждения"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user, _ = User.objects.get_or_create(phone=phone)
        login(request, user)

        # Очистка сессии
        request.session.pop('auth_code', None)
        request.session.pop('auth_phone', None)

        return Response({
            "status": "Успешная авторизация",
            "invite_code": user.invite_code
        })


class ProfileBaseView(APIView):
    """Базовый класс для работы с профилями"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def _get_profile_response(self, user: User) -> Response:
        """Формирует стандартный ответ с профилем и рефералами"""
        profile_data = ProfileService.get_user_profile(user)
        serializer = self.serializer_class(profile_data['profile'])

        return Response({
            "profile": serializer.data,
            "referrals": {
                "count": profile_data['referrals'].count(),
                "users": self.serializer_class(
                    profile_data['referrals'],
                    many=True
                ).data
            }
        })


class ProfileView(ProfileBaseView):
    def post(self, request):
        """Активация инвайт-кода"""
        if request.user.activated_invite:
            return Response(
                {"error": "Вы уже активировали код"},
                status=status.HTTP_400_BAD_REQUEST
            )

        invite_code = request.data.get('invite_code')
        if not invite_code:
            return Response(
                {"error": "Укажите инвайт-код"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            inviting_user = User.objects.get(invite_code=invite_code)
            request.user.activated_invite = inviting_user
            request.user.save()
            return Response({"status": "Код активирован"})
        except User.DoesNotExist:
            return Response(
                {"error": "Неверный инвайт-код"},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileByPhoneView(ProfileBaseView):
    """Получение профиля по номеру телефона"""
    def get(self, request, phone: str) -> Response:
        try:
            profile_data = ProfileService.get_profile_by_phone(request.user, phone)
            return self._get_profile_response(profile_data['profile'])
        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError:
            return Response(
                {"error": "Доступ запрещен"},
                status=status.HTTP_403_FORBIDDEN
            )


class LogoutAPIView(APIView):
    """Выход из системы"""
    def post(self, request) -> Response:
        logout(request)
        return Response({"status": "Успешный выход"})


# HTML Views (для фронтенда)
def auth_view(request):
    """Отображает страницу ввода телефона"""
    if request.user.is_authenticated:
        return redirect('profile-page')
    return render(request, 'referrals/auth.html')


def verify_view(request):
    """Отображает страницу ввода кода подтверждения"""
    if request.user.is_authenticated:
        return redirect('profile-page')

    if not request.GET.get('phone'):
        return redirect('auth-page')

    return render(request, 'referrals/verify.html', {
        'phone': request.GET['phone'],
        'debug_code': request.session.get('auth_code')
    })


@login_required
def profile_view(request):
    """Отображает страницу профиля"""
    return render(request, 'referrals/profile.html')


@login_required
def logout_view(request):
    """Обрабатывает выход из системы"""
    logout(request)
    return redirect('auth-page')