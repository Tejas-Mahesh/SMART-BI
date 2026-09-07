from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DatasetUploadForm
from .models import Dataset
from .quality import analyze_data_quality
from .services import analyze_uploaded_file


# =========================================================
# UPLOAD DATA
# =========================================================

def upload_data(request):

    if request.method == "POST":

        form = DatasetUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            uploaded_file = request.FILES["file"]

            try:

                analysis = analyze_uploaded_file(
                    uploaded_file
                )

                dataset = form.save(commit=False)

                dataset.file_size = uploaded_file.size

                dataset.row_count = (
                    analysis["statistics"]["rows"]
                )

                dataset.column_count = (
                    analysis["statistics"]["columns"]
                )

                dataset.save()

                request.session[
                    "last_uploaded_dataset_id"
                ] = dataset.id

                messages.success(
                    request,
                    f"Dataset '{dataset.name}' uploaded successfully."
                )

                return redirect(
                    "data_preview",
                    dataset_id=dataset.id
                )

            except Exception as error:

                messages.error(
                    request,
                    f"The file could not be processed: {error}"
                )

    else:

        form = DatasetUploadForm()

    return render(
        request,
        "data_manager/upload.html",
        {
            "form": form
        }
    )


# =========================================================
# DATA PREVIEW
# =========================================================

def data_preview(
    request,
    dataset_id
):

    dataset = get_object_or_404(
        Dataset,
        id=dataset_id
    )

    try:

        with dataset.file.open("rb") as uploaded_file:

            analysis = analyze_uploaded_file(
                uploaded_file
            )

        context = {
            "dataset": dataset,
            "statistics": analysis["statistics"],
            "columns": analysis["columns"],
            "column_types": analysis["column_types"],
            "preview": analysis["preview"],
        }

        return render(
            request,
            "data_manager/preview.html",
            context
        )

    except Exception as error:

        messages.error(
            request,
            f"Unable to generate preview: {error}"
        )

        return redirect(
            "upload_data"
        )


# =========================================================
# DATA QUALITY
# =========================================================

def data_quality(
    request,
    dataset_id
):

    dataset = get_object_or_404(
        Dataset,
        id=dataset_id
    )

    try:

        with dataset.file.open(
            "rb"
        ) as uploaded_file:

            analysis = analyze_data_quality(
                uploaded_file
            )

        context = {
            "dataset": dataset,
            "summary": analysis["summary"],
            "quality_score": analysis["quality_score"],
            "quality_level": analysis["quality_level"],
            "missing_analysis": analysis["missing_analysis"],
            "duplicate_analysis": analysis["duplicate_analysis"],
            "unique_analysis": analysis["unique_analysis"],
            "type_analysis": analysis["type_analysis"],
            "invalid_analysis": analysis["invalid_analysis"],
            "outlier_analysis": analysis["outlier_analysis"],
            "column_name_analysis": analysis["column_name_analysis"],
            "issues": analysis["issues"],
            "recommendations": analysis["recommendations"],
        }

        return render(
            request,
            "data_manager/quality.html",
            context
        )

    except Exception as error:

        messages.error(
            request,
            f"Unable to analyze data quality: {error}"
        )

        return redirect(
            "data_preview",
            dataset_id=dataset.id
        )


# =========================================================
# MANAGE DATA
# =========================================================

def manage_data(request):

    datasets = Dataset.objects.all()

    search = request.GET.get(
        "search",
        ""
    ).strip()

    dataset_type = request.GET.get(
        "type",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        datasets = datasets.filter(
            name__icontains=search
        )

    # -----------------------------------------------------
    # DATASET TYPE
    # -----------------------------------------------------

    if dataset_type:

        datasets = datasets.filter(
            dataset_type=dataset_type
        )

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    if status == "active":

        datasets = datasets.filter(
            is_active=True
        )

    elif status == "inactive":

        datasets = datasets.filter(
            is_active=False
        )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    all_datasets = Dataset.objects.all()

    summary = {
        "total": all_datasets.count(),

        "active": all_datasets.filter(
            is_active=True
        ).count(),

        "inactive": all_datasets.filter(
            is_active=False
        ).count(),

        "total_rows": sum(
            dataset.row_count
            for dataset in all_datasets
        ),
    }

    context = {
        "datasets": datasets,
        "summary": summary,
        "search": search,
        "dataset_type": dataset_type,
        "status": status,
        "dataset_types": Dataset.DATASET_TYPES,
    }

    return render(
        request,
        "data_manager/manage.html",
        context
    )


# =========================================================
# ACTIVATE DATASET
# =========================================================

def activate_dataset(
    request,
    dataset_id
):

    if request.method != "POST":

        return redirect(
            "manage_data"
        )

    dataset = get_object_or_404(
        Dataset,
        id=dataset_id
    )

    dataset.is_active = True

    dataset.save(
        update_fields=[
            "is_active",
            "updated_at"
        ]
    )

    messages.success(
        request,
        f"'{dataset.name}' is now active."
    )

    return redirect(
        "manage_data"
    )


# =========================================================
# DEACTIVATE DATASET
# =========================================================

def deactivate_dataset(
    request,
    dataset_id
):

    if request.method != "POST":

        return redirect(
            "manage_data"
        )

    dataset = get_object_or_404(
        Dataset,
        id=dataset_id
    )

    dataset.is_active = False

    dataset.save(
        update_fields=[
            "is_active",
            "updated_at"
        ]
    )

    messages.warning(
        request,
        f"'{dataset.name}' has been deactivated."
    )

    return redirect(
        "manage_data"
    )


# =========================================================
# DOWNLOAD DATASET
# =========================================================

def download_dataset(
    request,
    dataset_id
):

    dataset = get_object_or_404(
        Dataset,
        id=dataset_id
    )

    if not dataset.file:

        messages.error(
            request,
            "The dataset file is unavailable."
        )

        return redirect(
            "manage_data"
        )

    response = FileResponse(
        dataset.file.open("rb"),
        as_attachment=True,
        filename=dataset.file.name.split("/")[-1]
    )

    return response


# =========================================================
# DATASET DETAILS
# =========================================================

def dataset_details(
    request,
    dataset_id
):

    dataset = get_object_or_404(
        Dataset,
        id=dataset_id
    )

    try:

        with dataset.file.open(
            "rb"
        ) as uploaded_file:

            analysis = analyze_uploaded_file(
                uploaded_file
            )

        context = {
            "dataset": dataset,
            "statistics": analysis["statistics"],
            "columns": analysis["columns"],
            "column_types": analysis["column_types"],
            "preview": analysis["preview"],
        }

        return render(
            request,
            "data_manager/details.html",
            context
        )

    except Exception as error:

        messages.error(
            request,
            f"Unable to read dataset: {error}"
        )

        return redirect(
            "manage_data"
        )


# =========================================================
# DELETE DATASET
# =========================================================

def delete_dataset(
    request,
    dataset_id
):

    if request.method != "POST":

        return redirect(
            "manage_data"
        )

    dataset = get_object_or_404(
        Dataset,
        id=dataset_id
    )

    dataset_name = dataset.name

    # Delete database record + uploaded file
    dataset.delete()

    messages.success(
        request,
        f"Dataset '{dataset_name}' was deleted successfully."
    )

    return redirect(
        "manage_data"
    )