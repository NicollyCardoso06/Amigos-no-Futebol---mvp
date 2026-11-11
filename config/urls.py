"""
Roteamento de URLs do projeto Amigos no Futebol.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Personalização dos títulos do Django Admin em português
admin.site.site_header = "Amigos no Futebol — Administração"
admin.site.site_title = "Amigos no Futebol"
admin.site.index_title = "Gestão de Usuários e Alunos"
