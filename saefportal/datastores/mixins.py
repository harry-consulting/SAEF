from django.contrib.contenttypes.models import ContentType

from datasets.models import Connection


class GetConnectionMixin(object):
    @property
    def get_connection(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        try:
            connection = Connection.objects.get(datastore_type__pk=content_type.id, datastore_id=self.id)
        except Connection.DoesNotExist:
            return None

        return connection
