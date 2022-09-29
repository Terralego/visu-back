import logging
import sys
import psycopg2
from io import BytesIO

from django.conf import settings
from django.core.management import call_command
from django.dispatch import receiver
from django_geosource.signals import refresh_data_done

logger = logging.getLogger(__name__)

database = settings.DATABASES["default"]


@receiver(refresh_data_done)
def refresh_es(sender, **kwargs):
    try:
        logger.info("Starting elasticsearch indexing...")
        try:
            # Fix incompatibility with LoggingProxy from celery and
            # mondrian from bonobo
            sys.stdout.buffer = BytesIO()
            sys.stdout.encoding = None
        except AttributeError:
            # This is a hack, should fails with some conditions
            pass
        
        # Run database maintenance
        # After heavy transaction on tables,
        # Postgres needs to vacuun and reindex
        try:
            conn = psycopg2.connect(
                user=database["USER"],
                password=database["PASSWORD"],
                port=database["PORT"],
                dbname=database["NAME"],
                host=database["HOST"],
            )
        except psycopg2.OperationalError:
            logger.info("Database maintenance failed !")
        else:
            # Vacuum command cannot run inside transaction
            # cf https://www.psycopg.org/docs/extensions.html?highlight=isolation%20level#psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            cursor.execute("VACUUM ANALYZE")
            cursor.execute("VACUUM FULL")
            cursor.execute(f"REINDEX DATABASE {database['NAME']}")
            cursor.close()
            conn.close()

        call_command("etl_features_to_es", "-layer", kwargs["layer"])  # noqa

        logger.info("Elasticsearch indexing succeed")

    except:
        logger.error("An error occurend during elastic search indexing", exc_info=True)

    logger.info("End of elasticsearch indexing")
