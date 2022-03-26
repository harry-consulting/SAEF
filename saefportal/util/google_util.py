import ast
import io
import json

from decouple import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.cloud import storage

import datalakes.models as datalakes
import datastores.models as datastores
from datalakes.util import initialize_datalake
from datastores.util import initialize_connection


def build_auth_flow(redirect_uri, connection_type):
    client = {
        "web": {
            "client_id": config("GOOGLE_CLIENT_ID"),
            "client_secret": config("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    if connection_type == "GOOGLE_DRIVE":
        scopes = ["https://www.googleapis.com/auth/drive"]
    else:
        scopes = ["https://www.googleapis.com/auth/devstorage.read_write"]

    auth_flow = InstalledAppFlow.from_client_config(client, scopes)
    auth_flow.redirect_uri = redirect_uri

    return auth_flow


def start_google_authentication(request, form, object_type):
    """Initiate the authorization flow for connecting to a Google account."""
    redirect_uri = request.build_absolute_uri(reverse("save_google_token"))
    auth_flow = build_auth_flow(redirect_uri, form.data["type"])
    auth_url, _ = auth_flow.authorization_url(access_type="offline", approval_prompt="force")

    request.session["connection_name"] = form.data.get("name", None)
    request.session["connection_type"] = form.data.get("type", None)
    request.session["owner_id"] = form.data.get("owner", None)

    request.session["root_path"] = form.data.get("root_path", "").strip().rstrip("/")
    request.session["project_id"] = form.data.get("project_id", None)
    request.session["bucket_name"] = form.data.get("bucket_name", None)

    request.session["object_type"] = object_type
    request.session["migrate"] = "migrate-checkbox" in request.POST

    return HttpResponseRedirect(auth_url)


@login_required
def save_google_token(request):
    """This view is redirected to after the Google authorization process."""
    connection_type = request.session.get("connection_type")
    object_type = request.session.get("object_type")

    try:
        redirect_uri = request.build_absolute_uri(reverse("save_google_token"))
        auth_flow = build_auth_flow(redirect_uri, connection_type)
        auth_flow.fetch_token(code=request.GET.get("code"))

        token_cache = json.dumps(auth_flow.credentials.to_json())

        return create_google_object(connection_type, object_type, token_cache, request)
    except ValueError:
        messages.error(request, "Access was not approved to the Google account.")

        url = reverse("datasets:index") if object_type == "datastore" else reverse("settings:settings", args=[1])
        return HttpResponseRedirect(url)


def create_google_object(connection_type, object_type, cache, request):
    root_path = request.session.get("root_path")
    project_id = request.session.get("project_id")
    bucket_name = request.session.get("bucket_name")

    connection_name = request.session.get("connection_name")
    owner_id = request.session.get("owner_id")

    if object_type == "datalake":
        if connection_type == "GOOGLE_DRIVE":
            datalake = datalakes.GoogleDriveDatalake.objects.create(root_path=root_path, token_cache=cache)
        else:
            datalake = datalakes.GoogleCloudStorageDatalake.objects.create(project_id=project_id, token_cache=cache,
                                                                           bucket_name=bucket_name)

        return initialize_datalake(datalake, request, request.session.get("migrate"))
    else:
        if connection_type == "GOOGLE_DRIVE":
            datastore = datastores.GoogleDriveDatastore.objects.create(root_path=root_path, token_cache=cache)
        else:
            datastore = datastores.GoogleCloudStorageDatastore.objects.create(project_id=project_id, token_cache=cache,
                                                                              bucket_name=bucket_name)

        return initialize_connection(datastore, connection_name, owner_id, connection_type, request)


def get_service_from_cache(google_object, service):
    """
    Use the cached token to get the service that can be used to interact with either the Google Drive API
    or the Google Cloud Storage API.
    """
    if service == "drive":
        scopes = ["https://www.googleapis.com/auth/drive"]
    else:
        scopes = ["https://www.googleapis.com/auth/devstorage.read_write"]

    user_info = ast.literal_eval(json.loads(google_object.token_cache))
    credentials = Credentials.from_authorized_user_info(user_info, scopes)

    # Refresh the access token if it is expired.
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        google_object.token_cache = json.dumps(credentials.to_json())
        google_object.save()

    if service == "drive":
        return build("drive", "v3", credentials=credentials)
    else:
        return storage.Client(google_object.project_id, credentials=credentials)


def get_root_folder_id(service, root_path):
    """
    Given the complete path to the intended root folder, iteratively move up the path until the unique root path is
    found. This method is required since Google Drive does not allow for searching for a full path, only folder names.
    """
    root_path_folders = root_path.rstrip("/").split("/")

    # Get all folders with the root folder name. Each found folder could be the intended root folder.
    query = f"name = '{root_path_folders[-1]}'"
    response = service.files().list(q=query, spaces="drive", fields="files(id, name, parents)").execute()
    viable_root_folders = {file["id"]: [file["parents"][0]] for file in response.get("files")}

    # Since there can be duplicates, we move up the given root path using the parents until we find the unique path.
    for folder in root_path_folders[::-1][1:]:
        if len(viable_root_folders) == 1:
            break

        for viable_root_folder_id in list(viable_root_folders):
            file_id = viable_root_folders[viable_root_folder_id][-1]
            response = service.files().get(fileId=file_id, fields="name, parents").execute()

            if response.get("name") == folder:
                viable_root_folders[viable_root_folder_id].append(response.get("parents")[0])
            else:
                # If the parent does not match the root path, we remove the root folder id from the viable options.
                del viable_root_folders[viable_root_folder_id]

    return list(viable_root_folders)[0]


def download_data(service, file_id):
    """Download data from Google Drive to an in-memory bytes buffer."""
    request = service.files().get_media(fileId=file_id)
    data = io.BytesIO()
    downloader = MediaIoBaseDownload(data, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()

    return data
