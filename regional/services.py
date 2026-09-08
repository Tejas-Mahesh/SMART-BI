import pandas as pd
import numpy as np


# ============================================================
# COLUMN DETECTION
# ============================================================

def find_column(df, possible_names):
    """
    Find the first matching column from a list of possible names.
    Matching is case-insensitive and whitespace-insensitive.
    """

    normalized_columns = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:

        key = str(name).strip().lower()

        if key in normalized_columns:
            return normalized_columns[key]

    return None


def detect_regional_columns(df):
    """
    Detect columns required for regional intelligence.
    """

    return {

        "region": find_column(
            df,
            [
                "region",
                "area",
                "zone",
                "territory",
                "sales_region",
                "sales region",
                "geographic_region",
                "geographic region",
            ],
        ),

        "state": find_column(
            df,
            [
                "state",
                "state_name",
                "state name",
                "province",
            ],
        ),

        "city": find_column(
            df,
            [
                "city",
                "city_name",
                "city name",
                "location",
            ],
        ),

        "date": find_column(
            df,
            [
                "order_date",
                "order date",
                "date",
                "transaction_date",
                "transaction date",
                "sales_date",
                "sales date",
                "purchase_date",
                "created_at",
                "order_datetime",
            ],
        ),

        "order_id": find_column(
            df,
            [
                "order_id",
                "orderid",
                "order id",
                "transaction_id",
                "transactionid",
                "invoice_id",
                "invoiceid",
                "sale_id",
            ],
        ),

        "customer_id": find_column(
            df,
            [
                "customer_id",
                "customerid",
                "customer id",
                "client_id",
                "clientid",
                "client id",
                "user_id",
            ],
        ),

        "quantity": find_column(
            df,
            [
                "quantity",
                "qty",
                "units",
                "units_sold",
                "units sold",
            ],
        ),

        "revenue": find_column(
            df,
            [
                "revenue",
                "sales",
                "sales_amount",
                "sales amount",
                "total_sales",
                "total sales",
                "amount",
                "total_amount",
                "order_value",
                "order value",
                "sales_value",
                "sales value",
            ],
        ),

        "profit": find_column(
            df,
            [
                "profit",
                "profit_amount",
                "profit amount",
                "net_profit",
                "net profit",
                "gross_profit",
                "gross profit",
            ],
        ),

        "cost": find_column(
            df,
            [
                "cost",
                "cost_amount",
                "cost amount",
                "product_cost",
                "product cost",
                "total_cost",
                "total cost",
            ],
        ),

        "discount": find_column(
            df,
            [
                "discount",
                "discount_amount",
                "discount amount",
                "discount_percent",
                "discount percentage",
            ],
        ),

        "return_status": find_column(
            df,
            [
                "return",
                "returned",
                "return_status",
                "return status",
                "is_returned",
                "is returned",
            ],
        ),

        "status": find_column(
            df,
            [
                "order_status",
                "order status",
                "status",
                "sale_status",
                "sale status",
                "transaction_status",
                "transaction status",
            ],
        ),
    }


# ============================================================
# DATA PREPARATION
# ============================================================

def prepare_regional_dataframe(df):

    df = df.copy()

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    columns = detect_regional_columns(df)

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    if columns["date"]:

        df[columns["date"]] = pd.to_datetime(
            df[columns["date"]],
            errors="coerce",
            dayfirst=True,
        )

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    numeric_columns = [

        columns["quantity"],

        columns["revenue"],

        columns["profit"],

        columns["cost"],

        columns["discount"],

    ]

    for column in numeric_columns:

        if column:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # --------------------------------------------------------
    # Region fallback
    # --------------------------------------------------------

    if not columns["region"]:

        fallback = (
            columns["state"]
            or columns["city"]
        )

        if fallback:

            df["_detected_region"] = (
                df[fallback]
                .fillna("Unknown")
                .astype(str)
            )

            columns["region"] = "_detected_region"

    # --------------------------------------------------------
    # Remove records without region
    # --------------------------------------------------------

    if columns["region"]:

        df = df.dropna(
            subset=[columns["region"]]
        )

    return df, columns


