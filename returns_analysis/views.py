
from django.contrib import messages
from django.shortcuts import redirect, render

from data_manager.models import Dataset
from data_manager.services import load_uploaded_file

from .services import analyze_returns


def returns_analysis(request):

    # ========================================================
    # GET ACTIVE DATASET
    # ========================================================

    dataset = (
        Dataset.objects
        .filter(is_active=True)
        .order_by("-uploaded_at")
        .first()
    )

    # ========================================================
    # NO DATASET
    # ========================================================

    if not dataset:

        messages.warning(
            request,
            "Please upload a dataset before opening Returns Analysis.",
        )

        return redirect("upload_data")

    # ========================================================
    # ANALYZE DATASET
    # ========================================================

    try:

        with dataset.file.open("rb") as uploaded_file:

            df = load_uploaded_file(
                uploaded_file
            )

        analysis = analyze_returns(
            df
        )

        # ====================================================
        # CONTEXT
        # ====================================================

        context = {

            "dataset": dataset,

            # Main KPI metrics
            "metrics": analysis[
                "metrics"
            ],

            # Monthly return trend
            "trend_data": analysis[
                "trend_data"
            ],

            # Product analysis
            "product_returns": analysis[
                "product_returns"
            ],

            "high_return_products": analysis[
                "high_return_products"
            ],

            "risk_products": analysis[
                "risk_products"
            ],

            # Regional analysis
            "region_returns": analysis[
                "region_returns"
            ],

            # Return reasons
            "reason_data": analysis[
                "reason_data"
            ],

            # Customer analysis
            "customer_returns": analysis[
                "customer_returns"
            ],

            # Category analysis
            "category_returns": analysis[
                "category_returns"
            ],

            # Automatic insights
            "insights": analysis[
                "insights"
            ],

            # Detected dataset columns
            "columns": analysis[
                "columns"
            ],
        }

        # ====================================================
        # RENDER
        # ====================================================

        return render(
            request,
            "returns_analysis/returns_analysis.html",
            context,
        )

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as error:

        messages.error(
            request,
            f"Unable to analyze returns data: {error}",
        )

        return redirect(
            "upload_data"
        )
