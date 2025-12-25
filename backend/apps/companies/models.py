from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


# Validador para cores em formato HEX
hex_color_validator = RegexValidator(
    regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
    message=_('Cor deve estar no formato HEX. Ex: #FF5733 ou #FFF')
)


class Company(BaseModel):
    """
    Modelo de Empresa parceira do programa de fidelidade.

    Empresas podem ter múltiplos membros (usuários) gerenciando através do CompanyMember.
    """

    # Validador de CNPJ
    cnpj_validator = RegexValidator(
        regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
        message='CNPJ deve estar no formato: 00.000.000/0000-00'
    )

    # Dados básicos
    trade_name = models.CharField(
        _('nome fantasia'),
        max_length=255,
        help_text=_('Nome comercial da empresa')
    )

    legal_name = models.CharField(
        _('razão social'),
        max_length=255,
        help_text=_('Razão social da empresa')
    )

    cnpj = models.CharField(
        _('CNPJ'),
        max_length=18,
        unique=True,
        validators=[cnpj_validator],
        help_text=_('CNPJ no formato: 00.000.000/0000-00')
    )

    # Contato
    email = models.EmailField(
        _('email'),
        help_text=_('Email principal da empresa')
    )

    phone = models.CharField(
        _('telefone'),
        max_length=20,
        help_text=_('Telefone com DDD. Ex: (11) 3333-4444')
    )

    # Endereço
    address = models.CharField(
        _('endereço'),
        max_length=255,
        blank=True
    )

    city = models.CharField(
        _('cidade'),
        max_length=100,
        blank=True
    )

    state = models.CharField(
        _('estado'),
        max_length=2,
        blank=True,
        help_text=_('UF do estado. Ex: SP, RJ, MG')
    )

    zip_code = models.CharField(
        _('CEP'),
        max_length=9,
        blank=True,
        help_text=_('CEP no formato: 00000-000')
    )

    # Logo da empresa (para aparecer no app)
    logo = models.ImageField(
        _('logo'),
        upload_to='companies/logos/',
        blank=True,
        null=True,
        help_text=_('Logo da empresa para exibição no app')
    )

    # Configurações do programa de fidelidade
    points_per_real = models.DecimalField(
        _('pontos por real'),
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text=_('Quantos pontos o cliente ganha por real gasto. Ex: 1.50')
    )

    is_active = models.BooleanField(
        _('ativa'),
        default=True,
        help_text=_('Empresa ativa no programa de fidelidade')
    )

    # Relacionamento com usuários (através de CompanyMember)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='CompanyMember',
        related_name='companies',
        verbose_name=_('membros')
    )

    class Meta:
        verbose_name = _('empresa')
        verbose_name_plural = _('empresas')
        ordering = ['trade_name']
        indexes = [
            models.Index(fields=['cnpj']),
            models.Index(fields=['is_active', 'deleted_at']),
        ]

    def __str__(self):
        return self.trade_name

    def get_active_members(self):
        """
        Retorna membros ativos da empresa.
        """
        return self.companymember_set.filter(is_active=True)

    def get_owners(self):
        """
        Retorna os donos da empresa.
        """
        return self.companymember_set.filter(role='owner', is_active=True)


class CompanyMember(BaseModel):
    """
    Modelo de relacionamento entre Usuário e Empresa.

    Define o papel (role) de um usuário dentro de uma empresa específica.
    Um usuário pode ter diferentes roles em diferentes empresas.
    """

    class Role(models.TextChoices):
        OWNER = 'owner', _('Proprietário')
        ADMIN = 'admin', _('Administrador')
        ATTENDANT = 'attendant', _('Atendente')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('usuário'),
        related_name='company_memberships'
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name=_('empresa')
    )

    role = models.CharField(
        _('papel'),
        max_length=20,
        choices=Role.choices,
        default=Role.ATTENDANT,
        help_text=_(
            'Proprietário: controle total. '
            'Administrador: gerencia mas não deleta. '
            'Atendente: apenas registra pontos.'
        )
    )

    is_active = models.BooleanField(
        _('ativo'),
        default=True,
        help_text=_('Se False, o usuário não pode mais acessar esta empresa')
    )

    class Meta:
        verbose_name = _('membro da empresa')
        verbose_name_plural = _('membros da empresa')
        ordering = ['company', 'role', 'user']
        unique_together = [['user', 'company']]  # Um usuário não pode ter 2 roles na mesma empresa
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['company', 'is_active']),
        ]

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.company.trade_name} ({self.get_role_display()})'

    def has_permission(self, permission):
        """
        Verifica se o membro tem uma determinada permissão.

        Permissões por role:
        - owner: tudo
        - admin: tudo exceto deletar empresa e modificar owners
        - attendant: apenas registrar pontos
        """
        permissions_map = {
            self.Role.OWNER: ['manage_company', 'manage_members', 'manage_points', 'delete_company'],
            self.Role.ADMIN: ['manage_company', 'manage_points'],
            self.Role.ATTENDANT: ['manage_points'],
        }

        return permission in permissions_map.get(self.role, [])


