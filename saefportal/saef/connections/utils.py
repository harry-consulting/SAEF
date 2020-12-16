

from saef.models import Connection


def create_connection(connection_form, form):
    name = connection_form['connection_name']
    connection_type = form['connection_type']
    time_out = connection_form['time_out']

    return Connection(
        name=name,
        connection_type=connection_type,
        time_out=time_out
    )


def test_connection(connection_form, form, database_method, Datastore):
    try:
        _, connection = database_method(connection_form, form)

        datastore = Datastore(connection)
        return datastore.execute_query('SELECT 1')
    except Exception:
        return False


def save_connection(postgres_form, form, database_method):
    connection, database_connection = database_method(postgres_form, form)
    connection.save()
    database_connection.save()


def save_edit_connection_form(form, connection_id):
    connection_instance = Connection.objects.get(pk=connection_id)
    connection_instance.name = form.cleaned_data["connection_name"]
    connection_instance.time_out = form.cleaned_data["time_out"]
    connection_instance.save()


def edit_connection(EditDatabaseConnectionForm, edit_method, DatabaseConnection, post_request=None, connection_pk=None):
    if connection_pk:
        database_connection = DatabaseConnection.objects.get(
            connection__id=connection_pk)
        return edit_method(database_connection)
    if post_request:
        return EditDatabaseConnectionForm(post_request)
    return None
