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
