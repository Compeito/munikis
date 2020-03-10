from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

WEBPACK_LOADER['DEFAULT']['CACHE'] = not DEBUG

INSTALLED_APPS.extend([
    # django-extensions
    'django_extensions',
    # django-debug-toolbar
    'debug_toolbar',
])

# django-debug-toolbar
MIDDLEWARE += 'debug_toolbar.middleware.DebugToolbarMiddleware',

# django-debug-toolbar
INTERNAL_IPS = ['127.0.0.1', '192.168.99.1']

# django-cors-headers
CORS_ORIGIN_WHITELIST += ['http://localhost:8080']
