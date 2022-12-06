# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from .base import *  # noqa

# SECURITY #

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_HTTPONLY = True

# Suppose we are using HTTPS
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False

STATICFILES_DIRS = []
MEDIA_ACCEL_REDIRECT = False

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


try:
    from .local import *  # noqa
except ImportError:
    pass
