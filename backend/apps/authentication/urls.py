from django.urls import path
from .views import (
    LoginView, LogoutView, TokenRefreshView,
    PasswordResetRequestView, PasswordResetConfirmView,
    LoginHistoryView, MyDevicesView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
    path('login-history/', LoginHistoryView.as_view(), name='auth-login-history'),
    path('devices/', MyDevicesView.as_view(), name='auth-devices'),
    path('devices/<uuid:device_id>/', MyDevicesView.as_view(), name='auth-device-delete'),
]
