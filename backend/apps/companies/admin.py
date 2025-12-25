from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Company, CompanyMember, CompanyTheme


class CompanyMemberInline(admin.TabularInline):
    """
    Inline para gerenciar membros diretamente na tela de edição da empresa.
    """
    model = CompanyMember
    extra = 0
    fields = ['user', 'role', 'is_active']
    autocomplete_fields = ['user']
    verbose_name = _('Membro')
    verbose_name_plural = _('Membros da Empresa')


class CompanyThemeInline(admin.StackedInline):
    """
    Inline para gerenciar o tema da empresa diretamente na tela de edição.
    """
    model = CompanyTheme
    extra = 0
    can_delete = False
    verbose_name = _('Tema Visual')
    verbose_name_plural = _('Tema Visual')

    fieldsets = (
        (_('Logos'), {
            'fields': ('logo_light', 'logo_dark', 'favicon')
        }),
        (_('Cores Principais'), {
            'fields': (
                ('primary_color', 'secondary_color', 'accent_color'),
                ('success_color', 'warning_color', 'error_color'),
            )
        }),
        (_('Cores de Texto'), {
            'fields': (('text_primary', 'text_secondary'),)
        }),
        (_('Cores de Fundo'), {
            'fields': (('background_color', 'background_secondary', 'card_background'),)
        }),
        (_('Avançado'), {
            'fields': ('custom_css', 'extra_config', 'is_active'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar empresas do programa de fidelidade.
    """

    list_display = [
        'trade_name',
        'cnpj',
        'city',
        'state',
        'points_per_real',
        'is_active',
        'created_at'
    ]

    list_filter = [
        'is_active',
        'state',
        'created_at',
        'deleted_at'
    ]

    search_fields = [
        'trade_name',
        'legal_name',
        'cnpj',
        'email',
        'city'
    ]

    readonly_fields = ['uuid', 'created_at', 'updated_at', 'deleted_at']

    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('uuid', 'trade_name', 'legal_name', 'cnpj')
        }),
        (_('Contato'), {
            'fields': ('email', 'phone')
        }),
        (_('Endereço'), {
            'fields': ('address', 'city', 'state', 'zip_code'),
            'classes': ('collapse',)
        }),
        (_('Programa de Fidelidade'), {
            'fields': ('logo', 'points_per_real', 'is_active')
        }),
        (_('Auditoria'), {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [CompanyMemberInline, CompanyThemeInline]

    # Permite busca rápida de empresas em outros admins
    search_help_text = _('Buscar por nome fantasia, razão social, CNPJ, email ou cidade')

    def get_queryset(self, request):
        """
        Mostra empresas deletadas também (soft delete)
        """
        return Company.all_objects.all()


@admin.register(CompanyMember)
class CompanyMemberAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar relacionamento entre usuários e empresas.
    """

    list_display = [
        'user',
        'company',
        'role',
        'is_active',
        'created_at'
    ]

    list_filter = [
        'role',
        'is_active',
        'created_at'
    ]

    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'company__trade_name',
        'company__cnpj'
    ]

    autocomplete_fields = ['user', 'company']

    readonly_fields = ['uuid', 'created_at', 'updated_at', 'deleted_at']

    fieldsets = (
        (_('Relacionamento'), {
            'fields': ('uuid', 'user', 'company')
        }),
        (_('Permissões'), {
            'fields': ('role', 'is_active')
        }),
        (_('Auditoria'), {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """
        Mostra membros deletados também (soft delete)
        """
        return CompanyMember.all_objects.all()


@admin.register(CompanyTheme)
class CompanyThemeAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar temas das empresas.
    """

    list_display = [
        'company',
        'primary_color_display',
        'secondary_color_display',
        'is_active',
        'created_at'
    ]

    list_filter = [
        'is_active',
        'created_at'
    ]

    search_fields = [
        'company__trade_name',
        'company__cnpj'
    ]

    autocomplete_fields = ['company']

    readonly_fields = ['uuid', 'created_at', 'updated_at', 'deleted_at', 'preview_colors']

    fieldsets = (
        (_('Empresa'), {
            'fields': ('uuid', 'company')
        }),
        (_('Logos'), {
            'fields': ('logo_light', 'logo_dark', 'favicon')
        }),
        (_('Cores Principais'), {
            'fields': (
                'preview_colors',
                ('primary_color', 'secondary_color', 'accent_color'),
                ('success_color', 'warning_color', 'error_color'),
            )
        }),
        (_('Cores de Texto'), {
            'fields': (('text_primary', 'text_secondary'),)
        }),
        (_('Cores de Fundo'), {
            'fields': (('background_color', 'background_secondary', 'card_background'),)
        }),
        (_('Customizações Avançadas'), {
            'fields': ('custom_css', 'extra_config'),
            'classes': ('collapse',)
        }),
        (_('Configurações'), {
            'fields': ('is_active',)
        }),
        (_('Auditoria'), {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def primary_color_display(self, obj):
        """Mostra a cor principal com preview visual"""
        from django.utils.html import format_html
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; color: white; border-radius: 3px;">{}</span>',
            obj.primary_color,
            obj.primary_color
        )
    primary_color_display.short_description = _('Cor Principal')

    def secondary_color_display(self, obj):
        """Mostra a cor secundária com preview visual"""
        from django.utils.html import format_html
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; color: white; border-radius: 3px;">{}</span>',
            obj.secondary_color,
            obj.secondary_color
        )
    secondary_color_display.short_description = _('Cor Secundária')

    def preview_colors(self, obj):
        """Preview de todas as cores do tema"""
        from django.utils.html import format_html
        if obj.pk:
            return format_html(
                '''
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <div style="text-align: center;">
                        <div style="background-color: {}; width: 60px; height: 60px; border-radius: 5px; border: 1px solid #ddd;"></div>
                        <small>Principal</small>
                    </div>
                    <div style="text-align: center;">
                        <div style="background-color: {}; width: 60px; height: 60px; border-radius: 5px; border: 1px solid #ddd;"></div>
                        <small>Secundária</small>
                    </div>
                    <div style="text-align: center;">
                        <div style="background-color: {}; width: 60px; height: 60px; border-radius: 5px; border: 1px solid #ddd;"></div>
                        <small>Destaque</small>
                    </div>
                    <div style="text-align: center;">
                        <div style="background-color: {}; width: 60px; height: 60px; border-radius: 5px; border: 1px solid #ddd;"></div>
                        <small>Sucesso</small>
                    </div>
                    <div style="text-align: center;">
                        <div style="background-color: {}; width: 60px; height: 60px; border-radius: 5px; border: 1px solid #ddd;"></div>
                        <small>Aviso</small>
                    </div>
                    <div style="text-align: center;">
                        <div style="background-color: {}; width: 60px; height: 60px; border-radius: 5px; border: 1px solid #ddd;"></div>
                        <small>Erro</small>
                    </div>
                </div>
                ''',
                obj.primary_color,
                obj.secondary_color,
                obj.accent_color,
                obj.success_color,
                obj.warning_color,
                obj.error_color
            )
        return '-'
    preview_colors.short_description = _('Preview das Cores')

    def get_queryset(self, request):
        """
        Mostra temas deletados também (soft delete)
        """
        return CompanyTheme.all_objects.all()
