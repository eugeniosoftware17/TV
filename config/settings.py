"""
Django settings for Cloud Screen project.
"""
import sys
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Apps live inside app/ directory
sys.path.insert(0, str(BASE_DIR / "app"))

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="django-insecure-cloud-screen-dev-key-change-in-production")

DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "presentations",
    "screens",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = env("LANGUAGE_CODE", default="es-es")
TIME_ZONE = env("TIME_ZONE", default="America/Santiago")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "accounts:login"

# File upload limits
FILE_UPLOAD_MAX_MEMORY_SIZE = env.int("FILE_UPLOAD_MAX_MEMORY_SIZE", default=50 * 1024 * 1024)  # 50 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = env.int("DATA_UPLOAD_MAX_MEMORY_SIZE", default=50 * 1024 * 1024)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf"}
ALLOWED_MEDIA_EXTENSIONS = (
    ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS
)

# Screen offline threshold (seconds)
SCREEN_OFFLINE_THRESHOLD = env.int("SCREEN_OFFLINE_THRESHOLD", default=60)

# PowerPoint import
ALLOWED_POWERPOINT_EXTENSIONS = {".pptx", ".ppt"}
POWERPOINT_MAX_FILE_SIZE = env.int("POWERPOINT_MAX_FILE_SIZE", default=100 * 1024 * 1024)  # 100 MB
POWERPOINT_RENDER_DPI = env.int("POWERPOINT_RENDER_DPI", default=150)
POWERPOINT_DEFAULT_SLIDE_DURATION = env.int("POWERPOINT_DEFAULT_SLIDE_DURATION", default=10)
POWERPOINT_CONVERSION_TIMEOUT = env.int("POWERPOINT_CONVERSION_TIMEOUT", default=300)
POWERPOINT_USE_CELERY = env.bool("POWERPOINT_USE_CELERY", default=False)
LIBREOFFICE_BINARY = env("LIBREOFFICE_BINARY", default=None) or None  # Auto-detect; o ruta absoluta a soffice
