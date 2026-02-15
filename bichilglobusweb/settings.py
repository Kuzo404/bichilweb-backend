"""
Django settings for bichilglobusweb project.
"""

from pathlib import Path
import environ
import os

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'cloudinary',
    'app',
]

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

ROOT_URLCONF = 'bichilglobusweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bichilglobusweb.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("DB_NAME"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': env("DB_HOST", default="localhost"),
        'PORT': env("DB_PORT", default="5432"),
    }
}

# Render PostgreSQL руу SSL холболт (external холболтод шаардлагатай)
if 'render.com' in env("DB_HOST", default=""):
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=False)
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# ============================================================================
# UPLOAD & MEDIA SETTINGS
# ============================================================================
# Файл upload хэмжээний хязгаар (300MB хүртэл)
DATA_UPLOAD_MAX_MEMORY_SIZE = 314572800  # 300MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 314572800  # 300MB
# Үнэт видео, зураг файлуудыг хүлээн авах
FILE_UPLOAD_ALLOWED_MIME_TYPES = [
    # Зураг
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    # Видео
    'video/mp4',
    'video/webm',
    'video/quicktime',
    'video/mpeg',
    # Баримт
    'application/pdf',
]

# ============================================================================
# CLOUDINARY STORAGE CONFIGURATION
# ============================================================================
# Зураг, видео нуу бүх media файлуудыг Cloudinary дээр хадгалах
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME', default='ddkarwynp'),
    'API_KEY': env('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': env('CLOUDINARY_API_SECRET', default=''),
}

# Cloudinary шууд ашигла
import cloudinary
import cloudinary.api
import cloudinary.uploader

# API key үргэлж оршин байхыг шалгах (production дээр алдаа гаргана)
if not CLOUDINARY_STORAGE['API_KEY']:
    if not DEBUG:
        raise ValueError(
            "❌ CLOUDINARY_API_KEY environment variable идэвхгүй байна!\n"
            "Render Settings → Environment Variables дээр дараах хувьсагчуудыг нэмнэ үү:\n"
            "  - CLOUDINARY_CLOUD_NAME=ddkarwynp\n"
            "  - CLOUDINARY_API_KEY=114548364694963\n"
            "  - CLOUDINARY_API_SECRET=4T8kJhdnvGzyHKnPzxwBKl7xU30\n"
            "See: https://console.cloudinary.com"
        )

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "errors.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}