import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# SEGURANÇA / PRODUÇÃO
# =========================

# Em produção, ideal pegar do ambiente
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-x9fs7t9vkxky^dqwt98w1^k08whp9)_-a3xv@*z2qi+zupy28e'  # fallback pra dev
)

# Render: deixa False lá, e se quiser pode fazer lógica por ambiente
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Em produção, coloque o host do Render aqui, ex: 'controle-amazonia.onrender.com'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')
# Se quiser fixo pra teste:
# ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'app_financeiro',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise para servir arquivos estáticos em produção
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'projeto_financeiro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'projeto_financeiro.wsgi.application'


# Database (SQLite mesmo, ok para demo)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Cuiaba'

USE_I18N = True
USE_TZ = True


# =========================
# ARQUIVOS ESTÁTICOS
# =========================

STATIC_URL = '/static/'

# Onde o collectstatic vai jogar tudo (OBRIGATÓRIO pro Render)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Se você já usa uma pasta static/ no projeto:
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Whitenoise storage para servir estáticos em produção
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
