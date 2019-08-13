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

INSTALLED_APPS = ()
CUSTOM_APPS = (
    'terracommon.core',
    'terracommon.accounts',
    'terracommon.terra',
    'terracommon.events',
    'terracommon.datastore',
    'django_geosource',
    'terra_layer',
    'custom.dataloader',
)

os.environ.setdefault('RELATIVE_SETTINGS_MODULE', '')
RELATIVE_SETTINGS_MODULE = os.environ.get('RELATIVE_SETTINGS_MODULE')

for app in CUSTOM_APPS:
    try:
        app_settings = import_module(
            f"{app}.settings{RELATIVE_SETTINGS_MODULE}", ["settings"])

        for setting in dir(app_settings):
            if setting == setting.upper():
                globals()[setting] = getattr(app_settings, setting)

    except ImportError:
        pass

INSTALLED_APPS += CUSTOM_APPS

JWT_AUTH['JWT_EXPIRATION_DELTA'] = timedelta(hours=1)
JWT_AUTH['JWT_AUTH_COOKIE'] = 'jwt'

STATIC_ROOT = '/code/public/static/'
STATIC_URL = '/static_dj/'
MEDIA_ROOT = '/code/public/media/'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
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
    'visu': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('VISU_DB'),
        'USER': os.environ.get('VISU_USER'),
        'PASSWORD': os.environ.get('VISU_PASSWORD'),
        'HOST': os.environ.get('VISU_HOST', 'db'),
        'PORT': os.environ.get('VISU_PORT', 5432),
    }
}

REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = ()

ALLOWED_HOSTS = ['*', ]
CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK.update({
    'DEFAULT_PERMISSION_CLASSES': (),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
})

SWAGGER_ENABLED = False

CELERY_BROKER_URL = 'redis://redis:6379/2'
CELERY_RESULT_BACKEND = 'redis://redis:6379/2'

# let DEBUG & CORS be overridable in prod
DEBUG = False
CORS_ORIGIN_ALLOW_ALL = False

###########################################
# Visu specifics
###########################################

# Tile generation flavour
TILE_FLAVOR = 'smart'

# Tile min and max zoom
MIN_TILE_ZOOM = 7
MAX_TILE_ZOOM = 16

TERRA_TILES_HOSTNAMES = []

# Graphhopper URL
GRAPHHOPPER = ''

GEOSOURCE_LAYER_CALLBACK = 'custom.dataloader.geosource_callbacks.layer_callback'
GEOSOURCE_FEATURE_CALLBACK = 'custom.dataloader.geosource_callbacks.feature_callback'
GEOSOURCE_CLEAN_FEATURE_CALLBACK = 'custom.dataloader.geosource_callbacks.clear_features'
GEOSOURCE_DELETE_LAYER_CALLBACK = 'custom.dataloader.geosource_callbacks.delete_layer'


TERRA_DEFAULT_MAP_SETTINGS = {
    'accessToken': '',
    'backgroundStyle': 'mapbox://styles/makinacorpus/cjx0630i50y1d1cpk006a92k9',
    'center': [-2.028, 47.852],
    'zoom': 7.7,
    'maxZoom': 19.9,
    'minZoom': 7,
    'fitBounds': {
        'coordinates': [
            [-4.850, 46.776],
            [-0.551, 48.886]
        ],
    },
}

TERRA_APPLIANCE_SETTINGS = {}
