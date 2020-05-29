import logging
import sys
from io import BytesIO

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_geosource.models import Source, GeoJSONSource
from django_geosource.signals import refresh_data_done
from geostore.models import Layer, LayerGroup
from terra_geocrud.models import CrudView, CrudViewProperty
from terra_geocrud.properties.schema import sync_layer_schema

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


@receiver(post_save)
def update_layer_on_source_creation(sender, **kwargs):
    obj = kwargs['instance']
    if isinstance(obj, Source):
        source = obj
        group_name = source.settings.pop('group', 'reference')

        defaults = {
            'settings': source.settings,
        }

        layer, created = Layer.objects.get_or_create(name=source.slug, defaults=defaults, geom_type=source.geom_type)

        layer_groups = Group.objects.filter(pk__in=source.settings.get('groups', []))

        if set(layer.authorized_groups.all()) != set(layer_groups):
            layer.authorized_groups.set(layer_groups)

        if not layer.layer_groups.filter(name=group_name).exists():
            group, _ = LayerGroup.objects.get_or_create(name=group_name)
            group.layers.add(layer)

        if settings.USE_TERRAGEOCRUD:
            crud_view = CrudView.objects.get_or_create(layer=layer,
                                                       defaults={"name": layer.name, "order": 0})[0]
            fields = source.fields.all()
            for field in fields:
                data_type = field.data_type
                name = field.name
                label = field.label
                if data_type == 1:
                    final_type = "string"
                elif data_type == 2:
                    final_type = "string"
                elif data_type == 3:
                    final_type = "float"
                elif data_type == 4:
                    final_type = "boolean"
                property, created = CrudViewProperty.objects.get_or_create(view=crud_view, key=name)
                property.json_schema = {"title": label, "type": final_type}
                property.save()

            sync_layer_schema(crud_view)
