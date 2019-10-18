import logging

import bonobo
from bonobo.contrib.django import ETLCommand
from django.db.models import F
from elasticsearch import Elasticsearch, ElasticsearchException
from elasticsearch.client import IndicesClient
from geostore.models import Feature
from terra_bonobo_nodes.common import ExcludeAttributes, GeometryToJson
from terra_bonobo_nodes.elasticsearch import ESGeometryField, ESOptimizeIndexing, LoadInES
from terra_bonobo_nodes.terra import ExtractFeatures


logger = logging.getLogger(__name__)

EXCLUDED_FIELDS = ()
GEOMETRY_FIELD = 'geom'


class Command(ETLCommand):
    """ This is the ETL for indexing features in elasticsearch
    """
    INDEX_NAME = 'features'

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
        queryset = Feature.objects.annotate(layer_name=F('layer__name'))
        if options['layer'] is not None:
            queryset = queryset.filter(layer__pk=options['layer'])
            if queryset.count():
                self.clean_layer_index(queryset.first().layer)
            else:
                logger.error("Layer couldn't be found")
                return

        graph = bonobo.Graph()

        graph.add_chain(
            LoadInES(index=self.INDEX_NAME),
            _name="load",
            _input=None,
        )

        graph.add_chain(
            ESGeometryField(self.INDEX_NAME, 'geom'),
            ESOptimizeIndexing(self.INDEX_NAME),
            ExtractFeatures(queryset, extra_properties={'geom': 'geom', 'layer': 'layer_name'}),
            ExcludeAttributes(excluded=EXCLUDED_FIELDS),
            GeometryToJson(source='geom', destination='geom'),

            _output='load'
        )

        yield graph

        es = IndicesClient(self.get_services().get('es'))
        es.flush(
            index=self.INDEX_NAME,
            wait_if_ongoing=True,
        )
        es.put_settings(
            index=self.INDEX_NAME,
            body={
                "index.refresh_interval": "1s",
            }
        )

    def clean_layer_index(self, layer):
        es = self.get_services()['es']
        try:
            es.delete_by_query(
                index=self.INDEX_NAME, body={'query': {'match': {'layer.keyword': layer.name}}})
        except ElasticsearchException:
            pass
