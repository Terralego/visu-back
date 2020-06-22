import asyncio

from django.conf import settings
from django.core.management import BaseCommand
from pyfiles.storages import get_storage


class Command(BaseCommand):
    help = "Add new test data to storage"

    def add_arguments(self, parser):
        parser.add_argument("filepath", help="path of the file to add")
        parser.add_argument("namespace", help="namespace where file is stored")
        parser.add_argument("filename", help="name of the file in the storage")
        parser.add_argument("version", help="version of the file")

    def handle(self, **options):
        filepath = options.get("filepath")
        namespace = options.get("namespace")
        filename = options.get("filename")
        version = options.get("version")

        storage = get_storage(settings.PYFILE_BACKEND, settings.PYFILE_OPTIONS)
        loop = asyncio.get_event_loop()
        with open(filepath, mode="rb") as f:
            loop.run_until_complete(storage.store(f, namespace, filename, version))
        loop.close()
