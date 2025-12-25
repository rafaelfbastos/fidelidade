from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.companies.models import Company, CompanyTheme
from .serializers import (
    CompanySerializer,
    CompanyThemeSerializer,
    CompanyThemeUpdateSerializer
)
from .permissions import IsCompanyMemberWithPermission, CanManageCompanyTheme


@extend_schema_view(
    retrieve=extend_schema(
        tags=['themes'],
        summary='Obter tema da empresa',
        description='Retorna as configurações de tema da empresa pelo UUID da empresa.'
    ),
    update=extend_schema(
        tags=['themes'],
        summary='Atualizar tema completo',
        description='Atualiza todas as configurações do tema. Requer role owner ou admin.'
    ),
    partial_update=extend_schema(
        tags=['themes'],
        summary='Atualizar tema parcialmente',
        description='Atualiza campos específicos do tema. Requer role owner ou admin.'
    ),
)
class CompanyThemeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar temas das empresas.

    Permissões:
    - Leitura (GET): Qualquer membro da empresa
    - Edição (PUT/PATCH): Apenas owner e admin
    - Deleção (DELETE): Apenas owner
    """
    serializer_class = CompanyThemeSerializer
    permission_classes = [IsAuthenticated, CanManageCompanyTheme]
    lookup_field = 'company__uuid'
    lookup_url_kwarg = 'company_uuid'

    def get_queryset(self):
        """
        Retorna apenas temas de empresas que o usuário é membro.
        """
        user = self.request.user

        # IDs das empresas que o usuário gerencia
        company_ids = user.company_memberships.filter(
            is_active=True,
            deleted_at__isnull=True
        ).values_list('company_id', flat=True)

        return CompanyTheme.objects.filter(
            company_id__in=company_ids
        ).select_related('company')

    def get_serializer_class(self):
        """
        Usa serializer diferente para update.
        """
        if self.action in ['update', 'partial_update']:
            return CompanyThemeUpdateSerializer
        return CompanyThemeSerializer

    @extend_schema(
        tags=['themes'],
        summary='Atualizar apenas cores',
        description='Atualiza apenas as cores do tema. Requer role owner ou admin.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'primary_color': {'type': 'string', 'example': '#FF5733'},
                    'secondary_color': {'type': 'string', 'example': '#3498DB'},
                    'accent_color': {'type': 'string', 'example': '#E74C3C'},
                }
            }
        }
    )
    @action(detail=True, methods=['patch'])
    def update_colors(self, request, company_uuid=None):
        """
        Endpoint específico para atualizar apenas cores.
        """
        theme = self.get_object()

        # Validar cores HEX
        color_fields = [
            'primary_color', 'secondary_color', 'accent_color',
            'success_color', 'warning_color', 'error_color',
            'text_primary', 'text_secondary',
            'background_color', 'background_secondary', 'card_background'
        ]

        data = {k: v for k, v in request.data.items() if k in color_fields}

        serializer = CompanyThemeUpdateSerializer(
            theme,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            CompanyThemeSerializer(theme, context={'request': request}).data
        )

    @extend_schema(
        tags=['themes'],
        summary='Resetar tema para padrão',
        description='Restaura todas as configurações para os valores padrão. Requer role owner ou admin.'
    )
    @action(detail=True, methods=['post'])
    def reset_to_default(self, request, company_uuid=None):
        """
        Reseta o tema para os valores padrão.
        """
        theme = self.get_object()

        # Valores padrão
        defaults = {
            'primary_color': '#1976D2',
            'secondary_color': '#424242',
            'accent_color': '#FF5722',
            'success_color': '#4CAF50',
            'warning_color': '#FF9800',
            'error_color': '#F44336',
            'text_primary': '#212121',
            'text_secondary': '#757575',
            'background_color': '#FFFFFF',
            'background_secondary': '#FAFAFA',
            'card_background': '#FFFFFF',
            'custom_css': '',
            'extra_config': {},
        }

        for field, value in defaults.items():
            setattr(theme, field, value)

        theme.save()

        return Response(
            CompanyThemeSerializer(theme, context={'request': request}).data
        )
