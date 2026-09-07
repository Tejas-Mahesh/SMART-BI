from django.urls import path

from . import views


urlpatterns = [

    # Upload
    path(
        "upload/",
        views.upload_data,
        name="upload_data",
    ),

    # Preview
    path(
        "preview/<int:dataset_id>/",
        views.data_preview,
        name="data_preview",
    ),

    # Quality
    path(
        "quality/<int:dataset_id>/",
        views.data_quality,
        name="data_quality",
    ),

    # Manage
    path(
        "manage/",
        views.manage_data,
        name="manage_data",
    ),

    # Dataset details
    path(
        "details/<int:dataset_id>/",
        views.dataset_details,
        name="dataset_details",
    ),

    # Download
    path(
        "download/<int:dataset_id>/",
        views.download_dataset,
        name="download_dataset",
    ),

    # Activate
    path(
        "activate/<int:dataset_id>/",
        views.activate_dataset,
        name="activate_dataset",
    ),

    # Deactivate
    path(
        "deactivate/<int:dataset_id>/",
        views.deactivate_dataset,
        name="deactivate_dataset",
    ),

    # Delete
    path(
        "delete/<int:dataset_id>/",
        views.delete_dataset,
        name="delete_dataset",
    ),

]