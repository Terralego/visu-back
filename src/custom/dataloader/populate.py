import asyncio
import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.db.utils import IntegrityError
from django_geosource.models import (
    GeoJSONSource,
    GeometryTypes,
)
from pyfiles.storages import get_storage
from terra_layer.models import Layer, Scene

UserModel = get_user_model()

# Use for test datas
TEST_SOURCE_FILES = [
    (
        "aerodromes_points_4326.geojson",
        "Point",
        "id",
        "Airport",
        {
            "table_enable": True,
            "table_export_enable": True,
            "popup_config": {
                "enable": True,
                "template": "# {{TOPONYME}}",
            },
            "settings": {
                "widgets": [
                    {
                        "items": [
                            {
                                "name": "nbAirport",
                                "type": "value_count",
                                "field": "_feature_id",
                                "label": "Airport count",
                                "template": "{{value | int | formatNumber }}",
                            }
                        ],
                        "component": "synthesis",
                    }
                ]
            },
        },
    ),
    ("autoroutes_lines_4326.geojson", "MultiLineString", "fid", "Highway", {}),
    ("departements_polygons_4326.geojson", "MultiPolygon", "gid", "Departement", {}),
    ("chefslieux_points_4326.geojson", "Point", "ID", "Chef lieux", {}),
    ("regions_polygon_4326.geojson", "MultiPolygon", "gid", "Region", {}),
    (
        "reseauferre_lines_4326.geojson",
        "MultiLineString",
        "fid",
        "Train line",
        {},
    ),
]


def load_data():
    print("Nothing to do here !")
    #  Load your default data here


def load_test_data():
    create_test_users()
    load_test_source_and_layer()


colors = [
    "#40d892",
    "#d86500",
    "#6e90ff",
    "#abcb00",
    "#8da2dd",
    "#a90c13",
    "#94f686",
    "#dcb927",
    "#0063E4",
]


def get_default_style(geom_type):
    current_color = colors.pop()
    if geom_type == "Point":
        return {"type": "circle", "paint": {"circle-color": current_color}}
    elif geom_type == "MultiLineString":
        return {"type": "line", "paint": {"line-color": current_color, "line-width": 2}}
    elif geom_type == "MultiPolygon":
        return {"type": "line", "paint": {"line-color": current_color, "line-width": 2}}

    return {"type": "circle", "paint": {"circle-color": current_color}}


@transaction.atomic()
def load_test_source_and_layer():
    print("Populate sources and scenes")

    pyfile_storage = get_storage(
        settings.PYFILE_BACKEND,
        settings.PYFILE_OPTIONS,
    )

    # Create test scenes
    map_scene, _ = Scene.objects.update_or_create(
        name="Map scene", defaults={"tree": []}
    )
    story_scene, _ = Scene.objects.get_or_create(
        name="Story scene", category="story", defaults={"tree": []}
    )

    loop = asyncio.get_event_loop()

    for i, source_file in enumerate(TEST_SOURCE_FILES):

        print(f"Loading source file {source_file[0]}...")
        file_name, geom_name, id_field, name, extra_layer_data = source_file
        geom_type = GeometryTypes[geom_name].value

        result = loop.run_until_complete(
            pyfile_storage.search(settings.STORAGE_NAMESPACE, file_name)
        )
        r = requests.get(result["url"])

        print("File download complete")

        # directly get content from storage, need a file object for the filefield
        f = SimpleUploadedFile(file_name, r.content)

        print("Load data into db...")
        source, created = GeoJSONSource.objects.update_or_create(
            name=name,
            defaults={
                "file": f,
                "geom_type": geom_type,
                "id_field": id_field,
            },
        )

        source.update_fields()

        layer, _ = Layer.objects.update_or_create(
            source=source,
            name=source.name,
            active_by_default=True,
            defaults={"layer_style": get_default_style(geom_name), **extra_layer_data},
        )

        for field in source.fields.all():
            if not layer.fields_filters.filter(field__name=field.name).exists():
                layer.fields_filters.create(field=field)

        # roughly split the test files between two scenes so both map & story can be tested
        if i < len(TEST_SOURCE_FILES) / 2:
            map_scene.insert_in_tree(
                layer,
                [
                    "Group",
                ],
            )
        else:
            story_scene.insert_in_tree(
                layer,
                [
                    "Group",
                ],
            )

        # data needs to be refresh to be accessible on the map
        print("Refresh data...")
        source.run_async_method("refresh_data")


def create_test_users():
    print("Populate test users...")

    users_data = [
        {
            "email": "admin@terralego.fake",
            "_groups": [],
            "_is_superuser": True,
            "password": "password",
        },
        {
            "email": "visu@terralego.fake",
            "_groups": [],
            "_is_superuser": False,
            "password": "password",
        },
    ]

    groups = {}
    for user_data in users_data:
        is_superuser = user_data.get("_is_superuser")

        # Common properties
        user_data["password"] = "visu"

        fields = {k: v for k, v in user_data.items() if not k.startswith("_")}

        try:
            UserModel.objects.get(email=user_data["email"])
            # TODO should update user
        except UserModel.DoesNotExist:
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

    print("Users ok !")