class CompanyTheme(BaseModel):
    """
    Configurações de tema/identidade visual da empresa.

    Cada empresa pode personalizar cores, logos e outros elementos visuais
    que serão renderizados no painel React e no app mobile.

    Abordagem híbrida:
    - Campos específicos para configurações principais (validação forte)
    - JSONField extra_config para configurações futuras/experimentais
    """

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='theme',
        verbose_name=_('empresa')
    )

    # =========================================================================
    # LOGOS E IMAGENS
    # =========================================================================
    logo_light = models.ImageField(
        _('logo (tema claro)'),
        upload_to='companies/themes/logos/',
        blank=True,
        null=True,
        help_text=_('Logo para fundos claros. Recomendado: PNG com transparência')
    )

    logo_dark = models.ImageField(
        _('logo (tema escuro)'),
        upload_to='companies/themes/logos/',
        blank=True,
        null=True,
        help_text=_('Logo para fundos escuros. Recomendado: PNG com transparência')
    )

    favicon = models.ImageField(
        _('favicon'),
        upload_to='companies/themes/favicons/',
        blank=True,
        null=True,
        help_text=_('Ícone do navegador. Recomendado: 32x32px ou 64x64px')
    )

    # =========================================================================
    # CORES PRINCIPAIS
    # =========================================================================
    primary_color = models.CharField(
        _('cor principal'),
        max_length=7,
        validators=[hex_color_validator],
        default='#1976D2',
        help_text=_('Cor principal da marca. Ex: #1976D2 (azul)')
    )

    secondary_color = models.CharField(
        _('cor secundária'),
        max_length=7,
        validators=[hex_color_validator],
        default='#424242',
        help_text=_('Cor secundária. Ex: #424242 (cinza escuro)')
    )

    accent_color = models.CharField(
        _('cor de destaque'),
        max_length=7,
        validators=[hex_color_validator],
        default='#FF5722',
        help_text=_('Cor de destaque/ação. Ex: #FF5722 (laranja)')
    )

    success_color = models.CharField(
        _('cor de sucesso'),
        max_length=7,
        validators=[hex_color_validator],
        default='#4CAF50',
        help_text=_('Cor para mensagens de sucesso. Ex: #4CAF50 (verde)')
    )

    warning_color = models.CharField(
        _('cor de aviso'),
        max_length=7,
        validators=[hex_color_validator],
        default='#FF9800',
        help_text=_('Cor para avisos. Ex: #FF9800 (laranja)')
    )

    error_color = models.CharField(
        _('cor de erro'),
        max_length=7,
        validators=[hex_color_validator],
        default='#F44336',
        help_text=_('Cor para erros. Ex: #F44336 (vermelho)')
    )

    # =========================================================================
    # CORES DE TEXTO
    # =========================================================================
    text_primary = models.CharField(
        _('texto principal'),
        max_length=7,
        validators=[hex_color_validator],
        default='#212121',
        help_text=_('Cor do texto principal. Ex: #212121 (preto)')
    )

    text_secondary = models.CharField(
        _('texto secundário'),
        max_length=7,
        validators=[hex_color_validator],
        default='#757575',
        help_text=_('Cor do texto secundário. Ex: #757575 (cinza)')
    )

    # =========================================================================
    # CORES DE FUNDO
    # =========================================================================
    background_color = models.CharField(
        _('fundo principal'),
        max_length=7,
        validators=[hex_color_validator],
        default='#FFFFFF',
        help_text=_('Cor do fundo principal. Ex: #FFFFFF (branco)')
    )

    background_secondary = models.CharField(
        _('fundo secundário'),
        max_length=7,
        validators=[hex_color_validator],
        default='#FAFAFA',
        help_text=_('Cor do fundo secundário. Ex: #FAFAFA (cinza muito claro)')
    )

    card_background = models.CharField(
        _('fundo de cartões'),
        max_length=7,
        validators=[hex_color_validator],
        default='#FFFFFF',
        help_text=_('Cor de fundo dos cards/cartões. Ex: #FFFFFF')
    )

    # =========================================================================
    # CUSTOMIZAÇÕES AVANÇADAS
    # =========================================================================
    custom_css = models.TextField(
        _('CSS customizado'),
        blank=True,
        help_text=_('CSS adicional para customizações avançadas (use com cuidado)')
    )

    extra_config = models.JSONField(
        _('configurações extras'),
        default=dict,
        blank=True,
        help_text=_(
            'Configurações adicionais em formato JSON. '
            'Ex: {"border_radius": "8px", "font_family": "Roboto"}'
        )
    )

    # =========================================================================
    # CONFIGURAÇÕES DE EXIBIÇÃO
    # =========================================================================
    is_active = models.BooleanField(
        _('tema ativo'),
        default=True,
        help_text=_('Se False, usa o tema padrão do sistema')
    )

    class Meta:
        verbose_name = _('tema da empresa')
        verbose_name_plural = _('temas das empresas')
        ordering = ['company']

    def __str__(self):
        return f'Tema: {self.company.trade_name}'

    def get_theme_dict(self):
        """
        Retorna todas as configurações do tema em formato de dicionário.
        Útil para serialização na API.
        """
        return {
            'logos': {
                'light': self.logo_light.url if self.logo_light else None,
                'dark': self.logo_dark.url if self.logo_dark else None,
                'favicon': self.favicon.url if self.favicon else None,
            },
            'colors': {
                'primary': self.primary_color,
                'secondary': self.secondary_color,
                'accent': self.accent_color,
                'success': self.success_color,
                'warning': self.warning_color,
                'error': self.error_color,
            },
            'text': {
                'primary': self.text_primary,
                'secondary': self.text_secondary,
            },
            'background': {
                'primary': self.background_color,
                'secondary': self.background_secondary,
                'card': self.card_background,
            },
            'extra': self.extra_config,
        }
