from pathlib import Path
from dotenv import load_dotenv
import os

# BASE DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Project root is two levels up from BASE_DIR (src/backend -> src -> project_root)
PROJECT_ROOT = BASE_DIR.parent.parent

# Load environment variables from .env file (if it exists)
# In Docker, environment variables are passed via docker-compose, so this is optional
env_file = os.path.join(PROJECT_ROOT, '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)

# SECURITY
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [
    'stock-tracking-dc-production.up.railway.app',
    'localhost',
    '127.0.0.1',
]

CSRF_TRUSTED_ORIGINS = [
    'https://stock-tracking-dc-production.up.railway.app'
]

# INSTALLED APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'registration',
    'corsheaders',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap4',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django_filters',
    'api',
    'stock',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    'https://stock-tracking-dc-production.up.railway.app',
    'http://localhost:5173',  # Vite dev server
    'http://127.0.0.1:5173',
    'http://localhost:5174',  # Vite dev server alternate port
    'http://127.0.0.1:5174',
]

# Allow all origins in development
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'stockmgtr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'stock.context_processors.user_role',
            ],
        },
    },
]

WSGI_APPLICATION = 'stockmgtr.wsgi.application'

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("MYSQL_DATABASE"),
        'USER': os.getenv("MYSQL_USER"),
        'PASSWORD': os.getenv("MYSQL_PASSWORD"),
        'HOST': os.getenv("MYSQL_HOST"),
        'PORT': os.getenv("MYSQL_PORT"),
    }
}

# AUTH PASSWORD VALIDATORS
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Sydney'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# STATIC FILES
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise: Serve React build files from root (for /assets/ paths)
WHITENOISE_ROOT = os.path.join(BASE_DIR, 'frontend_build')

# Include both Django static files and React build files
# Check multiple possible locations for React build
REACT_BUILD_LOCATIONS = [
    os.path.join(BASE_DIR, 'frontend_build'),  # Railway/Docker production
    os.path.join(BASE_DIR.parent, 'frontend', 'dist'),  # Local development
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Add React build directory if it exists (for production)
for react_dir in REACT_BUILD_LOCATIONS:
    if os.path.exists(react_dir):
        STATICFILES_DIRS.append(react_dir)
        REACT_BUILD_DIR = react_dir
        break

# MEDIA FILES - Use local storage for all environments
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CACHING - Use Redis in production, local memory in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/0'),
        'KEY_PREFIX': 'stockdc',
        'TIMEOUT': 300,  # 5 minutes default timeout
    }
}

# SESSION - Use Redis for sessions in production
if not DEBUG:
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

# CRISPY FORMS
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# DJANGO REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# DRF Spectacular (OpenAPI documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Stock Tracking DC API',
    'DESCRIPTION': 'API for Stock Tracking and Inventory Management',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'COMPONENT_SPLIT_REQUEST': True,
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# DEFAULT PK
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ACCOUNT SETTINGS
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = False
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
REGISTRATION_OPEN = True

# EMAIL SETTINGS - Production-friendly configuration
# Always try SMTP first, handle failures gracefully in code
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_USE_SSL = True
EMAIL_TIMEOUT = 30
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_USER")

# SendGrid configuration (if API key is available)
if os.getenv('SENDGRID_API_KEY'):
    EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    DEFAULT_FROM_EMAIL = os.getenv("EMAIL_USER", 'noreply@yourdomain.com')
    
# Keep Gmail settings for manual override
GMAIL_SMTP_SETTINGS = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': 587,
    'EMAIL_HOST_USER': os.getenv("EMAIL_USER"),
    'EMAIL_HOST_PASSWORD': os.getenv("EMAIL_PASSWORD"),
    'EMAIL_USE_TLS': True,
    'EMAIL_TIMEOUT': 30,
}

# Alternative SMTP settings (uncomment if Gmail fails)
# EMAIL_HOST = 'smtp.outlook.com'
# EMAIL_PORT = 587
# Alternative: Try port 465 with SSL instead of TLS
# EMAIL_PORT = 465
# EMAIL_USE_SSL = True
# EMAIL_USE_TLS = False

# Logging for email debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'stock.tasks': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# CELERY CONFIGURATION
# Check if Redis is available, if not, disable Celery
def is_redis_available():
    try:
        import redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        return True
    except:
        return False

# Only configure Celery if Redis is available
if is_redis_available():
    CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = TIME_ZONE
    CELERY_ENABLE_UTC = True

    # Celery task routing
    CELERY_TASK_ROUTES = {
        'stock.tasks.send_email_async': {'queue': 'email'},
        'stock.tasks.send_purchase_order_email': {'queue': 'email'},
    }

    # Celery worker configuration
    CELERY_WORKER_PREFETCH_MULTIPLIER = 1
    CELERY_TASK_ACKS_LATE = True

    # Task result expires in 1 hour
    CELERY_RESULT_EXPIRES = 3600
    
    # Set a flag to indicate Celery is available
    CELERY_AVAILABLE = True
else:
    # Disable Celery if Redis is not available
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    CELERY_AVAILABLE = False

REGISTRATION_FORM = 'stock.form.CustomRegistrationForm'
