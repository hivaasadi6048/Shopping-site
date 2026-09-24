# config/settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.1.100']

# برای Django Debug Toolbar
import debug_toolbar
INTERNAL_IPS = ['127.0.0.1', 'localhost']

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

INSTALLED_APPS += ['debug_toolbar']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env.str('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', 587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

AXES_ENABLED = False
AXES_FAILURE_LIMIT = 10
AXES_COOLOFF_TIME = timedelta(seconds=10)
