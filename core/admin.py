"""
Configuração do Django Admin para o Projeto Amigos no Futebol.
Permite ao educador cadastrar e gerenciar contas de responsáveis e alunos.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Aluno, FotoAtividade


def educador_admin_has_permission(request):
    """
    Garante que SOMENTE o educador autorizado e ativo possa acessar o Django Admin,
    bloqueando explicitamente responsáveis mesmo que eventualmente possuam is_staff=True.
    """
    return bool(
        request.user.is_authenticated and
        request.user.is_active and
        request.user.is_staff and
        getattr(request.user, 'perfil', None) == 'educador'
    )


admin.site.has_permission = educador_admin_has_permission


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Administração personalizada do modelo Usuario para cadastro
    de educadores e responsáveis com autenticação por e-mail.
    """
    list_display = ('nome', 'email', 'perfil', 'is_active', 'is_staff', 'data_cadastro')
    list_filter = ('perfil', 'is_active', 'is_staff')
    search_fields = ('nome', 'email')
    ordering = ('nome',)

    fieldsets = (
        ('Identificação', {'fields': ('nome', 'email', 'password')}),
        ('Perfil e Permissões', {'fields': ('perfil', 'is_active', 'is_staff', 'is_superuser')}),
        ('Datas Importantes', {'fields': ('last_login', 'data_cadastro')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nome', 'email', 'perfil', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('data_cadastro', 'last_login')


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    """
    Administração do cadastro de alunos.
    """
    list_display = ('nome', 'data_nascimento', 'responsavel', 'status', 'data_cadastro')
    list_filter = ('status', 'data_cadastro')
    search_fields = ('nome', 'responsavel__nome', 'responsavel__email')
    ordering = ('nome',)

    fieldsets = (
        ('Dados do Aluno', {
            'fields': ('nome', 'data_nascimento', 'responsavel', 'status')
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "responsavel":
            kwargs["queryset"] = Usuario.objects.filter(perfil='responsavel', is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(FotoAtividade)
class FotoAtividadeAdmin(admin.ModelAdmin):
    list_display = ('legenda', 'educador', 'data_publicacao')
    list_filter = ('data_publicacao',)
    search_fields = ('legenda', 'educador__nome')
    ordering = ('-data_publicacao',)
    readonly_fields = ('data_publicacao',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.educador = request.user
        super().save_model(request, obj, form, change)