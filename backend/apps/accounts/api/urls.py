from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema

from .views import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    CurrentUserView,
    ChangePasswordView,
    logout_view,
)

# Adicionar documentação ao TokenRefreshView padrão
TokenRefreshView = extend_schema(
    tags=['auth'],
    summary='Renovar access token',
    description='Usa o refresh token para obter um novo access token.',
)(TokenRefreshView)

urlpatterns = [
    # Autenticação
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout'),

    # Registro
    path('register/', UserRegistrationView.as_view(), name='register'),

    # Usuário atual
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('me/password/', ChangePasswordView.as_view(), name='change_password'),
]
