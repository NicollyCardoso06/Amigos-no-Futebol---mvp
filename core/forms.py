"""
Formulários da aplicação Amigos no Futebol.
Implementa a validação no servidor com mensagens em português
e formatação para Bootstrap 5.3 com requisitos de acessibilidade.
"""

from datetime import date
from django import forms
from django.contrib.auth import authenticate
from .models import Aluno, Usuario


class LoginForm(forms.Form):
    """
    Formulário de login seguro por e-mail e senha.
    """

    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu e-mail',
            'autocomplete': 'email',
            'required': 'required',
            'aria-required': 'true',
            'id': 'id_email',
        }),
        error_messages={
            'required': 'Por favor, informe seu e-mail.',
            'invalid': 'Informe um endereço de e-mail válido.',
        }
    )

    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha',
            'autocomplete': 'current-password',
            'required': 'required',
            'aria-required': 'true',
            'id': 'id_senha',
        }),
        error_messages={
            'required': 'Por favor, informe sua senha.',
        }
    )

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        senha = cleaned_data.get('senha')

        if email and senha:
            self.user_cache = authenticate(username=email, password=senha)
            if self.user_cache is None:
                raise forms.ValidationError(
                    'E-mail ou senha incorretos. Por favor, verifique os dados informados.',
                    code='invalid_login'
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    'Esta conta de usuário está inativa. Entre em contato com a coordenação.',
                    code='inactive'
                )

        return cleaned_data

    def get_user(self):
        return self.user_cache


class AlunoForm(forms.ModelForm):
    """
    Formulário de cadastro e validação de alunos (acesso exclusivo do educador).
    """

    class Meta:
        model = Aluno
        fields = ['nome', 'data_nascimento', 'responsavel']
        labels = {
            'nome': 'Nome do Aluno',
            'data_nascimento': 'Data de Nascimento',
            'responsavel': 'Responsável',
        }
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome do aluno',
                'required': 'required',
                'aria-required': 'true',
                'id': 'id_nome',
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required',
                'aria-required': 'true',
                'id': 'id_data_nascimento',
            }),
            'responsavel': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'aria-required': 'true',
                'id': 'id_responsavel',
            }),
        }
        error_messages = {
            'nome': {
                'required': 'O nome do aluno é obrigatório.',
                'max_length': 'O nome não pode exceder 150 caracteres.',
            },
            'data_nascimento': {
                'required': 'A data de nascimento é obrigatória.',
                'invalid': 'Informe uma data de nascimento válida no formato DD/MM/AAAA.',
            },
            'responsavel': {
                'required': 'Selecione um responsável cadastrado.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limita a lista de opções estritamente a usuários com perfil de 'responsavel' ativos
        self.fields['responsavel'].queryset = Usuario.objects.filter(
            perfil='responsavel',
            is_active=True
        ).order_by('nome')
        self.fields['responsavel'].empty_label = 'Selecione o responsável'

    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        if data_nascimento:
            hoje = date.today()
            if data_nascimento > hoje:
                raise forms.ValidationError('A data de nascimento não pode ser futura.')
            idade = hoje.year - data_nascimento.year - (
                (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day)
            )
            if idade < 6 or idade > 17:
                raise forms.ValidationError(
                    f'Idade inválida ({idade} anos). O Projeto Amigos no Futebol '
                    'atende exclusivamente crianças e adolescentes de 6 a 17 anos.'
                )
        return data_nascimento
