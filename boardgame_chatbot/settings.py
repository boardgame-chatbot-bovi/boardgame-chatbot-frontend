"""
Django settings for boardgame_chatbot project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
import socket

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 환경 감지 (로컬 vs EC2)
def is_ec2_environment():
    """EC2 환경인지 감지"""
    try:
        # EC2 메타데이터 서비스 확인
        socket.create_connection(('169.254.169.254', 80), timeout=1)
        return True
    except:
        return False

IS_EC2 = is_ec2_environment()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if IS_EC2:
    # EC2 프로덕션 환경
    SECRET_KEY = 'ec2-prod-bovi-boardgame-chatbot-2025-secure-key-a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3'
    DEBUG = True  # 에러 확인을 위해 임시로 True
    ALLOWED_HOSTS = ['*']  # 모든 호스트 허용
else:
    # 로컬 개발 환경
    SECRET_KEY = 'django-insecure-local-dev-key-for-boardgame-chatbot-bovi-2025'
    DEBUG = True
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]

# WhiteNoise는 EC2에서만 사용
if IS_EC2:
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

MIDDLEWARE.extend([
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])

ROOT_URLCONF = 'boardgame_chatbot.urls'

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

WSGI_APPLICATION = 'boardgame_chatbot.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if IS_EC2:
    # EC2 PostgreSQL 환경
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'boardgame_db',
            'USER': 'juno',
            'PASSWORD': 'hwang0719',
            'HOST': 'localhost',
            'PORT': '5432',
            'OPTIONS': {
                'connect_timeout': 20,
            }
        }
    }
else:
    # 로컬 개발 환경 (SQLite)
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

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

if IS_EC2:
    # EC2 프로덕션 환경
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]
    # WhiteNoise 설정 (EC2에서 whitenoise가 설치된 경우만)
    try:
        import whitenoise
        STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    except ImportError:
        # WhiteNoise가 없으면 기본 설정 사용
        STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    # 로컬 개발 환경
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]
    # 로컬에서는 STATIC_ROOT 설정하지 않음 (개발 서버가 자동 처리)

# Static Files Finders (파일 탐색 순서)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AI 서비스 설정
# OpenAI API 키는 실제 서비스에서는 환경변수로 설정하거나 별도 관리 필요
OPENAI_API_KEY = 'sk-placeholder-key-add-your-real-key-here'  # 실제 키로 교체 필요
FINETUNING_MODEL_ID = 'ft:gpt-3.5-turbo-0125:tset::BX2RnWfq'
AI_DATA_PATH = 'ai_data'

# Runpod 백엔드 설정
RUNPOD_API_URL = 'https://r8asrxwuomha7r-8000.proxy.runpod.net'
RUNPOD_API_KEY = None  # 필요시 설정
RUNPOD_TIMEOUT = 30.0
RUNPOD_USE_FALLBACK = True

# 보안 설정 (EC2 배포용)
if IS_EC2:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # CSRF 설정
    CSRF_TRUSTED_ORIGINS = [
        'http://13.125.251.186',
        'https://13.125.251.186',
    ]

# 로깅 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'chatbot': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 캐시 설정
if IS_EC2:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'boardgame-cache',
        }
    }

# 세션 설정
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24시간
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True

# 개발 도구 (로컬에서만)
if DEBUG and not IS_EC2:
    try:
        import debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        INTERNAL_IPS = ['127.0.0.1']
    except ImportError:
        pass
