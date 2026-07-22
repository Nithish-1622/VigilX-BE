import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class AdapterMetadata(BaseModel):
    source_uri = models.CharField(max_length=2048, unique=True, help_text="URI of the data source")
    source_type = models.CharField(max_length=100, help_text="e.g. pdf, postgres, mysql")
    metadata_payload = models.JSONField(default=dict, blank=True, help_text="Metadata extracted by the adapter")
    profile_payload = models.JSONField(default=dict, blank=True, help_text="Data profiling information")

    class Meta:
        db_table = 'adapter_metadata'
        verbose_name_plural = 'Adapter Metadata'

    def __str__(self):
        return f"{self.source_type} - {self.source_uri}"