# ============================================================
# REGION NAME
# ============================================================

def clean_region_name(value):

    if pd.isna(value):
        return "Unknown"

    text = str(value).strip()

    if not text:
        return "Unknown"

    return text


# ============================================================
# RETURN DETECTION
# ============================================================

def is_returned_value(value):

    if pd.isna(value):
        return False

    text = str(value).strip().lower()

    return text in [
        "yes",
        "true",
        "1",
        "returned",
        "return",
        "refund",
        "refunded",
        "y",
    ]


# ============================================================
# REGIONAL PERFORMANCE TABLE
# ============================================================

def build_regional_table(
    df,
    columns,
):

    region_column = columns["region"]

    if not region_column:

        return pd.DataFrame()

    grouped = df.groupby(
        region_column,
        dropna=False,
    )

    table = grouped.size().to_frame(
        name="records"
    )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    if columns["revenue"]:

        table["revenue"] = (
            grouped[
                columns["revenue"]
            ]
            .sum()
            .fillna(0)
        )

    else:

        table["revenue"] = 0

    # --------------------------------------------------------
    # Profit
    # --------------------------------------------------------

    if columns["profit"]:

        table["profit"] = (
            grouped[
                columns["profit"]
            ]
            .sum()
            .fillna(0)
        )

    elif columns["cost"]:

        table["profit"] = (
            table["revenue"]
            -
            grouped[
                columns["cost"]
            ]
            .sum()
            .fillna(0)
        )

    else:

        table["profit"] = 0

    # --------------------------------------------------------
    # Units
    # --------------------------------------------------------

    if columns["quantity"]:

        table["units"] = (
            grouped[
                columns["quantity"]
            ]
            .sum()
            .fillna(0)
        )

    else:

        table["units"] = table["records"]

    # --------------------------------------------------------
    # Orders
    # --------------------------------------------------------

    if columns["order_id"]:

        table["orders"] = (
            grouped[
                columns["order_id"]
            ]
            .nunique()
        )

    else:

        table["orders"] = table["records"]

    # --------------------------------------------------------
    # Customers
    # --------------------------------------------------------

    if columns["customer_id"]:

        table["customers"] = (
            grouped[
                columns["customer_id"]
            ]
            .nunique()
        )

    else:

        table["customers"] = 0

    # --------------------------------------------------------
    # Discount
    # --------------------------------------------------------

    if columns["discount"]:

        table["discount"] = (
            grouped[
                columns["discount"]
            ]
            .mean()
            .fillna(0)
        )

    else:

        table["discount"] = 0

    # --------------------------------------------------------
    # Returns
    # --------------------------------------------------------

    if columns["return_status"]:

        working = df.copy()

        working["_returned"] = (
            working[
                columns["return_status"]
            ]
            .apply(is_returned_value)
        )

        returned_counts = (
            working
            .groupby(
                region_column
            )["_returned"]
            .sum()
        )

        table["returns"] = (
            returned_counts
            .reindex(table.index)
            .fillna(0)
        )

    else:

        table["returns"] = 0

    # --------------------------------------------------------
    # Return rate
    # --------------------------------------------------------

    table["return_rate"] = np.where(
        table["records"] > 0,
        (
            table["returns"]
            /
            table["records"]
        ) * 100,
        0,
    )

    # --------------------------------------------------------
    # Profit margin
    # --------------------------------------------------------

    table["profit_margin"] = np.where(
        table["revenue"] != 0,
        (
            table["profit"]
            /
            table["revenue"]
        ) * 100,
        0,
    )

    # --------------------------------------------------------
    # AOV
    # --------------------------------------------------------

    table["aov"] = np.where(
        table["orders"] > 0,
        (
            table["revenue"]
            /
            table["orders"]
        ),
        0,
    )

    # --------------------------------------------------------
    # Revenue per customer
    # --------------------------------------------------------

    table["revenue_per_customer"] = np.where(
        table["customers"] > 0,
        (
            table["revenue"]
            /
            table["customers"]
        ),
        0,
    )

    # --------------------------------------------------------
    # Revenue per unit
    # --------------------------------------------------------

    table["revenue_per_unit"] = np.where(
        table["units"] > 0,
        (
            table["revenue"]
            /
            table["units"]
        ),
        0,
    )

    # --------------------------------------------------------
    # Rename region
    # --------------------------------------------------------

    table = (
        table
        .reset_index()
        .rename(
            columns={
                region_column: "region"
            }
        )
    )

    table["region"] = (
        table["region"]
        .apply(clean_region_name)
    )

    return table


