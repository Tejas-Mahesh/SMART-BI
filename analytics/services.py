import pandas as pd
import numpy as np


# =========================================================
# BASIC HELPERS
# =========================================================

def find_column(df, possible_names):
    """
    Find a column using common business-data names.
    """

    normalized_columns = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:

        key = name.strip().lower()

        if key in normalized_columns:
            return normalized_columns[key]

    return None


def find_columns(df, possible_groups):
    """
    Find multiple possible columns.
    """

    results = []

    for group in possible_groups:

        column = find_column(
            df,
            group
        )

        if column is not None:
            results.append(column)

    return results


# =========================================================
# DATA PREPARATION
# =========================================================

def prepare_dataframe(df):
    """
    Prepare uploaded business data for analytics.
    """

    df = df.copy()

    # Clean column names
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # Convert common date columns
    date_column = find_column(
        df,
        [
            "order_date",
            "date",
            "transaction_date",
            "sales_date",
            "purchase_date",
            "created_at",
            "order_datetime",
        ]
    )

    if date_column:

        df[date_column] = pd.to_datetime(
            df[date_column],
            errors="coerce",
            dayfirst=True
        )

    # Convert common numeric columns
    numeric_candidates = [
        "revenue",
        "sales",
        "sales_amount",
        "total_sales",
        "amount",
        "profit",
        "profit_amount",
        "cost",
        "quantity",
        "units",
        "discount",
    ]

    for column_name in numeric_candidates:

        column = find_column(
            df,
            [column_name]
        )

        if column:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


# =========================================================
# COLUMN DISCOVERY
# =========================================================

def detect_business_columns(df):

    return {
        "date": find_column(
            df,
            [
                "order_date",
                "date",
                "transaction_date",
                "sales_date",
                "purchase_date",
                "created_at",
                "order_datetime",
            ]
        ),

        "revenue": find_column(
            df,
            [
                "revenue",
                "sales",
                "sales_amount",
                "total_sales",
                "amount",
                "total_amount",
                "order_value",
            ]
        ),

        "profit": find_column(
            df,
            [
                "profit",
                "profit_amount",
                "net_profit",
                "gross_profit",
            ]
        ),

        "order_id": find_column(
            df,
            [
                "order_id",
                "orderid",
                "transaction_id",
                "invoice_id",
                "sale_id",
            ]
        ),

        "customer_id": find_column(
            df,
            [
                "customer_id",
                "customerid",
                "client_id",
                "user_id",
            ]
        ),

        "product_id": find_column(
            df,
            [
                "product_id",
                "productid",
                "item_id",
                "sku",
            ]
        ),

        "product_name": find_column(
            df,
            [
                "product_name",
                "product",
                "item_name",
                "item",
            ]
        ),

        "region": find_column(
            df,
            [
                "region",
                "area",
                "zone",
                "territory",
                "location",
            ]
        ),

        "quantity": find_column(
            df,
            [
                "quantity",
                "qty",
                "units",
                "units_sold",
            ]
        ),

        "status": find_column(
            df,
            [
                "order_status",
                "status",
                "sale_status",
                "transaction_status",
            ]
        ),
    }


# =========================================================
# CORE BUSINESS METRICS
# =========================================================

