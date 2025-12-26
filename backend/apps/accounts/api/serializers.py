from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


# Import necessário para evitar circular import
def get_user_company_serializer():
    from apps.companies.api.serializers import UserCompanySerializer
    return UserCompanySerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer customizado para login com JWT.
    Retorna access token, refresh token e informações do usuário.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Adicionar claims customizados ao token
        token['email'] = user.email
        token['name'] = user.get_full_name()

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Adicionar informações completas do usuário (com empresas e temas)
        user_serializer = UserSerializer(self.user, context={'request': self.context.get('request')})
        data['user'] = user_serializer.data

        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para visualização de dados do usuário.
    Inclui empresas que o usuário gerencia com roles e temas.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    companies = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'is_active',
            'date_joined',
            'companies',  # Lista de empresas que o usuário gerencia
        ]
        read_only_fields = [
            'id',
            'email',
            'date_joined',
            'companies',
            'full_name',
            'is_active',
        ]

    def get_companies(self, obj):
        """
        Retorna todas as empresas que o usuário gerencia (através de CompanyMember).
        Inclui: dados da empresa, role do usuário e tema da empresa.
        """
        UserCompanySerializer = get_user_company_serializer()

        # Buscar apenas memberships ativos
        memberships = obj.company_memberships.filter(
            is_active=True,
            deleted_at__isnull=True
        ).select_related('company').order_by('company__trade_name')

        return UserCompanySerializer(
            memberships,
            many=True,
            context=self.context
        ).data

    def update(self, instance, validated_data):
        """
        Limita atualização do perfil a campos básicos.
        """
        allowed_fields = {'first_name', 'last_name', 'phone'}
        updated_fields = []
        for field in allowed_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
                updated_fields.append(field)
        if updated_fields:
            instance.save(update_fields=updated_fields)
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'phone',
            'password',
            'password_confirm',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password': 'As senhas não coincidem.'
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para alteração de senha do usuário autenticado.
    """
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Senha atual incorreta.')
        return value

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('new_password_confirm')

        if new_password != confirm_password:
            raise serializers.ValidationError({'new_password_confirm': 'As senhas não coincidem.'})

        from django.contrib.auth.password_validation import validate_password

        validate_password(new_password, self.context['request'].user)
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user
