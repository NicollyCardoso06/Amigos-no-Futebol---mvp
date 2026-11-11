# Projeto Amigos no Futebol — MVP

Sistema web desenvolvido para o **Projeto Amigos no Futebol**, sob responsabilidade do educador social **Rafael Moreira**.

O objetivo do sistema é facilitar o cadastro e a consulta organizada de crianças e adolescentes (exclusivamente de **6 a 17 anos**) atendidos pelo projeto, permitindo que o educador gerencie os registros e que os responsáveis familiares consultem com segurança as informações dos seus respectivos filhos.

---

## 1. Tecnologias Utilizadasx

- **Linguagem:** Python 3.12
- **Framework Web:** Django 5.2 LTS
- **Banco de Dados:** PostgreSQL
- **Apresentação:** HTML5 semântico e CSS3
- **Framework Visual:** Bootstrap 5.3 (via CDN) e Bootstrap Icons
- **Autenticação:** Sistema nativo do Django com modelo customizado por e-mail
- **Servidor WSGI:** `config/wsgi.py` padrão

> **Nota de Arquitetura:** O projeto adota uma arquitetura monolítica organizada em camadas (MVT), sem frameworks JavaScript externos, sem APIs REST, sem SQLite definitivo e sem arquivos desnecessários.

---

## 2. Estrutura do Projeto

```text
amigos_no_futebol/
│
├── manage.py                     # Ponto de entrada CLI do Django
├── requirements.txt              # Dependências estritas (Django 5.2 LTS e psycopg)
├── .gitignore                    # Regras para Python, Django e segredos
├── .env.example                  # Template das variáveis de ambiente obrigatórias
├── README.md                     # Documentação do projeto
│
├── config/
│   ├── __init__.py
│   ├── settings.py               # Configurações do Django (SECRET_KEY obrigatória via ambiente)
│   ├── urls.py                   # Roteamento raiz do projeto
│   └── wsgi.py                   # Ponto de entrada WSGI da aplicação
│
├── core/
│   ├── __init__.py
│   ├── apps.py                   # Configuração da aplicação core
│   ├── models.py                 # Modelos Usuario (autenticação por e-mail) e Aluno (6 a 17 anos)
│   ├── forms.py                  # Formulários com validação estrita no servidor
│   ├── views.py                  # Views com controle rigoroso de acesso por perfil
│   ├── urls.py                   # Rotas internas da aplicação
│   ├── admin.py                  # Django Admin restrito exclusivamente a educadores
│   ├── tests.py                  # Suíte completa de testes funcionais e de segurança
│   └── migrations/
│       ├── __init__.py
│       └── 0001_initial.py       # Migração inicial gerada para PostgreSQL
│
├── templates/
│   ├── base.html                 # Estrutura base com Bootstrap 5.3 e logo oficial
│   ├── login.html                # Tela 1: Login seguro por e-mail e senha
│   ├── cadastro_aluno.html       # Tela 2: Cadastro de aluno (exclusivo do educador)
│   └── lista_alunos.html         # Tela 3: Listagem de alunos com identificação de status
│
└── static/
    ├── css/
    │   └── style.css             # Estilização oficial (Azul-marinho, Dourado e Branco)
    └── images/
        └── logo-amigos-no-futebol.png  # Logo oficial do Projeto Amigos no Futebol
```

---

## 3. Requisitos para Instalação

Para executar o projeto no **Windows** utilizando **VS Code** e **PowerShell**:

1. **Python 3.12** instalado (com a opção *"Add python.exe to PATH"* marcada).
2. **PostgreSQL** instalado e em execução (versão 15 ou superior).
3. **Git** para controle de versão.

---

## 4. Passo a Passo de Instalação e Execução

Abra o terminal **PowerShell** na pasta raiz do projeto:

### Passo 1: Criar e Ativar o Ambiente Virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*(Caso o PowerShell bloqueie a execução de scripts, execute previamente: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`)*

### Passo 2: Instalar as Dependências

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Passo 3: Criar o Banco de Dados no PostgreSQL

No terminal do PostgreSQL (`psql`) ou via pgAdmin:

```sql
CREATE DATABASE amigos_no_futebol;
```

### Passo 4: Configurar as Variáveis de Ambiente no PowerShell

O projeto exige a variável `SECRET_KEY` configurada no ambiente (sem fallback padrão insecure):

```powershell
$env:SECRET_KEY="sua_chave_secreta_segura_gerada_aqui"
$env:DEBUG="True"
$env:ALLOWED_HOSTS="localhost,127.0.0.1"

$env:DB_NAME="amigos_no_futebol"
$env:DB_USER="postgres"
$env:DB_PASSWORD="sua_senha_do_postgres"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
```

### Passo 5: Criar e Aplicar as Migrações

```powershell
python manage.py makemigrations core
python manage.py migrate
```

### Passo 6: Criar o Primeiro Usuário Educador

```powershell
python manage.py createsuperuser
```

Informe o e-mail, nome e senha para o educador (ex: `educador@amigosnofutebol.org`).

### Passo 7: Iniciar o Servidor

```powershell
python manage.py runserver
```

Acesse no navegador:
- **Aplicação Principal:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Painel Administrativo:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