def calculate_business_metrics(
    df,
    columns
):

    revenue_column = columns["revenue"]
    profit_column = columns["profit"]
    order_column = columns["order_id"]
    customer_column = columns["customer_id"]
    quantity_column = columns["quantity"]

    # -----------------------------------------------------
    # Revenue
    # -----------------------------------------------------

    if revenue_column:

        total_revenue = float(
            df[revenue_column]
            .fillna(0)
            .sum()
        )

    else:

        total_revenue = 0.0

    # -----------------------------------------------------
    # Profit
    # -----------------------------------------------------

    if profit_column:

        total_profit = float(
            df[profit_column]
            .fillna(0)
            .sum()
        )

    else:

        total_profit = 0.0

    # -----------------------------------------------------
    # Orders
    # -----------------------------------------------------

    if order_column:

        total_orders = int(
            df[order_column]
            .nunique()
        )

    else:

        total_orders = int(
            len(df)
        )

    # -----------------------------------------------------
    # Customers
    # -----------------------------------------------------

    if customer_column:

        total_customers = int(
            df[customer_column]
            .nunique()
        )

    else:

        total_customers = 0

    # -----------------------------------------------------
    # Quantity
    # -----------------------------------------------------

    if quantity_column:

        total_units = int(
            df[quantity_column]
            .fillna(0)
            .sum()
        )

    else:

        total_units = 0

    # -----------------------------------------------------
    # AOV
    # -----------------------------------------------------

    if total_orders > 0:

        average_order_value = (
            total_revenue
            / total_orders
        )

    else:

        average_order_value = 0

    # -----------------------------------------------------
    # Profit Margin
    # -----------------------------------------------------

    if total_revenue != 0:

        profit_margin = (
            total_profit
            / total_revenue
        ) * 100

    else:

        profit_margin = 0

    return {
        "total_revenue": round(
            total_revenue,
            2
        ),

        "total_profit": round(
            total_profit,
            2
        ),

        "total_orders": total_orders,

        "total_customers": total_customers,

        "total_units": total_units,

        "average_order_value": round(
            average_order_value,
            2
        ),

        "profit_margin": round(
            profit_margin,
            2
        ),
    }


# =========================================================
# DATE RANGE
# =========================================================

def apply_date_filter(
    df,
    date_column,
    start_date=None,
    end_date=None
):

    if not date_column:
        return df

    if not start_date and not end_date:
        return df

    result = df.copy()

    result[date_column] = pd.to_datetime(
        result[date_column],
        errors="coerce"
    )

    if start_date:

        start_date = pd.to_datetime(
            start_date
        )

        result = result[
            result[date_column] >= start_date
        ]

    if end_date:

        end_date = pd.to_datetime(
            end_date
        )

        result = result[
            result[date_column] <= end_date
        ]

    return result


# =========================================================
# DATE RANGE INFORMATION
# =========================================================

def get_available_date_range(
    df,
    date_column
):

    if not date_column:

        return {
            "min_date": None,
            "max_date": None,
        }

    dates = pd.to_datetime(
        df[date_column],
        errors="coerce"
    ).dropna()

    if dates.empty:

        return {
            "min_date": None,
            "max_date": None,
        }

    return {
        "min_date": dates.min(),
        "max_date": dates.max(),
    }


# =========================================================
# REVENUE / PROFIT TREND
# =========================================================

def calculate_daily_trend(
    df,
    columns
):

    date_column = columns["date"]
    revenue_column = columns["revenue"]
    profit_column = columns["profit"]

    if not date_column:

        return []

    working = df.copy()

    working[date_column] = pd.to_datetime(
        working[date_column],
        errors="coerce"
    )

    working = working.dropna(
        subset=[date_column]
    )

    if working.empty:

        return []

    grouped = working.groupby(
        working[date_column].dt.date
    )

    results = []

    for date, group in grouped:

        if revenue_column:

            revenue = float(
                group[revenue_column]
                .fillna(0)
                .sum()
            )

        else:

            revenue = 0

        if profit_column:

            profit = float(
                group[profit_column]
                .fillna(0)
                .sum()
            )

        else:

            profit = 0

        results.append({
            "date": date.strftime(
                "%Y-%m-%d"
            ),

            "revenue": round(
                revenue,
                2
            ),

            "profit": round(
                profit,
                2
            ),

            "orders": int(
                group[
                    columns["order_id"]
                ].nunique()
            )
            if columns["order_id"]
            else len(group),
        })

    return results


# =========================================================
# REGION ANALYSIS
# =========================================================

