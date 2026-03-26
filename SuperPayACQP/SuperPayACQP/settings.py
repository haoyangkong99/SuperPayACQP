"""
Django settings for SuperPayACQP project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
# Add Railway domain - use wildcard to allow all railway.app subdomains
ALLOWED_HOSTS.append('.railway.app')
# Also allow the specific production domain
ALLOWED_HOSTS.append('superpayacqp-production.up.railway.app')

# CSRF Trusted Origins - required for cross-origin POST requests
CSRF_TRUSTED_ORIGINS = [
    'https://superpayacqp-production.up.railway.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
# Add any additional origins from environment variable
csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in csrf_origins_env.split(',')])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'background_task',
    # Local apps
    'apps.merchants',
    'apps.orders',
    'apps.payments',
    'apps.refunds',
    'apps.api_records',
    'apps.user_auth',
    'apps.goods',
    'apps.frontend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.merchant_auth.MerchantAuthMiddleware',
    'middleware.header_cleanup.HeaderCleanupMiddleware',
]

# Security headers configuration - disable unwanted headers
SECURE_CROSS_ORIGIN_OPENER_POLICY = None
SECURE_REFERRER_POLICY = None
SECURE_CONTENT_TYPE_NOSNIFF = False
# Note: X_FRAME_OPTIONS must be a string, not None. Use empty string to effectively disable.
X_FRAME_OPTIONS = ''

ROOT_URLCONF = 'SuperPayACQP.urls'

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

WSGI_APPLICATION = 'SuperPayACQP.wsgi.application'

# Database
# PostgreSQL configuration (supports both Railway and local development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGDATABASE', os.getenv('POSTGRES_DB', 'superpayacqp')),
        'USER': os.getenv('PGUSER', os.getenv('POSTGRES_USER', 'postgres')),
        'PASSWORD': os.getenv('PGPASSWORD', os.getenv('POSTGRES_PASSWORD', '')),
        'HOST': os.getenv('PGHOST', os.getenv('POSTGRES_HOST', 'localhost')),
        'PORT': os.getenv('PGPORT', os.getenv('POSTGRES_PORT', '5432')),
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Additional locations of static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Static root for collectstatic
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise storage for serving static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [origin.rstrip('/') for origin in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')]
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all origins in debug mode

# Alipay+ Configuration
ALIPAY_PUBLIC_KEY = os.getenv('ALIPAY_PUBLIC_KEY', '')
ALIPAY_PRIVATE_KEY = os.getenv('ALIPAY_PRIVATE_KEY', '')
ALIPAY_CLIENT_ID = os.getenv('ALIPAY_CLIENT_ID', '')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'services': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
