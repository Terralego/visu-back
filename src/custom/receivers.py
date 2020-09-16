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
        logger.info('Starting elasticsearch indexing...')
        try:
            # Fix incompatibility with LoggingProxy from celery and 
            # mondrian from bonobo
            sys.stdout.buffer = BytesIO()
            sys.stdout.encoding = None
        except AttributeError:
            # This is a hack, should fails with some conditions
            pass

        call_command('etl_features_to_es', '-layer', kwargs['layer']) #noqa

        logger.info('Elasticsearch indexing succeed')

    except:
        logger.error('An error occurend during elastic search indexing', exc_info=True)

    logger.info('End of elasticsearch indexing')
