from django.contrib import messages
from django.shortcuts import redirect, render

from data_manager.models import Dataset
from data_manager.services import load_uploaded_file

from .services import analyze_customer_intelligence


def customer_intelligence(request):

    dataset = (
        Dataset.objects
        .filter(is_active=True)
        .order_by("-uploaded_at")
        .first()
    )

    if not dataset:

        messages.warning(
            request,
            "Please upload a dataset before opening Customer Intelligence."
        )

        return redirect("upload_data")

    try:

        with dataset.file.open("rb") as uploaded_file:

            df = load_uploaded_file(
                uploaded_file
            )

        analysis = analyze_customer_intelligence(
            df
        )

        context = {
            "dataset": dataset,

            "metrics": analysis["metrics"],

            "segment_summary": (
                analysis["segment_summary"]
            ),

            "rfm_distribution": (
                analysis["rfm_distribution"]
            ),

            "top_customers": (
                analysis["top_customers"]
            ),

            "at_risk_customers": (
                analysis["at_risk_customers"]
            ),

            "insights": analysis["insights"],

            "columns": analysis["columns"],
        }

        return render(
            request,
            "customers/customer_intelligence.html",
            context,
        )

    except Exception as error:

        messages.error(
            request,
            (
                "Unable to analyze customer data: "
                f"{error}"
            ),
        )

        return redirect("upload_data")