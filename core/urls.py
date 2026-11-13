"""
Roteamento interno da aplicação core.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('alunos/', views.lista_alunos_view, name='lista_alunos'),
    path('alunos/novo/', views.cadastro_aluno_view, name='cadastro_aluno'),
    path('responsaveis/novo/', views.cadastro_responsavel_view, name='cadastro_responsavel'),
    path('alunos/<int:aluno_id>/status/', views.alternar_status_aluno_view, name='alternar_status_aluno'),
    path('alunos/<int:aluno_id>/perfil/', views.perfil_aluno_view, name='perfil_aluno'),
    path('alunos/<int:aluno_id>/foto/', views.foto_aluno_view, name='foto_aluno'),
    path('galeria/', views.galeria_atividades_view, name='galeria_atividades'),
    path('galeria/publicar/', views.publicar_foto_view, name='publicar_foto'),
    path('galeria/foto/<int:foto_id>/', views.foto_atividade_view, name='foto_atividade'),
]
