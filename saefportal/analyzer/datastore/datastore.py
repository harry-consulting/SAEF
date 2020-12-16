class Datastore:
    def __init__(self):
        pass

    def execute_query(self, query):
        raise NotImplementedError()

    def fetch_one(self, query, get_column_names=False):
        raise NotImplementedError()

    def fetch_all(self, query, get_column_names=False, timeout=None):
        raise NotImplementedError()
