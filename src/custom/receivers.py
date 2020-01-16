import logging
import sys
from io import BytesIO

from django.core.management import call_command
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_geosource.models import Source
from django_geosource.signals import refresh_data_done
from geostore.models import Layer
from terra_geocrud.models import CrudView

logger = logging.getLogger(__name__)


@receiver(refresh_data_done)
def refresh_es(sender, **kwargs):
    try:
        logger.info('Starting elasticsearch indexing')
        sys.stdout.encoding = None
        sys.stdout.buffer = BytesIO()
        call_command('etl_features_to_es', '-layer', kwargs['layer']) #noqa
        logger.info('Elasticsearch indexing sucess')
    except Exception:
        logger.error('An error occurend during indexing', exc_info=True)
    logger.info('End of elasticsearch indexing')


@receiver(post_save, sender=Layer)
def my_handler(sender, **kwargs):
    layer = kwargs['instance']
    if Source.objects.filter(slug=layer.name).exists():
        CrudView.objects.get_or_create(name=layer.name, layer=layer, order=0, )
