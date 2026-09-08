
import pandas as pd
import numpy as np


# ============================================================
# SMART BI
# RETURNS ANALYSIS ENGINE
# ============================================================


# ============================================================
# COLUMN DETECTION
# ============================================================

def find_column(df, possible_names):
    """
    Find the first matching column from a list of possible names.
    Matching is case-insensitive and ignores spaces/underscores.
    """

    normalized_columns = {
        str(column).strip().lower().replace("_", " ").replace("-", " "): column
        for column in df.columns
    }

    for name in possible_names:

        normalized_name = (
            str(name)
            .strip()
            .lower()
            .replace("_", " ")
            .replace("-", " ")
        )

        if normalized_name in normalized_columns:
            return normalized_columns[normalized_name]

    return None


def find_columns(df, possible_names):
    """
    Return all matching columns.
    """

    found = []

    normalized_columns = {
        str(column).strip().lower().replace("_", " ").replace("-", " "): column
        for column in df.columns
    }

    for name in possible_names:

        normalized_name = (
            str(name)
            .strip()
            .lower()
            .replace("_", " ")
            .replace("-", " ")
        )

        if normalized_name in normalized_columns:
            found.append(normalized_columns[normalized_name])

    return found


# ============================================================
# DETECT RETURN COLUMNS
# ============================================================

