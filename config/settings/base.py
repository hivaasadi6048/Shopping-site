# config/settings/base.py
from pathlib import Path
from environs import Env
import os
from datetime import timedelta

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- مسیر ترجمه ---
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

# --- کلیدها ---
SECRET_KEY = env.str("DJANGO_SECRET_KEY")
DEBUG = env.bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", [])

# --- Zarinpal ---
ZARINPAL_MERCHANT_ID = env.str("DJANGO_ZARINPAL_MERCHANT_ID", "")
ZARINPAL_SANDBOX_MERCHANT_ID = env.str("DJANGO_ZARINPAL_SANDBOX_MERCHANT_ID", "")
ZARINPAL_USE_SANDBOX = env.bool("DJANGO_ZARINPAL_USE_SANDBOX", True)

# --- برنامه‌ها ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party
    'jalali_date',
    'crispy_forms',
    'crispy_bootstrap5',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rosetta',
    'django_ckeditor_5',
    'axes',

    # Local
    'accounts',
    'pages',
    'products',
    'cart',
    'dashboard',
    'adminpanel',
    'orders.apps.OrdersConfig',
]

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'adminpanel.middleware.AutoLogoutMiddleware',
]

ROOT_URLCONF = 'config.urls'

# --- Templates ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart',
                'core.context_processors.categories_processor',

            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- Database (پایه) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Passwords ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'accounts.backends.PhoneBackend',
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# --- Language ---
LANGUAGE_CODE = 'en'
LANGUAGES = (('en', 'English'), ('fa', 'Persian'))
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- Static & Media ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR / 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CKEditor ---
CKEDITOR_5_UPLOAD_PATH = "uploads/"
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': {
            'items': [
                'heading', '|', 'bold', 'italic', 'underline', 'link',
                'bulletedList', 'numberedList', '|',
                'outdent', 'indent', '|',
                'blockQuote', 'insertTable', 'undo', 'redo',
            ],
            'shouldNotGroupWhenFull': True
        },
        'language': 'fa',
    }
}

# --- Allauth ---
SITE_ID = 1
AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'account_login'
LOGOUT_REDIRECT_URL = '/accounts/login/'
ACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSignupForm',
}



# --- ایمیل ---
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SIGNUP_FIELDS = ['password1*', 'password2*']
ACCOUNT_LOGIN_METHODS = {'username'}

# --- Crispy ---
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --- Axes ---
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=5)
AXES_ONLY_USER_FAILURES = True
AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address']
AXES_META_PRECEDENCE_ORDER = ['HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']
AXES_USERNAME_FORM_FIELD = 'username'
AXES_DISALLOW_SUPERUSER = False
AXES_ONLY_SUPERUSER_FAILURES = False
AXES_CACHE = 'default'
AXES_LOCKOUT_TEMPLATE = 'registration/account_locked.html'
AXES_USE_USER_AGENT = True
AXES_VERBOSE = True

# --- Sessions ---
SESSION_COOKIE_AGE = 1200 #ثانیه
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"


ROSETTA_ACCESS_CONTROL_FUNCTION = 'django.contrib.admin.views.decorators.staff_member_required'