def calculate_region_analysis(
    df,
    columns
):

    region_column = columns["region"]
    revenue_column = columns["revenue"]
    profit_column = columns["profit"]

    if not region_column:

        return []

    grouped = df.groupby(
        region_column,
        dropna=False
    )

    results = []

    for region, group in grouped:

        region_name = (
            "Unknown"
            if pd.isna(region)
            else str(region)
        )

        revenue = (
            float(
                group[revenue_column]
                .fillna(0)
                .sum()
            )
            if revenue_column
            else 0
        )

        profit = (
            float(
                group[profit_column]
                .fillna(0)
                .sum()
            )
            if profit_column
            else 0
        )

        orders = (
            int(
                group[
                    columns["order_id"]
                ].nunique()
            )
            if columns["order_id"]
            else len(group)
        )

        results.append({
            "region": region_name,
            "revenue": round(
                revenue,
                2
            ),
            "profit": round(
                profit,
                2
            ),
            "orders": orders,
        })

    results.sort(
        key=lambda item: item["revenue"],
        reverse=True
    )

    return results


# =========================================================
# TOP PRODUCTS
# =========================================================

def calculate_product_analysis(
    df,
    columns
):

    product_column = (
        columns["product_name"]
        or columns["product_id"]
    )

    revenue_column = columns["revenue"]
    profit_column = columns["profit"]
    quantity_column = columns["quantity"]

    if not product_column:

        return []

    grouped = df.groupby(
        product_column,
        dropna=False
    )

    results = []

    for product, group in grouped:

        product_name = (
            "Unknown"
            if pd.isna(product)
            else str(product)
        )

        revenue = (
            float(
                group[revenue_column]
                .fillna(0)
                .sum()
            )
            if revenue_column
            else 0
        )

        profit = (
            float(
                group[profit_column]
                .fillna(0)
                .sum()
            )
            if profit_column
            else 0
        )

        quantity = (
            float(
                group[quantity_column]
                .fillna(0)
                .sum()
            )
            if quantity_column
            else len(group)
        )

        results.append({
            "product": product_name,
            "revenue": round(
                revenue,
                2
            ),
            "profit": round(
                profit,
                2
            ),
            "quantity": int(
                quantity
            ),
        })

    results.sort(
        key=lambda item: item["revenue"],
        reverse=True
    )

    return results


# =========================================================
# ORDER STATUS ANALYSIS
# =========================================================

def calculate_status_analysis(
    df,
    columns
):

    status_column = columns["status"]

    if not status_column:

        return []

    grouped = (
        df[status_column]
        .fillna("Unknown")
        .value_counts()
    )

    total = grouped.sum()

    results = []

    for status, count in grouped.items():

        percentage = (
            count / total * 100
            if total
            else 0
        )

        results.append({
            "status": str(status),
            "count": int(count),
            "percentage": round(
                percentage,
                2
            ),
        })

    return results


# =========================================================
# GROWTH
# =========================================================

def calculate_growth(
    current_value,
    previous_value
):

    if previous_value == 0:

        if current_value > 0:
            return 100.0

        return 0.0

    return round(
        (
            (
                current_value
                - previous_value
            )
            / abs(previous_value)
        )
        * 100,
        2
    )


# =========================================================
# PERIOD COMPARISON
# =========================================================

def compare_periods(
    current_df,
    previous_df,
    columns
):

    current = calculate_business_metrics(
        current_df,
        columns
    )

    previous = calculate_business_metrics(
        previous_df,
        columns
    )

    return {

        "revenue": {
            "current": current[
                "total_revenue"
            ],
            "previous": previous[
                "total_revenue"
            ],
            "growth": calculate_growth(
                current[
                    "total_revenue"
                ],
                previous[
                    "total_revenue"
                ]
            ),
        },

        "profit": {
            "current": current[
                "total_profit"
            ],
            "previous": previous[
                "total_profit"
            ],
            "growth": calculate_growth(
                current[
                    "total_profit"
                ],
                previous[
                    "total_profit"
                ]
            ),
        },

        "orders": {
            "current": current[
                "total_orders"
            ],
            "previous": previous[
                "total_orders"
            ],
            "growth": calculate_growth(
                current[
                    "total_orders"
                ],
                previous[
                    "total_orders"
                ]
            ),
        },

        "customers": {
            "current": current[
                "total_customers"
            ],
            "previous": previous[
                "total_customers"
            ],
            "growth": calculate_growth(
                current[
                    "total_customers"
                ],
                previous[
                    "total_customers"
                ]
            ),
        },

    }