# ============================================================
# REGIONAL METRICS
# ============================================================

def calculate_regional_metrics(
    regional_table,
):

    if regional_table.empty:

        return {

            "total_regions": 0,

            "total_revenue": 0,

            "total_profit": 0,

            "total_orders": 0,

            "total_customers": 0,

            "total_units": 0,

            "average_revenue_per_region": 0,

            "average_profit_margin": 0,

        }

    total_regions = len(
        regional_table
    )

    total_revenue = float(
        regional_table[
            "revenue"
        ].sum()
    )

    total_profit = float(
        regional_table[
            "profit"
        ].sum()
    )

    total_orders = int(
        regional_table[
            "orders"
        ].sum()
    )

    total_customers = int(
        regional_table[
            "customers"
        ].sum()
    )

    total_units = int(
        regional_table[
            "units"
        ].sum()
    )

    average_revenue = (
        total_revenue
        /
        total_regions
        if total_regions
        else 0
    )

    margin = (
        total_profit
        /
        total_revenue
        * 100
        if total_revenue
        else 0
    )

    return {

        "total_regions":
            total_regions,

        "total_revenue":
            round(
                total_revenue,
                2,
            ),

        "total_profit":
            round(
                total_profit,
                2,
            ),

        "total_orders":
            total_orders,

        "total_customers":
            total_customers,

        "total_units":
            total_units,

        "average_revenue_per_region":
            round(
                average_revenue,
                2,
            ),

        "average_profit_margin":
            round(
                margin,
                2,
            ),

    }


# ============================================================
# REVENUE SHARE
# ============================================================

def calculate_revenue_share(
    regional_table,
):

    if regional_table.empty:
        return []

    total_revenue = float(
        regional_table[
            "revenue"
        ].sum()
    )

    results = []

    for _, row in (
        regional_table
        .sort_values(
            "revenue",
            ascending=False,
        )
        .iterrows()
    ):

        revenue = float(
            row["revenue"]
        )

        share = (
            revenue
            /
            total_revenue
            * 100
            if total_revenue
            else 0
        )

        results.append({

            "region":
                str(row["region"]),

            "revenue":
                round(
                    revenue,
                    2,
                ),

            "share":
                round(
                    share,
                    2,
                ),

        })

    return results


# ============================================================
# REGIONAL GROWTH
# ============================================================

