"""
Configurações Globais do Projeto SGA (Sistema de Gestão de Amostras).

Este arquivo centraliza todas as configurações de ambiente, segurança,
banco de dados e integrações (Correios).

Utiliza a biblioteca 'python-decouple' para separar configurações sensíveis
do código fonte (arquivo .env).
"""

import os
import dj_database_url
from pathlib import Path
from decouple import config, Csv
from django.contrib.messages import constants as messages

# ==============================================================================
# 1. CAMINHOS E DIRETÓRIOS BASE
# ==============================================================================
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# 2. SEGURANÇA E AMBIENTE
# ==============================================================================
# A SECRET_KEY deve ser mantida em segredo absoluto em produção
SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-utzl+ul+!@2&z@tqg-^tp(a1$hc*xvgxol_&s@%knp$&9_y@*o'
)

# DEBUG deve ser False em produção para evitar vazamento de dados de erro
DEBUG = config('DEBUG', default=True, cast=bool)

# Lista de hosts/domínios que podem servir esta aplicação
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost',
    cast=Csv()  # type: ignore
)


# ==============================================================================
# 3. APLICAÇÕES INSTALADAS
# ==============================================================================
INSTALLED_APPS = [
    # Apps Padrão do Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps do Projeto (Local Apps)
    'apps.core',        # Utilitários globais
    'apps.accounts',    # Gestão de Usuários Customizados
    'apps.dashboard',   # Visualização de Dados e KPIs
    'apps.samples',     # Lógica de Negócio (Processos/Amostras)
    'apps.correios',    # Integração API Correios
]


# ==============================================================================
# 4. MIDDLEWARE (Processamento de Requisições)
# ==============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise: Permite servir arquivos estáticos de forma eficiente em produção
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sga.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Templates globais poderiam ser adicionados aqui
        'APP_DIRS': True,  # Busca templates dentro das pastas dos apps
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sga.wsgi.application'


# ==============================================================================
# 5. BANCO DE DADOS
# ==============================================================================
# Padrão: SQLite (Desenvolvimento). Em produção, recomenda-se PostgreSQL.
DATABASES = {
    'default': config(
        'DATABASE_URL',
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        cast=dj_database_url.parse
    )
}


# ==============================================================================
# 6. VALIDAÇÃO DE SENHAS
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# ==============================================================================
# 7. INTERNACIONALIZAÇÃO
# ==============================================================================
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# ==============================================================================
# 8. ARQUIVOS ESTÁTICOS E MÍDIA
# ==============================================================================
# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuração do WhiteNoise para compressão e cache de estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media Files (Uploads de Usuários)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ==============================================================================
# 9. CONFIGURAÇÕES CUSTOMIZADAS DO SISTEMA
# ==============================================================================

# Definição de Chave Primária Padrão
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modelo de Usuário Customizado (app accounts)
# Substitui o User padrão do Django para permitir login com campos extras (Função/Setor)
AUTH_USER_MODEL = 'accounts.UsuarioCustomizado'

# Redirecionamentos de Autenticação
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Integração com Mensagens do Bootstrap (Mapeamento de Tags)
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# Credenciais da API dos Correios (Carregadas do .env via decouple)
CORREIOS_CREDENTIALS = {
    'usuario': config('CORREIOS_USER', default=''),
    'senha': config('CORREIOS_CODIGO_ACESSO', default=''),
    'contrato': config('CORREIOS_CONTRATO', default=''),
    'cartao': config('CORREIOS_CARTAO', default=''),
    'url_base': config('CORREIOS_URL_BASE', default='https://api.correios.com.br'),
}

# ==============================================================================
# 10. CONFIGURAÇÕES DE PRODUÇÃO (HEROKU)
# ==============================================================================

# Se estiver rodando no Heroku (identificado pela variável de ambiente do banco)
if config('DATABASE_URL', default=None):
    # 1. Configuração de Proxy (Essencial para HTTPS no Heroku)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # --- HSTS (HTTP Strict Transport Security) ---
    # Força navegadores a usarem HTTPS por 1 ano
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # 2. Domínios Confiáveis para CSRF
    CSRF_TRUSTED_ORIGINS = ['https://*.herokuapp.com']

    # 3. Estáticos (Compressão e Cache)
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
