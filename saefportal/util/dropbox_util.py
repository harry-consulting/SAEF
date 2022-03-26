import json

import dropbox
from decouple import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from dropbox.oauth import NotApprovedException

import datalakes.models as datalakes
import datastores.models as datastores
from datalakes.util import initialize_datalake
from datastores.util import initialize_connection


def build_auth_flow(request):
    redirect_uri = request.build_absolute_uri(reverse("save_dropbox_token"))

    return dropbox.oauth.DropboxOAuth2Flow(config("DROPBOX_APP_KEY"), redirect_uri, request.session,
                                           "dropbox-auth-csrf-token", config("DROPBOX_APP_SECRET"),
                                           token_access_type="offline")


def start_dropbox_authentication(request, form, object_type):
    """Initiate the authorization flow for connecting to a Dropbox account."""
    auth_flow = build_auth_flow(request)
    auth_url = auth_flow.start()

    request.session["connection_name"] = form.data.get("name", None)
    request.session["connection_type"] = form.data.get("type", None)
    request.session["owner_id"] = form.data.get("owner", None)

    request.session["root_path"] = form.data.get("root_path", "").strip().rstrip("/")
    request.session["object_type"] = object_type
    request.session["migrate"] = "migrate-checkbox" in request.POST

    return HttpResponseRedirect(auth_url)


@login_required
def save_dropbox_token(request):
    root_path = request.session.get("root_path")
    object_type = request.session.get("object_type")

    try:
        auth_flow = build_auth_flow(request)
        flow_result = auth_flow.finish(request.GET)
        token_cache = json.dumps({"refresh_token": flow_result.refresh_token})

        dbx = dropbox.Dropbox(oauth2_access_token=flow_result.access_token)
        username = dbx.users_get_current_account().email

        if object_type == "datalake":
            return create_dropbox_datalake(username, root_path, token_cache, request)
        else:
            return create_dropbox_datastore(username, root_path, token_cache, request)
    except NotApprovedException:
        messages.error(request, "Access was not approved to the Dropbox account.")

        url = reverse("datasets:index") if object_type == "datastore" else reverse("settings:settings", args=[1])
        return HttpResponseRedirect(url)


def create_dropbox_datalake(username, root_path, cache, request):
    datalake = datalakes.DropboxDatalake.objects.create(username=username, root_path=root_path, token_cache=cache)
    return initialize_datalake(datalake, request, request.session.get("migrate"))


def create_dropbox_datastore(username, root_path, cache, request):
    connection_name = request.session.get("connection_name")
    connection_type = request.session.get("connection_type")
    owner_id = request.session.get("owner_id")

    datastore = datastores.DropboxDatastore.objects.create(username=username, root_path=root_path, token_cache=cache)

    return initialize_connection(datastore, connection_name, owner_id, connection_type, request)


def get_service_from_cache(token_cache):
    return dropbox.Dropbox(oauth2_refresh_token=token_cache["refresh_token"], user_agent="SAEF/1.0",
                           app_key=config("DROPBOX_APP_KEY"), app_secret=config("DROPBOX_APP_SECRET"))
