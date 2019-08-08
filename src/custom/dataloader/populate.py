import os
from copy import deepcopy

from django.conf import settings
from django.contrib.auth.models import Group
from django_geosource.models import Field, PostGISSource, Source
from terra_layer.models import CustomStyle, FilterField, Layer, LayerGroup
from terracommon.accounts.models import TerraUser


def load_data():
    pass
    #  Load your default data here


def load_test_data():
    create_test_users()


def create_test_users():
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
            user = TerraUser.objects.create_superuser(**fields)
        else:
            user = TerraUser.objects.create_user(**fields)

        user_groups = user_data.get("_groups")
        if user_groups:
            for groupname in user_groups:
                if not groups.get(groupname):
                    groups[groupname], _ = Group.objects.get_or_create(name=groupname)
                user.groups.add(groups[groupname])
