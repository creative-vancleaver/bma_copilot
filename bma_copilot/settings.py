"""
Django settings for bma_copilot project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from datetime import timedelta
from pathlib import Path
import sys

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '3.134.240.51',
    'bmacopilot.com',
    'www.bmacopilot.com',
]


# Application definition

INSTALLED_APPS = [

    # CAN ADD LATER IF NEEDED
    # 'rest_framework',
    # 'rest_framework_simplejwt',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
    'users',
    
    'cases',
    'regions',
    'cells',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bma_copilot.urls'

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

WSGI_APPLICATION = 'bma_copilot.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
USE_AZURE_DB = config('USE_AZURE_DB', default='True') == 'True'
print('use_azure_db ', USE_AZURE_DB)
if (config('USE_AZURE_DB') == 'True'):
    print('Azure SQL')
    DATABASES = {
        'default': {
            'ENGINE': 'mssql',
            'NAME': config('AZURE_DATABASE'),
            'USER': config('AZURE_USERNAME'),
            'PASSWORD': config('AZURE_PASSWORD'),
            'HOST': config('AZURE_SERVER'),
            'PORT': config('AZURE_PORT'),
            'OPTIONS': {
                'driver': 'ODBC Driver 18 for SQL Server',
                'unicode_results': True,
                'host_is_server': True,
                'extra_params': 'TrustServerCertificate=yes;',
                'isolation_level': 'READ COMMITTED',
            },
        }
    }
else:
    print('SQLite')
    print(config('USE_AZURE_DB'))
    print('S3?')
    print(config('UPLOAD_TO_S3'))
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

#####

STATIC_URL = '/static/'
# STATICFILES_DIRS = [
#     # BASE_DIR / 'static', # LOCAL STATIC FILES
#     os.path.join(BASE_DIR, 'core/static')
# ]
STATIC_ROOT = BASE_DIR / 'staticfiles' # WHERE DJANGO COLLECTS STATIC FILES


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CELERY TASK CONFIG
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# AZURE BLOB UPLOAD SETTIGNS
AZURE_STORAGE_CONNECTION_STRING = config('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER = config('AZURE_STORAGE_CONTAINER')

# LOGIN_URL = "/login/"
LOGIN_URL = '/login/?next=' # REDIRECTS BACK TO ORIGINAL PAGE
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Default backend
)

# PYTHON LOGGING - FOR PRODUCTION
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.utils.autoreload': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        }
    },
    
}