from django.contrib import messages
from django.shortcuts import redirect, render

from data_manager.models import Dataset
from data_manager.services import load_uploaded_file

from .services import analyze_regional_intelligence


def regional_analysis(request):

    dataset = (
        Dataset.objects
        .filter(is_active=True)
        .order_by("-uploaded_at")
        .first()
    )

    if not dataset:

        messages.warning(
            request,
            "Please upload a dataset before opening Regional Analysis.",
        )

        return redirect("upload_data")

    try:

        with dataset.file.open("rb") as uploaded_file:

            df = load_uploaded_file(
                uploaded_file
            )

        analysis = analyze_regional_intelligence(
            df
        )

        context = {

            "dataset":
                dataset,

            "metrics":
                analysis["metrics"],

            "revenue_share":
                analysis["revenue_share"],

            "growth_data":
                analysis["growth_data"],

            "ranking":
                analysis["ranking"],

            "matrix":
                analysis["matrix"],

            "performance_scores":
                analysis["performance_scores"],

            "top_revenue_regions":
                analysis["top_revenue_regions"],

            "top_profit_regions":
                analysis["top_profit_regions"],

            "regional_table":
                analysis["regional_table"]
                .head(100)
                .to_dict(
                    orient="records"
                ),

            "insights":
                analysis["insights"],

            "columns":
                analysis["columns"],

        }

        return render(
            request,
            "regional/regional_analysis.html",
            context,
        )

    except Exception as error:

        messages.error(
            request,
            (
                "Unable to analyze regional data: "
                f"{error}"
            ),
        )

        return redirect("upload_data")