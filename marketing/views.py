from django.contrib import messages
from django.shortcuts import redirect, render

from data_manager.models import Dataset
from data_manager.services import load_uploaded_file

from .services import analyze_marketing_intelligence


def marketing_analysis(request):
    dataset = (
        Dataset.objects
        .filter(is_active=True)
        .order_by("-uploaded_at")
        .first()
    )

    if not dataset:
        messages.warning(
            request,
            "Please upload a dataset before opening Marketing Analysis.",
        )
        return redirect("upload_data")

    try:
        with dataset.file.open("rb") as uploaded_file:
            df = load_uploaded_file(uploaded_file)

        analysis = analyze_marketing_intelligence(df)

        context = {
            "dataset": dataset,

            "metrics": analysis["metrics"],

            "channel_data": analysis["channel_data"],

            "campaign_data": analysis["campaign_data"],

            "trend_data": analysis["trend_data"],

            "top_revenue_channels":
                analysis["top_revenue_channels"],

            "top_roas_channels":
                analysis["top_roas_channels"],

            "top_revenue_campaigns":
                analysis["top_revenue_campaigns"],

            "top_roi_campaigns":
                analysis["top_roi_campaigns"],

            "insights":
                analysis["insights"],

            "columns":
                analysis["columns"],
        }

        return render(
            request,
            "marketing/marketing_analysis.html",
            context,
        )

    except Exception as error:

        messages.error(
            request,
            f"Unable to analyze marketing data: {error}",
        )

        return redirect("upload_data")