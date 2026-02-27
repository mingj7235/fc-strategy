from django.apps import AppConfig


class NexonApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nexon_api'

    def ready(self):
        from nexon_api.metadata import MetadataLoader
        try:
            MetadataLoader.load_metadata('spid')
            MetadataLoader.load_metadata('seasonid')
        except Exception:
            pass
