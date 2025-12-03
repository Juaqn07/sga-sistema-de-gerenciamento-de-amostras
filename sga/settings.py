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
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# 2. SEGURANÇA E AMBIENTE
# ==============================================================================
SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-utzl+ul+!@2&z@tqg-^tp(a1$hc*xvgxol_&s@%knp$&9_y@*o'
)

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost',
    cast=Csv()
)  # type: ignore


# ==============================================================================
# 3. APLICAÇÕES INSTALADAS
# ==============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Armazenamento de Mídia (Cloudinary) - Ordem Importa!
    'cloudinary_storage',
    'cloudinary',

    # Apps do Projeto (Local Apps)
    'apps.core',
    'apps.accounts',
    'apps.dashboard',
    'apps.samples',
    'apps.correios',
]


# ==============================================================================
# 4. MIDDLEWARE
# ==============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Essencial para estáticos no Heroku
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
        'DIRS': [],
        'APP_DIRS': True,
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
# 5. BANCO DE DADOS (Híbrido: SQLite Local / Postgres Heroku)
# ==============================================================================
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
# 8. ARQUIVOS ESTÁTICOS E MÍDIA (Configuração Moderna - Django 5+)
# ==============================================================================

# URLs Base
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuração das Credenciais do Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

# Definição dos Backends de Armazenamento (STORAGES)
STORAGES = {
    # 1. Arquivos de Mídia (Uploads) -> Vão para o Cloudinary
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    # 2. Arquivos Estáticos (CSS/JS do Sistema) -> Vão para o Whitenoise
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ==============================================================================
# 9. CONFIGURAÇÕES DO PROJETO
# ==============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.UsuarioCustomizado'

# Login/Logout
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Tags de Mensagem (Bootstrap)
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# Correios
CORREIOS_CREDENTIALS = {
    'usuario': config('CORREIOS_USER', default=''),
    'senha': config('CORREIOS_CODIGO_ACESSO', default=''),
    'contrato': config('CORREIOS_CONTRATO', default=''),
    'cartao': config('CORREIOS_CARTAO', default=''),
    'url_base': config('CORREIOS_URL_BASE', default='https://api.correios.com.br'),
}

CEP_ORIGEM_EMPRESA = config('CEP_ORIGEM_EMPRESA', default='00000000')


# ==============================================================================
# 10. SEGURANÇA EM PRODUÇÃO (HEROKU)
# ==============================================================================
if config('DATABASE_URL', default=None):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    CSRF_TRUSTED_ORIGINS = ['https://*.herokuapp.com']