def detect_return_columns(df):

    columns = {

        "return_id": find_column(
            df,
            [
                "return_id",
                "returnid",
                "return id",
                "refund_id",
                "refundid",
                "refund id",
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
                "transaction id",
                "invoice_id",
                "invoiceid",
                "invoice id",
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
                "userid",
                "user id",
            ],
        ),

        "product_id": find_column(
            df,
            [
                "product_id",
                "productid",
                "product id",
                "item_id",
                "itemid",
                "item id",
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

        "region": find_column(
            df,
            [
                "region",
                "sales_region",
                "sales region",
                "geographic_region",
                "geographic region",
                "area",
                "zone",
                "territory",
            ],
        ),

        "state": find_column(
            df,
            [
                "state",
                "province",
            ],
        ),

        "city": find_column(
            df,
            [
                "city",
                "location",
            ],
        ),

        "date": find_column(
            df,
            [
                "return_date",
                "return date",
                "refund_date",
                "refund date",
                "date",
                "order_date",
                "order date",
                "transaction_date",
                "transaction date",
                "sales_date",
                "sales date",
                "created_at",
                "created at",
            ],
        ),

        "quantity": find_column(
            df,
            [
                "return_quantity",
                "return quantity",
                "returned_quantity",
                "returned quantity",
                "quantity",
                "qty",
                "units",
                "units_returned",
                "units returned",
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
                "total amount",
                "order_value",
                "order value",
                "sales_value",
                "sales value",
            ],
        ),

        "return_amount": find_column(
            df,
            [
                "return_amount",
                "return amount",
                "refund_amount",
                "refund amount",
                "refunded_amount",
                "refunded amount",
                "refund_value",
                "refund value",
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

        "reason": find_column(
            df,
            [
                "return_reason",
                "return reason",
                "refund_reason",
                "refund reason",
                "reason",
                "return_type",
                "return type",
            ],
        ),

        "return_status": find_column(
            df,
            [
                "return_status",
                "return status",
                "returned",
                "is_returned",
                "is returned",
                "return",
                "refund_status",
                "refund status",
            ],
        ),

        "order_status": find_column(
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
    }

    return columns


# ============================================================
# PREPARE DATAFRAME
# ============================================================

def prepare_returns_dataframe(df):

    df = df.copy()

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Remove completely empty columns
    df = df.dropna(axis=1, how="all")

    # Clean column names
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    columns = detect_return_columns(df)

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if columns["date"]:

        df[columns["date"]] = pd.to_datetime(
            df[columns["date"]],
            errors="coerce",
            dayfirst=True,
        )

    # --------------------------------------------------------
    # NUMERIC COLUMNS
    # --------------------------------------------------------

    numeric_keys = [
        "quantity",
        "revenue",
        "return_amount",
        "profit",
        "discount",
        "cost",
    ]

    for key in numeric_keys:

        column = columns.get(key)

        if column:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    return df, columns


# ============================================================
# RETURN VALUE DETECTION
# ============================================================

def is_returned_value(value):

    if pd.isna(value):
        return False

    if isinstance(value, bool):
        return value

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
        "r",
    ]


# ============================================================
# IDENTIFY RETURN RECORDS
# ============================================================

def identify_return_records(df, columns):

    df = df.copy()

    return_column = columns.get("return_status")
    order_status_column = columns.get("order_status")

    # --------------------------------------------------------
    # Explicit return status
    # --------------------------------------------------------

    if return_column:

        df["_is_returned"] = df[
            return_column
        ].apply(is_returned_value)

        return df

    # --------------------------------------------------------
    # Order status fallback
    # --------------------------------------------------------

    if order_status_column:

        return_values = [
            "returned",
            "return",
            "refunded",
            "refund",
        ]

        df["_is_returned"] = (
            df[order_status_column]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(return_values)
        )

        return df

    # --------------------------------------------------------
    # If no return field exists
    # --------------------------------------------------------

    df["_is_returned"] = False

    return df


# ============================================================
# BASIC RETURN METRICS
# ============================================================

def calculate_return_metrics(df, columns):

    total_records = len(df)

    returned_df = df[
        df["_is_returned"]
    ].copy()

    total_returns = len(
        returned_df
    )

    # --------------------------------------------------------
    # Return rate
    # --------------------------------------------------------

    if total_records > 0:

        return_rate = (
            total_returns
            / total_records
            * 100
        )

    else:

        return_rate = 0

    # --------------------------------------------------------
    # Returned units
    # --------------------------------------------------------

    quantity_column = columns.get(
        "quantity"
    )

    if quantity_column:

        returned_units = (
            returned_df[
                quantity_column
            ]
            .fillna(0)
            .sum()
        )

    else:

        returned_units = total_returns

    # --------------------------------------------------------
    # Revenue affected
    # --------------------------------------------------------

    return_amount_column = columns.get(
        "return_amount"
    )

    revenue_column = columns.get(
        "revenue"
    )

    if return_amount_column:

        revenue_affected = (
            returned_df[
                return_amount_column
            ]
            .fillna(0)
            .sum()
        )

    elif revenue_column:

        revenue_affected = (
            returned_df[
                revenue_column
            ]
            .fillna(0)
            .sum()
        )

    else:

        revenue_affected = 0

    # --------------------------------------------------------
    # Profit affected
    # --------------------------------------------------------

    profit_column = columns.get(
        "profit"
    )

    if profit_column:

        profit_affected = (
            returned_df[
                profit_column
            ]
            .fillna(0)
            .sum()
        )

    else:

        profit_affected = 0

    # --------------------------------------------------------
    # Average return value
    # --------------------------------------------------------

    if total_returns > 0:

        average_return_value = (
            revenue_affected
            / total_returns
        )

    else:

        average_return_value = 0

    return {
        "total_records": int(total_records),
        "total_returns": int(total_returns),
        "return_rate": round(
            float(return_rate),
            2,
        ),
        "returned_units": int(
            returned_units
        ),
        "revenue_affected": round(
            float(revenue_affected),
            2,
        ),
        "profit_affected": round(
            float(profit_affected),
            2,
        ),
        "average_return_value": round(
            float(average_return_value),
            2,
        ),
    }


# ============================================================
# RETURN TREND
# ============================================================

def calculate_return_trend(df, columns):

    date_column = columns.get(
        "date"
    )

    if not date_column:

        return []

    working = df[
        df["_is_returned"]
    ].copy()

    working = working.dropna(
        subset=[date_column]
    )

    if working.empty:

        return []

    working["_month"] = (
        working[date_column]
        .dt.to_period("M")
        .astype(str)
    )

    grouped = (
        working
        .groupby("_month")
        .size()
        .reset_index(
            name="returns"
        )
    )

    revenue_column = columns.get(
        "revenue"
    )

    return_amount_column = columns.get(
        "return_amount"
    )

    quantity_column = columns.get(
        "quantity"
    )

    if revenue_column:

        revenue_data = (
            working
            .groupby("_month")[
                revenue_column
            ]
            .sum()
            .reset_index(
                name="revenue_affected"
            )
        )

        grouped = grouped.merge(
            revenue_data,
            on="_month",
            how="left",
        )

    elif return_amount_column:

        amount_data = (
            working
            .groupby("_month")[
                return_amount_column
            ]
            .sum()
            .reset_index(
                name="revenue_affected"
            )
        )

        grouped = grouped.merge(
            amount_data,
            on="_month",
            how="left",
        )

    else:

        grouped[
            "revenue_affected"
        ] = 0

    if quantity_column:

        quantity_data = (
            working
            .groupby("_month")[
                quantity_column
            ]
            .sum()
            .reset_index(
                name="returned_units"
            )
        )

        grouped = grouped.merge(
            quantity_data,
            on="_month",
            how="left",
        )

    else:

        grouped[
            "returned_units"
        ] = grouped["returns"]

    grouped = grouped.sort_values(
        "_month"
    )

    return grouped.to_dict(
        orient="records"
    )


# ============================================================
# PRODUCT RETURN ANALYSIS
# ============================================================

def calculate_product_returns(
    df,
    columns,
):

    product_column = (
        columns.get("product_name")
        or columns.get("product_id")
    )

    if not product_column:

        return []

    total_group = (
        df
        .groupby(product_column)
        .size()
        .reset_index(
            name="total_records"
        )
    )

    returned = (
        df[df["_is_returned"]]
        .groupby(product_column)
        .size()
        .reset_index(
            name="returns"
        )
    )

    result = total_group.merge(
        returned,
        on=product_column,
        how="left",
    )

    result["returns"] = (
        result["returns"]
        .fillna(0)
        .astype(int)
    )

    result["return_rate"] = np.where(
        result["total_records"] > 0,
        result["returns"]
        / result["total_records"]
        * 100,
        0,
    )

    quantity_column = columns.get(
        "quantity"
    )

    if quantity_column:

        returned_units = (
            df[df["_is_returned"]]
            .groupby(product_column)[
                quantity_column
            ]
            .sum()
            .reset_index(
                name="returned_units"
            )
        )

        result = result.merge(
            returned_units,
            on=product_column,
            how="left",
        )

    else:

        result[
            "returned_units"
        ] = result["returns"]

    revenue_column = columns.get(
        "revenue"
    )

    if revenue_column:

        affected_revenue = (
            df[df["_is_returned"]]
            .groupby(product_column)[
                revenue_column
            ]
            .sum()
            .reset_index(
                name="revenue_affected"
            )
        )

        result = result.merge(
            affected_revenue,
            on=product_column,
            how="left",
        )

    else:

        result[
            "revenue_affected"
        ] = 0

    result[
        "revenue_affected"
    ] = (
        result[
            "revenue_affected"
        ]
        .fillna(0)
    )

    result = result.sort_values(
        "return_rate",
        ascending=False,
    )

    return result.to_dict(
        orient="records"
    )


# ============================================================
# REGION RETURN ANALYSIS
# ============================================================

def calculate_region_returns(
    df,
    columns,
):

    region_column = columns.get(
        "region"
    )

    if not region_column:

        region_column = (
            columns.get("state")
            or columns.get("city")
        )

    if not region_column:

        return []

    total = (
        df
        .groupby(region_column)
        .size()
        .reset_index(
            name="total_records"
        )
    )

    returned = (
        df[df["_is_returned"]]
        .groupby(region_column)
        .size()
        .reset_index(
            name="returns"
        )
    )

    result = total.merge(
        returned,
        on=region_column,
        how="left",
    )

    result["returns"] = (
        result["returns"]
        .fillna(0)
        .astype(int)
    )

    result["return_rate"] = np.where(
        result["total_records"] > 0,
        result["returns"]
        / result["total_records"]
        * 100,
        0,
    )

    revenue_column = columns.get(
        "revenue"
    )

    if revenue_column:

        affected_revenue = (
            df[df["_is_returned"]]
            .groupby(region_column)[
                revenue_column
            ]
            .sum()
            .reset_index(
                name="revenue_affected"
            )
        )

        result = result.merge(
            affected_revenue,
            on=region_column,
            how="left",
        )

    else:

        result[
            "revenue_affected"
        ] = 0

    result[
        "revenue_affected"
    ] = (
        result[
            "revenue_affected"
        ]
        .fillna(0)
    )

    result = result.sort_values(
        "return_rate",
        ascending=False,
    )

    return result.to_dict(
        orient="records"
    )


# ============================================================
# RETURN REASON ANALYSIS
# ============================================================

def calculate_return_reasons(
    df,
    columns,
):

    reason_column = columns.get(
        "reason"
    )

    if not reason_column:

        return []

    working = df[
        df["_is_returned"]
    ].copy()

    if working.empty:

        return []

    working[
        reason_column
    ] = (
        working[
            reason_column
        ]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    working.loc[
        working[reason_column] == "",
        reason_column,
    ] = "Unknown"

    result = (
        working
        .groupby(reason_column)
        .size()
        .reset_index(
            name="returns"
        )
    )

    total = result[
        "returns"
    ].sum()

    if total > 0:

        result[
            "percentage"
        ] = (
            result["returns"]
            / total
            * 100
        )

    else:

        result[
            "percentage"
        ] = 0

    result = result.sort_values(
        "returns",
        ascending=False,
    )

    return result.to_dict(
        orient="records"
    )


# ============================================================
# CUSTOMER RETURN ANALYSIS
# ============================================================

def calculate_customer_returns(
    df,
    columns,
):

    customer_column = columns.get(
        "customer_id"
    )

    if not customer_column:

        return []

    total = (
        df
        .groupby(customer_column)
        .size()
        .reset_index(
            name="total_orders"
        )
    )

    returned = (
        df[df["_is_returned"]]
        .groupby(customer_column)
        .size()
        .reset_index(
            name="returns"
        )
    )

    result = total.merge(
        returned,
        on=customer_column,
        how="left",
    )

    result["returns"] = (
        result["returns"]
        .fillna(0)
        .astype(int)
    )

    result["return_rate"] = np.where(
        result["total_orders"] > 0,
        result["returns"]
        / result["total_orders"]
        * 100,
        0,
    )

    result = result[
        result["returns"] > 0
    ]

    result = result.sort_values(
        [
            "return_rate",
            "returns",
        ],
        ascending=False,
    )

    return result.head(100).to_dict(
        orient="records"
    )


# ============================================================
# CATEGORY RETURN ANALYSIS
# ============================================================

def calculate_category_returns(
    df,
    columns,
):

    category_column = columns.get(
        "category"
    )

    if not category_column:

        return []

    total = (
        df
        .groupby(category_column)
        .size()
        .reset_index(
            name="total_records"
        )
    )

    returned = (
        df[df["_is_returned"]]
        .groupby(category_column)
        .size()
        .reset_index(
            name="returns"
        )
    )

    result = total.merge(
        returned,
        on=category_column,
        how="left",
    )

    result["returns"] = (
        result["returns"]
        .fillna(0)
        .astype(int)
    )

    result["return_rate"] = np.where(
        result["total_records"] > 0,
        result["returns"]
        / result["total_records"]
        * 100,
        0,
    )

    result = result.sort_values(
        "return_rate",
        ascending=False,
    )

    return result.to_dict(
        orient="records"
    )


# ============================================================
# RETURN CLASSIFICATION
# ============================================================

def classify_return_rate(rate):

    if rate >= 20:
        return "Critical"

    if rate >= 15:
        return "High"

    if rate >= 8:
        return "Moderate"

    return "Low"


def classify_products_by_return(
    product_returns,
):

    classified = []

    for product in product_returns:

        rate = float(
            product.get(
                "return_rate",
                0,
            )
        )

        product_copy = product.copy()

        product_copy[
            "classification"
        ] = classify_return_rate(
            rate
        )

        classified.append(
            product_copy
        )

    return classified


# ============================================================
# HIGH RETURN PRODUCTS
# ============================================================

def get_high_return_products(
    product_returns,
):

    high_return = [
        product
        for product in product_returns
        if float(
            product.get(
                "return_rate",
                0,
            )
        ) >= 15
    ]

    return sorted(
        high_return,
        key=lambda item: float(
            item.get(
                "return_rate",
                0,
            )
        ),
        reverse=True,
    )[:20]


# ============================================================
# RETURN RISK SCORE
# ============================================================

def calculate_return_risk_score(
    product_returns,
):

    result = []

    for product in product_returns:

        rate = float(
            product.get(
                "return_rate",
                0,
            )
        )

        returns = int(
            product.get(
                "returns",
                0,
            )
        )

        # Return rate contributes 70%
        rate_score = min(
            rate / 25 * 70,
            70,
        )

        # Number of returns contributes 30%
        volume_score = min(
            returns / 20 * 30,
            30,
        )

        risk_score = (
            rate_score
            + volume_score
        )

        product_copy = product.copy()

        product_copy[
            "risk_score"
        ] = round(
            risk_score,
            2,
        )

        if risk_score >= 70:
            risk_level = "Critical"

        elif risk_score >= 50:
            risk_level = "High"

        elif risk_score >= 30:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        product_copy[
            "risk_level"
        ] = risk_level

        result.append(
            product_copy
        )

    return sorted(
        result,
        key=lambda item: item[
            "risk_score"
        ],
        reverse=True,
    )


# ============================================================
# AUTOMATIC BUSINESS INSIGHTS
# ============================================================

def generate_return_insights(
    metrics,
    product_returns,
    region_returns,
    reason_data,
    category_returns,
):

    insights = []

    # --------------------------------------------------------
    # Overall return rate
    # --------------------------------------------------------

    return_rate = metrics[
        "return_rate"
    ]

    if return_rate >= 15:

        insights.append(
            {
                "type": "critical",
                "title": "High Return Rate",
                "message": (
                    f"Overall return rate is "
                    f"{return_rate:.2f}%, which "
                    "requires immediate investigation."
                ),
            }
        )

    elif return_rate >= 8:

        insights.append(
            {
                "type": "warning",
                "title": "Elevated Returns",
                "message": (
                    f"Overall return rate is "
                    f"{return_rate:.2f}%. "
                    "Review products and customer "
                    "return reasons."
                ),
            }
        )

    else:

        insights.append(
            {
                "type": "positive",
                "title": "Return Rate Controlled",
                "message": (
                    f"Overall return rate is "
                    f"{return_rate:.2f}%, indicating "
                    "relatively controlled returns."
                ),
            }
        )

    # --------------------------------------------------------
    # Highest-return product
    # --------------------------------------------------------

    if product_returns:

        highest_product = max(
            product_returns,
            key=lambda item: float(
                item.get(
                    "return_rate",
                    0,
                )
            ),
        )

        product_name = (
            highest_product.get(
                "product_name"
            )
            or highest_product.get(
                "product"
            )
            or highest_product.get(
                "product_id"
            )
            or "Unknown Product"
        )

        # Find actual key dynamically
        product_keys = [
            key
            for key in highest_product.keys()
            if key not in [
                "total_records",
                "returns",
                "return_rate",
                "returned_units",
                "revenue_affected",
                "classification",
            ]
        ]

        if product_keys:

            product_name = str(
                highest_product[
                    product_keys[0]
                ]
            )

        insights.append(
            {
                "type": "warning",
                "title": "Highest Return Product",
                "message": (
                    f"{product_name} has the highest "
                    f"return rate at "
                    f"{float(highest_product['return_rate']):.2f}%."
                ),
            }
        )

    # --------------------------------------------------------
    # Highest-return region
    # --------------------------------------------------------

    if region_returns:

        highest_region = max(
            region_returns,
            key=lambda item: float(
                item.get(
                    "return_rate",
                    0,
                )
            ),
        )

        region_keys = [
            key
            for key in highest_region.keys()
            if key not in [
                "total_records",
                "returns",
                "return_rate",
                "revenue_affected",
            ]
        ]

        if region_keys:

            region_name = str(
                highest_region[
                    region_keys[0]
                ]
            )

            insights.append(
                {
                    "type": "warning",
                    "title": "High Return Region",
                    "message": (
                        f"{region_name} has the highest "
                        f"return rate at "
                        f"{float(highest_region['return_rate']):.2f}%."
                    ),
                }
            )

    # --------------------------------------------------------
    # Top return reason
    # --------------------------------------------------------

    if reason_data:

        top_reason = reason_data[0]

        reason_keys = [
            key
            for key in top_reason.keys()
            if key not in [
                "returns",
                "percentage",
            ]
        ]

        if reason_keys:

            reason = str(
                top_reason[
                    reason_keys[0]
                ]
            )

            insights.append(
                {
                    "type": "info",
                    "title": "Leading Return Reason",
                    "message": (
                        f"'{reason}' is the most common "
                        f"return reason, representing "
                        f"{float(top_reason['percentage']):.2f}% "
                        "of returns."
                    ),
                }
            )

    # --------------------------------------------------------
    # Revenue affected
    # --------------------------------------------------------

    revenue_affected = metrics[
        "revenue_affected"
    ]

    if revenue_affected > 0:

        insights.append(
            {
                "type": "critical"
                if return_rate >= 15
                else "warning",
                "title": "Revenue Impact",
                "message": (
                    f"Approximately "
                    f"{revenue_affected:,.2f} "
                    "in revenue is associated "
                    "with returned transactions."
                ),
            }
        )

    # --------------------------------------------------------
    # High-return product count
    # --------------------------------------------------------

    high_return_count = sum(
        1
        for product in product_returns
        if float(
            product.get(
                "return_rate",
                0,
            )
        ) >= 15
    )

    if high_return_count > 0:

        insights.append(
            {
                "type": "warning",
                "title": "Products Requiring Attention",
                "message": (
                    f"{high_return_count} product(s) "
                    "have return rates of 15% or higher. "
                    "Consider reviewing quality, pricing, "
                    "descriptions and customer expectations."
                ),
            }
        )

    return insights


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def analyze_returns(
    df,
):

    # --------------------------------------------------------
    # Prepare
    # --------------------------------------------------------

    df, columns = (
        prepare_returns_dataframe(df)
    )

    # --------------------------------------------------------
    # Identify returns
    # --------------------------------------------------------

    df = identify_return_records(
        df,
        columns,
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    metrics = calculate_return_metrics(
        df,
        columns,
    )

    # --------------------------------------------------------
    # Trend
    # --------------------------------------------------------

    trend_data = calculate_return_trend(
        df,
        columns,
    )

    # --------------------------------------------------------
    # Product analysis
    # --------------------------------------------------------

    product_returns = (
        calculate_product_returns(
            df,
            columns,
        )
    )

    classified_products = (
        classify_products_by_return(
            product_returns
        )
    )

    high_return_products = (
        get_high_return_products(
            product_returns
        )
    )

    risk_products = (
        calculate_return_risk_score(
            product_returns
        )
    )

    # --------------------------------------------------------
    # Region analysis
    # --------------------------------------------------------

    region_returns = (
        calculate_region_returns(
            df,
            columns,
        )
    )

    # --------------------------------------------------------
    # Reason analysis
    # --------------------------------------------------------

    reason_data = (
        calculate_return_reasons(
            df,
            columns,
        )
    )

    # --------------------------------------------------------
    # Customer analysis
    # --------------------------------------------------------

    customer_returns = (
        calculate_customer_returns(
            df,
            columns,
        )
    )

    # --------------------------------------------------------
    # Category analysis
    # --------------------------------------------------------

    category_returns = (
        calculate_category_returns(
            df,
            columns,
        )
    )

    # --------------------------------------------------------
    # Insights
    # --------------------------------------------------------

    insights = generate_return_insights(
        metrics,
        product_returns,
        region_returns,
        reason_data,
        category_returns,
    )

    # --------------------------------------------------------
    # Columns
    # --------------------------------------------------------

    detected_columns = {
        key: value
        for key, value in columns.items()
        if value is not None
    }

    # --------------------------------------------------------
    # Return complete analysis
    # --------------------------------------------------------

    return {
        "metrics": metrics,
        "trend_data": trend_data,
        "product_returns": classified_products,
        "high_return_products": high_return_products,
        "risk_products": risk_products[:50],
        "region_returns": region_returns,
        "reason_data": reason_data,
        "customer_returns": customer_returns,
        "category_returns": category_returns,
        "insights": insights,
        "columns": detected_columns,
    }
