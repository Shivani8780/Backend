import os
import dj_database_url
from .settings import BASE_DIR
from .settings import *

ALLOWED_HOSTS = [os.environ.get("RENDER_EXTERNAL_HOSTNAME")]
CSRF_TRUSTED_ORIGINS = ['https://'+os.environ.get("RENDER_EXTERNAL_HOSTNAME")]  

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')

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

CORS_ALLOWED_ORIGINS = [
    # Add your deployed frontend URLs here as needed
    "https://auth-ebooklet-frontend.onrender.com",
    "https://backend-un6n.onrender.com"
]

CSRF_TRUSTED_ORIGINS = [
    # Add your deployed frontend URLs here as needed
    "https://auth-ebooklet-frontend.onrender.com",
    "https://backend-un6n.onrender.com"
]

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600
    )
}

# Media and Static files configuration for deployment
# For static PDF booklets that don't change often
MEDIA_ROOT = BASE_DIR / 'media'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Additional static files directories
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# URL configurations
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# WhiteNoise configuration for better static file serving
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
