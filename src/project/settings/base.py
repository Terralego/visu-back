# -*- coding: utf-8 -*-
"""
Django settings

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
from __future__ import absolute_import, division, print_function

import copy
import os
from datetime import timedelta
from importlib import import_module

import six
from django.utils.log import DEFAULT_LOGGING

USE_TZ = True

INSTALLED_APPS = (
    "terra_settings",
    "django.contrib.admin",
    "django.contrib.messages",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "rest_framework_gis",
    "corsheaders",
    "terra_accounts",
    "geostore",
    "django_geosource",
    "terra_layer",
    "mapbox_baselayer",
    "custom.dataloader",
)

AUTH_USER_MODEL = "terra_accounts.TerraUser"

PROJECT_DIR = os.path.abspath(".")
PUBLIC_DIR = os.path.join(PROJECT_DIR, "public")
PROJECT_NAME = os.environ.get("PROJECT_PACKAGE")
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
ROOT_URLCONF = PROJECT_NAME + ".urls"

os.environ.setdefault("RELATIVE_SETTINGS_MODULE", "")
RELATIVE_SETTINGS_MODULE = os.environ.get("RELATIVE_SETTINGS_MODULE")

JWT_AUTH = {
    "JWT_PAYLOAD_HANDLER": "terra_accounts.jwt_payload.terra_payload_handler",
    "JWT_EXPIRATION_DELTA": timedelta(hours=1),
    "JWT_ALLOW_REFRESH": True,
}

TOKEN_TIMEOUT = 3600

REST_FRAMEWORK = {
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_PAGINATION_CLASS": "terra_settings.pagination.PagePagination",
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
        "url_filter.integrations.drf.URLFilterBackend",
    ),
    "PAGE_SIZE": 100,
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    **JWT_AUTH,
}

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

LOGGING = copy.deepcopy(DEFAULT_LOGGING)

STATIC_ROOT = "/code/public/static/"
STATIC_URL = "/static_dj/"
MEDIA_ROOT = "/code/public/media/"
MEDIA_ROOT_SECURE = os.path.join(MEDIA_ROOT, "private")
MEDIA_URL = "/media/"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

CELERY_BROKER_URL = "redis://redis:6379/2"
CELERY_RESULT_BACKEND = "redis://redis:6379/2"

GEOSOURCE_LAYER_CALLBACK = "custom.dataloader.geosource_callbacks.layer_callback"
GEOSOURCE_FEATURE_CALLBACK = "custom.dataloader.geosource_callbacks.feature_callback"
GEOSOURCE_CLEAN_FEATURE_CALLBACK = (
    "custom.dataloader.geosource_callbacks.clear_features"
)
GEOSOURCE_DELETE_LAYER_CALLBACK = "custom.dataloader.geosource_callbacks.delete_layer"

TERRA_DEFAULT_MAP_SETTINGS = {
    "accessToken": "",
    "backgroundStyle": "mapbox://styles/makinacorpus/cjx0630i50y1d1cpk006a92k9",
    "center": [-2.028, 47.852],
    "zoom": 7.7,
    "maxZoom": 19.9,
    "minZoom": 7,
    "fitBounds": {"coordinates": [[-4.850, 46.776], [-0.551, 48.886]]},
}

TERRA_LAYER_VIEWS = {}

TERRA_APPLIANCE_SETTINGS = {
    "VIEW_ROOT_PATH": "visualiser",
    "DEFAULT_VIEWNAME": 1,
    "enabled_modules": ["User", "DataSource", "DataLayer", "View", "BaseLayer"],
}

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", 5432),
    },
}

TILE_FLAVOR = "smart"

MIN_TILE_ZOOM = 7
MAX_TILE_ZOOM = 16

TERRA_TILES_HOSTNAMES = []

# let DEBUG & CORS be overridable in prod
DEBUG = False
CORS_ORIGIN_ALLOW_ALL = False


# pyfile storage use to load and store data
PYFILES_BACKEND = os.getenv("PYFILES_BACKEND")
PYFILES_OPTIONS = {
    "access_key": os.getenv("PYFILES_ACCESS_KEY"),
    "secret_key": os.getenv("PYFILES_SECRET_KEY"),
    "endpoint_url": os.getenv("PYFILES_ENDPOINT_URL"),
    "region_name": os.getenv("PYFILES_REGION_NAME"),
    "bucket_name": os.getenv("PYFILES_BUCKET_NAME"),
}


STORAGE_NAMESPACE = "VISU:datas"


import ldap
from django_auth_ldap.config import LDAPSearch, LDAPGroupQuery,GroupOfNamesType,PosixGroupType

AUTHENTICATION_BACKENDS = ["django_auth_ldap.backend.LDAPBackend"]


AUTH_LDAP_SERVER_URI = "ldap://ldap"


AUTH_LDAP_CACHE_GROUPS = False
# #
# AUTH_LDAP_USER_SEARCH = LDAPSearch('ou=users,dc=example,dc=org', ldap.SCOPE_SUBTREE, '(uid=%(user)s)')
# AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=org'
# AUTH_LDAP_BIND_PASSWORD = 'admin'

# AUTH_LDAP_GROUP_SEARCH = LDAPSearch('ou=groups,dc=example,dc=org', ldap.SCOPE_SUBTREE, '(objectClass=posixGroup)')
#
AUTH_LDAP_USER_ATTR_MAP = {
    "is_active": True,
    "is_staff": True,
    "first_name": "givenName",
    "last_name": "sn",
    "email": "uid",
    "username": "uid",
    "password": "userPassword",
}

# AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#    "is_active": "cn=active,dc=example,dc=org",
#    "is_staff": "cn=staff,dc=example,dc=org",
#    "is_superuser": "cn=staff,dc=example,dc=org",
# }
# AUTH_LDAP_GROUP_TYPE = PosixGroupType(name_attr="cn")
# AUTH_LDAP_MIRROR_GROUPS = True
# # This is the default, but I like to be explicit.
# AUTH_LDAP_ALWAYS_UPDATE_USER = True

# # Use LDAP group membership to calculate group permissions.
# AUTH_LDAP_FIND_GROUP_PERMS = True

AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=org"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"django_auth_ldap": {"level": "DEBUG", "handlers": ["console"]}},
}
