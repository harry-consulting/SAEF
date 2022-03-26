class SaveWithoutHistoricalRecordMixin:
    """Mixin to avoid creating a "django-simply-history" historical record every time an object is saved."""
    def save_without_historical_record(self, *args, **kwargs):
        self.skip_history_when_saving = True
        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret
