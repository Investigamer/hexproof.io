"""
* Django Project Settings

* For more information on this file, see:
https://docs.djangoproject.com/en/4.2/topics/settings/
https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
"""
# Standard Library Imports
import shutil
from pathlib import Path

# Third Party Imports
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'

# Load environment variables
if not ENV_PATH.is_file():
    shutil.copy2(ENV_PATH.with_stem('.env.dist'), ENV_PATH)
ENV = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'super-secret-django-key'),
    TIMEZONE=(str, 'America/Chicago')
)
environ.Env.read_env(ENV_PATH)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV('DEBUG')

# Hosts allowed access
ALLOWED_HOSTS = ENV.list('ALLOWED_HOSTS', default=['*'])

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = ENV.bool('CORS_ALLOW_ALL_ORIGINS', default=True)

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = ENV.list(
    "CSRF_TRUSTED_ORIGINS",
    # Required for Docker with Django 4.x+
    # May need custom assignments for advanced docker networks
    default=[
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.staticfiles',
    'corsheaders',
    'api'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'core.middleware.SubdomainRoutesMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'hexproof': {
            'class': 'api.utils.logger.LoguruHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['hexproof'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['hexproof'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['hexproof'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}

ROOT_URLCONF = 'core.urls'

SUBDOMAIN_ROUTES = {
    'cdn': 'cdn.urls',
    '*': 'core.urls',
}

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
            ]
        }
    }
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': ENV('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': ENV('DB_NAME', default='hexproof'),
        'USER': ENV('DB_USER', default='hexproof'),
        'PASSWORD': ENV('DB_PASS', default='hexproof'),
        'HOST': ENV('DB_HOST', default='localhost'),
        'PORT': ENV.int('DB_PORT', default=5432)
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

TIME_ZONE = ENV('TIMEZONE')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'staticfiles'
]
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
