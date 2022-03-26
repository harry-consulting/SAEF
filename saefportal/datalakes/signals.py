import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from datalakes.util import save_dataset_to_datalake
from datasets.models import Connection, Dataset
from settings.models import Settings

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Connection)
def create_connection_folder(instance, created, **kwargs):
    if created:
        datalake = Settings.objects.get().datalake
        datalake.create_folder("saef/landing", instance.name)


@receiver(post_delete, sender=Connection)
def delete_connection_folder(instance, **kwargs):
    datalake = Settings.objects.get().datalake

    try:
        datalake.delete_path(f"saef/landing/{instance.name}/")
    except Exception:
        logger.error(f"The folder 'saef/landing/{instance.name}/' could not be deleted.")


@receiver(post_save, sender=Dataset)
def upload_to_datalake(instance, created, **kwargs):
    """
    Save the first instance of the data, preview and schema to the datalake. Note that if the created dataset is
    uploaded from the users local environment, we only create the folders since the data is uploaded separately.
    """
    if created:
        datalake = Settings.objects.get().datalake
        datalake_path = instance.get_datalake_path()
        [path, folder_name] = datalake_path.rsplit('/', 1)

        datalake.create_folder(path, folder_name)
        datalake.create_folder(datalake_path, "data")
        datalake.create_folder(datalake_path, "meta")

        # If the instance does not have a connection, it is a manual upload.
        if instance.connection:
            save_dataset_to_datalake(instance)


@receiver(post_delete, sender=Dataset)
def delete_from_datalake(instance, **kwargs):
    """Delete the folder representing the deleted dataset in the datalake."""
    datalake = Settings.objects.get().datalake
    path = instance.get_datalake_path()

    try:
        # If the path is None the datasets' connection was deleted which means the dataset subfolder was also deleted.
        if path is not None:
            datalake.delete_path(f"{path}/")
    except Exception:
        logger.error(f"The folder '{path}/' could not be deleted.")
