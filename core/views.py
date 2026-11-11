"""
Views da aplicação Amigos no Futebol — MVP.
Controle estrito de permissões e segurança no servidor.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Aluno
from .forms import LoginForm, AlunoForm


def login_view(request):
    """
    TELA 1 — LOGIN
    Autentica usuários (educador ou responsável) utilizando e-mail e senha.
    Redireciona usuários já autenticados para a lista de alunos.
    """
    if request.user.is_authenticated:
        return redirect('lista_alunos')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('lista_alunos')
    else:
        form = LoginForm()

    context = {
        'form': form,
    }
    return render(request, 'login.html', context)


def logout_view(request):
    """
    Encerra a sessão do usuário com segurança e redireciona para a tela de login.
    """
    logout(request)
    messages.info(request, 'Você encerrou sua sessão com segurança.')
    return redirect('login')


@login_required
def lista_alunos_view(request):
    """
    TELA 3 — LISTA DE ALUNOS
    Regras de negócio:
    - O educador consulta todos os alunos (ativos e inativos).
    - O responsável consulta exclusivamente os alunos vinculados à sua própria conta.
    - Suporta busca por nome preservando o isolamento por perfil.
    """
    usuario = request.user
    termo_busca = request.GET.get('busca', '').strip()

    if usuario.is_educador:
        # Educador pode consultar todos os alunos
        alunos_query = Aluno.objects.all().select_related('responsavel')
    else:
        # Responsável consulta APENAS os alunos onde ele é o responsável registrado
        alunos_query = Aluno.objects.filter(responsavel=usuario)

    if termo_busca:
        alunos_query = alunos_query.filter(nome__icontains=termo_busca)

    alunos = alunos_query.order_by('nome')

    context = {
        'alunos': alunos,
        'termo_busca': termo_busca,
        'is_educador': usuario.is_educador,
        'total_alunos': alunos.count(),
    }
    return render(request, 'lista_alunos.html', context)


@login_required
def cadastro_aluno_view(request):
    """
    TELA 2 — CADASTRO DE ALUNO
    Acesso exclusivo do educador.
    Responsáveis recebem código 403 (Forbidden) no servidor.
    """
    if not request.user.is_educador:
        return HttpResponseForbidden(
            'Acesso negado. Apenas o educador responsável pelo projeto tem '
            'permissão para cadastrar novos alunos.'
        )

    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aluno cadastrado com sucesso!')
            return redirect('lista_alunos')
    else:
        form = AlunoForm()

    context = {
        'form': form,
    }
    return render(request, 'cadastro_aluno.html', context)


@login_required
@require_POST
def alternar_status_aluno_view(request, aluno_id):
    """
    Altera o status do aluno entre 'ativo' e 'inativo'.
    Acesso exclusivo do educador via requisição POST protegida por CSRF.
    """
    if not request.user.is_educador:
        return HttpResponseForbidden(
            'Acesso negado. Apenas o educador tem permissão para alterar o '
            'status de alunos.'
        )

    aluno = get_object_or_404(Aluno, id=aluno_id)
    if aluno.status == 'ativo':
        aluno.status = 'inativo'
        mensagem = f'O aluno {aluno.nome} foi marcado como inativo.'
    else:
        aluno.status = 'ativo'
        mensagem = f'O aluno {aluno.nome} foi ativado com sucesso.'

    aluno.save(update_fields=['status'])
    messages.success(request, mensagem)
    return redirect('lista_alunos')
