from .base import *
import json
from google.oauth2 import service_account

DEBUG = False

WEBPACK_LOADER['DEFAULT']['CACHE'] = not DEBUG

ADMINS = [('admin', env('ADMIN_MAIL', default='admin@example.com'))]
SERVER_EMAIL = 'admin@tsukuriga.net'

# 設定参考
# https://www.monotalk.xyz/blog/Validate-security-settings-by-adding-deploy-option-to-Django-check-command/
# security.W004
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# security.W006
SECURE_CONTENT_TYPE_NOSNIFF = True
# security.W007
SECURE_BROWSER_XSS_FILTER = True
# security.W008
# SECURE_SSL_REDIRECT = True
# security.W012
SESSION_COOKIE_SECURE = True
# security.W016, security.W017
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
# security.W019
X_FRAME_OPTIONS = 'DENY'
# security.W021
# SECURE_HSTS_PRELOAD = True

# https://github.com/python-social-auth/social-core/issues/250#issuecomment-436832460
SESSION_COOKIE_SAMESITE = None

# django-storage-swift
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'tsukuriga-test-bucket'
GS_CREDENTIALS = service_account.Credentials.from_service_account_info(
    json.load(env('RUN_SA_KEY')),
)

# mail
EMAIL_USE_SSL = True
EMAIL_HOST = 'smtp.muumuu-mail.com'
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = 465
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'Tsukuriga <mail@tsukuriga.net>'

# django-social-auth
# https://stackoverflow.com/a/51503408
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
