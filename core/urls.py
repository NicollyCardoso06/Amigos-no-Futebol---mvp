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
    path('alunos/<int:aluno_id>/status/', views.alternar_status_aluno_view, name='alternar_status_aluno'),
]
