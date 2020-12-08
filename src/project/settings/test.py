# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import tempfile

from .base import *  # noqa

for a in INSTALLED_APPS:
    if "rest_framework" in a:
        REST_FRAMEWORK["TEST_REQUEST_DEFAULT_FORMAT"] = "json"

SECRET_KEY = "spam-spam-spam-spam"

MEDIA_ROOT = tempfile.mkdtemp()
FILE_UPLOAD_TEMP_DIR = tempfile.mkdtemp()

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Boost perf a little
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

del DATABASES["visu"]

# Force every loggers to use null handler only. Note that using 'root'
# logger is not enough if children don't propage.
for logger in six.itervalues(LOGGING["loggers"]):  # noqa
    logger["handlers"] = ["console"]

try:
    from .local import *  # noqa
except ImportError:
    pass
