from django.contrib import admin
from .models import Dataset


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "dataset_type",
        "row_count",
        "column_count",
        "file_size",
        "is_active",
        "uploaded_at",
    )

    list_filter = (
        "dataset_type",
        "is_active",
        "uploaded_at",
    )

    search_fields = (
        "name",
    )

    readonly_fields = (
        "file_size",
        "row_count",
        "column_count",
        "uploaded_at",
        "updated_at",
    )