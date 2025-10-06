# core/settings.py
"""
Django settings for core project (LMS).

Optimized for local dev and deployment (e.g., Render, Railway, etc.)
"""

import os
from pathlib import Path
from decouple import config
import dj_database_url

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure logs directory exists
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)  # Creates logs directory if it doesn't exist

# Security
SECRET_KEY = config("SECRET_KEY", default="django-insecure-temp-key")
DEBUG = config("DEBUG", cast=bool, default=True)

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    config("BACKEND_HOST", default=""),
]

# Installed apps
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "corsheaders",
    "cloudinary",
    "cloudinary_storage",
    "django_filters",  # Added for filtering

    # LMS apps
    "accounts",
    "assignments",
    "certificates",
    "courses",
    "editprofile",
    "messaging",

    # Optional AI integration (create ai/ app later if needed)
    "ai_chat",
    "public_announcements",
    "support",
]

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # must come first
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"  # kept if you want WebSockets later

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# Database
ENV = config("ENV", default="dev")

if ENV == "prod":
    DATABASES = {
        "default": dj_database_url.config(
            default=config("DATABASE_URL", default="sqlite:///db.sqlite3"),
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static & Media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME", default=""),
    "API_KEY": config("CLOUDINARY_API_KEY", default=""),
    "API_SECRET": config("CLOUDINARY_API_SECRET", default=""),
}
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
MEDIA_URL = f"https://res.cloudinary.com/{CLOUDINARY_STORAGE['CLOUD_NAME']}/" if CLOUDINARY_STORAGE["CLOUD_NAME"] else "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
}

# CORS
CORS_ALLOWED_ORIGINS = [
    config("FRONTEND_ORIGIN", default="http://localhost:5173"),
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# Default PK
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === AI Integration ===
# Hugging Face API (free tier)
HF_API_URL = config("HF_API_URL", default="https://api-inference.huggingface.co/models/distilgpt2")
HF_API_TOKEN = config("HF_API_TOKEN", default="")  # optional

# If running locally with transformers
LOCAL_AI_MODEL = config("LOCAL_AI_MODEL", default="distilgpt2")

# === EMAIL CONFIGURATION ===
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="yourgmail@gmail.com")      # your Gmail address
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="your_app_password")    # Gmail App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ADMIN_EMAIL = "admin@example.com"            # where support emails are sent

# === LOGGING ===
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "app.log",  # Use LOGS_DIR
        },
    },
    "loggers": {
        "accounts": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    },
}