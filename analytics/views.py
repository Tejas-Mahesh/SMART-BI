from django.contrib import messages
from django.shortcuts import redirect, render

from data_manager.models import Dataset
from data_manager.services import load_uploaded_file

from .services import analyze_business_overview


def business_overview(request):

    # =====================================================
    # FIND ACTIVE DATASET
    # =====================================================

    dataset = (
        Dataset.objects
        .filter(is_active=True)
        .order_by("-uploaded_at")
        .first()
    )

    if not dataset:

        messages.warning(
            request,
            (
                "No active dataset is available. "
                "Please upload and activate a dataset first."
            )
        )

        return redirect(
            "manage_data"
        )

    # =====================================================
    # LOAD DATA
    # =====================================================

    try:

        with dataset.file.open(
            "rb"
        ) as uploaded_file:

            df = load_uploaded_file(
                uploaded_file
            )

        # =================================================
        # DATE FILTER
        # =================================================

        start_date = request.GET.get(
            "start_date"
        )

        end_date = request.GET.get(
            "end_date"
        )

        analysis = analyze_business_overview(
            df,
            start_date=start_date,
            end_date=end_date
        )

        context = {

            "dataset": dataset,

            "metrics": analysis[
                "metrics"
            ],

            "daily_trend": analysis[
                "daily_trend"
            ],

            "regions": analysis[
                "regions"
            ],

            "products": analysis[
                "products"
            ],

            "status_analysis": analysis[
                "status_analysis"
            ],

            "insights": analysis[
                "insights"
            ],

            "columns": analysis[
                "columns"
            ],

            "date_range": analysis[
                "date_range"
            ],

            "start_date": start_date or "",

            "end_date": end_date or "",

        }

        return render(
            request,
            "analytics/business_overview.html",
            context
        )

    except Exception as error:

        messages.error(
            request,
            (
                "Unable to analyze the business dataset: "
                f"{error}"
            )
        )

        return redirect(
            "manage_data"
        )