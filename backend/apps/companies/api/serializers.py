from rest_framework import serializers
from apps.companies.models import Company, CompanyMember, CompanyTheme
from django.core.validators import RegexValidator


class CompanyThemeSerializer(serializers.ModelSerializer):
    """
    Serializer para o tema da empresa.
    Retorna todas as configurações visuais.
    """
    logos = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    background = serializers.SerializerMethodField()

    class Meta:
        model = CompanyTheme
        fields = [
            'uuid',
            'logos',
            'colors',
            'text',
            'background',
            'custom_css',
            'extra_config',
            'is_active',
        ]

    def get_logos(self, obj):
        request = self.context.get('request')
        return {
            'light': request.build_absolute_uri(obj.logo_light.url) if obj.logo_light else None,
            'dark': request.build_absolute_uri(obj.logo_dark.url) if obj.logo_dark else None,
            'favicon': request.build_absolute_uri(obj.favicon.url) if obj.favicon else None,
        }

    def get_colors(self, obj):
        return {
            'primary': obj.primary_color,
            'secondary': obj.secondary_color,
            'accent': obj.accent_color,
            'success': obj.success_color,
            'warning': obj.warning_color,
            'error': obj.error_color,
        }

    def get_text(self, obj):
        return {
            'primary': obj.text_primary,
            'secondary': obj.text_secondary,
        }

    def get_background(self, obj):
        return {
            'primary': obj.background_color,
            'secondary': obj.background_secondary,
            'card': obj.card_background,
        }


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer básico para Company.
    """
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'uuid',
            'trade_name',
            'legal_name',
            'cnpj',
            'email',
            'phone',
            'address',
            'city',
            'state',
            'zip_code',
            'logo',
            'points_per_real',
            'is_active',
        ]

    def get_logo(self, obj):
        request = self.context.get('request')
        if obj.logo:
            return request.build_absolute_uri(obj.logo.url)
        return None


class UserCompanySerializer(serializers.ModelSerializer):
    """
    Serializer para empresas do usuário (com role e tema).
    Usado em UserSerializer para mostrar empresas que o usuário gerencia.
    """
    company = CompanySerializer(read_only=True)
    theme = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CompanyMember
        fields = [
            'uuid',
            'company',
            'role',
            'role_display',
            'theme',
            'is_active',
            'created_at',
        ]

    def get_theme(self, obj):
        """
        Retorna o tema da empresa se existir.
        """
        try:
            theme = obj.company.theme
            return CompanyThemeSerializer(theme, context=self.context).data
        except CompanyTheme.DoesNotExist:
            return None


class CompanyThemeUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para atualização do tema da empresa.
    Permite que owner/admin modifiquem as configurações visuais.
    """

    class Meta:
        model = CompanyTheme
        fields = [
            'logo_light',
            'logo_dark',
            'favicon',
            'primary_color',
            'secondary_color',
            'accent_color',
            'success_color',
            'warning_color',
            'error_color',
            'text_primary',
            'text_secondary',
            'background_color',
            'background_secondary',
            'card_background',
            'custom_css',
            'extra_config',
            'is_active',
        ]

    def validate_primary_color(self, value):
        """Validação adicional de cor HEX"""
        hex_validator = RegexValidator(
            regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
            message='Cor deve estar no formato HEX. Ex: #FF5733'
        )
        hex_validator(value)
        return value

    def validate_secondary_color(self, value):
        hex_validator = RegexValidator(
            regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
            message='Cor deve estar no formato HEX. Ex: #FF5733'
        )
        hex_validator(value)
        return value
