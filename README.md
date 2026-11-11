# Projeto Amigos no Futebol — MVP

Sistema web desenvolvido para auxiliar no gerenciamento de alunos e responsáveis de um projeto social esportivo.

## 1. Tecnologias utilizadas

- Python 3.12 ou superior
- Django 5.2
- PostgreSQL
- psycopg 3
- HTML5
- CSS3
- Bootstrap 5.3

## 2. Funcionalidades

- Login com autenticação por e-mail e senha.
- Cadastro de usuários com perfil de educador e responsável.
- Cadastro de responsáveis pelo educador.
- Cadastro de alunos vinculados aos responsáveis.
- Listagem de alunos.
- Controle de acesso conforme o perfil do usuário.
- Visualização dos alunos vinculados ao responsável autenticado.
- Ativação e desativação de alunos.

## 3. Estrutura do projeto

```text
Amigos-no-Futebol---mvp/
│
├── config/
│   ├── settings.py
│   ├── settings_local.py
│   ├── urls.py
│   └── ...
│
├── core/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── lista_alunos.html
│   ├── cadastro_aluno.html
│   └── cadastro_responsavel.html
│
├── static/
├── manage.py
├── requirements.txt
└── README.md
```

## 4. Requisitos

- Python 3.12 ou superior.
- PostgreSQL.
- Git.

## 5. Instalação e configuração

Clone o repositório:

```bash
git clone https://github.com/NicollyCardoso06/Amigos-no-Futebol---mvp.git
cd Amigos-no-Futebol---mvp
```

Crie e ative um ambiente virtual.

No Windows:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## 6. Configuração do banco de dados

Crie um banco de dados PostgreSQL com o nome:

```sql
CREATE DATABASE amigos_no_futebol;
```

Configure as variáveis de ambiente no PowerShell:

```powershell
$env:SECRET_KEY="sua_chave_secreta_segura"
$env:DEBUG="True"
$env:ALLOWED_HOSTS="localhost,127.0.0.1"

$env:DB_NAME="amigos_no_futebol"
$env:DB_USER="postgres"
$env:DB_PASSWORD="sua_senha_do_postgres"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
```

Substitua os valores de exemplo pelas configurações do seu ambiente. Não compartilhe nem publique senhas ou chaves secretas.

## 7. Migrações e criação do educador

Aplique as migrações:

```bash
python manage.py migrate
```

Crie o primeiro usuário educador:

```bash
python manage.py createsuperuser
```

Informe os dados solicitados pelo Django.

## 8. Executar o projeto

Inicie o servidor:

```bash
python manage.py runserver
```

Acesse:

```text
http://127.0.0.1:8000/
```

## 9. Ambiente de desenvolvimento no GitHub Codespaces

Para executar utilizando as configurações locais do Codespaces, configure a variável `SECRET_KEY` e execute:

```bash
python manage.py migrate --settings=config.settings_local
python manage.py runserver 0.0.0.0:8000 --settings=config.settings_local
```

O ambiente local utiliza configurações próprias, separadas das configurações principais do PostgreSQL.

## 10. Testes

Execute a suíte de testes:

```bash
python manage.py test --settings=config.settings_local
```

Para verificar a cobertura de testes, instale o Coverage:

```bash
python -m pip install coverage
```

Execute:

```bash
coverage run manage.py test --settings=config.settings_local
coverage report
```

## 11. Controle de acesso

O sistema possui dois perfis principais:

**Educador**
- Pode cadastrar responsáveis.
- Pode cadastrar alunos.
- Pode visualizar os alunos cadastrados.
- Pode alterar o status dos alunos.

**Responsável**
- Pode acessar o sistema com seu e-mail e senha.
- Visualiza somente os alunos vinculados ao seu cadastro.

## 12. Observações

Este projeto corresponde a um MVP (Produto Mínimo Viável), desenvolvido com Django e organizado segundo o padrão MVT (Model-View-Template).

As configurações locais de desenvolvimento não devem ser confundidas com as configurações destinadas ao uso com PostgreSQL.

Arquivos que contenham senhas, chaves secretas e bancos de dados locais não devem ser publicados no repositório.