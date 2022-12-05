"""
Django settings for ag_smile_leaseback_crm_back project.

Generated by 'django-admin startproject' using Django 4.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG') == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
    "django_filters",
    "debug_toolbar",
    "django_extensions",
    "crm.apps.CrmConfig",
    "django_ses",
    "storages",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "ag_smile_leaseback_crm_back.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ag_smile_leaseback_crm_back.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# MySQLのパラメータを.envから取得
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        # コンテナ内の環境変数をDATABASESのパラメータに反映
        "NAME": os.environ.get("MYSQL_DATABASE"),
        "USER": os.environ.get("MYSQL_USER"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD"),
        "HOST": os.environ.get("MYSQL_HOST", "db"),
        "PORT": os.environ.get("MYSQL_PORT", "3306"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

# 言語を日本語に設定
LANGUAGE_CODE = "ja"
# タイムゾーンをAsia/Tokyoに設定
TIME_ZONE = "Asia/Tokyo"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_ROOT = "/static/"
STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": [
        'rest_framework.permissions.IsAuthenticated'
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 15,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "住まいるリースバック",
    "DESCRIPTION": "住まいるリースバックの案件管理システム",
    "VERSION": "1.0.0",
}

AUTH_USER_MODEL = "crm.User"

# ユーザー登録token有効期間１日
VERIFY_USER_TOKEN_EXPIRE = 60 * 60 * 24
# パスワードリセットtoken有効期間30分
PASSWORD_RESET_TOKEN_EXPIRE = 60 * 30

SESSION_COOKIE_AGE = 60 * 60 * 9 # 9時間 - セッション時間は自動的に伸ばす。
SESSION_SAVE_EVERY_REQUEST = True

# CORSの設定
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = (os.environ.get("TRUSTED_ORIGINS").split(" "))
CORS_PREFLIGHT_MAX_AGE = 60 * 30 #30分だけ

if DEBUG:
    EMAIL_HOST = 'mail'
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False

    SESSION_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    CSRF_COOKIE_SAMESITE = 'Strict'
    CSRF_COOKIE_SECURE = False
    CSRF_COOKIE_HTTPONLY = False
    CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1']
    USE_X_FORWARDED_HOST = True
else:
    #メールの設定
    EMAIL_BACKEND = 'django_ses.SESBackend'
    AWS_SES_REGION_NAME = os.environ.get("AWS_SES_REGION_NAME")
    AWS_SES_REGION_ENDPOINT = os.environ.get("AWS_SES_REGION_ENDPOINT")
    DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")

    #クッキーとCSRFの設定
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = False
    CSRF_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = False
    CSRF_TRUSTED_ORIGINS = os.environ.get("TRUSTED_ORIGINS").split(" ")
    CSRF_COOKIE_DOMAIN = os.environ.get("CSRF_COOKIE_DOMAIN")

    #AWS S3の設定
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    AWS_STORAGE_BUCKET_NAME = "leasebackcrm-bucket"

MEDIA_URL = '/upload/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'upload')

CRM_BASE_URL = os.environ.get("CRM_BASE_URL")
