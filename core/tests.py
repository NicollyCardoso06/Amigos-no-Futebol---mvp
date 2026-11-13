
"""
Testes automatizados e de segurança do sistema Amigos no Futebol — MVP.
Verifica regras de negócio, validações de faixa etária (6 a 17 anos),
isolamento de dados entre responsáveis e bloqueios de acesso indevido
no Django Admin e na galeria de atividades.
"""

from datetime import date, timedelta
from io import BytesIO

from PIL import Image

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Usuario, Aluno, FotoAtividade


class AmigosNoFutebolTests(TestCase):
    """
    Conjunto completo de testes funcionais e de segurança.
    """

    def setUp(self):
        self.client = Client()

        # Educador autorizado
        self.educador = Usuario.objects.create_user(
            email='educador@amigosnofutebol.org',
            nome='Rafael Moreira',
            password='SenhaSegura123',
            perfil='educador',
            is_staff=True
        )

        # Responsáveis
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

        # Responsável com is_staff=True, que deve ser bloqueado no Admin
        self.responsavel_com_staff = Usuario.objects.create_user(
            email='carlos.staff@email.com',
            nome='Carlos Staff',
            password='SenhaSegura123',
            perfil='responsavel',
            is_staff=True
        )

        # Alunos
        self.aluno_1 = Aluno.objects.create(
            nome='Ana Souza',
            data_nascimento=date.today() - timedelta(days=10 * 365),
            status='ativo',
            responsavel=self.responsavel_1
        )

        self.aluno_2 = Aluno.objects.create(
            nome='Carlos Lima',
            data_nascimento=date.today() - timedelta(days=14 * 365),
            status='inativo',
            responsavel=self.responsavel_2
        )

    # Cria uma imagem PNG válida para os testes da galeria
    def criar_imagem_teste(self, nome):
        buffer = BytesIO()

        imagem = Image.new('RGB', (10, 10), color='white')
        imagem.save(buffer, format='PNG')

        return SimpleUploadedFile(
            nome,
            buffer.getvalue(),
            content_type='image/png'
        )

    # Limpa os arquivos de imagem criados durante os testes
    def tearDown(self):
        for foto in FotoAtividade.objects.all():
            if foto.foto:
                foto.foto.delete(save=False)

        super().tearDown()

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

    # 3. Cadastro de aluno pelo educador
    def test_03_cadastro_aluno_pelo_educador(self):
        self.client.login(
            username='educador@amigosnofutebol.org',
            password='SenhaSegura123'
        )

        url = reverse('cadastro_aluno')
        data_nasc_valida = (
            date.today() - timedelta(days=8 * 365)
        ).strftime('%Y-%m-%d')

        dados = {
            'nome': 'Lucas Souza',
            'data_nascimento': data_nasc_valida,
            'responsavel': self.responsavel_1.id
        }

        response = self.client.post(url, dados)

        self.assertRedirects(response, reverse('lista_alunos'))
        self.assertTrue(
            Aluno.objects.filter(nome='Lucas Souza').exists()
        )

    # 4. Bloqueio do cadastro para responsáveis
    def test_04_bloqueio_cadastro_para_responsaveis(self):
        self.client.login(
            username='maria.souza@email.com',
            password='SenhaSegura123'
        )

        url = reverse('cadastro_aluno')

        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 403)

        data_nasc_valida = (
            date.today() - timedelta(days=8 * 365)
        ).strftime('%Y-%m-%d')

        dados = {
            'nome': 'Tentativa Invalida',
            'data_nascimento': data_nasc_valida,
            'responsavel': self.responsavel_1.id
        }

        response_post = self.client.post(url, dados)

        self.assertEqual(response_post.status_code, 403)
        self.assertFalse(
            Aluno.objects.filter(nome='Tentativa Invalida').exists()
        )

    # 5. Educador visualiza todos os alunos
    def test_05_consulta_geral_pelo_educador(self):
        self.client.login(
            username='educador@amigosnofutebol.org',
            password='SenhaSegura123'
        )

        response = self.client.get(reverse('lista_alunos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana Souza')
        self.assertContains(response, 'Carlos Lima')
        self.assertContains(response, 'Novo Cadastro')

    # 6. Responsável visualiza apenas o próprio filho
    def test_06_consulta_restrita_para_responsaveis(self):
        self.client.login(
            username='maria.souza@email.com',
            password='SenhaSegura123'
        )

        response = self.client.get(reverse('lista_alunos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana Souza')
        self.assertNotContains(response, 'Carlos Lima')
        self.assertNotContains(response, 'Novo Cadastro')

    # 7. Isolamento entre responsáveis
    def test_07_isolamento_estrito_entre_responsaveis(self):
        self.client.login(
            username='jose.lima@email.com',
            password='SenhaSegura123'
        )

        response = self.client.get(reverse('lista_alunos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Carlos Lima')
        self.assertNotContains(response, 'Ana Souza')

    # 8. Educador altera o status do aluno
    def test_08_alteracao_de_status_de_aluno_pelo_educador(self):
        self.client.login(
            username='educador@amigosnofutebol.org',
            password='SenhaSegura123'
        )

        url_status = reverse(
            'alternar_status_aluno',
            args=[self.aluno_2.id]
        )

        response = self.client.post(url_status)

        self.assertRedirects(response, reverse('lista_alunos'))

        self.aluno_2.refresh_from_db()
        self.assertEqual(self.aluno_2.status, 'ativo')

    # 9. Responsável não pode alterar o status
    def test_09_bloqueio_alteracao_status_para_responsavel(self):
        self.client.login(
            username='maria.souza@email.com',
            password='SenhaSegura123'
        )

        url_status = reverse(
            'alternar_status_aluno',
            args=[self.aluno_1.id]
        )

        response = self.client.post(url_status)

        self.assertEqual(response.status_code, 403)

    # 10. Validação de campos obrigatórios
    def test_10_validacao_campos_obrigatorios(self):
        self.client.login(
            username='educador@amigosnofutebol.org',
            password='SenhaSegura123'
        )

        url = reverse('cadastro_aluno')
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 200)

        self.assertFormError(
            response.context['form'],
            'nome',
            'O nome do aluno é obrigatório.'
        )

        self.assertFormError(
            response.context['form'],
            'data_nascimento',
            'A data de nascimento é obrigatória.'
        )

        self.assertFormError(
            response.context['form'],
            'responsavel',
            'Selecione um responsável cadastrado.'
        )

    # 11. Validação da idade mínima de 6 anos
    def test_11_validacao_idade_minima_6_anos(self):
        self.client.login(
            username='educador@amigosnofutebol.org',
            password='SenhaSegura123'
        )

        url = reverse('cadastro_aluno')
        data_nasc_5_anos = (
            date.today() - timedelta(days=5 * 365)
        ).strftime('%Y-%m-%d')

        response = self.client.post(url, {
            'nome': 'Criança Pequena',
            'data_nascimento': data_nasc_5_anos,
            'responsavel': self.responsavel_1.id
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '6 a 17 anos')
        self.assertFalse(
            Aluno.objects.filter(nome='Criança Pequena').exists()
        )

    # 12. Validação da idade máxima de 17 anos
    def test_12_validacao_idade_maxima_17_anos(self):
        self.client.login(
            username='educador@amigosnofutebol.org',
            password='SenhaSegura123'
        )

        url = reverse('cadastro_aluno')
        data_nasc_18_anos = (
            date.today() - timedelta(days=18 * 365 + 10)
        ).strftime('%Y-%m-%d')

        response = self.client.post(url, {
            'nome': 'Jovem Adulto',
            'data_nascimento': data_nasc_18_anos,
            'responsavel': self.responsavel_1.id
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '6 a 17 anos')
        self.assertFalse(
            Aluno.objects.filter(nome='Jovem Adulto').exists()
        )

    # 13. Validação de data de nascimento futura
    def test_13_validacao_data_nascimento_futura(self):
        self.client.login(
            username='educador@amigosnofutebol.org',
            password='SenhaSegura123'
        )

        url = reverse('cadastro_aluno')
        data_futura = (
            date.today() + timedelta(days=30)
        ).strftime('%Y-%m-%d')

        response = self.client.post(url, {
            'nome': 'Aluno Futuro',
            'data_nascimento': data_futura,
            'responsavel': self.responsavel_1.id
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'A data de nascimento não pode ser futura.'
        )
        self.assertFalse(
            Aluno.objects.filter(nome='Aluno Futuro').exists()
        )

    # 14. Responsável comum não acessa o Django Admin
    def test_14_bloqueio_responsavel_comum_django_admin(self):
        self.client.login(
            username='maria.souza@email.com',
            password='SenhaSegura123'
        )

        response = self.client.get('/admin/')

        self.assertIn(response.status_code, [302, 403])

    # 15. Responsável com is_staff=True não acessa o Admin
    def test_15_bloqueio_responsavel_com_staff_no_django_admin(self):
        self.client.login(
            username='carlos.staff@email.com',
            password='SenhaSegura123'
        )

        fake_request = type(
            'Request',
            (),
            {'user': self.responsavel_com_staff}
        )()

        self.assertFalse(admin.site.has_permission(fake_request))
        self.assertFalse(
            self.responsavel_com_staff.has_module_perms('core')
        )

        response = self.client.get('/admin/')

        self.assertIn(response.status_code, [302, 403])

    # 16. Educador autorizado acessa o Django Admin
    def test_16_educador_acessa_django_admin(self):
        self.client.login(
            username='educador@amigosnofutebol.org',
            password='SenhaSegura123'
        )

        fake_request = type(
            'Request',
            (),
            {'user': self.educador}
        )()

        self.assertTrue(admin.site.has_permission(fake_request))
        self.assertTrue(self.educador.has_module_perms('core'))

        response = self.client.get('/admin/')

        self.assertEqual(response.status_code, 200)

    # 17. Acesso sem autenticação redireciona para login
    def test_17_acesso_sem_autenticacao(self):
        rotas_protegidas = [
            reverse('lista_alunos'),
            reverse('cadastro_aluno'),
            reverse(
                'alternar_status_aluno',
                args=[self.aluno_1.id]
            ),
        ]

        for rota in rotas_protegidas:
            response = self.client.get(rota)

            self.assertEqual(response.status_code, 302)
            self.assertTrue(
                response.url.startswith(reverse('login'))
            )

    # 18. Cadastro de responsável e acesso à conta
    def test_18_cadastro_de_responsavel_pelo_admin(self):
        self.client.login(
            username='educador@amigosnofutebol.org',
            password='SenhaSegura123'
        )

        novo_responsavel = Usuario.objects.create_user(
            email='novo.responsavel@email.com',
            nome='Fernanda Santos',
            password='SenhaResponsavel123',
            perfil='responsavel'
        )

        self.assertTrue(
            Usuario.objects.filter(
                email='novo.responsavel@email.com'
            ).exists()
        )
        self.assertEqual(novo_responsavel.perfil, 'responsavel')

        self.client.logout()

        response_login = self.client.post(reverse('login'), {
            'email': 'novo.responsavel@email.com',
            'senha': 'SenhaResponsavel123'
        })

        self.assertRedirects(
            response_login,
            reverse('lista_alunos')
        )

        response_lista = self.client.get(reverse('lista_alunos'))

        self.assertEqual(response_lista.status_code, 200)
        self.assertNotContains(response_lista, 'Novo Cadastro')

    # 19. Pesquisa de alunos pelo educador
    def test_19_pesquisa_de_alunos_por_nome_pelo_educador(self):
        self.client.login(
            username='educador@amigosnofutebol.org',
            password='SenhaSegura123'
        )

        response_ana = self.client.get(
            reverse('lista_alunos'),
            {'busca': 'Ana'}
        )

        self.assertEqual(response_ana.status_code, 200)
        self.assertContains(response_ana, 'Ana Souza')
        self.assertNotContains(response_ana, 'Carlos Lima')
        self.assertEqual(response_ana.context['termo_busca'], 'Ana')

        response_carlos = self.client.get(
            reverse('lista_alunos'),
            {'busca': 'carlos'}
        )

        self.assertEqual(response_carlos.status_code, 200)
        self.assertContains(response_carlos, 'Carlos Lima')
        self.assertNotContains(response_carlos, 'Ana Souza')

        response_inexistente = self.client.get(
            reverse('lista_alunos'),
            {'busca': 'Ziraldo'}
        )

        self.assertEqual(response_inexistente.status_code, 200)
        self.assertContains(
            response_inexistente,
            'Nenhum aluno encontrado para'
        )

    # 20. Pesquisa preserva o isolamento entre responsáveis
    def test_20_pesquisa_de_alunos_respeita_isolamento_do_responsavel(self):
        self.client.login(
            username='maria.souza@email.com',
            password='SenhaSegura123'
        )

        response_proprio = self.client.get(
            reverse('lista_alunos'),
            {'busca': 'Ana'}
        )

        self.assertEqual(response_proprio.status_code, 200)
        self.assertContains(response_proprio, 'Ana Souza')

        response_outro = self.client.get(
            reverse('lista_alunos'),
            {'busca': 'Carlos'}
        )

        self.assertEqual(response_outro.status_code, 200)
        self.assertNotContains(response_outro, 'Carlos Lima')
        self.assertContains(
            response_outro,
            'Nenhum aluno encontrado para'
        )

    # 21. Educador publica várias fotos de uma só vez
    def test_21_educador_publica_varias_fotos(self):
        self.client.login(
            username='educador@amigosnofutebol.org',
            password='SenhaSegura123'
        )

        resposta = self.client.post(
            reverse('publicar_foto'),
            {
                'foto': [
                    self.criar_imagem_teste('atividade1.png'),
                    self.criar_imagem_teste('atividade2.png'),
                ],
                'legenda': 'Treino de futebol',
            }
        )

        self.assertRedirects(
            resposta,
            reverse('galeria_atividades')
        )

        self.assertEqual(FotoAtividade.objects.count(), 2)

        self.assertEqual(
            FotoAtividade.objects.filter(
                educador=self.educador,
                legenda='Treino de futebol'
            ).count(),
            2
        )

    # 22. Responsável não pode publicar fotos
    def test_22_responsavel_nao_pode_publicar_fotos(self):
        self.client.login(
            username='maria.souza@email.com',
            password='SenhaSegura123'
        )

        resposta = self.client.post(
            reverse('publicar_foto'),
            {
                'foto': self.criar_imagem_teste('tentativa.png'),
                'legenda': 'Tentativa de publicação',
            }
        )

        self.assertEqual(resposta.status_code, 403)
        self.assertEqual(FotoAtividade.objects.count(), 0)

    # 23. Responsável consegue acessar a galeria compartilhada
    def test_23_responsavel_acessa_galeria_compartilhada(self):
        FotoAtividade.objects.create(
            foto=self.criar_imagem_teste('foto_treino.png'),
            legenda='Treino de futebol',
            educador=self.educador
        )

        self.client.login(
            username='maria.souza@email.com',
            password='SenhaSegura123'
        )

        resposta = self.client.get(
            reverse('galeria_atividades')
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Treino de futebol')

    # 24. Acesso direto à foto exige autenticação
    def test_24_foto_exige_autenticacao(self):
        foto = FotoAtividade.objects.create(
            foto=self.criar_imagem_teste('foto_privada.png'),
            legenda='Foto protegida',
            educador=self.educador
        )

        resposta = self.client.get(
            reverse('foto_atividade',
                    args=[foto.id])
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(
            resposta.url.startswith(reverse('login'))
        )
