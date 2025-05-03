import os
import dj_database_url
from .settings import *
from .settings import BASE_DIR

ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME')]

CSRF_TRUSTED_ORIGINS = [f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"]

DEBUG = False

FRONTEND_URL = "https://wildwijs.nl/"


AWS_ACCESS_KEY_ID = os.environ.get(('AWS_ACCESS_KEY_ID'))
AWS_SECRET_ACCESS_KEY = os.environ.get(('AWS_SECRET_ACCESS_KEY'))
AWS_STORAGE_BUCKET_NAME = os.environ.get(('AWS_STORAGE_BUCKET_NAME'))
SECRET_KEY = os.environ.get(('SECRET_KEY'))

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = ['https://wildwijs.nl','https://wildwijs-frontend.onrender.com']

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ['DATABASE_URL'],
        conn_max_age=600,
    )
}

FRONTEND_URL = "https://wildwijs.nl"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.eu-central-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get(('EMAIL_HOST_USER'))
EMAIL_HOST_PASSWORD = os.environ.get(('EMAIL_HOST_PASSWORD'))
DEFAULT_FROM_EMAIL = 'noreply@wildwijs.nl'

CSRF_TRUSTED_ORIGINS = [
    "https://wildwijs.nl",
]

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True