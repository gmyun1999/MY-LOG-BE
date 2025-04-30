from pathlib import Path
import environ
from decimal import ROUND_HALF_UP, DefaultContext

# Initialize environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(env_file=BASE_DIR / ".env")

# Environment Settings
ENV = env("ENV", default="localhost")
SECRET_KEY = env("SECRET_KEY", default="")
DEBUG = env.bool("DEBUG", default=True)
<<<<<<< HEAD
ALLOWED_HOSTS = ["*"]
=======
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])
>>>>>>> de5c1f7c2bef64ea8c8bf84a7a103952a0bad448

# Logging Settings
LOG_FILE = BASE_DIR / "logs/debug.log"
LOG_FILE.parent.mkdir(exist_ok=True)
LOG_FILE.touch(exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} || {message}", "style": "{"},},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "filename": LOG_FILE,
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 10,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "django": {"handlers": ["file", "console"], "level": "INFO", "propagate": True},
    },
}

<<<<<<< HEAD
# swagger
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema"
}
# SPECTACULAR_SETTINGS = {
#     "TITLE": "user API",
#     "DESCRIPTION": "Documentation for user API",
#     "VERSION": "1.0.0",
#     "APPEND_COMPONENTS": APPEND_COMPONENTS,
# }

=======
>>>>>>> de5c1f7c2bef64ea8c8bf84a7a103952a0bad448
# Installed Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
<<<<<<< HEAD
    "user"
=======
>>>>>>> de5c1f7c2bef64ea8c8bf84a7a103952a0bad448
]

# Middleware
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# URL Configuration
ROOT_URLCONF = "config.urls"

# Templates
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

# WSGI Application
WSGI_APPLICATION = "config.wsgi.application"

# Database Configuration

# PostgreSQL Configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
<<<<<<< HEAD
        "NAME": "mylogbe",
=======
        "NAME": "postgres",
>>>>>>> de5c1f7c2bef64ea8c8bf84a7a103952a0bad448
        "USER": "postgres",
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default=""),
        "PORT": "5432",
        "OPTIONS": {
            "options": "-c search_path=public,content",
        },
        "POOL_OPTIONS": {
            "POOL_SIZE": 30,
            "MAX_OVERFLOW": 10,
            "RECYCLE": 90,
            "PRE_PING": True,
        },
    }
}


# Static Files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Language and Time Zone
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# Default Primary Key
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DefaultContext.rounding = ROUND_HALF_UP
<<<<<<< HEAD
JWT_SECRET = env("JWT_SECRET", default="")
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default="GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET", default="GOOGLE_CLIENT_SECRET")
BASE_URL=env("BASE_URL", default="http://localhost:8000")
=======
>>>>>>> de5c1f7c2bef64ea8c8bf84a7a103952a0bad448
