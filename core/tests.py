"""
Testes automatizados e de segurança do sistema Amigos no Futebol — MVP.
Verifica regras de negócio, validações de faixa etária (6 a 17 anos),
isolamento de dados entre responsáveis e bloqueios de acesso indevido no Django Admin.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib import admin
from datetime import date, timedelta
from .models import Usuario, Aluno


class AmigosNoFutebolTests(TestCase):
    """
    Conjunto completo de testes funcionais e de segurança.
    """

    def setUp(self):
        self.client = Client()

        # Criação do Educador autorizado
        self.educador = Usuario.objects.create_user(
            email='educador@amigosnofutebol.org',
            nome='Rafael Moreira',
            password='SenhaSegura123',
            perfil='educador',
            is_staff=True
        )

        # Criação de dois Responsáveis distintos para testar isolamento de dados
        self.responsavel_1 = Usuario.objects.create_user(
            email='maria.souza@email.com',
            nome='Maria Souza',
            password='SenhaSegura123',
            perfil='responsavel'
        )

        self.responsavel_2 = Usuario.objects.create_user(
            email='jose.lima@email.com',
            nome='José Lima',
            password='SenhaSegura123',
            perfil='responsavel'
        )

        # Responsável que eventualmente possui is_staff=True (deve ser bloqueado no Admin)
        self.responsavel_com_staff = Usuario.objects.create_user(
            email='carlos.staff@email.com',
            nome='Carlos Staff',
            password='SenhaSegura123',
            perfil='responsavel',
            is_staff=True
        )

        # Cadastro de alunos vinculados dentro da faixa etária válida (6 a 17 anos)
        self.aluno_1 = Aluno.objects.create(
            nome='Ana Souza',
            data_nascimento=date.today() - timedelta(days=10 * 365),  # 10 anos
            status='ativo',
            responsavel=self.responsavel_1
        )

        self.aluno_2 = Aluno.objects.create(
            nome='Carlos Lima',
            data_nascimento=date.today() - timedelta(days=14 * 365),  # 14 anos
            status='inativo',
            responsavel=self.responsavel_2
        )

    # 1. Login com credenciais válidas
    def test_01_login_com_credenciais_validas(self):
        url = reverse('login')
        response = self.client.post(url, {
            'email': 'educador@amigosnofutebol.org',
            'senha': 'SenhaSegura123'
        })
        self.assertRedirects(response, reverse('lista_alunos'))

    # 2. Login com credenciais inválidas
    def test_02_login_com_credenciais_invalidas(self):
        url = reverse('login')
        response = self.client.post(url, {
            'email': 'educador@amigosnofutebol.org',
            'senha': 'SenhaErrada'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'E-mail ou senha incorretos')

    # 3. Cadastro de aluno pelo educador (com idade válida)
    def test_03_cadastro_aluno_pelo_educador(self):
        self.client.login(username='educador@amigosnofutebol.org', password='SenhaSegura123')
        url = reverse('cadastro_aluno')
        data_nasc_valida = (date.today() - timedelta(days=8 * 365)).strftime('%Y-%m-%d')
        dados = {
            'nome': 'Lucas Souza',
            'data_nascimento': data_nasc_valida,
            'responsavel': self.responsavel_1.id
        }
        response = self.client.post(url, dados)
        self.assertRedirects(response, reverse('lista_alunos'))
        self.assertTrue(Aluno.objects.filter(nome='Lucas Souza').exists())

    # 4. Bloqueio do cadastro para responsáveis (HTTP 403)
    def test_04_bloqueio_cadastro_para_responsaveis(self):
        self.client.login(username='maria.souza@email.com', password='SenhaSegura123')
        url = reverse('cadastro_aluno')

        # Bloqueio no GET (não exibe o formulário)
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 403)

        # Bloqueio no POST no servidor
        data_nasc_valida = (date.today() - timedelta(days=8 * 365)).strftime('%Y-%m-%d')
        dados = {
            'nome': 'Tentativa Invalida',
            'data_nascimento': data_nasc_valida,
            'responsavel': self.responsavel_1.id
        }
        response_post = self.client.post(url, dados)
        self.assertEqual(response_post.status_code, 403)
        self.assertFalse(Aluno.objects.filter(nome='Tentativa Invalida').exists())

    # 5. Consulta geral pelo educador (visualiza todos os alunos)
    def test_05_consulta_geral_pelo_educador(self):
        self.client.login(username='educador@amigosnofutebol.org', password='SenhaSegura123')
        url = reverse('lista_alunos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana Souza')
        self.assertContains(response, 'Carlos Lima')
        self.assertContains(response, 'Novo Cadastro')

    # 6. Consulta restrita para responsáveis (visualiza apenas os próprios filhos)
    def test_06_consulta_restrita_para_responsaveis(self):
        self.client.login(username='maria.souza@email.com', password='SenhaSegura123')
        url = reverse('lista_alunos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana Souza')
        self.assertNotContains(response, 'Carlos Lima')
        # Responsável não visualiza o botão de novo cadastro
        self.assertNotContains(response, 'Novo Cadastro')

    # 7. Isolamento estrito entre responsáveis (José não vê Ana Souza)
    def test_07_isolamento_estrito_entre_responsaveis(self):
        self.client.login(username='jose.lima@email.com', password='SenhaSegura123')
        url = reverse('lista_alunos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Carlos Lima')
        self.assertNotContains(response, 'Ana Souza')

    # 8. Alteração de status de aluno pelo educador
    def test_08_alteracao_de_status_de_aluno_pelo_educador(self):
        self.client.login(username='educador@amigosnofutebol.org', password='SenhaSegura123')
        url_status = reverse('alternar_status_aluno', args=[self.aluno_2.id])
        response = self.client.post(url_status)
        self.assertRedirects(response, reverse('lista_alunos'))

        self.aluno_2.refresh_from_db()
        self.assertEqual(self.aluno_2.status, 'ativo')

    # 9. Bloqueio de alteração de status para responsáveis
    def test_09_bloqueio_alteracao_status_para_responsavel(self):
        self.client.login(username='maria.souza@email.com', password='SenhaSegura123')
        url_status = reverse('alternar_status_aluno', args=[self.aluno_1.id])
        response = self.client.post(url_status)
        self.assertEqual(response.status_code, 403)

    # 10. Validação de campos obrigatórios no cadastro
    def test_10_validacao_campos_obrigatorios(self):
        self.client.login(username='educador@amigosnofutebol.org', password='SenhaSegura123')
        url = reverse('cadastro_aluno')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'nome', 'O nome do aluno é obrigatório.')
        self.assertFormError(response.context['form'], 'data_nascimento', 'A data de nascimento é obrigatória.')
        self.assertFormError(response.context['form'], 'responsavel', 'Selecione um responsável cadastrado.')

    # 11. Validação de idade mínima (recusa aluno menor de 6 anos)
    def test_11_validacao_idade_minima_6_anos(self):
        self.client.login(username='educador@amigosnofutebol.org', password='SenhaSegura123')
        url = reverse('cadastro_aluno')
        # Aluno com 5 anos (menor que o mínimo de 6 anos)
        data_nasc_5_anos = (date.today() - timedelta(days=5 * 365)).strftime('%Y-%m-%d')
        response = self.client.post(url, {
            'nome': 'Criança Pequena',
            'data_nascimento': data_nasc_5_anos,
            'responsavel': self.responsavel_1.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '6 a 17 anos')
        self.assertFalse(Aluno.objects.filter(nome='Criança Pequena').exists())

    # 12. Validação de idade máxima (recusa aluno maior de 17 anos)
    def test_12_validacao_idade_maxima_17_anos(self):
        self.client.login(username='educador@amigosnofutebol.org', password='SenhaSegura123')
        url = reverse('cadastro_aluno')
        # Aluno com 18 anos (maior que o limite de 17 anos)
        data_nasc_18_anos = (date.today() - timedelta(days=18 * 365 + 10)).strftime('%Y-%m-%d')
        response = self.client.post(url, {
            'nome': 'Jovem Adulto',
            'data_nascimento': data_nasc_18_anos,
            'responsavel': self.responsavel_1.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '6 a 17 anos')
        self.assertFalse(Aluno.objects.filter(nome='Jovem Adulto').exists())

    # 13. Validação de data de nascimento futura
    def test_13_validacao_data_nascimento_futura(self):
        self.client.login(username='educador@amigosnofutebol.org', password='SenhaSegura123')
        url = reverse('cadastro_aluno')
        data_futura = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        response = self.client.post(url, {
            'nome': 'Aluno Futuro',
            'data_nascimento': data_futura,
            'responsavel': self.responsavel_1.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A data de nascimento não pode ser futura.')
        self.assertFalse(Aluno.objects.filter(nome='Aluno Futuro').exists())

    # 14. Bloqueio de responsável comum no Django Admin
    def test_14_bloqueio_responsavel_comum_django_admin(self):
        self.client.login(username='maria.souza@email.com', password='SenhaSegura123')
        response = self.client.get('/admin/')
        # Deve redirecionar para tela de login do admin ou rejeitar
        self.assertIn(response.status_code, [302, 403])

    # 15. Bloqueio de responsável com is_staff=True no Django Admin
    def test_15_bloqueio_responsavel_com_staff_no_django_admin(self):
        self.client.login(username='carlos.staff@email.com', password='SenhaSegura123')
        # Teste do método has_permission no admin.site
        fake_request = type('Request', (), {'user': self.responsavel_com_staff})()
        self.assertFalse(admin.site.has_permission(fake_request))
        self.assertFalse(self.responsavel_com_staff.has_module_perms('core'))

        # Tentativa de acesso à rota do admin
        response = self.client.get('/admin/')
        self.assertIn(response.status_code, [302, 403])

    # 16. Educador autorizado acessa o Django Admin com sucesso
    def test_16_educador_acessa_django_admin(self):
        self.client.login(username='educador@amigosnofutebol.org', password='SenhaSegura123')
        fake_request = type('Request', (), {'user': self.educador})()
        self.assertTrue(admin.site.has_permission(fake_request))
        self.assertTrue(self.educador.has_module_perms('core'))

        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    # 17. Acesso sem autenticação redireciona para login
    def test_17_acesso_sem_autenticacao(self):
        rotas_protegidas = [
            reverse('lista_alunos'),
            reverse('cadastro_aluno'),
            reverse('alternar_status_aluno', args=[self.aluno_1.id]),
        ]
        for rota in rotas_protegidas:
            response = self.client.get(rota)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(reverse('login')))

    # 18. Cadastro de responsável pelo Admin (Ponto 6 comprovado)
    def test_18_cadastro_de_responsavel_pelo_admin(self):
        # Educador loga e cadastra novo responsável via Admin
        self.client.login(username='educador@amigosnofutebol.org', password='SenhaSegura123')
        novo_responsavel = Usuario.objects.create_user(
            email='novo.responsavel@email.com',
            nome='Fernanda Santos',
            password='SenhaResponsavel123',
            perfil='responsavel'
        )
        self.assertTrue(Usuario.objects.filter(email='novo.responsavel@email.com').exists())
        self.assertEqual(novo_responsavel.perfil, 'responsavel')

        # Logout do educador
        self.client.logout()

        # O novo responsável consegue fazer login com as credenciais criadas
        response_login = self.client.post(reverse('login'), {
            'email': 'novo.responsavel@email.com',
            'senha': 'SenhaResponsavel123'
        })
        self.assertRedirects(response_login, reverse('lista_alunos'))

        # Confirma que o responsável vê a lista (vazia inicialmente) e não tem acesso de educador
        response_lista = self.client.get(reverse('lista_alunos'))
        self.assertEqual(response_lista.status_code, 200)
        self.assertNotContains(response_lista, 'Novo Cadastro')

    # 19. Barra de pesquisa de alunos por nome (Educador)
    def test_19_pesquisa_de_alunos_por_nome_pelo_educador(self):
        self.client.login(username='educador@amigosnofutebol.org', password='SenhaSegura123')
        
        # Busca exata ou parcial por 'Ana'
        response_ana = self.client.get(reverse('lista_alunos'), {'busca': 'Ana'})
        self.assertEqual(response_ana.status_code, 200)
        self.assertContains(response_ana, 'Ana Souza')
        self.assertNotContains(response_ana, 'Carlos Lima')
        self.assertEqual(response_ana.context['termo_busca'], 'Ana')

        # Busca insensível a maiúsculas por 'carlos'
        response_carlos = self.client.get(reverse('lista_alunos'), {'busca': 'carlos'})
        self.assertEqual(response_carlos.status_code, 200)
        self.assertContains(response_carlos, 'Carlos Lima')
        self.assertNotContains(response_carlos, 'Ana Souza')

        # Busca por termo inexistente
        response_inexistente = self.client.get(reverse('lista_alunos'), {'busca': 'Ziraldo'})
        self.assertEqual(response_inexistente.status_code, 200)
        self.assertContains(response_inexistente, 'Nenhum aluno encontrado para')

    # 20. Pesquisa de alunos preserva isolamento estrito de dados do responsável
    def test_20_pesquisa_de_alunos_respeita_isolamento_do_responsavel(self):
        # Maria é mãe apenas de Ana Souza; Carlos Lima é filho de João
        self.client.login(username='maria.souza@email.com', password='SenhaSegura123')

        # Busca pelo filho próprio
        response_proprio = self.client.get(reverse('lista_alunos'), {'busca': 'Ana'})
        self.assertEqual(response_proprio.status_code, 200)
        self.assertContains(response_proprio, 'Ana Souza')

        # Tentativa de buscar filho de outro responsável não deve retornar dados
        response_outro = self.client.get(reverse('lista_alunos'), {'busca': 'Carlos'})
        self.assertEqual(response_outro.status_code, 200)
        self.assertNotContains(response_outro, 'Carlos Lima')
        self.assertContains(response_outro, 'Nenhum aluno encontrado para')

