import logging

import bonobo
from bonobo.contrib.django import ETLCommand
from elasticsearch import Elasticsearch, ElasticsearchException
from elasticsearch.client import IndicesClient
from geostore.models import Layer
from terra_bonobo_nodes.common import ExcludeAttributes, GeometryToJson
from terra_bonobo_nodes.elasticsearch import (ESGeometryField,
                                              ESOptimizeIndexing, LoadInES)
from terra_bonobo_nodes.terra import ExtractFeatures
from django_geosource.models import Source, FieldTypes
from collections import defaultdict

logger = logging.getLogger(__name__)

EXCLUDED_FIELDS = ()
GEOMETRY_FIELD = 'geom'


class Command(ETLCommand):
    """ This is the ETL for indexing features in elasticsearch
    """

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        parser.add_argument('-layer', type=int, help='Index only a layer with pk', required=False)

    def get_services(self):
        return {
            'es': Elasticsearch(['elasticsearch'],
                                port=9200,
                                max_retries=10,
                                retry_on_timeout=True,
                                timeout=30,
                                ),
        }

    def get_graph(self, **options):
        if options['layer'] is not None:
            layer_qs = Layer.objects.filter(pk=options['layer'])
            if not layer_qs:
                logger.error("Layer couldn't be found")
                return
        else:
            layer_qs = Layer.objects.all()

        for layer in layer_qs:
            index_name = layer.name
            queryset = layer.features.all()

            graph = bonobo.Graph()

            graph.add_chain(
                LoadInES(index=index_name),
                _name="load",
                _input=None,
            )

            graph.add_chain(
                ESGeometryField(index_name, 'geom'),
                ESOptimizeIndexing(index_name),
                ExtractFeatures(queryset, extra_properties={'geom': 'geom', }),
                ExcludeAttributes(excluded=EXCLUDED_FIELDS),
                GeometryToJson(source='geom', destination='geom'),

                _output='load'
            )

            self.clean_index(index_name)
            self.create_index(layer)

            yield graph

            es = IndicesClient(self.get_services().get('es'))
            es.flush(
                index=index_name,
                wait_if_ongoing=True,
            )
            es.put_settings(
                index=index_name,
                body={
                    "index.refresh_interval": "1s",
                }
            )

    def clean_index(self, index):
        es = self.get_services()['es']
        try:
            es.indices.delete(index=index, ignore=[400, 404])
        except ElasticsearchException:
            pass

    def create_index(self, layer):
        """
        Create ES index with specified type mapping from layer source
        If mapping not available, we switch on ES type guessing
        """
        try:
            s = Source.objects.get(slug=layer.name)
        except Source.DoesNotExist:
            # If no source, we ignore it. Type will be guessed later.
            return

        # Pre create index only for source if configured
        if not s.settings.get('create_index'):
            logger.info(f'No index pre-creation for layer {layer.name}')
            return

        logger.info(f'Index creation for layer {layer.name}')

        type_mapping = defaultdict(lambda: 'text')
        type_mapping['integer'] = 'long'
        type_mapping['float'] = 'float'
        type_mapping['boolean'] = 'boolean'
        type_mapping['date'] = 'date'

        # Get type from source field configuration. Ignore undefined types.
        field_conf = {}
        for field in s.fields.all():
            if field.data_type != 5:
                field_type = type_mapping[FieldTypes(field.data_type).name.lower()]
                if field_type == 'text':
                    # Exception for text field, we also want them to be keyword accessible
                    field_conf[field.name] = {
                        "type": field_type,
                        "fields":{"keyword":{"type":"keyword","ignore_above":256}}
                    }
                else:
                    field_conf[field.name] = { "type": field_type }

        # Add geom default type mapping
        field_conf['geom'] = {
            "type": "geo_shape",
            "ignore_z_value": True
        }

        # Create query body with mapping
        body = {
            'mappings': {
                "properties": field_conf
            }
        }
        
        es = self.get_services()['es']
        try:
            es.indices.create(layer.name, body=body)
        except ElasticsearchException:
            logger.exception("ES index for layer {layer.name} can't be created")

