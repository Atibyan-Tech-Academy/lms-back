"""
Django settings for core project.

Optimized for deployment on Render with a shared hosting frontend subdomain.
"""

import os
from decouple import config
import dj_database_url
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('SECRET_KEY', default='django-insecure-%h9s&eixn#v#nvck@pxp09t_5)va^hc*v4fb&7&!bd+#=tqc3y')  # Set in Render env
DEBUG = config('DEBUG', cast=bool, default=False)  # False for production
ALLOWED_HOSTS = ['*']  # Update to your Render URL (e.g., 'lms-backend.onrender.com') in production

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'accounts',
    'messaging',  # Core app for chat
    'cloudinary_storage',
    'cloudinary',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For serving static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
}

ROOT_URLCONF = 'core.urls'

ASGI_APPLICATION = "core.asgi.application"  # Kept for potential future WebSocket use

# Database (Render provides DATABASE_URL)
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',  # Fallback for local dev
        conn_max_age=600
    )
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (WhiteNoise for Render)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (Cloudinary)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = f'https://res.cloudinary.com/{CLOUDINARY_STORAGE["CLOUD_NAME"]}/' if CLOUDINARY_STORAGE["CLOUD_NAME"] else '/media/'

# CORS settings (allow frontend subdomain)
CORS_ALLOWED_ORIGINS = [
    config('FRONTEND_ORIGIN', default='http://localhost:5173'),  # Update to 'https://lms.yourdomain.com'
]
CSRF_TRUSTED_ORIGINS = [
    config('FRONTEND_ORIGIN', default='http://localhost:5173'),
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'