from analyzer.utilities import connection_type


def datastore_factory(connection_pk):
    connection, Object = connection_type(connection_pk, False)

    if Object is None:
        return None

    return Object(connection)