def calculate_regional_growth(
    df,
    columns,
):

    region_column = columns["region"]
    date_column = columns["date"]
    revenue_column = columns["revenue"]

    if (
        not region_column
        or not date_column
    ):

        return []

    working = df.copy()

    working = working.dropna(
        subset=[date_column]
    )

    if working.empty:
        return []

    min_date = working[
        date_column
    ].min()

    max_date = working[
        date_column
    ].max()

    if pd.isna(min_date) or pd.isna(max_date):
        return []

    total_days = (
        max_date - min_date
    ).days

    if total_days < 2:
        return []

    midpoint = (
        min_date
        +
        (
            max_date
            -
            min_date
        ) / 2
    )

    first_period = working[
        working[date_column] <= midpoint
    ]

    second_period = working[
        working[date_column] > midpoint
    ]

    if revenue_column:

        first_values = (
            first_period
            .groupby(region_column)[
                revenue_column
            ]
            .sum()
        )

        second_values = (
            second_period
            .groupby(region_column)[
                revenue_column
            ]
            .sum()
        )

    else:

        first_values = (
            first_period
            .groupby(region_column)
            .size()
        )

        second_values = (
            second_period
            .groupby(region_column)
            .size()
        )

    regions = set(
        first_values.index
    ).union(
        set(second_values.index)
    )

    results = []

    for region in regions:

        region_name = clean_region_name(
            region
        )

        previous_value = float(
            first_values.get(
                region,
                0,
            )
        )

        current_value = float(
            second_values.get(
                region,
                0,
            )
        )

        if previous_value == 0:

            growth = (
                100
                if current_value > 0
                else 0
            )

        else:

            growth = (
                (
                    current_value
                    -
                    previous_value
                )
                /
                abs(previous_value)
            ) * 100

        results.append({

            "region":
                region_name,

            "previous_value":
                round(
                    previous_value,
                    2,
                ),

            "current_value":
                round(
                    current_value,
                    2,
                ),

            "growth":
                round(
                    growth,
                    2,
                ),

        })

    results.sort(
        key=lambda item:
            item["growth"],
        reverse=True,
    )

    return results


# ============================================================
# REGIONAL PERFORMANCE RANKING
# ============================================================

