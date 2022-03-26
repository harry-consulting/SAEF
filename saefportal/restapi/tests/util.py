from model_bakery import baker


def create_test_data(owner):
    """Create multiple objects of each model type. The given user is the owner of half of the ownable objects."""
    # Setting up an empty local datalake.
    datalake = baker.make("datalakes.LocalDatalake", root_path="test_datalake")
    baker.make("settings.Settings", try_live_connection=False, datalake=datalake)

    user = baker.make("users.user", email="test2@test.com")

    baker.make("users.Organization", name="organization 1")

    baker.make("users.OrganizationGroup", name="All")
    baker.make("users.OrganizationGroup", name="Admin")

    datastore_1 = baker.make("datastores.PostgresDatastore", database_name="postgres 1", password="test")
    datastore_2 = baker.make("datastores.postgresDatastore", database_name="postgres 2", password="test")
    datastore_3 = baker.make("datastores.AzureDatastore", database_name="azure 1", password="test")
    datastore_4 = baker.make("datastores.AzureDatastore", database_name="azure 2", password="test")

    baker.make("datasets.Connection", name="connection 1", owner=owner, type="POSTGRES", datastore=datastore_1)
    baker.make("datasets.Connection", name="connection 2", owner=user, type="POSTGRES", datastore=datastore_2)
    baker.make("datasets.Connection", name="connection 3", owner=owner, type="AZURE", datastore=datastore_3)
    baker.make("datasets.Connection", name="connection 4", owner=user, type="AZURE", datastore=datastore_4)

    dataset_1 = baker.make("datasets.Dataset", name="dataset 1", owner=owner)
    dataset_2 = baker.make("datasets.Dataset", name="dataset 2", owner=user)

    baker.make("datasets.DatasetRun", dataset=dataset_1, execution_id="938c276c-b2ab-4410-9142-af7d1054bfc2")
    baker.make("datasets.DatasetRun", dataset=dataset_2, execution_id="71672ac1-7038-4ed9-a8b6-81794a8d239f")

    baker.make("datasets.Note", dataset=dataset_1, created_by=user, text="note 1")
    baker.make("datasets.Note", dataset=dataset_2, created_by=user, text="note 2")

    job_1 = baker.make("jobs.Job", name="job 1", owner=owner)
    job_2 = baker.make("jobs.Job", name="job 2", owner=user)

    baker.make("jobs.JobRun", job=job_1, execution_id="65cf3c6c-dabd-4256-b068-d717de40375d")
    baker.make("jobs.JobRun", job=job_2, execution_id="99dd1a79-e4f0-4311-8d79-44b5ce5402e5")

    baker.make("settings.Contact", name="contact 1")
    baker.make("settings.Contact", name="contact 2")
