import msal
from decouple import config
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

import datalakes.models as datalakes
import datastores.models as datastores
from datalakes.util import initialize_datalake
from datastores.util import initialize_connection


def build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(config("ONE_DRIVE_CLIENT_ID"),
                                              authority="https://login.microsoftonline.com/consumers",
                                              client_credential=config("ONE_DRIVE_CLIENT_SECRET"),
                                              token_cache=cache)


def start_one_drive_authentication(request, form, object_type):
    """Initiate the authorization flow for connecting to a OneDrive account."""
    msal_app = build_msal_app()

    redirect_uri = request.build_absolute_uri(reverse("save_one_drive_token"))
    auth_flow = msal_app.initiate_auth_code_flow(["Files.ReadWrite"], redirect_uri=redirect_uri)

    request.session["connection_name"] = form.data.get("name", None)
    request.session["connection_type"] = form.data.get("type", None)
    request.session["owner_id"] = form.data.get("owner", None)

    request.session["auth_flow"] = auth_flow
    request.session["root_path"] = form.data.get("root_path", "").strip().rstrip("/")
    request.session["object_type"] = object_type
    request.session["migrate"] = "migrate-checkbox" in request.POST

    return HttpResponseRedirect(auth_flow["auth_uri"])


@login_required
def save_one_drive_token(request):
    """This view is redirected to after the OneDrive authorization process."""
    root_path = request.session.get("root_path")

    cache = msal.SerializableTokenCache()
    msal_app = build_msal_app(cache=cache)

    result = msal_app.acquire_token_by_auth_code_flow(request.session["auth_flow"], request.GET)
    username = result["id_token_claims"]["preferred_username"]

    if request.session["object_type"] == "datalake":
        return create_one_drive_datalake(username, root_path, cache, request)
    else:
        return create_one_drive_datastore(username, root_path, cache, request)


def create_one_drive_datalake(username, root_path, cache, request):
    datalake = datalakes.OneDriveDatalake.objects.create(username=username, root_path=root_path,
                                                         token_cache=cache.serialize())
    return initialize_datalake(datalake, request, request.session.get("migrate"))


def create_one_drive_datastore(username, root_path, cache, request):
    connection_name = request.session.get("connection_name")
    connection_type = request.session.get("connection_type")
    owner_id = request.session.get("owner_id")

    datastore = datastores.OneDriveDatastore.objects.create(username=username, root_path=root_path,
                                                            token_cache=cache.serialize())

    return initialize_connection(datastore, connection_name, owner_id, connection_type, request)


def get_token_from_cache(one_drive_object):
    # Load the cache from persistent storage.
    cache = msal.SerializableTokenCache()
    cache.deserialize(one_drive_object.token_cache)

    msal_app = build_msal_app(cache=cache)

    # Acquire the token without user interaction by using the cached token (and refresh token if necessary).
    accounts = msal_app.get_accounts()
    token = msal_app.acquire_token_silent(scopes=["Files.ReadWrite"], account=accounts[0])

    # Update the cache since a new token could have been retrieved if the previous was expired.
    if cache.has_state_changed:
        one_drive_object.token_cache = cache.serialize()
        one_drive_object.save()

    return token
