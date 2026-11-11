"""
Modelos de dados para o Projeto Amigos no Futebol — MVP.
Define o modelo de usuário customizado (com autenticação por e-mail)
e o modelo Aluno com relacionamento obrigatório com o responsável.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date


class UsuarioManager(BaseUserManager):
    """
    Gerenciador personalizado para o modelo Usuario onde o e-mail
    é o identificador único para autenticação.
    """

    def create_user(self, email, nome, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório para cadastrar o usuário.')
        if not nome:
            raise ValueError('O nome é obrigatório para cadastrar o usuário.')

        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome.strip(), **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('perfil', 'educador')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('O superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('O superusuário deve ter is_superuser=True.')

        return self.create_user(email, nome, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuário customizado com perfis definidos:
    - educador: acesso total ao cadastro, status e visualização geral.
    - responsavel: consulta restrita exclusivamente aos seus filhos.
    """

    PERFIL_CHOICES = (
        ('educador', 'Educador'),
        ('responsavel', 'Responsável'),
    )

    nome = models.CharField('Nome completo', max_length=150)
    email = models.EmailField('E-mail', unique=True)
    perfil = models.CharField(
        'Perfil de acesso',
        max_length=20,
        choices=PERFIL_CHOICES,
        default='responsavel'
    )
    is_active = models.BooleanField('Ativo', default=True)
    is_staff = models.BooleanField('Acesso administrativo', default=False)
    data_cadastro = models.DateTimeField('Data de cadastro', default=timezone.now)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_perfil_display()})"

    @property
    def is_educador(self):
        return self.perfil == 'educador'

    @property
    def is_responsavel(self):
        return self.perfil == 'responsavel'

    def has_module_perms(self, app_label):
        """Permite visualização dos módulos do Django Admin exclusivamente para educadores ativos."""
        if not self.is_active or self.perfil != 'educador':
            return False
        return True

    def has_perm(self, perm, obj=None):
        """Garante permissões administrativas exclusivamente para educadores ativos."""
        if not self.is_active or self.perfil != 'educador':
            return False
        return True


class Aluno(models.Model):
    """
    Representa as crianças e adolescentes beneficiários do projeto (6 a 17 anos).
    Possui relacionamento obrigatório com o responsável familiar.
    """

    STATUS_CHOICES = (
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
    )

    nome = models.CharField('Nome do aluno', max_length=150)
    data_nascimento = models.DateField('Data de nascimento')
    data_cadastro = models.DateTimeField('Data de cadastro', auto_now_add=True)
    status = models.CharField(
        'Status',
        max_length=10,
        choices=STATUS_CHOICES,
        default='ativo'
    )
    responsavel = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='alunos',
        limit_choices_to={'perfil': 'responsavel'},
        verbose_name='Responsável familiar'
    )

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_status_display()})"

    def clean(self):
        super().clean()
        if self.data_nascimento:
            hoje = date.today()
            if self.data_nascimento > hoje:
                raise ValidationError({
                    'data_nascimento': 'A data de nascimento não pode ser futura.'
                })
            idade = hoje.year - self.data_nascimento.year - (
                (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
            if idade < 6 or idade > 17:
                raise ValidationError({
                    'data_nascimento': (
                        f'A idade calculada é de {idade} anos. O Projeto Amigos no Futebol '
                        'atende exclusivamente crianças e adolescentes de 6 a 17 anos.'
                    )
                })

    @property
    def is_ativo(self):
        return self.status == 'ativo'
