"""
Views da aplicação Amigos no Futebol — MVP.
Controle estrito de permissões e segurança no servidor.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, FileResponse
from django.contrib import messages
from .models import Aluno, FotoAtividade
from .forms import LoginForm, AlunoForm, ResponsavelForm, AlunoPerfilForm, FotoAtividadeForm


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
        form = AlunoForm(request.POST, request.FILES)
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


@login_required
def cadastro_responsavel_view(request):
    """
    Cadastro de responsáveis realizado exclusivamente pelo educador.
    """
    if not request.user.is_educador:
        return HttpResponseForbidden(
            'Acesso negado. Apenas o educador pode cadastrar responsáveis.'
        )

    if request.method == 'POST':
        form = ResponsavelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Responsável cadastrado com sucesso!')
            return redirect('lista_alunos')
    else:
        form = ResponsavelForm()

    return render(request, 'cadastro_responsavel.html', {'form': form})

@login_required
def perfil_aluno_view(request, aluno_id):
    if request.user.is_educador:
        aluno = get_object_or_404(Aluno, id=aluno_id)
    else:
        aluno = get_object_or_404(
            Aluno,
            id=aluno_id,
            responsavel=request.user
        )

    if request.method == 'POST':
        form = AlunoPerfilForm(
            request.POST,
            request.FILES,
            instance=aluno
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Informações do aluno atualizadas com sucesso!'
            )
            return redirect('perfil_aluno', aluno_id=aluno.id)
    else:
        form = AlunoPerfilForm(instance=aluno)

    return render(
        request,
        'perfil_aluno.html',
        {
            'aluno': aluno,
            'form': form,
        }
    )

@login_required
def foto_aluno_view(request, aluno_id):
    if request.user.is_educador:
        aluno = get_object_or_404(Aluno, id=aluno_id)
    else:
        aluno = get_object_or_404(
            Aluno,
            id=aluno_id,
            responsavel=request.user
        )

    if not aluno.foto:
        return get_object_or_404(Aluno, id=-1)

    import mimetypes

    tipo_conteudo = (
        mimetypes.guess_type(aluno.foto.name)[0]
        or 'application/octet-stream'
    )

    return FileResponse(
        aluno.foto.open('rb'),
        content_type=tipo_conteudo
    )

@login_required
def galeria_atividades_view(request):
    fotos = FotoAtividade.objects.select_related('educador').order_by(
        '-data_publicacao'
    )

    return render(
        request,
        'galeria_atividades.html',
        {
            'fotos': fotos,
            'is_educador': request.user.is_educador,
        }
    )

@login_required
def foto_atividade_view(request, foto_id):
    foto = get_object_or_404(FotoAtividade, id=foto_id)

    import mimetypes

    tipo_conteudo = (
        mimetypes.guess_type(foto.foto.name)[0]
        or 'application/octet-stream'
    )

    return FileResponse(
        foto.foto.open('rb'),
        content_type=tipo_conteudo
    )

@login_required
def publicar_foto_view(request):
    if not request.user.is_educador:
        return HttpResponseForbidden(
            'Somente educadores podem publicar fotos.'
        )

    if request.method == 'POST':
        form = FotoAtividadeForm(request.POST, request.FILES)

        if form.is_valid():
            fotos = form.cleaned_data['foto']
            legenda = form.cleaned_data['legenda']

            for arquivo in fotos:
                FotoAtividade.objects.create(
                    foto=arquivo,
                    legenda=legenda,
                    educador=request.user
                )

            messages.success(
                request,
                f'{len(fotos)} foto(s) publicada(s) com sucesso!'
            )
            return redirect('galeria_atividades')
    else:
        form = FotoAtividadeForm()

    return render(
        request,
        'publicar_foto.html',
        {'form': form}
    )