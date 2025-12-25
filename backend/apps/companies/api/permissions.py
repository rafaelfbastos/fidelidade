from rest_framework import permissions


class IsCompanyMemberWithPermission(permissions.BasePermission):
    """
    Permissão customizada para verificar se o usuário é membro da empresa
    e tem permissão adequada (owner ou admin).

    Regras:
    - Owner: pode tudo
    - Admin: pode editar, mas não deletar
    - Attendant: apenas leitura
    """

    def has_permission(self, request, view):
        # Usuário precisa estar autenticado
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Verifica se o usuário tem permissão sobre o objeto (Company ou CompanyTheme).
        """
        # Se for CompanyTheme, pegar a empresa relacionada
        if hasattr(obj, 'company'):
            company = obj.company
        else:
            company = obj

        # Buscar membership do usuário nesta empresa
        try:
            membership = company.companymember_set.get(
                user=request.user,
                is_active=True,
                deleted_at__isnull=True
            )
        except:
            return False  # Usuário não é membro desta empresa

        # Métodos seguros (GET, HEAD, OPTIONS) - todos os membros podem ler
        if request.method in permissions.SAFE_METHODS:
            return True

        # PUT, PATCH - owner e admin podem editar
        if request.method in ['PUT', 'PATCH']:
            return membership.role in ['owner', 'admin']

        # DELETE - apenas owner pode deletar
        if request.method == 'DELETE':
            return membership.role == 'owner'

        # POST (criar) - owner e admin
        if request.method == 'POST':
            return membership.role in ['owner', 'admin']

        return False


class CanManageCompanyTheme(permissions.BasePermission):
    """
    Permissão específica para gerenciar tema da empresa.
    Apenas owner e admin podem modificar.
    """

    message = "Apenas proprietários e administradores podem modificar o tema da empresa."

    def has_object_permission(self, request, view, obj):
        # Leitura permitida para todos os membros
        if request.method in permissions.SAFE_METHODS:
            return True

        # Pegar a empresa do tema
        company = obj.company

        # Verificar se usuário é owner ou admin
        try:
            membership = company.companymember_set.get(
                user=request.user,
                is_active=True,
                deleted_at__isnull=True
            )
            return membership.role in ['owner', 'admin']
        except:
            return False
