import os
from pathlib import Path

from decouple import config
from loguru import logger
import mimetypes

from django.utils.timezone import timedelta
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', cast=bool)

# HOSTS, ORIGINS AND CSRF
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    cast=lambda v: [
        s.strip() for s in v.split(',')
    ]
)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', cast=bool)

CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', cast=bool)

SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', cast=bool)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'corsheaders',
    'django_celery_beat',
    'django_countries',
    'crispy_forms',
    'mathfilters',
    'accounts',
    'shop',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'templates', 'allauth')],
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

WSGI_APPLICATION = 'ecommerce.wsgi.application'

# Database
DB_NAME = config('DB_NAME')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_HOST_DOCKER = config('DB_HOST_DOCKER')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': '6432',
    }
}

# Auth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomUserCreationForm',
}

AUTH_USER_MODEL = 'accounts.User'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'

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

# Languages And Timezone
LOCALE_PATHS = (
    'locale',
)

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'

USE_I18N = True

LANGUAGES = [
    ('ru', _('Russian')),
    ('en', _('English')),
]

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django allauth
SITE_ID = 1
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_CLIENT_SECRET'),
            'key': ''
        }
    }
}
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Static files and media (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CRISPY FORMS
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Logging
logger.add("info_django.log", format="{time} {level} {message}",
           level="INFO", rotation="1000 KB", compression="zip")
logger.add("error_django.log", format="{time} {level} {message}",
           level="ERROR", rotation="1000 KB", compression="zip")

# CELERY
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_IMPORTS = ('payment.tasks', 'shop.tasks',)
CELERY_BEAT_SCHEDULE = {
    'update_orders': {
        'task': 'update_orders',
        'schedule': timedelta(minutes=2),
        'args': ()
    }
}

# SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = config('EMAIL_ADDRESS')
EMAIL_HOST_PASSWORD = config('EMAIL_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# CSS error
mimetypes.add_type("text/css", ".css", True)