def calculate_regional_ranking(
    regional_table,
):

    if regional_table.empty:
        return []

    ranking = (
        regional_table
        .copy()
        .sort_values(
            [
                "revenue",
                "profit",
            ],
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )

    results = []

    for index, row in ranking.iterrows():

        results.append({

            "rank":
                index + 1,

            "region":
                str(row["region"]),

            "revenue":
                round(
                    float(
                        row["revenue"]
                    ),
                    2,
                ),

            "profit":
                round(
                    float(
                        row["profit"]
                    ),
                    2,
                ),

            "orders":
                int(
                    row["orders"]
                ),

            "customers":
                int(
                    row["customers"]
                ),

            "margin":
                round(
                    float(
                        row["profit_margin"]
                    ),
                    2,
                ),

            "return_rate":
                round(
                    float(
                        row["return_rate"]
                    ),
                    2,
                ),

        })

    return results


# ============================================================
# REGIONAL MATRIX
# ============================================================

def calculate_regional_matrix(
    regional_table,
):

    if regional_table.empty:
        return []

    revenue_median = (
        regional_table[
            "revenue"
        ].median()
    )

    profit_median = (
        regional_table[
            "profit"
        ].median()
    )

    results = []

    for _, row in regional_table.iterrows():

        revenue = float(
            row["revenue"]
        )

        profit = float(
            row["profit"]
        )

        if (
            revenue >= revenue_median
            and profit >= profit_median
        ):

            quadrant = (
                "High Revenue / High Profit"
            )

        elif (
            revenue >= revenue_median
            and profit < profit_median
        ):

            quadrant = (
                "High Revenue / Low Profit"
            )

        elif (
            revenue < revenue_median
            and profit >= profit_median
        ):

            quadrant = (
                "Low Revenue / High Profit"
            )

        else:

            quadrant = (
                "Low Revenue / Low Profit"
            )

        results.append({

            "region":
                str(row["region"]),

            "revenue":
                round(
                    revenue,
                    2,
                ),

            "profit":
                round(
                    profit,
                    2,
                ),

            "quadrant":
                quadrant,

        })

    return results


# ============================================================
# REGION PERFORMANCE SCORE
# ============================================================

def calculate_regional_score(
    regional_table,
):

    if regional_table.empty:
        return []

    table = regional_table.copy()

    def normalize(series):

        minimum = series.min()
        maximum = series.max()

        if maximum == minimum:

            return pd.Series(
                [50] * len(series),
                index=series.index,
            )

        return (
            (
                series
                -
                minimum
            )
            /
            (
                maximum
                -
                minimum
            )
        ) * 100

    revenue_score = normalize(
        table["revenue"]
    )

    profit_score = normalize(
        table["profit"]
    )

    margin_score = normalize(
        table["profit_margin"]
    )

    return_score = (
        100
        -
        normalize(
            table["return_rate"]
        )
    )

    table["performance_score"] = (
        revenue_score * 0.35
        +
        profit_score * 0.35
        +
        margin_score * 0.20
        +
        return_score * 0.10
    )

    table = table.sort_values(
        "performance_score",
        ascending=False,
    )

    results = []

    for _, row in table.iterrows():

        score = float(
            row[
                "performance_score"
            ]
        )

        if score >= 75:

            performance = "Excellent"

        elif score >= 55:

            performance = "Strong"

        elif score >= 35:

            performance = "Average"

        else:

            performance = "Needs Attention"

        results.append({

            "region":
                str(row["region"]),

            "score":
                round(
                    score,
                    2,
                ),

            "performance":
                performance,

        })

    return results


# ============================================================
# TOP / BOTTOM REGIONS
# ============================================================

def get_top_regions(
    regional_table,
    metric="revenue",
    limit=10,
):

    if regional_table.empty:
        return []

    if metric not in regional_table.columns:

        metric = "revenue"

    top = (
        regional_table
        .sort_values(
            metric,
            ascending=False,
        )
        .head(limit)
    )

    results = []

    for _, row in top.iterrows():

        results.append({

            "region":
                str(row["region"]),

            "revenue":
                round(
                    float(
                        row["revenue"]
                    ),
                    2,
                ),

            "profit":
                round(
                    float(
                        row["profit"]
                    ),
                    2,
                ),

            "orders":
                int(
                    row["orders"]
                ),

            "margin":
                round(
                    float(
                        row["profit_margin"]
                    ),
                    2,
                ),

        })

    return results


# ============================================================
# REGIONAL INSIGHTS
# ============================================================

def generate_regional_insights(
    regional_table,
    growth_data,
):

    insights = []

    if regional_table.empty:
        return insights

    # --------------------------------------------------------
    # Revenue leader
    # --------------------------------------------------------

    revenue_leader = (
        regional_table
        .sort_values(
            "revenue",
            ascending=False,
        )
        .iloc[0]
    )

    insights.append({

        "type": "positive",

        "title": "Revenue-leading region",

        "message": (
            f"{revenue_leader['region']} generated "
            f"₹{revenue_leader['revenue']:,.2f} "
            "in revenue, making it the strongest "
            "regional revenue contributor."
        ),

    })

    # --------------------------------------------------------
    # Profit leader
    # --------------------------------------------------------

    profit_leader = (
        regional_table
        .sort_values(
            "profit",
            ascending=False,
        )
        .iloc[0]
    )

    insights.append({

        "type": "positive",

        "title": "Profit-leading region",

        "message": (
            f"{profit_leader['region']} generated "
            f"₹{profit_leader['profit']:,.2f} "
            "in profit."
        ),

    })

    # --------------------------------------------------------
    # Highest margin
    # --------------------------------------------------------

    margin_leader = (
        regional_table
        .sort_values(
            "profit_margin",
            ascending=False,
        )
        .iloc[0]
    )

    insights.append({

        "type": "positive",

        "title": "Highest-margin region",

        "message": (
            f"{margin_leader['region']} has the highest "
            f"profit margin at "
            f"{margin_leader['profit_margin']:.2f}%."
        ),

    })

    # --------------------------------------------------------
    # Highest return
    # --------------------------------------------------------

    return_leader = (
        regional_table
        .sort_values(
            "return_rate",
            ascending=False,
        )
        .iloc[0]
    )

    if return_leader["return_rate"] > 0:

        insights.append({

            "type": "warning",

            "title": "Highest regional return rate",

            "message": (
                f"{return_leader['region']} has the highest "
                f"return rate at "
                f"{return_leader['return_rate']:.2f}%. "
                "Review product mix and customer issues "
                "in this region."
            ),

        })

    # --------------------------------------------------------
    # Growth leader
    # --------------------------------------------------------

    if growth_data:

        positive_growth = [
            item
            for item in growth_data
            if item["growth"] > 0
        ]

        if positive_growth:

            growth_leader = max(
                positive_growth,
                key=lambda item:
                    item["growth"],
            )

            insights.append({

                "type": "positive",

                "title": "Fastest-growing region",

                "message": (
                    f"{growth_leader['region']} recorded "
                    f"{growth_leader['growth']:.2f}% growth "
                    "between the earlier and later periods."
                ),

            })

        # ----------------------------------------------------
        # Declining region
        # ----------------------------------------------------

        declining = [
            item
            for item in growth_data
            if item["growth"] <= -20
        ]

        if declining:

            weakest = min(
                declining,
                key=lambda item:
                    item["growth"],
            )

            insights.append({

                "type": "warning",

                "title": "Regional decline",

                "message": (
                    f"{weakest['region']} declined by "
                    f"{abs(weakest['growth']):.2f}%. "
                    "Investigate demand, pricing and "
                    "marketing performance."
                ),

            })

    # --------------------------------------------------------
    # Revenue concentration
    # --------------------------------------------------------

    total_revenue = float(
        regional_table[
            "revenue"
        ].sum()
    )

    if total_revenue > 0:

        top_three = (
            regional_table
            .sort_values(
                "revenue",
                ascending=False,
            )
            .head(3)
        )

        top_three_share = (
            top_three["revenue"].sum()
            /
            total_revenue
            *
            100
        )

        if top_three_share >= 70:

            insights.append({

                "type": "warning",

                "title": "High revenue concentration",

                "message": (
                    f"The top three regions contribute "
                    f"{top_three_share:.2f}% of total revenue. "
                    "Consider reducing dependence on a small "
                    "number of markets."
                ),

            })

    return insights


# ============================================================
# COMPLETE REGIONAL INTELLIGENCE ENGINE
# ============================================================

def analyze_regional_intelligence(df):

    # --------------------------------------------------------
    # Prepare
    # --------------------------------------------------------

    df, columns = (
        prepare_regional_dataframe(df)
    )

    # --------------------------------------------------------
    # Regional table
    # --------------------------------------------------------

    regional_table = (
        build_regional_table(
            df,
            columns,
        )
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    metrics = (
        calculate_regional_metrics(
            regional_table
        )
    )

    # --------------------------------------------------------
    # Revenue share
    # --------------------------------------------------------

    revenue_share = (
        calculate_revenue_share(
            regional_table
        )
    )

    # --------------------------------------------------------
    # Growth
    # --------------------------------------------------------

    growth_data = (
        calculate_regional_growth(
            df,
            columns,
        )
    )

    # --------------------------------------------------------
    # Ranking
    # --------------------------------------------------------

    ranking = (
        calculate_regional_ranking(
            regional_table
        )
    )

    # --------------------------------------------------------
    # Matrix
    # --------------------------------------------------------

    matrix = (
        calculate_regional_matrix(
            regional_table
        )
    )

    # --------------------------------------------------------
    # Performance score
    # --------------------------------------------------------

    performance_scores = (
        calculate_regional_score(
            regional_table
        )
    )

    # --------------------------------------------------------
    # Top regions
    # --------------------------------------------------------

    top_revenue_regions = (
        get_top_regions(
            regional_table,
            "revenue",
            10,
        )
    )

    top_profit_regions = (
        get_top_regions(
            regional_table,
            "profit",
            10,
        )
    )

    # --------------------------------------------------------
    # Insights
    # --------------------------------------------------------

    insights = (
        generate_regional_insights(
            regional_table,
            growth_data,
        )
    )

    return {

        "columns":
            columns,

        "metrics":
            metrics,

        "regional_table":
            regional_table,

        "revenue_share":
            revenue_share,

        "growth_data":
            growth_data,

        "ranking":
            ranking,

        "matrix":
            matrix,

        "performance_scores":
            performance_scores,

        "top_revenue_regions":
            top_revenue_regions,

        "top_profit_regions":
            top_profit_regions,

        "insights":
            insights,

    }