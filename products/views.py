from django.contrib import messages
from django.shortcuts import redirect, render

from data_manager.models import Dataset
from data_manager.services import load_uploaded_file

from .services import analyze_product_intelligence


def product_intelligence(request):

    dataset = (
        Dataset.objects
        .filter(is_active=True)
        .order_by("-uploaded_at")
        .first()
    )

    if not dataset:

        messages.warning(
            request,
            "Please upload a dataset before opening Product Intelligence.",
        )

        return redirect("upload_data")

    try:

        with dataset.file.open("rb") as uploaded_file:

            df = load_uploaded_file(
                uploaded_file
            )

        analysis = analyze_product_intelligence(
            df
        )

        context = {

            "dataset": dataset,

            "metrics":
                analysis["metrics"],

            "category_data":
                analysis["category_data"],

            "growth_data":
                analysis["growth_data"],

            "return_data":
                analysis["return_data"],

            "profitability_matrix":
                analysis["profitability_matrix"],

            "top_revenue_products":
                analysis["top_revenue_products"],

            "top_profit_products":
                analysis["top_profit_products"],

            "top_units_products":
                analysis["top_units_products"],

            "product_table":
                analysis["product_table"]
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
            "products/product_intelligence.html",
            context,
        )

    except Exception as error:

        messages.error(
            request,
            (
                "Unable to analyze product data: "
                f"{error}"
            ),
        )

        return redirect("upload_data")