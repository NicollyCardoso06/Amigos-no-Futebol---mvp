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

## 5. Instalação

Clone o repositório:

```bash
git clone https://github.com/NicollyCardoso06/Amigos-no-Futebol---mvp.git
cd Amigos-no-Futebol---mvp
```

Crie um ambiente virtual:

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

Substitua os valores de exemplo pelas configurações do seu ambiente. Não publique senhas ou chaves secretas.

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

http://127.0.0.1:8000/

## 9. Ambiente de desenvolvimento no GitHub Codespaces

Para executar utilizando as configurações locais do Codespaces, configure a variável `SECRET_KEY` e execute:

```bash
python manage.py migrate --settings=config.settings_local
python manage.py runserver 0.0.0.0:8000 --settings=config.settings_local
```

O ambiente local utiliza SQLite, enquanto as configurações principais utilizam PostgreSQL.

## 10. Contas e dados de demonstração

O projeto possui os seguintes cadastros fictícios para demonstração:

senha geral: projeto2026

| Perfil | Nome | E-mail |
|---|---|---|
| Educador | Rafael M | educador@amigonofutebol.ong |
| Responsável | Maria Oliveira | maria.oliveira@exemplo.com |

**Aluno cadastrado:**

| Nome | Data de nascimento | Responsável |
|---|---|---|
| Lucas Oliveira | 10/05/2016 | Maria Oliveira |

**Acesso às contas:**

As senhas das contas de demonstração devem ser fornecidas separadamente ao avaliador, por segurança. Elas não são disponibilizadas neste repositório.

Observação: os dados acima estão cadastrados no banco de desenvolvimento utilizado durante a demonstração. Em uma nova instalação, será necessário criar os usuários e o aluno novamente.

## 11. Testes

Execute a suíte de testes:

```bash
python manage.py test --settings=config.settings_local
```

Para verificar a cobertura de testes:

```bash
python -m pip install coverage
coverage run manage.py test --settings=config.settings_local
coverage report
```

Na última execução registrada durante o desenvolvimento, foram aprovados 20 testes e a cobertura total foi de 88%.

## 12. Controle de acesso

**Educador**
- Pode cadastrar responsáveis.
- Pode cadastrar alunos.
- Pode visualizar os alunos cadastrados.
- Pode alterar o status dos alunos.

**Responsável**
- Pode acessar o sistema com seu e-mail e senha.
- Visualiza somente os alunos vinculados ao seu cadastro.

## 13. Observações finais

Este projeto corresponde a um MVP (Produto Mínimo Viável), desenvolvido com Django e organizado segundo o padrão MVT (Model-View-Template).

As configurações locais de desenvolvimento não devem ser confundidas com as configurações destinadas ao uso com PostgreSQL.

Arquivos que contenham senhas, chaves secretas e bancos de dados locais não devem ser publicados no repositório.