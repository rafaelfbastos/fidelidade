from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserRegistrationSerializer,
    ChangePasswordSerializer,
)


@extend_schema(
    tags=['auth'],
    summary='Login com email e senha',
    description='Autentica o usuário e retorna tokens JWT + dados do usuário com empresas e temas.',
    responses={200: CustomTokenObtainPairSerializer},
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login com email e senha.
    Retorna access token, refresh token e dados completos do usuário incluindo
    empresas que gerencia e seus respectivos temas visuais.
    """
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    tags=['auth'],
    summary='Registrar novo usuário',
    description='Cria uma nova conta de usuário e retorna tokens JWT.',
    responses={201: UserSerializer},
)
class UserRegistrationView(generics.CreateAPIView):
    """
    Registro de novos usuários.
    Cria a conta e retorna automaticamente os tokens de autenticação.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Gerar tokens para o usuário recém-criado
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        tags=['auth'],
        summary='Obter dados do usuário autenticado',
        description='Retorna informações completas do usuário incluindo empresas e temas.',
        responses={200: UserSerializer},
    ),
    patch=extend_schema(
        tags=['auth'],
        summary='Atualizar dados do usuário autenticado',
        description='Permite alterar nome e telefone do usuário autenticado.',
        responses={200: UserSerializer},
    ),
    put=extend_schema(
        tags=['auth'],
        summary='Atualizar dados do usuário autenticado',
        description='Permite alterar nome e telefone do usuário autenticado.',
        responses={200: UserSerializer},
    ),
)
class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Permite visualizar e atualizar os dados básicos do usuário autenticado.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(
    tags=['auth'],
    summary='Alterar senha do usuário autenticado',
    description='Valida a senha atual e atualiza a senha conforme regras do Django.',
    request=ChangePasswordSerializer,
)
class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Senha atualizada com sucesso.'}, status=status.HTTP_200_OK)


@extend_schema(
    tags=['auth'],
    summary='Logout do usuário',
    description='Invalida o refresh token adicionando-o à blacklist.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'refresh': {
                    'type': 'string',
                    'description': 'Refresh token para invalidar'
                }
            },
            'required': ['refresh']
        }
    },
    responses={
        200: {'description': 'Logout realizado com sucesso'},
        400: {'description': 'Token inválido ou ausente'}
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout do usuário.
    Adiciona o refresh token à blacklist para invalidá-lo.
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            {'message': 'Logout realizado com sucesso'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': 'Token inválido ou já expirado'},
            status=status.HTTP_400_BAD_REQUEST
        )
