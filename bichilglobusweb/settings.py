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
    'app',
]

# Cloudinary суусан бол INSTALLED_APPS-д нэмнэ
try:
    import cloudinary as _cl_check  # noqa: F401
    INSTALLED_APPS.insert(-1, 'cloudinary')
except ImportError:
    pass

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

# Render эсвэл гадны PostgreSQL руу SSL холболт
DB_HOST = env("DB_HOST", default="localhost")
if env.bool("DB_SSL", default=False) or 'render.com' in DB_HOST:
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
# Файл upload хэмжээний хязгаар
DATA_UPLOAD_MAX_MEMORY_SIZE = 314572800   # 300MB — хүсэлтийн нийт хэмжээ
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760   # 10MB  — үүнээс том файл disk-д temp хадгална (OOM-с хамгаална)
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
# CLOUDINARY / LOCAL STORAGE CONFIGURATION
# ============================================================================
# Cloudinary API_KEY байвал Cloudinary ашиглана,
# байхгүй бол local media folder руу хадгална.
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': env('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': env('CLOUDINARY_API_SECRET', default=''),
}

# USE_CLOUDINARY: API key байвал True, байхгүй бол False (local storage)
USE_CLOUDINARY = bool(CLOUDINARY_STORAGE['API_KEY'])

if USE_CLOUDINARY:
    import cloudinary
    import cloudinary.api
    import cloudinary.uploader
    cloudinary.config(
        cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
        api_key=CLOUDINARY_STORAGE['API_KEY'],
        api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    )
else:
    print("ℹ️  Cloudinary идэвхгүй — local media storage ашиглана (/media/)")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SSL тохиргоо: .env дээр SECURE_SSL=True гэж тохируулна (reverse proxy SSL-тэй бол)
if env.bool("SECURE_SSL", default=False):
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
elif not DEBUG:
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