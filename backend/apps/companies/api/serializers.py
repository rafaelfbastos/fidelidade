from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.companies.models import Company, CompanyMember, CompanyTheme

User = get_user_model()


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


class CompanyMemberUserSerializer(serializers.ModelSerializer):
    """
    Representação resumida do usuário associado a uma empresa.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
        ]
        read_only_fields = fields


class CompanyMemberSerializer(serializers.ModelSerializer):
    """
    Serializer principal para membros da empresa exibindo dados do usuário.
    """
    user = CompanyMemberUserSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CompanyMember
        fields = [
            'uuid',
            'role',
            'role_display',
            'is_active',
            'created_at',
            'user',
        ]
        read_only_fields = [
            'uuid',
            'role_display',
            'is_active',
            'created_at',
            'user',
        ]


class CompanyMemberCreateSerializer(serializers.Serializer):
    """
    Serializer usado para criar/associar usuários a uma empresa.
    """
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=CompanyMember.Role.choices, default=CompanyMember.Role.ATTENDANT)
    password = serializers.CharField(
        max_length=128,
        required=False,
        allow_blank=True,
        style={'input_type': 'password'}
    )

    default_error_messages = {
        'missing_name': 'Informe o nome do usuário para criar um novo cadastro.',
        'already_member': 'Este usuário já está associado à empresa.',
    }

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        attrs['email'] = email

        user_exists = User.objects.filter(email=email).exists()
        if not user_exists and not attrs.get('first_name'):
            raise ValidationError({'first_name': self.error_messages['missing_name']})
        return attrs

    def create(self, validated_data):
        company = self.context['company']
        email = validated_data['email']
        defaults = {
            'first_name': validated_data.get('first_name') or '',
            'last_name': validated_data.get('last_name') or '',
            'phone': validated_data.get('phone') or '',
        }

        user = User.objects.filter(email=email).first()
        if not user:
            password = validated_data.get('password') or None
            user = User.objects.create_user(email=email, password=password, **defaults)
        else:
            updated = False
            for field, value in defaults.items():
                if value and getattr(user, field) != value:
                    setattr(user, field, value)
                    updated = True
            if validated_data.get('password'):
                user.set_password(validated_data['password'])
                updated = True
            if updated:
                user.save()

        role = validated_data['role']

        try:
            membership = CompanyMember.all_objects.get(user=user, company=company)
            if membership.deleted_at:
                membership.restore()
        except CompanyMember.DoesNotExist:
            membership = CompanyMember(user=user, company=company)

        if membership.pk and membership.is_active and membership.deleted_at is None and membership.role == role:
            return membership

        membership.role = role
        membership.is_active = True
        membership.save()

        return membership


class CompanyMemberPasswordResetSerializer(serializers.Serializer):
    """
    Serializer utilizado para redefinir a senha de um membro específico.
    """
    password = serializers.CharField(
        min_length=8,
        max_length=128,
        style={'input_type': 'password'}
    )


class CompanyMemberPasswordResetResponseSerializer(serializers.Serializer):
    """
    Serializer de resposta para redefinição de senha.
    """
    password = serializers.CharField(read_only=True)


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
