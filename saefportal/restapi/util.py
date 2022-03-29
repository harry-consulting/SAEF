def get_access_dependant_object(model_name, obj):
    """If the given object depends on another object for access, return the object that it depends on."""
    if model_name in ["PostgresDatastore", "AzureDatastore", "OneDriveDatastore", "GoogleDriveDatastore",
                      "DropboxDatastore", "GoogleCloudStorageDatastore", "AzureBlobStorageDatastore",
                      "AzureDataLakeDatastore", "AmazonS3Datastore"]:
        obj = obj.get_connection
    elif model_name == "Note" or model_name == "DatasetRun":
        obj = obj.dataset
    elif model_name == "JobRun":
        obj = obj.job

    return obj
