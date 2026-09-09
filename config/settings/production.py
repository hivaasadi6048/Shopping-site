# config/settings/production.py
from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", [])

# دیتابیس واقعی
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('POSTGRES_DB'),
        'USER': env.str('POSTGRES_USER'),
        'PASSWORD': env.str('POSTGRES_PASSWORD'),
        'HOST': env.str('POSTGRES_HOST', 'localhost'),
        'PORT': env.int('POSTGRES_PORT', 5432),
    }
}

# ایمیل واقعی (Gmail موقت)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env.str('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', 587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ارسال ایمیل به ادمین برای خطاها
ADMINS = [('Admin', 'admin@yourdomain.com')]
SERVER_EMAIL = 'server@yourdomain.com'


# تنظیمات امنیتی
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True




# هر خطایی که در سایت پیش بیاد در فایل لاگ ذخیره میشود و یک ایمیل هم به ادمین ارسال میشود
LOG_DIR = BASE_DIR / 'logs'
os.makedirs(LOG_DIR, exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },

    'handlers': {
        # ذخیره همه لاگ‌ها
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'django.log',
            'formatter': 'verbose',
        },
        # خطاهای بحرانی
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'errors.log',
            'formatter': 'verbose',
        },
        # نمایش در کنسول (برای Debug)
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        # 🔹 مخصوص AutoLogoutMiddleware
        'auto_logout_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'auto_logout.log',
            'formatter': 'verbose',
        },
    },

    'loggers': {
        # لاگر اصلی جنگو
        'django': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },

        # 🔹 لاگر مخصوص middleware ما
        'adminpanel.middleware': {
            'handlers': ['auto_logout_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


#پیکربندی Whitenoise (برای Static Files)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

