from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Manager customizado para CustomUser onde o email é o identificador único.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Cria e salva um usuário com email e senha.
        """
        if not email:
            raise ValueError(_('O email é obrigatório'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Cria e salva um superusuário com email e senha.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superusuário precisa ter is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superusuário precisa ter is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Modelo de usuário customizado onde o email é usado para autenticação.

    Este é o modelo base para TODOS os usuários do sistema:
    - Gerentes/donos de empresas
    - Atendentes
    - Clientes finais (usuários do app)

    Perfis específicos (CompanyMember, Customer) são criados separadamente.
    """

    # Remove o campo username (não vamos usar)
    username = None

    # Email como identificador único
    email = models.EmailField(
        _('email'),
        unique=True,
        error_messages={
            'unique': _('Já existe um usuário com este email.'),
        }
    )

    # Nome completo do usuário
    first_name = models.CharField(_('nome'), max_length=150)
    last_name = models.CharField(_('sobrenome'), max_length=150, blank=True)

    # Telefone (opcional, mas útil para recuperação de conta)
    phone = models.CharField(
        _('telefone'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Telefone com DDD. Ex: (11) 99999-9999')
    )

    # Data de criação já vem do AbstractUser (date_joined)
    # is_active, is_staff, is_superuser também vêm do AbstractUser

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']  # Campos obrigatórios além de email e password

    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Retorna o nome completo do usuário.
        """
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email

    def get_short_name(self):
        """
        Retorna o primeiro nome do usuário.
        """
        return self.first_name or self.email.split('@')[0]
