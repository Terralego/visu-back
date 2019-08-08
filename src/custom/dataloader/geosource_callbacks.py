import logging

from django.contrib.gis.geos import GEOSGeometry
from rest_framework.exceptions import MethodNotAllowed
from terracommon.terra.models import Layer

from custom.receivers import *  # noqa

logger = logging.getLogger(__name__)


def layer_callback(geosource):
    defaults = {
        'group': geosource.settings.pop('group', 'reference'),
        'settings': geosource.settings,
    }
    return Layer.objects.get_or_create(name=geosource.slug, defaults=defaults)[0]


def feature_callback(geosource, layer, identifier, geometry, attributes):
    # Force converting geometry to 4326 projection
    try:
        geom = GEOSGeometry(geometry)
        geom.transform(4326)
        return layer.features.update_or_create(identifier=identifier,
                                               defaults={'properties': attributes, 'geom': geom})[0]
    except TypeError:
        logger.warning(f'One record was ignored from source, because of invalid geometry: {attributes}')
        return None


def clear_features(geosource, layer, begin_date):
    return layer.features.filter(updated_at__lt=begin_date).delete()


def delete_layer(geosource):
    if geosource.layers.count() > 0:
        raise MethodNotAllowed('No layers must be linked to this source to be deleted')
    geosource.get_layer().features.all().delete()
    return geosource.get_layer().delete()
