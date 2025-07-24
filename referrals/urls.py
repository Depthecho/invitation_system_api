from django.urls import path
from .views import auth_view, verify_view, profile_view, LogoutAPIView, logout_view, UserProfileByPhoneView
from .views import AuthView, VerifyView, ProfileView

urlpatterns = [
    path('', auth_view, name='auth-page'),
    path('verify/', verify_view, name='verify-page'),
    path('profile/', profile_view, name='profile-page'),
    path('logout/', logout_view, name='logout'),

    path('api/auth/', AuthView.as_view(), name='auth-api'),
    path('api/verify/', VerifyView.as_view(), name='verify-api'),
    path('api/profile/', ProfileView.as_view(), name='profile-api'),
    path('api/logout/', LogoutAPIView.as_view(), name='logout-api'),
    path('api/profile/<str:phone>/', UserProfileByPhoneView.as_view(), name='profile-by-phone-api'),
]