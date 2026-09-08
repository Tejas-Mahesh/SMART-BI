import pandas as pd
import numpy as np


# ============================================================
# COLUMN DETECTION
# ============================================================

def find_column(df, possible_names):
    """
    Find a column using multiple possible names.
    Matching is case-insensitive.
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


def detect_product_columns(df):
    """
    Detect columns required for product intelligence.
    """

    return {
        "product_id": find_column(
            df,
            [
                "product_id",
                "productid",
                "product id",
                "item_id",
                "itemid",
                "sku",
            ],
        ),

        "product_name": find_column(
            df,
            [
                "product_name",
                "product name",
                "product",
                "item_name",
                "item name",
                "item",
            ],
        ),

        "category": find_column(
            df,
            [
                "category",
                "product_category",
                "product category",
                "category_name",
                "category name",
                "department",
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
                "sales_value",
            ],
        ),

        "profit": find_column(
            df,
            [
                "profit",
                "profit_amount",
                "profit amount",
                "net_profit",
                "gross_profit",
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

        "return_reason": find_column(
            df,
            [
                "return_reason",
                "return reason",
                "reason",
            ],
        ),

        "status": find_column(
            df,
            [
                "order_status",
                "order status",
                "status",
                "sale_status",
                "transaction_status",
            ],
        ),
    }


# ============================================================
# DATA PREPARATION
# ============================================================

def prepare_product_dataframe(df):

    df = df.copy()

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    columns = detect_product_columns(df)

    # Date
    if columns["date"]:

        df[columns["date"]] = pd.to_datetime(
            df[columns["date"]],
            errors="coerce",
            dayfirst=True,
        )

    # Numeric columns
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

    # Product identifier must exist
    product_column = (
        columns["product_name"]
        or columns["product_id"]
    )

    if product_column:

        df = df.dropna(
            subset=[product_column]
        )

    return df, columns


# ============================================================
# PRODUCT IDENTIFIER
# ============================================================

def get_product_column(columns):

    return (
        columns["product_name"]
        or columns["product_id"]
    )


# ============================================================
# PRODUCT LEVEL TABLE
# ============================================================

def build_product_table(df, columns):

    product_column = get_product_column(
        columns
    )

    if not product_column:
        return pd.DataFrame()

    grouped = df.groupby(
        product_column,
        dropna=False,
    )

    product_table = grouped.size().to_frame(
        name="records"
    )

    # Units
    if columns["quantity"]:

        product_table["units"] = (
            grouped[
                columns["quantity"]
            ]
            .sum()
            .fillna(0)
        )

    else:

        product_table["units"] = (
            product_table["records"]
        )

    # Revenue
    if columns["revenue"]:

        product_table["revenue"] = (
            grouped[
                columns["revenue"]
            ]
            .sum()
            .fillna(0)
        )

    else:

        product_table["revenue"] = 0

    # Profit
    if columns["profit"]:

        product_table["profit"] = (
            grouped[
                columns["profit"]
            ]
            .sum()
            .fillna(0)
        )

    elif columns["revenue"] and columns["cost"]:

        revenue = (
            grouped[
                columns["revenue"]
            ]
            .sum()
            .fillna(0)
        )

        cost = (
            grouped[
                columns["cost"]
            ]
            .sum()
            .fillna(0)
        )

        product_table["profit"] = (
            revenue - cost
        )

    else:

        product_table["profit"] = 0

    # Cost
    if columns["cost"]:

        product_table["cost"] = (
            grouped[
                columns["cost"]
            ]
            .sum()
            .fillna(0)
        )

    else:

        product_table["cost"] = (
            product_table["revenue"]
            - product_table["profit"]
        )

    # Discount
    if columns["discount"]:

        product_table["discount"] = (
            grouped[
                columns["discount"]
            ]
            .mean()
            .fillna(0)
        )

    else:

        product_table["discount"] = 0

    # Orders
    if columns["order_id"]:

        product_table["orders"] = (
            grouped[
                columns["order_id"]
            ]
            .nunique()
        )

    else:

        product_table["orders"] = (
            product_table["records"]
        )

    # Customers
    if columns["customer_id"]:

        product_table["customers"] = (
            grouped[
                columns["customer_id"]
            ]
            .nunique()
        )

    else:

        product_table["customers"] = 0

    # First / Last sale
    if columns["date"]:

        product_table["first_sale"] = (
            grouped[
                columns["date"]
            ]
            .min()
        )

        product_table["last_sale"] = (
            grouped[
                columns["date"]
            ]
            .max()
        )

    else:

        product_table["first_sale"] = pd.NaT
        product_table["last_sale"] = pd.NaT

    # Average selling value
    product_table["average_order_value"] = np.where(
        product_table["orders"] > 0,
        product_table["revenue"]
        / product_table["orders"],
        0,
    )

    # Profit margin
    product_table["profit_margin"] = np.where(
        product_table["revenue"] != 0,
        (
            product_table["profit"]
            / product_table["revenue"]
        ) * 100,
        0,
    )

    # Revenue per unit
    product_table["revenue_per_unit"] = np.where(
        product_table["units"] > 0,
        product_table["revenue"]
        / product_table["units"],
        0,
    )

    product_table = (
        product_table
        .reset_index()
        .rename(
            columns={
                product_column: "product"
            }
        )
    )

    return product_table


# ============================================================
# CATEGORY ANALYSIS
# ============================================================

def calculate_category_analysis(
    df,
    columns,
):

    category_column = columns["category"]

    if not category_column:

        return []

    revenue_column = columns["revenue"]
    profit_column = columns["profit"]
    quantity_column = columns["quantity"]
    product_column = get_product_column(
        columns
    )

    grouped = df.groupby(
        category_column,
        dropna=False,
    )

    results = []

    for category, group in grouped:

        category_name = (
            "Unknown"
            if pd.isna(category)
            else str(category)
        )

        if revenue_column:

            revenue = float(
                group[
                    revenue_column
                ]
                .fillna(0)
                .sum()
            )

        else:

            revenue = 0

        if profit_column:

            profit = float(
                group[
                    profit_column
                ]
                .fillna(0)
                .sum()
            )

        elif columns["cost"] and revenue_column:

            profit = float(
                (
                    group[revenue_column]
                    .fillna(0)
                    -
                    group[columns["cost"]]
                    .fillna(0)
                ).sum()
            )

        else:

            profit = 0

        if quantity_column:

            units = float(
                group[
                    quantity_column
                ]
                .fillna(0)
                .sum()
            )

        else:

            units = len(group)

        if product_column:

            products = int(
                group[
                    product_column
                ].nunique()
            )

        else:

            products = 0

        margin = (
            profit / revenue * 100
            if revenue
            else 0
        )

        results.append({

            "category": category_name,

            "revenue": round(
                revenue,
                2,
            ),

            "profit": round(
                profit,
                2,
            ),

            "units": int(units),

            "products": products,

            "profit_margin": round(
                margin,
                2,
            ),

        })

    results.sort(
        key=lambda item: item["revenue"],
        reverse=True,
    )

    return results


# ============================================================
# PRODUCT GROWTH
# ============================================================

def calculate_product_growth(
    df,
    columns,
):

    product_column = get_product_column(
        columns
    )

    date_column = columns["date"]
    revenue_column = columns["revenue"]
    quantity_column = columns["quantity"]

    if (
        not product_column
        or not date_column
    ):

        return []

    working = df.copy()

    working = working.dropna(
        subset=[date_column]
    )

    if working.empty:
        return []

    max_date = working[
        date_column
    ].max()

    min_date = working[
        date_column
    ].min()

    total_days = (
        max_date - min_date
    ).days

    if total_days <= 1:

        return []

    midpoint = (
        min_date
        + (
            max_date
            - min_date
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
            .groupby(product_column)[
                revenue_column
            ]
            .sum()
        )

        second_values = (
            second_period
            .groupby(product_column)[
                revenue_column
            ]
            .sum()
        )

    else:

        first_values = (
            first_period
            .groupby(product_column)
            .size()
        )

        second_values = (
            second_period
            .groupby(product_column)
            .size()
        )

    products = set(
        first_values.index
    ).union(
        set(second_values.index)
    )

    results = []

    for product in products:

        first_value = float(
            first_values.get(
                product,
                0,
            )
        )

        second_value = float(
            second_values.get(
                product,
                0,
            )
        )

        if first_value == 0:

            growth = (
                100.0
                if second_value > 0
                else 0.0
            )

        else:

            growth = (
                (
                    second_value
                    - first_value
                )
                / abs(first_value)
            ) * 100

        results.append({

            "product": str(product),

            "previous_value": round(
                first_value,
                2,
            ),

            "current_value": round(
                second_value,
                2,
            ),

            "growth": round(
                growth,
                2,
            ),

        })

    results.sort(
        key=lambda item: item["growth"],
        reverse=True,
    )

    return results


# ============================================================
# RETURN ANALYSIS
# ============================================================

def calculate_product_returns(
    df,
    columns,
):

    product_column = get_product_column(
        columns
    )

    return_column = columns[
        "return_status"
    ]

    if (
        not product_column
        or not return_column
    ):

        return []

    working = df.copy()

    def is_returned(value):

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
        ]

    working["_is_returned"] = (
        working[return_column]
        .apply(is_returned)
    )

    grouped = working.groupby(
        product_column,
        dropna=False,
    )

    results = []

    for product, group in grouped:

        total_records = len(group)

        returned_records = int(
            group["_is_returned"].sum()
        )

        return_rate = (
            returned_records
            / total_records
            * 100
            if total_records
            else 0
        )

        results.append({

            "product": str(product),

            "total": total_records,

            "returns": returned_records,

            "return_rate": round(
                return_rate,
                2,
            ),

        })

    results.sort(
        key=lambda item: item["return_rate"],
        reverse=True,
    )

    return results


# ============================================================
# PRODUCT CLASSIFICATION
# ============================================================

def classify_products(
    product_table,
    growth_data,
    return_data,
):

    if product_table.empty:
        return product_table

    result = product_table.copy()

    # --------------------------------------------------------
    # Growth map
    # --------------------------------------------------------

    growth_map = {
        item["product"]: item["growth"]
        for item in growth_data
    }

    result["growth"] = (
        result["product"]
        .astype(str)
        .map(growth_map)
        .fillna(0)
    )

    # --------------------------------------------------------
    # Return map
    # --------------------------------------------------------

    return_map = {
        item["product"]: item["return_rate"]
        for item in return_data
    }

    result["return_rate"] = (
        result["product"]
        .astype(str)
        .map(return_map)
        .fillna(0)
    )

    # --------------------------------------------------------
    # Classifications
    # --------------------------------------------------------

    result["classification"] = "Potential"

    if not result.empty:

        revenue_median = (
            result["revenue"].median()
        )

        profit_median = (
            result["profit"].median()
        )

        for index, row in result.iterrows():

            revenue = row["revenue"]
            profit = row["profit"]
            growth = row["growth"]
            return_rate = row["return_rate"]

            if (
                return_rate >= 15
            ):

                classification = (
                    "High Return"
                )

            elif (
                growth <= -20
                and revenue >= revenue_median
            ):

                classification = (
                    "Declining"
                )

            elif (
                profit >= profit_median
                and profit > 0
            ):

                classification = (
                    "Most Profitable"
                )

            elif (
                growth >= 20
            ):

                classification = (
                    "Fast Growing"
                )

            elif (
                revenue >= revenue_median
            ):

                classification = (
                    "Best Seller"
                )

            else:

                classification = (
                    "Potential"
                )

            result.at[
                index,
                "classification"
            ] = classification

    return result


# ============================================================
# PROFITABILITY MATRIX
# ============================================================

def calculate_profitability_matrix(
    product_table,
):

    if product_table.empty:
        return []

    results = []

    revenue_median = (
        product_table["revenue"].median()
    )

    profit_median = (
        product_table["profit"].median()
    )

    for _, row in product_table.iterrows():

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

            "product": str(
                row["product"]
            ),

            "revenue": round(
                revenue,
                2,
            ),

            "profit": round(
                profit,
                2,
            ),

            "quadrant": quadrant,

        })

    return results


# ============================================================
# TOP PRODUCTS
# ============================================================

def get_top_products(
    product_table,
    metric="revenue",
    limit=10,
):

    if product_table.empty:
        return []

    if metric not in product_table.columns:

        metric = "revenue"

    top = (
        product_table
        .sort_values(
            metric,
            ascending=False,
        )
        .head(limit)
    )

    results = []

    for _, row in top.iterrows():

        results.append({

            "product": str(
                row["product"]
            ),

            "revenue": round(
                float(
                    row["revenue"]
                ),
                2,
            ),

            "profit": round(
                float(
                    row["profit"]
                ),
                2,
            ),

            "units": int(
                row["units"]
            ),

            "margin": round(
                float(
                    row["profit_margin"]
                ),
                2,
            ),

        })

    return results


# ============================================================
# PRODUCT METRICS
# ============================================================

def calculate_product_metrics(
    product_table,
):

    if product_table.empty:

        return {

            "total_products": 0,

            "total_units": 0,

            "total_revenue": 0,

            "total_profit": 0,

            "average_product_revenue": 0,

            "average_profit_margin": 0,

        }

    total_products = len(
        product_table
    )

    total_units = int(
        product_table[
            "units"
        ].sum()
    )

    total_revenue = float(
        product_table[
            "revenue"
        ].sum()
    )

    total_profit = float(
        product_table[
            "profit"
        ].sum()
    )

    average_product_revenue = (
        total_revenue
        / total_products
        if total_products
        else 0
    )

    average_profit_margin = (
        total_profit
        / total_revenue
        * 100
        if total_revenue
        else 0
    )

    return {

        "total_products": total_products,

        "total_units": total_units,

        "total_revenue": round(
            total_revenue,
            2,
        ),

        "total_profit": round(
            total_profit,
            2,
        ),

        "average_product_revenue": round(
            average_product_revenue,
            2,
        ),

        "average_profit_margin": round(
            average_profit_margin,
            2,
        ),

    }


# ============================================================
# PRODUCT INSIGHTS
# ============================================================

def generate_product_insights(
    product_table,
    category_data,
    growth_data,
    return_data,
):

    insights = []

    if product_table.empty:

        return insights

    # --------------------------------------------------------
    # Best revenue product
    # --------------------------------------------------------

    best_product = (
        product_table
        .sort_values(
            "revenue",
            ascending=False,
        )
        .iloc[0]
    )

    insights.append({

        "type": "positive",

        "title": "Top revenue product",

        "message": (
            f"{best_product['product']} generated "
            f"₹{best_product['revenue']:,.2f} "
            "in revenue."
        ),

    })

    # --------------------------------------------------------
    # Most profitable product
    # --------------------------------------------------------

    profitable_product = (
        product_table
        .sort_values(
            "profit",
            ascending=False,
        )
        .iloc[0]
    )

    insights.append({

        "type": "positive",

        "title": "Most profitable product",

        "message": (
            f"{profitable_product['product']} generated "
            f"₹{profitable_product['profit']:,.2f} "
            "in profit."
        ),

    })

    # --------------------------------------------------------
    # Fast growing product
    # --------------------------------------------------------

    if growth_data:

        fastest = max(
            growth_data,
            key=lambda item: item["growth"],
        )

        if fastest["growth"] > 0:

            insights.append({

                "type": "positive",

                "title": "Fastest growing product",

                "message": (
                    f"{fastest['product']} grew by "
                    f"{fastest['growth']}% between "
                    "the earlier and later periods."
                ),

            })

    # --------------------------------------------------------
    # Declining products
    # --------------------------------------------------------

    declining_count = sum(
        1
        for item in growth_data
        if item["growth"] <= -20
    )

    if declining_count > 0:

        insights.append({

            "type": "warning",

            "title": "Products losing momentum",

            "message": (
                f"{declining_count} products experienced "
                "a decline of at least 20%. Review pricing, "
                "demand and marketing activity."
            ),

        })

    # --------------------------------------------------------
    # High return products
    # --------------------------------------------------------

    high_return_products = [
        item
        for item in return_data
        if item["return_rate"] >= 15
    ]

    if high_return_products:

        highest_return = max(
            high_return_products,
            key=lambda item: item[
                "return_rate"
            ],
        )

        insights.append({

            "type": "warning",

            "title": "High return product",

            "message": (
                f"{highest_return['product']} has a "
                f"{highest_return['return_rate']}% "
                "return rate. Investigate product quality "
                "or customer expectations."
            ),

        })

    # --------------------------------------------------------
    # Category insight
    # --------------------------------------------------------

    if category_data:

        top_category = category_data[0]

        insights.append({

            "type": "neutral",

            "title": "Leading category",

            "message": (
                f"{top_category['category']} generated "
                f"₹{top_category['revenue']:,.2f} "
                "in revenue."
            ),

        })

    return insights


# ============================================================
# COMPLETE PRODUCT INTELLIGENCE ANALYSIS
# ============================================================

def analyze_product_intelligence(df):

    # Prepare
    df, columns = (
        prepare_product_dataframe(df)
    )

    # Product table
    product_table = (
        build_product_table(
            df,
            columns,
        )
    )

    # Categories
    category_data = (
        calculate_category_analysis(
            df,
            columns,
        )
    )

    # Growth
    growth_data = (
        calculate_product_growth(
            df,
            columns,
        )
    )

    # Returns
    return_data = (
        calculate_product_returns(
            df,
            columns,
        )
    )

    # Classification
    product_table = (
        classify_products(
            product_table,
            growth_data,
            return_data,
        )
    )

    # Profitability matrix
    profitability_matrix = (
        calculate_profitability_matrix(
            product_table
        )
    )

    # Metrics
    metrics = (
        calculate_product_metrics(
            product_table
        )
    )

    # Top products
    top_revenue_products = (
        get_top_products(
            product_table,
            "revenue",
            10,
        )
    )

    top_profit_products = (
        get_top_products(
            product_table,
            "profit",
            10,
        )
    )

    top_units_products = (
        get_top_products(
            product_table,
            "units",
            10,
        )
    )

    # Insights
    insights = (
        generate_product_insights(
            product_table,
            category_data,
            growth_data,
            return_data,
        )
    )

    return {

        "columns": columns,

        "metrics": metrics,

        "product_table": product_table,

        "category_data": category_data,

        "growth_data": growth_data,

        "return_data": return_data,

        "profitability_matrix":
            profitability_matrix,

        "top_revenue_products":
            top_revenue_products,

        "top_profit_products":
            top_profit_products,

        "top_units_products":
            top_units_products,

        "insights": insights,

    }