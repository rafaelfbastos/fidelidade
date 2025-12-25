import uuid
from django.db import models
from django.utils import timezone


class UUIDMixin(models.Model):
    """
    Mixin que adiciona campo UUID para exposição externa segura.
    Use o UUID nas URLs da API ao invés do ID numérico.
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="UUID"
    )

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    """
    Mixin que adiciona campos de timestamp para rastreamento de criação e atualização.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Manager customizado que filtra registros soft-deleted por padrão.
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteMixin(models.Model):
    """
    Mixin que adiciona funcionalidade de soft delete.
    Registros não são deletados do banco, apenas marcados como deletados.
    """
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Deletado em"
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Sobrescreve o delete padrão para fazer soft delete.
        """
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self):
        """
        Deleta o registro permanentemente do banco de dados.
        """
        super().delete()

    def restore(self):
        """
        Restaura um registro soft-deleted.
        """
        self.deleted_at = None
        self.save()

    @property
    def is_deleted(self):
        """
        Retorna True se o registro foi soft-deleted.
        """
        return self.deleted_at is not None


class TimeStampedModel(TimeStampedMixin):
    """
    Modelo base apenas com timestamp.
    Use para: logs, histórico, configurações, tabelas auxiliares.
    """
    class Meta:
        abstract = True


class BaseModel(UUIDMixin, TimeStampedMixin, SoftDeleteMixin):
    """
    Modelo base completo com UUID + timestamp + soft delete.
    Use para: dados de negócio principais expostos na API
    (empresas, usuários, produtos, transações, recompensas, etc).

    - id: PK interna (int) para JOINs e performance
    - uuid: Identificador externo seguro para API
    - created_at/updated_at: Auditoria temporal
    - deleted_at: Soft delete para recuperação
    """
    class Meta:
        abstract = True
