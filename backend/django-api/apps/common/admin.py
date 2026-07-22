from django.contrib import admin
from .models import AdapterMetadata

@admin.register(AdapterMetadata)
class AdapterMetadataAdmin(admin.ModelAdmin):
    list_display = ('source_type', 'source_uri', 'created_at', 'updated_at')
    search_fields = ('source_uri', 'source_type')
    list_filter = ('source_type', 'created_at')
