import logging
import sys
from io import BytesIO

from django.core.management import call_command
from django.dispatch import receiver
from django_geosource.signals import refresh_data_done

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
