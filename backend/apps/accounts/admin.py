from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """
    Admin customizado para CustomUser com login por email.
    """

    # Campos exibidos na listagem
    list_display = ['email', 'first_name', 'last_name', 'phone', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']

    # Configuração dos fieldsets (tela de edição)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informações Pessoais'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Permissões'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Datas Importantes'), {'fields': ('last_login', 'date_joined')}),
    )

    # Configuração para adicionar novo usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'password1', 'password2'),
        }),
        (_('Permissões'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # Como não temos username, removemos ele dos filtros
    filter_horizontal = ('groups', 'user_permissions')
