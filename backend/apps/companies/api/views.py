from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.companies.models import Company, CompanyMember, CompanyTheme
from .serializers import (
    CompanySerializer,
    CompanyThemeSerializer,
    CompanyThemeUpdateSerializer,
    CompanyMemberSerializer,
    CompanyMemberCreateSerializer,
    CompanyMemberPasswordResetSerializer,
    CompanyMemberPasswordResetResponseSerializer,
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


class CompanyMemberCompanyMixin:
    """
    Utilitário para recuperar a empresa e validar permissões de owner/admin.
    """
    manage_roles = {CompanyMember.Role.OWNER, CompanyMember.Role.ADMIN}

    def get_company(self):
        if not hasattr(self, '_company_cache'):
            self._company_cache = get_object_or_404(
                Company,
                uuid=self.kwargs['company_uuid'],
                deleted_at__isnull=True
            )
        return self._company_cache

    def ensure_manage_permission(self, request):
        company = self.get_company()
        membership = company.companymember_set.filter(
            user=request.user,
            is_active=True,
            deleted_at__isnull=True
        ).first()
        if not membership:
            raise PermissionDenied('Você não tem acesso a esta empresa.')
        if membership.role not in self.manage_roles:
            raise PermissionDenied('Apenas proprietários ou administradores podem gerenciar usuários.')
        return membership


@extend_schema_view(
    get=extend_schema(
        tags=['company-members'],
        summary='Listar membros da empresa',
        description='Retorna usuários associados à empresa escolhida (apenas para owner/admin).',
        responses=CompanyMemberSerializer(many=True),
    ),
    post=extend_schema(
        tags=['company-members'],
        summary='Adicionar usuário à empresa',
        description='Cria ou associa um usuário existente à empresa e define o papel.',
        request=CompanyMemberCreateSerializer,
        responses=CompanyMemberSerializer,
    ),
)
class CompanyMemberListCreateView(
    CompanyMemberCompanyMixin,
    generics.ListCreateAPIView,
):
    """
    Permite que owners e admins listem e adicionem usuários à empresa atual.
    """
    serializer_class = CompanyMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        self.ensure_manage_permission(self.request)
        company = self.get_company()
        return CompanyMember.objects.filter(
            company=company,
            is_active=True,
        ).select_related('user').order_by('user__first_name', 'user__email')

    def create(self, request, *args, **kwargs):
        self.ensure_manage_permission(request)
        company = self.get_company()
        serializer = CompanyMemberCreateSerializer(
            data=request.data,
            context={'request': request, 'company': company},
        )
        serializer.is_valid(raise_exception=True)
        membership = serializer.save()
        output_serializer = CompanyMemberSerializer(
            membership,
            context={'request': request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        tags=['company-members'],
        summary='Detalhar membro da empresa',
        description='Retorna os dados completos de um usuário da empresa.',
        responses=CompanyMemberSerializer,
    ),
    patch=extend_schema(
        tags=['company-members'],
        summary='Atualizar papel do membro',
        description='Permite alterar o papel do usuário dentro da empresa.',
        request=CompanyMemberSerializer,
        responses=CompanyMemberSerializer,
    ),
    delete=extend_schema(
        tags=['company-members'],
        summary='Remover usuário da empresa',
        description='Desativa o vínculo do usuário com a empresa.',
    ),
)
class CompanyMemberDetailView(
    CompanyMemberCompanyMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    """
    Opera sobre um membro específico de uma empresa.
    """
    serializer_class = CompanyMemberSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    lookup_url_kwarg = 'member_uuid'

    def get_queryset(self):
        self.ensure_manage_permission(self.request)
        company = self.get_company()
        return CompanyMember.objects.filter(
            company=company,
        ).select_related('user')

    def update(self, request, *args, **kwargs):
        self.ensure_manage_permission(request)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.ensure_manage_permission(request)
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['company-members'],
    summary='Resetar senha do membro',
    description='Define uma nova senha para o usuário selecionado. Apenas owners/admins.',
    request=CompanyMemberPasswordResetSerializer,
    responses={
        200: CompanyMemberPasswordResetResponseSerializer,
    },
)
class CompanyMemberPasswordResetView(
    CompanyMemberCompanyMixin,
    generics.GenericAPIView,
):
    serializer_class = CompanyMemberPasswordResetSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        self.ensure_manage_permission(request)
        company = self.get_company()
        member = get_object_or_404(
            CompanyMember,
            company=company,
            uuid=self.kwargs['member_uuid'],
        )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        user = member.user
        user.set_password(password)
        user.save(update_fields=['password'])
        return Response({
            'password': password,
        })
