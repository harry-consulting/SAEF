from django.apps import AppConfig


class DatalakesConfig(AppConfig):
    name = 'datalakes'

    def ready(self):
        import datalakes.signals