# =========================================================
# BUSINESS INSIGHTS
# =========================================================

def generate_business_insights(
    metrics,
    regions,
    products,
    status_analysis
):

    insights = []

    # -----------------------------------------------------
    # Profitability
    # -----------------------------------------------------

    margin = metrics[
        "profit_margin"
    ]

    if margin >= 25:

        insights.append({
            "type": "positive",
            "title": "Strong profitability",
            "message": (
                f"Profit margin is {margin}%, "
                "indicating healthy profitability."
            ),
        })

    elif margin >= 10:

        insights.append({
            "type": "neutral",
            "title": "Moderate profitability",
            "message": (
                f"Profit margin is {margin}%. "
                "There may be opportunities to improve margins."
            ),
        })

    else:

        insights.append({
            "type": "warning",
            "title": "Low profit margin",
            "message": (
                f"Profit margin is only {margin}%. "
                "Review pricing, costs and discounts."
            ),
        })

    # -----------------------------------------------------
    # Region
    # -----------------------------------------------------

    if regions:

        top_region = regions[0]

        insights.append({
            "type": "positive",
            "title": "Leading region",
            "message": (
                f"{top_region['region']} is the leading "
                f"region with revenue of "
                f"{top_region['revenue']:,.2f}."
            ),
        })

    # -----------------------------------------------------
    # Product
    # -----------------------------------------------------

    if products:

        top_product = products[0]

        insights.append({
            "type": "positive",
            "title": "Top revenue product",
            "message": (
                f"{top_product['product']} generated "
                f"{top_product['revenue']:,.2f} in revenue."
            ),
        })

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    if status_analysis:

        completed = None

        for item in status_analysis:

            if item["status"].lower() in [
                "completed",
                "complete",
                "delivered",
                "success",
            ]:

                completed = item
                break

        if completed:

            insights.append({
                "type": "neutral",
                "title": "Order completion",
                "message": (
                    f"{completed['percentage']}% of records "
                    f"are marked as {completed['status']}."
                ),
            })

    return insights


# =========================================================
# COMPLETE BUSINESS OVERVIEW
# =========================================================

def analyze_business_overview(
    df,
    start_date=None,
    end_date=None
):

    # -----------------------------------------------------
    # Prepare
    # -----------------------------------------------------

    df = prepare_dataframe(
        df
    )

    columns = detect_business_columns(
        df
    )

    # -----------------------------------------------------
    # Date filter
    # -----------------------------------------------------

    filtered_df = apply_date_filter(
        df,
        columns["date"],
        start_date,
        end_date
    )

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    metrics = calculate_business_metrics(
        filtered_df,
        columns
    )

    # -----------------------------------------------------
    # Trends
    # -----------------------------------------------------

    daily_trend = calculate_daily_trend(
        filtered_df,
        columns
    )

    # -----------------------------------------------------
    # Regions
    # -----------------------------------------------------

    regions = calculate_region_analysis(
        filtered_df,
        columns
    )

    # -----------------------------------------------------
    # Products
    # -----------------------------------------------------

    products = calculate_product_analysis(
        filtered_df,
        columns
    )

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    status_analysis = calculate_status_analysis(
        filtered_df,
        columns
    )

    # -----------------------------------------------------
    # Insights
    # -----------------------------------------------------

    insights = generate_business_insights(
        metrics,
        regions,
        products,
        status_analysis
    )

    # -----------------------------------------------------
    # Date information
    # -----------------------------------------------------

    date_range = get_available_date_range(
        filtered_df,
        columns["date"]
    )

    return {

        "dataframe": filtered_df,

        "columns": columns,

        "metrics": metrics,

        "daily_trend": daily_trend,

        "regions": regions,

        "products": products,

        "status_analysis": status_analysis,

        "insights": insights,

        "date_range": date_range,

    }