import asyncio
import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django_geosource.models import (
    GeoJSONSource,
    GeometryTypes,
)
from pyfiles.storages import get_storage
from terra_layer.models import Layer, Scene

UserModel = get_user_model()


def load_data():
    pass
    #  Load your default data here


@transaction.atomic()
def load_test_source_and_layer():
    pyfile_storage = get_storage(settings.PYFILE_BACKEND, settings.PYFILE_OPTIONS,)

    # Create test scenes
    map_scene, _ = Scene.objects.get_or_create(name="test_map_scene")
    story_scene, _ = Scene.objects.get_or_create(
        name="test_story_scene", category="story"
    )

    loop = asyncio.get_event_loop()
    for i, source_file in enumerate(settings.SOURCE_FILES):
        name, geom_name, id_field = source_file
        geom_type = GeometryTypes[geom_name].value

        result = loop.run_until_complete(
            pyfile_storage.search(settings.STORAGE_NAMESPACE, name)
        )
        r = requests.get(result["url"])
        # directly get content from storage, need a file object for the filefield
        f = SimpleUploadedFile(name, r.content)
        source, created = GeoJSONSource.objects.get_or_create(
            file=f, name=f.name, geom_type=geom_type, id_field=id_field
        )
        source.update_fields()
        layer, _ = Layer.objects.get_or_create(
            source=source,
            name=source.name,
            active_by_default=True,
            layer_style={"type": "circle", "paint": {"circle-color": "#40d892"}},
        )

        for field in source.fields.all():
            if not layer.fields_filters.filter(field__name=field.name).exists():
                layer.fields_filters.create(field=field)

        # roughly split the test files between two scenes so both map & story can be tested
        if i < len(settings.SOURCE_FILES) / 2:
            map_scene.insert_in_tree(layer, ["group_map",])
        else:
            story_scene.insert_in_tree(layer, ["group_story",])

        # data needs to be refresh to be accessible on the map
        source.run_sync_method("refresh_data")
    loop.close()


def load_test_data():
    create_test_users()
    load_test_source_and_layer()


def create_test_users():
    print("Populate test users...")
    users_data = [
        {"email": "visu@terralego.fake", "_groups": [], "_is_superuser": True}
    ]

    groups = {}
    for user_data in users_data:
        is_superuser = user_data.get("_is_superuser")

        # Common properties
        user_data["password"] = "visu"

        fields = {k: v for k, v in user_data.items() if not k.startswith("_")}
        if is_superuser:
            user = UserModel.objects.create_superuser(**fields)
        else:
            user = UserModel.objects.create_user(**fields)

        user_groups = user_data.get("_groups")
        if user_groups:
            for groupname in user_groups:
                if not groups.get(groupname):
                    groups[groupname], _ = Group.objects.get_or_create(name=groupname)
                user.groups.add(groups[groupname])
