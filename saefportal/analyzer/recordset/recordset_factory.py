from analyzer.utilities import connection_type
from saef.enums import ConnectionType


def recordset_factory(dataset):
    connection, Object = connection_type(dataset.connection.pk, True)

    if Object is None:
        return None

    if dataset.dataset_access_method == 'TABLE':
        if dataset.dataset_extraction_table != '':
            schema, table = dataset.dataset_extraction_table.split(".") 
            return Object(connection, f'SELECT * FROM {schema}."{table}"')
        return Object(connection, f'')
    else:
        if dataset.connection.connection_type.name == ConnectionType.AZURE_BLOB_STORAGE.value:
            parameters = {"connection": connection, "dataset": dataset}
            return Object(parameters, dataset.dataset_extraction_sql)
        else:
            return Object(connection, dataset.dataset_extraction_sql)
