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
from terra_utils.helpers import Choices

USE_TZ = True

USE_TERRAGEOCRUD =  os.environ.get('TERRAGEOCRUD', False)

INSTALLED_APPS = (
    'terra_utils',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework',
    'rest_framework_gis',
    'corsheaders',

    'terra_accounts',
    'geostore',
    'django_geosource',
    'terra_layer',

    'template_model',
    'mapbox_baselayer',
    'django.contrib.admin',
    'django.contrib.messages',
    'custom.dataloader',
    'django_json_widget',
    'reversion',
    'sorl.thumbnail',
)

if USE_TERRAGEOCRUD:
    INSTALLED_APPS += ('terra_geocrud',
                       'django_object_actions')

AUTH_USER_MODEL = 'terra_accounts.TerraUser'

PROJECT_DIR = os.path.abspath('.')
PUBLIC_DIR = os.path.join(PROJECT_DIR, 'public')
PROJECT_NAME = os.environ.get('PROJECT_PACKAGE')
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
ROOT_URLCONF = PROJECT_NAME + '.urls'

os.environ.setdefault('RELATIVE_SETTINGS_MODULE', '')
RELATIVE_SETTINGS_MODULE = os.environ.get('RELATIVE_SETTINGS_MODULE')

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(hours=1),
    'JWT_ALLOW_REFRESH': True,
    'JWT_PAYLOAD_HANDLER': 'terra_accounts.jwt_payload.terra_payload_handler',
}

TOKEN_TIMEOUT = 3600

REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PAGINATION_CLASS':
        'terra_utils.pagination.PagePagination',
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
        'url_filter.integrations.drf.URLFilterBackend',
     ),
    'PAGE_SIZE': 100,

    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    **JWT_AUTH,
}

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

LOGGING = copy.deepcopy(DEFAULT_LOGGING)

STATIC_ROOT = '/code/public/static/'
STATIC_URL = '/static_dj/'
MEDIA_ROOT = '/code/public/media/'
MEDIA_ROOT_SECURE = os.path.join(MEDIA_ROOT, 'private')
MEDIA_URL = '/media/'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CELERY_BROKER_URL = 'redis://redis:6379/2'
CELERY_RESULT_BACKEND = 'redis://redis:6379/2'

GEOSOURCE_LAYER_CALLBACK = 'custom.dataloader.geosource_callbacks.layer_callback'
GEOSOURCE_FEATURE_CALLBACK = 'custom.dataloader.geosource_callbacks.feature_callback'
GEOSOURCE_CLEAN_FEATURE_CALLBACK = 'custom.dataloader.geosource_callbacks.clear_features'
GEOSOURCE_DELETE_LAYER_CALLBACK = 'custom.dataloader.geosource_callbacks.delete_layer'

TERRA_DEFAULT_MAP_SETTINGS = {
    "accessToken": "",
    "backgroundStyle": "mapbox://styles/makinacorpus/cjx0630i50y1d1cpk006a92k9",
    "center": [-2.028, 47.852],
    "zoom": 7.7,
    "maxZoom": 19.9,
    "minZoom": 7,
    "fitBounds": {"coordinates": [[-4.850, 46.776], [-0.551, 48.886]]},
}

TERRA_LAYER_VIEWS = {
}

TERRA_APPLIANCE_SETTINGS = {
    'VIEW_ROOT_PATH': 'visualiser',
    'DEFAULT_VIEWNAME': 1,
    'enabled_modules': ['User', 'DataSource', 'DataLayer', 'View'],
}

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', 5432),
    },
}

STATES = Choices()

ALLOWED_HOSTS = ['*', ]
CORS_ORIGIN_ALLOW_ALL = True

TILE_FLAVOR = 'smart'

MIN_TILE_ZOOM = 2
MAX_TILE_ZOOM = 16
INTERNAL_GEOMETRY_SRID = 4326

TERRA_TILES_HOSTNAMES = []

# let DEBUG & CORS be overridable in prod
DEBUG = False
