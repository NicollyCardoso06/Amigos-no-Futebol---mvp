"""
Configuração WSGI para o projeto Amigos no Futebol.

Expõe o chamável WSGI como uma variável de nível de módulo chamada 'application'.

Para mais informações sobre este arquivo, consulte:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
