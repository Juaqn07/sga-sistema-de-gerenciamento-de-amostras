from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

"""
Roteamento Principal do Projeto (URL Dispatcher).

Este arquivo atua como o 'porteiro' da aplicação, delegando as requisições
para os arquivos urls.py específicos de cada App (dashboard, samples, accounts, etc).
"""

urlpatterns = [
    # 1. Interface Administrativa (Django Admin)
    path('admin/', admin.site.urls),

    # 2. App Dashboard (Visão Gerencial e KPIs)
    # URL Base: /dashboard/
    path('dashboard/', include('apps.dashboard.urls')),

    # 3. App Samples/Processos (Core do Negócio: Amostras)
    # URL Base: /processos/
    path('processos/', include('apps.samples.urls')),

    # 4. App Accounts (Autenticação, Perfil e Usuários)
    # URL Base: / (Raiz para login)
    path('', include('apps.accounts.urls')),

    # 5. App Correios (Integrações e APIs Externas)
    # URL Base: /correios/
    path('correios/', include('apps.correios.urls'))
]

# Configuração para servir arquivos de Mídia (Uploads) em ambiente de Desenvolvimento
# NOTA: Em produção, isso deve ser gerido pelo servidor web (Nginx/Apache/S3)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)  # type: ignore
