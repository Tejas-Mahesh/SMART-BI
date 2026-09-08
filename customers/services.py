import pandas as pd
import numpy as np

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# ============================================================
# COLUMN DETECTION
# ============================================================

def find_column(df, possible_names):
    """
    Find a column using a list of possible column names.
    Matching is case-insensitive and ignores surrounding spaces.
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


def detect_customer_columns(df):
    """
    Detect the important columns required for customer analysis.
    """

    return {
        "customer_id": find_column(
            df,
            [
                "customer_id",
                "customerid",
                "customer id",
                "client_id",
                "clientid",
                "user_id",
                "userid",
                "buyer_id",
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
                "sales_value",
            ],
        ),

        "profit": find_column(
            df,
            [
                "profit",
                "profit_amount",
                "net_profit",
                "gross_profit",
            ],
        ),

        "quantity": find_column(
            df,
            [
                "quantity",
                "qty",
                "units",
                "units_sold",
            ],
        ),
    }


# ============================================================
# DATA PREPARATION
# ============================================================

def prepare_customer_dataframe(df):
    """
    Prepare the dataframe for customer analysis.
    """

    df = df.copy()

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    columns = detect_customer_columns(df)

    # Convert date
    if columns["date"]:
        df[columns["date"]] = pd.to_datetime(
            df[columns["date"]],
            errors="coerce",
            dayfirst=True,
        )

    # Convert numeric columns
    numeric_columns = [
        columns["revenue"],
        columns["profit"],
        columns["quantity"],
    ]

    for column in numeric_columns:

        if column:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # Remove rows without customer ID
    if columns["customer_id"]:
        df = df.dropna(
            subset=[columns["customer_id"]]
        )

    return df, columns


# ============================================================
# CUSTOMER BASE METRICS
# ============================================================

def calculate_customer_metrics(df, columns):

    customer_column = columns["customer_id"]
    order_column = columns["order_id"]
    revenue_column = columns["revenue"]
    date_column = columns["date"]

    if not customer_column:
        return {
            "total_customers": 0,
            "new_customers": 0,
            "repeat_customers": 0,
            "repeat_rate": 0,
            "average_customer_value": 0,
            "total_customer_revenue": 0,
            "active_customers": 0,
        }

    total_customers = int(
        df[customer_column].nunique()
    )

    if revenue_column:
        total_customer_revenue = float(
            df[revenue_column]
            .fillna(0)
            .sum()
        )
    else:
        total_customer_revenue = 0

    if total_customers > 0:
        average_customer_value = (
            total_customer_revenue
            / total_customers
        )
    else:
        average_customer_value = 0

    # Orders per customer
    if order_column:
        customer_orders = (
            df.groupby(customer_column)[order_column]
            .nunique()
        )
    else:
        customer_orders = (
            df.groupby(customer_column)
            .size()
        )

    repeat_customers = int(
        (customer_orders > 1).sum()
    )

    repeat_rate = (
        repeat_customers
        / total_customers
        * 100
        if total_customers
        else 0
    )

    # New customers based on first purchase
    if date_column:

        valid_dates = df.dropna(
            subset=[date_column]
        )

        if not valid_dates.empty:

            first_purchase = (
                valid_dates
                .groupby(customer_column)[date_column]
                .min()
            )

            first_purchase_counts = (
                first_purchase
                .dt.date
                .value_counts()
            )

            new_customers = int(
                first_purchase_counts.sum()
            )

        else:
            new_customers = 0

    else:
        new_customers = 0

    return {
        "total_customers": total_customers,
        "new_customers": new_customers,
        "repeat_customers": repeat_customers,
        "repeat_rate": round(
            repeat_rate,
            2,
        ),
        "average_customer_value": round(
            average_customer_value,
            2,
        ),
        "total_customer_revenue": round(
            total_customer_revenue,
            2,
        ),
        "active_customers": total_customers,
    }


# ============================================================
# CUSTOMER LEVEL DATA
# ============================================================

def build_customer_table(df, columns):

    customer_column = columns["customer_id"]
    order_column = columns["order_id"]
    date_column = columns["date"]
    revenue_column = columns["revenue"]
    profit_column = columns["profit"]
    quantity_column = columns["quantity"]

    if not customer_column:
        return pd.DataFrame()

    grouped = df.groupby(
        customer_column
    )

    customer_data = grouped.size().to_frame(
        name="record_count"
    )

    # Orders
    if order_column:
        customer_data["orders"] = (
            grouped[order_column]
            .nunique()
        )
    else:
        customer_data["orders"] = (
            customer_data["record_count"]
        )

    # Revenue
    if revenue_column:
        customer_data["revenue"] = (
            grouped[revenue_column]
            .sum()
            .fillna(0)
        )
    else:
        customer_data["revenue"] = 0

    # Profit
    if profit_column:
        customer_data["profit"] = (
            grouped[profit_column]
            .sum()
            .fillna(0)
        )
    else:
        customer_data["profit"] = 0

    # Quantity
    if quantity_column:
        customer_data["units"] = (
            grouped[quantity_column]
            .sum()
            .fillna(0)
        )
    else:
        customer_data["units"] = (
            customer_data["record_count"]
        )

    # First purchase
    if date_column:

        customer_data["first_purchase"] = (
            grouped[date_column]
            .min()
        )

        customer_data["last_purchase"] = (
            grouped[date_column]
            .max()
        )

    else:

        customer_data["first_purchase"] = pd.NaT
        customer_data["last_purchase"] = pd.NaT

    customer_data = customer_data.reset_index()

    # AOV
    customer_data["aov"] = np.where(
        customer_data["orders"] > 0,
        customer_data["revenue"]
        / customer_data["orders"],
        0,
    )

    return customer_data


# ============================================================
# RFM ANALYSIS
# ============================================================

def calculate_rfm(customer_table, analysis_date=None):

    if customer_table.empty:
        return customer_table

    rfm = customer_table.copy()

    if analysis_date is None:

        if "last_purchase" in rfm.columns:

            valid_dates = (
                rfm["last_purchase"]
                .dropna()
            )

            if not valid_dates.empty:

                analysis_date = (
                    valid_dates.max()
                    + pd.Timedelta(days=1)
                )

            else:
                analysis_date = pd.Timestamp.today()

        else:
            analysis_date = pd.Timestamp.today()

    analysis_date = pd.to_datetime(
        analysis_date
    )

    if "last_purchase" in rfm.columns:

        rfm["recency"] = (
            analysis_date
            - rfm["last_purchase"]
        ).dt.days

    else:

        rfm["recency"] = 0

    rfm["frequency"] = rfm["orders"]

    rfm["monetary"] = rfm["revenue"]

    rfm["recency"] = (
        rfm["recency"]
        .fillna(0)
        .clip(lower=0)
    )

    rfm["frequency"] = (
        rfm["frequency"]
        .fillna(0)
    )

    rfm["monetary"] = (
        rfm["monetary"]
        .fillna(0)
    )

    # RFM scores from 1 to 5
    if len(rfm) >= 2:

        rfm["r_score"] = pd.qcut(
            rfm["recency"],
            5,
            labels=False,
            duplicates="drop",
        )

        # Lower recency is better
        rfm["r_score"] = (
            rfm["r_score"]
            .max()
            - rfm["r_score"]
            + 1
        )

        rfm["f_score"] = pd.qcut(
            rfm["frequency"].rank(
                method="first"
            ),
            5,
            labels=False,
            duplicates="drop",
        ) + 1

        rfm["m_score"] = pd.qcut(
            rfm["monetary"].rank(
                method="first"
            ),
            5,
            labels=False,
            duplicates="drop",
        ) + 1

    else:

        rfm["r_score"] = 3
        rfm["f_score"] = 3
        rfm["m_score"] = 3

    rfm["r_score"] = (
        pd.to_numeric(
            rfm["r_score"],
            errors="coerce",
        )
        .fillna(1)
        .astype(int)
    )

    rfm["f_score"] = (
        pd.to_numeric(
            rfm["f_score"],
            errors="coerce",
        )
        .fillna(1)
        .astype(int)
    )

    rfm["m_score"] = (
        pd.to_numeric(
            rfm["m_score"],
            errors="coerce",
        )
        .fillna(1)
        .astype(int)
    )

    rfm["rfm_score"] = (
        rfm["r_score"].astype(str)
        + rfm["f_score"].astype(str)
        + rfm["m_score"].astype(str)
    )

    return rfm


# ============================================================
# CUSTOMER SEGMENTATION
# ============================================================

def assign_customer_segments(rfm):

    if rfm.empty:
        return rfm

    result = rfm.copy()

    def classify(row):

        r = row["r_score"]
        f = row["f_score"]
        m = row["m_score"]

        # High-value customers
        if r >= 4 and f >= 4 and m >= 4:
            return "High Value"

        # Loyal customers
        if r >= 4 and f >= 4:
            return "Loyal"

        # New / promising
        if r >= 4 and f <= 2:
            return "New Customers"

        # At risk
        if r <= 2 and f >= 3:
            return "At Risk"

        # Low value
        if r <= 2 and f <= 2 and m <= 2:
            return "Low Value"

        return "Potential"

    result["segment"] = result.apply(
        classify,
        axis=1,
    )

    return result


# ============================================================
# K-MEANS CUSTOMER CLUSTERING
# ============================================================

def perform_kmeans_clustering(
    customer_table,
    number_of_clusters=4,
):

    if customer_table.empty:
        return customer_table

    result = customer_table.copy()

    features = [
        "recency",
        "frequency",
        "monetary",
    ]

    for feature in features:

        if feature not in result.columns:
            result[feature] = 0

    model_data = result[
        features
    ].copy()

    model_data = model_data.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    model_data = model_data.fillna(0)

    if len(result) < 2:
        result["cluster"] = 0
        return result

    number_of_clusters = min(
        number_of_clusters,
        len(result),
    )

    if number_of_clusters < 2:
        result["cluster"] = 0
        return result

    scaler = StandardScaler()

    scaled_data = scaler.fit_transform(
        model_data
    )

    model = KMeans(
        n_clusters=number_of_clusters,
        random_state=42,
        n_init=10,
    )

    result["cluster"] = model.fit_predict(
        scaled_data
    )

    return result


# ============================================================
# SEGMENT SUMMARY
# ============================================================

def calculate_segment_summary(customer_data):

    if customer_data.empty:
        return []

    grouped = (
        customer_data
        .groupby("segment")
    )

    results = []

    for segment, group in grouped:

        results.append({
            "segment": str(segment),
            "customers": int(len(group)),
            "revenue": round(
                float(
                    group["monetary"]
                    .sum()
                ),
                2,
            ),
            "orders": int(
                group["frequency"]
                .sum()
            ),
            "average_value": round(
                float(
                    group["monetary"]
                    .mean()
                ),
                2,
            ),
        })

    results.sort(
        key=lambda item: item["revenue"],
        reverse=True,
    )

    total_customers = len(
        customer_data
    )

    for item in results:

        item["percentage"] = round(
            (
                item["customers"]
                / total_customers
                * 100
            ),
            2,
        )

    return results


# ============================================================
# RFM DISTRIBUTION
# ============================================================

def calculate_rfm_distribution(customer_data):

    if customer_data.empty:
        return {
            "recency": [],
            "frequency": [],
            "monetary": [],
        }

    return {
        "recency": [
            round(float(value), 2)
            for value in customer_data[
                "recency"
            ].tolist()
        ],

        "frequency": [
            round(float(value), 2)
            for value in customer_data[
                "frequency"
            ].tolist()
        ],

        "monetary": [
            round(float(value), 2)
            for value in customer_data[
                "monetary"
            ].tolist()
        ],
    }


# ============================================================
# TOP CUSTOMERS
# ============================================================

def calculate_top_customers(
    customer_data,
    limit=10,
):

    if customer_data.empty:
        return []

    top = (
        customer_data
        .sort_values(
            "monetary",
            ascending=False,
        )
        .head(limit)
    )

    results = []

    for _, row in top.iterrows():

        results.append({
            "customer": str(
                row["customer_id"]
            ),
            "revenue": round(
                float(row["monetary"]),
                2,
            ),
            "orders": int(
                row["frequency"]
            ),
            "recency": int(
                row["recency"]
            ),
            "segment": str(
                row["segment"]
            ),
        })

    return results


# ============================================================
# AT-RISK CUSTOMERS
# ============================================================

def calculate_at_risk_customers(
    customer_data,
    limit=10,
):

    if customer_data.empty:
        return []

    at_risk = customer_data[
        customer_data["segment"]
        == "At Risk"
    ]

    at_risk = (
        at_risk
        .sort_values(
            "monetary",
            ascending=False,
        )
        .head(limit)
    )

    results = []

    for _, row in at_risk.iterrows():

        results.append({
            "customer": str(
                row["customer_id"]
            ),
            "revenue": round(
                float(row["monetary"]),
                2,
            ),
            "orders": int(
                row["frequency"]
            ),
            "recency": int(
                row["recency"]
            ),
        })

    return results


# ============================================================
# CUSTOMER INSIGHTS
# ============================================================

def generate_customer_insights(
    metrics,
    segment_summary,
    customer_data,
):

    insights = []

    # Repeat customer insight
    if metrics["repeat_rate"] >= 50:

        insights.append({
            "type": "positive",
            "title": "Strong customer loyalty",
            "message": (
                f"{metrics['repeat_rate']}% of customers "
                "are repeat customers."
            ),
        })

    else:

        insights.append({
            "type": "warning",
            "title": "Repeat purchases need attention",
            "message": (
                f"Only {metrics['repeat_rate']}% of customers "
                "are repeat customers. Consider retention campaigns."
            ),
        })

    # Highest-value segment
    if segment_summary:

        top_segment = segment_summary[0]

        insights.append({
            "type": "positive",
            "title": "Highest revenue segment",
            "message": (
                f"{top_segment['segment']} customers generated "
                f"{top_segment['revenue']:,.2f} in revenue."
            ),
        })

    # At-risk customers
    if not customer_data.empty:

        at_risk_count = int(
            (
                customer_data["segment"]
                == "At Risk"
            ).sum()
        )

        if at_risk_count > 0:

            insights.append({
                "type": "warning",
                "title": "Customers at risk",
                "message": (
                    f"{at_risk_count} customers are classified "
                    "as At Risk and may require retention campaigns."
                ),
            })

    # High-value customers
    if not customer_data.empty:

        high_value_count = int(
            (
                customer_data["segment"]
                == "High Value"
            ).sum()
        )

        if high_value_count > 0:

            insights.append({
                "type": "positive",
                "title": "High-value customer base",
                "message": (
                    f"{high_value_count} customers are classified "
                    "as High Value."
                ),
            })

    return insights


# ============================================================
# COMPLETE CUSTOMER INTELLIGENCE ANALYSIS
# ============================================================

def analyze_customer_intelligence(df):

    # Prepare data
    df, columns = prepare_customer_dataframe(
        df
    )

    # Base metrics
    metrics = calculate_customer_metrics(
        df,
        columns,
    )

    # Customer-level table
    customer_table = build_customer_table(
        df,
        columns,
    )

    # RFM
    customer_data = calculate_rfm(
        customer_table
    )

    # Segment customers
    customer_data = assign_customer_segments(
        customer_data
    )

    # K-Means
    customer_data = perform_kmeans_clustering(
        customer_data,
        number_of_clusters=4,
    )

    # Segment summary
    segment_summary = calculate_segment_summary(
        customer_data
    )

    # RFM distribution
    rfm_distribution = calculate_rfm_distribution(
        customer_data
    )

    # Top customers
    top_customers = calculate_top_customers(
        customer_data
    )

    # At-risk customers
    at_risk_customers = calculate_at_risk_customers(
        customer_data
    )

    # Insights
    insights = generate_customer_insights(
        metrics,
        segment_summary,
        customer_data,
    )

    return {
        "columns": columns,
        "metrics": metrics,
        "customer_data": customer_data,
        "segment_summary": segment_summary,
        "rfm_distribution": rfm_distribution,
        "top_customers": top_customers,
        "at_risk_customers": at_risk_customers,
        "insights": insights,
    }