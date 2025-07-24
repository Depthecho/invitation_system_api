from typing import Tuple
import random
from .models import User


class AuthService:
    @staticmethod
    def generate_and_store_code(phone: str) -> Tuple[str, str]:
        """Генерирует и возвращает код подтверждения для телефона"""
        code = str(random.randint(1000, 9999))
        return code, f"Код подтверждения для {phone}: {code}"

    @staticmethod
    def verify_code(stored_code: str, stored_phone: str,
                  input_code: str, input_phone: str) -> bool:
        """Проверяет соответствие кода подтверждения"""
        return stored_phone == input_phone and stored_code == input_code


class ProfileService:
    @staticmethod
    def get_user_profile(user: User) -> dict:
        """Возвращает профиль пользователя и его рефералов"""
        referrals = User.objects.filter(activated_invite=user)
        return {
            "profile": user,
            "referrals": referrals
        }

    @staticmethod
    def get_profile_by_phone(request_user: User, phone: str) -> dict:
        """Возвращает профиль по номеру телефона с проверкой доступа"""
        user = User.objects.get(phone=phone)
        if not (request_user.is_staff or request_user.phone == phone):
            raise PermissionError("Доступ запрещен")
        return ProfileService.get_user_profile(user)