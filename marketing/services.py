import pandas as pd
import numpy as np


# ============================================================
# COLUMN DETECTION
# ============================================================

def find_column(df, possible_names):
    """
    Find the first matching column from a list of possible
    column names.
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


def detect_marketing_columns(df):
    """
    Detect marketing-related columns from the uploaded dataset.
    """

    return {

        "date": find_column(
            df,
            [
                "date",
                "campaign_date",
                "campaign date",
                "marketing_date",
                "marketing date",
                "transaction_date",
                "transaction date",
                "order_date",
                "order date",
                "created_at",
            ],
        ),

        "campaign": find_column(
            df,
            [
                "campaign",
                "campaign_name",
                "campaign name",
                "campaign_id",
                "campaign id",
                "campaign_type",
                "campaign type",
            ],
        ),

        "channel": find_column(
            df,
            [
                "channel",
                "marketing_channel",
                "marketing channel",
                "source",
                "traffic_source",
                "traffic source",
                "medium",
                "platform",
            ],
        ),

        "spend": find_column(
            df,
            [
                "marketing_spend",
                "marketing spend",
                "marketing_cost",
                "marketing cost",
                "ad_spend",
                "ad spend",
                "advertising_spend",
                "advertising spend",
                "advertising_cost",
                "advertising cost",
                "campaign_spend",
                "campaign spend",
                "spend",
                "ad_cost",
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
                "marketing_revenue",
                "marketing revenue",
                "attributed_revenue",
                "attributed revenue",
                "conversion_revenue",
                "conversion revenue",
                "amount",
                "total_amount",
                "order_value",
            ],
        ),

        "orders": find_column(
            df,
            [
                "orders",
                "order_count",
                "order count",
                "total_orders",
                "total orders",
                "conversions",
                "conversion",
                "conversion_count",
                "conversion count",
            ],
        ),

        "customers": find_column(
            df,
            [
                "customer_id",
                "customerid",
                "customer id",
                "customers",
                "customer_count",
                "customer count",
                "unique_customers",
                "unique customers",
                "client_id",
                "client id",
            ],
        ),

        "clicks": find_column(
            df,
            [
                "clicks",
                "click",
                "total_clicks",
                "total clicks",
                "ad_clicks",
                "ad clicks",
            ],
        ),

        "impressions": find_column(
            df,
            [
                "impressions",
                "impression",
                "total_impressions",
                "total impressions",
                "ad_impressions",
                "ad impressions",
            ],
        ),

        "leads": find_column(
            df,
            [
                "leads",
                "lead",
                "total_leads",
                "total leads",
                "lead_count",
                "lead count",
            ],
        ),

        "conversions": find_column(
            df,
            [
                "conversions",
                "conversion",
                "total_conversions",
                "total conversions",
                "conversion_count",
                "conversion count",
                "converted_customers",
                "converted customers",
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
    }


# ============================================================
# DATA PREPARATION
# ============================================================

def prepare_marketing_dataframe(df):

    df = df.copy()

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    columns = detect_marketing_columns(df)

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

    numeric_keys = [
        "spend",
        "revenue",
        "orders",
        "clicks",
        "impressions",
        "leads",
        "conversions",
        "profit",
    ]

    for key in numeric_keys:

        column = columns[key]

        if column:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    return df, columns


# ============================================================
# MARKETING METRICS
# ============================================================

def calculate_marketing_metrics(
    df,
    columns,
):

    spend_column = columns["spend"]
    revenue_column = columns["revenue"]
    orders_column = columns["orders"]
    customer_column = columns["customers"]
    clicks_column = columns["clicks"]
    impressions_column = columns["impressions"]
    leads_column = columns["leads"]
    conversions_column = columns["conversions"]
    profit_column = columns["profit"]

    # --------------------------------------------------------
    # Spend
    # --------------------------------------------------------

    if spend_column:

        total_spend = float(
            df[spend_column]
            .fillna(0)
            .sum()
        )

    else:

        total_spend = 0

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    if revenue_column:

        total_revenue = float(
            df[revenue_column]
            .fillna(0)
            .sum()
        )

    else:

        total_revenue = 0

    # --------------------------------------------------------
    # Orders / conversions
    # --------------------------------------------------------

    if orders_column:

        total_orders = int(
            df[orders_column]
            .fillna(0)
            .sum()
        )

    elif conversions_column:

        total_orders = int(
            df[conversions_column]
            .fillna(0)
            .sum()
        )

    else:

        total_orders = len(df)

    # --------------------------------------------------------
    # Customers
    # --------------------------------------------------------

    if customer_column:

        if (
            pd.api.types.is_numeric_dtype(
                df[customer_column]
            )
        ):

            total_customers = int(
                df[customer_column]
                .nunique()
            )

        else:

            total_customers = int(
                df[customer_column]
                .nunique()
            )

    else:

        total_customers = 0

    # --------------------------------------------------------
    # Clicks
    # --------------------------------------------------------

    if clicks_column:

        total_clicks = int(
            df[clicks_column]
            .fillna(0)
            .sum()
        )

    else:

        total_clicks = 0

    # --------------------------------------------------------
    # Impressions
    # --------------------------------------------------------

    if impressions_column:

        total_impressions = int(
            df[impressions_column]
            .fillna(0)
            .sum()
        )

    else:

        total_impressions = 0

    # --------------------------------------------------------
    # Leads
    # --------------------------------------------------------

    if leads_column:

        total_leads = int(
            df[leads_column]
            .fillna(0)
            .sum()
        )

    else:

        total_leads = 0

    # --------------------------------------------------------
    # Conversions
    # --------------------------------------------------------

    if conversions_column:

        total_conversions = int(
            df[conversions_column]
            .fillna(0)
            .sum()
        )

    else:

        total_conversions = total_orders

    # --------------------------------------------------------
    # Profit
    # --------------------------------------------------------

    if profit_column:

        total_profit = float(
            df[profit_column]
            .fillna(0)
            .sum()
        )

    else:

        total_profit = (
            total_revenue
            -
            total_spend
        )

    # --------------------------------------------------------
    # ROI
    # --------------------------------------------------------

    if total_spend > 0:

        roi = (
            (
                total_revenue
                -
                total_spend
            )
            /
            total_spend
        ) * 100

    else:

        roi = 0

    # --------------------------------------------------------
    # ROAS
    # --------------------------------------------------------

    if total_spend > 0:

        roas = (
            total_revenue
            /
            total_spend
        )

    else:

        roas = 0

    # --------------------------------------------------------
    # CAC
    # --------------------------------------------------------

    if total_customers > 0:

        cac = (
            total_spend
            /
            total_customers
        )

    elif total_conversions > 0:

        cac = (
            total_spend
            /
            total_conversions
        )

    else:

        cac = 0

    # --------------------------------------------------------
    # Cost per click
    # --------------------------------------------------------

    if total_clicks > 0:

        cpc = (
            total_spend
            /
            total_clicks
        )

    else:

        cpc = 0

    # --------------------------------------------------------
    # Conversion rate
    # --------------------------------------------------------

    if total_clicks > 0:

        conversion_rate = (
            total_conversions
            /
            total_clicks
        ) * 100

    elif total_leads > 0:

        conversion_rate = (
            total_conversions
            /
            total_leads
        ) * 100

    else:

        conversion_rate = 0

    # --------------------------------------------------------
    # Profit margin
    # --------------------------------------------------------

    if total_revenue > 0:

        profit_margin = (
            total_profit
            /
            total_revenue
        ) * 100

    else:

        profit_margin = 0

    # --------------------------------------------------------
    # CTR
    # --------------------------------------------------------

    if total_impressions > 0:

        ctr = (
            total_clicks
            /
            total_impressions
        ) * 100

    else:

        ctr = 0

    return {

        "total_spend":
            round(
                total_spend,
                2,
            ),

        "total_revenue":
            round(
                total_revenue,
                2,
            ),

        "total_orders":
            total_orders,

        "total_customers":
            total_customers,

        "total_clicks":
            total_clicks,

        "total_impressions":
            total_impressions,

        "total_leads":
            total_leads,

        "total_conversions":
            total_conversions,

        "total_profit":
            round(
                total_profit,
                2,
            ),

        "roi":
            round(
                roi,
                2,
            ),

        "roas":
            round(
                roas,
                2,
            ),

        "cac":
            round(
                cac,
                2,
            ),

        "cpc":
            round(
                cpc,
                2,
            ),

        "conversion_rate":
            round(
                conversion_rate,
                2,
            ),

        "profit_margin":
            round(
                profit_margin,
                2,
            ),

        "ctr":
            round(
                ctr,
                2,
            ),

    }


# ============================================================
# CHANNEL ANALYSIS
# ============================================================

def calculate_channel_analysis(
    df,
    columns,
):

    channel_column = columns["channel"]

    if not channel_column:

        return []

    grouped = df.groupby(
        channel_column,
        dropna=False,
    )

    results = []

    for channel, group in grouped:

        channel_name = (
            "Unknown"
            if pd.isna(channel)
            else str(channel).strip()
        )

        if not channel_name:

            channel_name = "Unknown"

        # ----------------------------------------------------
        # Spend
        # ----------------------------------------------------

        if columns["spend"]:

            spend = float(
                group[
                    columns["spend"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            spend = 0

        # ----------------------------------------------------
        # Revenue
        # ----------------------------------------------------

        if columns["revenue"]:

            revenue = float(
                group[
                    columns["revenue"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            revenue = 0

        # ----------------------------------------------------
        # Profit
        # ----------------------------------------------------

        if columns["profit"]:

            profit = float(
                group[
                    columns["profit"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            profit = (
                revenue
                -
                spend
            )

        # ----------------------------------------------------
        # Orders
        # ----------------------------------------------------

        if columns["orders"]:

            orders = int(
                group[
                    columns["orders"]
                ]
                .fillna(0)
                .sum()
            )

        elif columns["conversions"]:

            orders = int(
                group[
                    columns["conversions"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            orders = len(group)

        # ----------------------------------------------------
        # Customers
        # ----------------------------------------------------

        if columns["customers"]:

            customers = int(
                group[
                    columns["customers"]
                ]
                .nunique()
            )

        else:

            customers = 0

        # ----------------------------------------------------
        # Clicks
        # ----------------------------------------------------

        if columns["clicks"]:

            clicks = int(
                group[
                    columns["clicks"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            clicks = 0

        # ----------------------------------------------------
        # Impressions
        # ----------------------------------------------------

        if columns["impressions"]:

            impressions = int(
                group[
                    columns["impressions"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            impressions = 0

        # ----------------------------------------------------
        # Leads
        # ----------------------------------------------------

        if columns["leads"]:

            leads = int(
                group[
                    columns["leads"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            leads = 0

        # ----------------------------------------------------
        # Conversions
        # ----------------------------------------------------

        if columns["conversions"]:

            conversions = int(
                group[
                    columns["conversions"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            conversions = orders

        # ----------------------------------------------------
        # ROAS
        # ----------------------------------------------------

        roas = (
            revenue / spend
            if spend > 0
            else 0
        )

        # ----------------------------------------------------
        # ROI
        # ----------------------------------------------------

        roi = (
            (
                revenue - spend
            )
            /
            spend
            *
            100
            if spend > 0
            else 0
        )

        # ----------------------------------------------------
        # CAC
        # ----------------------------------------------------

        if customers > 0:

            cac = (
                spend
                /
                customers
            )

        elif conversions > 0:

            cac = (
                spend
                /
                conversions
            )

        else:

            cac = 0

        # ----------------------------------------------------
        # Conversion Rate
        # ----------------------------------------------------

        if clicks > 0:

            conversion_rate = (
                conversions
                /
                clicks
                *
                100
            )

        elif leads > 0:

            conversion_rate = (
                conversions
                /
                leads
                *
                100
            )

        else:

            conversion_rate = 0

        # ----------------------------------------------------
        # CTR
        # ----------------------------------------------------

        if impressions > 0:

            ctr = (
                clicks
                /
                impressions
                *
                100
            )

        else:

            ctr = 0

        results.append({

            "channel":
                channel_name,

            "spend":
                round(
                    spend,
                    2,
                ),

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

            "orders":
                orders,

            "customers":
                customers,

            "clicks":
                clicks,

            "impressions":
                impressions,

            "leads":
                leads,

            "conversions":
                conversions,

            "roas":
                round(
                    roas,
                    2,
                ),

            "roi":
                round(
                    roi,
                    2,
                ),

            "cac":
                round(
                    cac,
                    2,
                ),

            "conversion_rate":
                round(
                    conversion_rate,
                    2,
                ),

            "ctr":
                round(
                    ctr,
                    2,
                ),

        })

    results.sort(
        key=lambda item:
            item["revenue"],
        reverse=True,
    )

    return results


# ============================================================
# CAMPAIGN ANALYSIS
# ============================================================

def calculate_campaign_analysis(
    df,
    columns,
):

    campaign_column = columns["campaign"]

    if not campaign_column:

        return []

    grouped = df.groupby(
        campaign_column,
        dropna=False,
    )

    results = []

    for campaign, group in grouped:

        campaign_name = (
            "Unknown"
            if pd.isna(campaign)
            else str(campaign).strip()
        )

        if not campaign_name:

            campaign_name = "Unknown"

        # Spend

        if columns["spend"]:

            spend = float(
                group[
                    columns["spend"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            spend = 0

        # Revenue

        if columns["revenue"]:

            revenue = float(
                group[
                    columns["revenue"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            revenue = 0

        # Profit

        if columns["profit"]:

            profit = float(
                group[
                    columns["profit"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            profit = (
                revenue
                -
                spend
            )

        # Orders

        if columns["orders"]:

            orders = int(
                group[
                    columns["orders"]
                ]
                .fillna(0)
                .sum()
            )

        elif columns["conversions"]:

            orders = int(
                group[
                    columns["conversions"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            orders = len(group)

        # Customers

        if columns["customers"]:

            customers = int(
                group[
                    columns["customers"]
                ]
                .nunique()
            )

        else:

            customers = 0

        # Clicks

        if columns["clicks"]:

            clicks = int(
                group[
                    columns["clicks"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            clicks = 0

        # Impressions

        if columns["impressions"]:

            impressions = int(
                group[
                    columns["impressions"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            impressions = 0

        # Leads

        if columns["leads"]:

            leads = int(
                group[
                    columns["leads"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            leads = 0

        # Conversions

        if columns["conversions"]:

            conversions = int(
                group[
                    columns["conversions"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            conversions = orders

        # ROI

        roi = (
            (
                revenue - spend
            )
            /
            spend
            *
            100
            if spend > 0
            else 0
        )

        # ROAS

        roas = (
            revenue / spend
            if spend > 0
            else 0
        )

        # CAC

        if customers > 0:

            cac = (
                spend
                /
                customers
            )

        elif conversions > 0:

            cac = (
                spend
                /
                conversions
            )

        else:

            cac = 0

        # Conversion rate

        if clicks > 0:

            conversion_rate = (
                conversions
                /
                clicks
                *
                100
            )

        elif leads > 0:

            conversion_rate = (
                conversions
                /
                leads
                *
                100
            )

        else:

            conversion_rate = 0

        # CTR

        if impressions > 0:

            ctr = (
                clicks
                /
                impressions
                *
                100
            )

        else:

            ctr = 0

        results.append({

            "campaign":
                campaign_name,

            "spend":
                round(
                    spend,
                    2,
                ),

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

            "orders":
                orders,

            "customers":
                customers,

            "clicks":
                clicks,

            "impressions":
                impressions,

            "leads":
                leads,

            "conversions":
                conversions,

            "roi":
                round(
                    roi,
                    2,
                ),

            "roas":
                round(
                    roas,
                    2,
                ),

            "cac":
                round(
                    cac,
                    2,
                ),

            "conversion_rate":
                round(
                    conversion_rate,
                    2,
                ),

            "ctr":
                round(
                    ctr,
                    2,
                ),

        })

    results.sort(
        key=lambda item:
            item["revenue"],
        reverse=True,
    )

    return results


# ============================================================
# MARKETING TREND
# ============================================================

def calculate_marketing_trend(
    df,
    columns,
):

    date_column = columns["date"]

    if not date_column:

        return []

    working = df.copy()

    working = working.dropna(
        subset=[date_column]
    )

    if working.empty:

        return []

    working["period"] = (
        working[
            date_column
        ]
        .dt.to_period("M")
        .astype(str)
    )

    grouped = working.groupby(
        "period"
    )

    results = []

    for period, group in grouped:

        if columns["spend"]:

            spend = float(
                group[
                    columns["spend"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            spend = 0

        if columns["revenue"]:

            revenue = float(
                group[
                    columns["revenue"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            revenue = 0

        if columns["profit"]:

            profit = float(
                group[
                    columns["profit"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            profit = (
                revenue
                -
                spend
            )

        if columns["conversions"]:

            conversions = int(
                group[
                    columns["conversions"]
                ]
                .fillna(0)
                .sum()
            )

        elif columns["orders"]:

            conversions = int(
                group[
                    columns["orders"]
                ]
                .fillna(0)
                .sum()
            )

        else:

            conversions = len(group)

        roas = (
            revenue / spend
            if spend > 0
            else 0
        )

        roi = (
            (
                revenue - spend
            )
            /
            spend
            *
            100
            if spend > 0
            else 0
        )

        results.append({

            "period":
                period,

            "spend":
                round(
                    spend,
                    2,
                ),

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

            "conversions":
                conversions,

            "roas":
                round(
                    roas,
                    2,
                ),

            "roi":
                round(
                    roi,
                    2,
                ),

        })

    return results


# ============================================================
# CAMPAIGN CLASSIFICATION
# ============================================================

def classify_campaigns(
    campaign_data,
):

    if not campaign_data:

        return []

    roas_values = [
        item["roas"]
        for item in campaign_data
    ]

    roi_values = [
        item["roi"]
        for item in campaign_data
    ]

    revenue_values = [
        item["revenue"]
        for item in campaign_data
    ]

    roas_median = float(
        np.median(
            roas_values
        )
    )

    roi_median = float(
        np.median(
            roi_values
        )
    )

    revenue_median = float(
        np.median(
            revenue_values
        )
    )

    results = []

    for item in campaign_data:

        roas = item["roas"]

        roi = item["roi"]

        revenue = item["revenue"]

        if (
            roas >= roas_median
            and roi >= roi_median
            and revenue >= revenue_median
        ):

            category = "High Performer"

        elif (
            roas < 1
            or roi < 0
        ):

            category = "Underperforming"

        elif (
            roas >= roas_median
            and revenue < revenue_median
        ):

            category = "Efficient / Low Scale"

        else:

            category = "Average"

        enriched = dict(item)

        enriched["classification"] = (
            category
        )

        results.append(enriched)

    return results


# ============================================================
# CHANNEL CLASSIFICATION
# ============================================================

def classify_channels(
    channel_data,
):

    if not channel_data:

        return []

    roas_values = [
        item["roas"]
        for item in channel_data
    ]

    roi_values = [
        item["roi"]
        for item in channel_data
    ]

    roas_median = float(
        np.median(
            roas_values
        )
    )

    roi_median = float(
        np.median(
            roi_values
        )
    )

    results = []

    for item in channel_data:

        enriched = dict(item)

        if (
            item["roas"] >= roas_median
            and item["roi"] >= roi_median
        ):

            enriched["classification"] = (
                "High Performing"
            )

        elif (
            item["roas"] < 1
            or item["roi"] < 0
        ):

            enriched["classification"] = (
                "Needs Attention"
            )

        else:

            enriched["classification"] = (
                "Stable"
            )

        results.append(enriched)

    return results


# ============================================================
# TOP MARKETING CHANNELS
# ============================================================

def get_top_channels(
    channel_data,
    metric="revenue",
    limit=10,
):

    if not channel_data:

        return []

    valid = sorted(
        channel_data,
        key=lambda item:
            item.get(
                metric,
                0,
            ),
        reverse=True,
    )

    return valid[:limit]


# ============================================================
# TOP CAMPAIGNS
# ============================================================

def get_top_campaigns(
    campaign_data,
    metric="revenue",
    limit=10,
):

    if not campaign_data:

        return []

    valid = sorted(
        campaign_data,
        key=lambda item:
            item.get(
                metric,
                0,
            ),
        reverse=True,
    )

    return valid[:limit]


# ============================================================
# MARKETING INSIGHTS
# ============================================================

def generate_marketing_insights(
    metrics,
    channel_data,
    campaign_data,
):

    insights = []

    # --------------------------------------------------------
    # Overall ROAS
    # --------------------------------------------------------

    if metrics["roas"] >= 4:

        insights.append({

            "type": "positive",

            "title": "Strong marketing efficiency",

            "message": (
                f"Overall ROAS is "
                f"{metrics['roas']:.2f}x, indicating "
                "strong revenue generated relative "
                "to marketing spend."
            ),

        })

    elif metrics["roas"] < 1:

        insights.append({

            "type": "warning",

            "title": "Marketing spend is inefficient",

            "message": (
                f"Overall ROAS is only "
                f"{metrics['roas']:.2f}x. "
                "Marketing revenue is below the "
                "amount being spent."
            ),

        })

    else:

        insights.append({

            "type": "opportunity",

            "title": "Marketing efficiency has room to grow",

            "message": (
                f"Overall ROAS is "
                f"{metrics['roas']:.2f}x. "
                "Review campaign allocation to "
                "identify opportunities for improvement."
            ),

        })

    # --------------------------------------------------------
    # Best channel
    # --------------------------------------------------------

    if channel_data:

        best_channel = max(
            channel_data,
            key=lambda item:
                item["roas"],
        )

        insights.append({

            "type": "positive",

            "title": "Best-performing channel",

            "message": (
                f"{best_channel['channel']} has the "
                f"highest ROAS at "
                f"{best_channel['roas']:.2f}x."
            ),

        })

        # ----------------------------------------------------
        # Worst channel
        # ----------------------------------------------------

        worst_channel = min(
            channel_data,
            key=lambda item:
                item["roas"],
        )

        if (
            worst_channel["roas"] < 1
        ):

            insights.append({

                "type": "warning",

                "title": "Channel requiring attention",

                "message": (
                    f"{worst_channel['channel']} has a "
                    f"ROAS of "
                    f"{worst_channel['roas']:.2f}x. "
                    "Review targeting, creative and "
                    "budget allocation."
                ),

            })

    # --------------------------------------------------------
    # Best campaign
    # --------------------------------------------------------

    if campaign_data:

        best_campaign = max(
            campaign_data,
            key=lambda item:
                item["roi"],
        )

        insights.append({

            "type": "positive",

            "title": "Highest ROI campaign",

            "message": (
                f"{best_campaign['campaign']} generated "
                f"{best_campaign['roi']:.2f}% ROI."
            ),

        })

        # ----------------------------------------------------
        # Underperforming campaigns
        # ----------------------------------------------------

        underperforming = [

            item
            for item in campaign_data
            if item["roas"] < 1
            or item["roi"] < 0

        ]

        if underperforming:

            insights.append({

                "type": "warning",

                "title": "Underperforming campaigns detected",

                "message": (
                    f"{len(underperforming)} campaign(s) "
                    "have negative ROI or ROAS below 1x. "
                    "Consider optimizing or reallocating "
                    "their budgets."
                ),

            })

    # --------------------------------------------------------
    # CAC
    # --------------------------------------------------------

    if metrics["cac"] > 0:

        insights.append({

            "type": "opportunity",

            "title": "Customer acquisition cost",

            "message": (
                f"Estimated CAC is "
                f"₹{metrics['cac']:,.2f}. "
                "Compare acquisition cost against "
                "customer value before increasing spend."
            ),

        })

    # --------------------------------------------------------
    # Conversion
    # --------------------------------------------------------

    if metrics["conversion_rate"] > 0:

        if (
            metrics["conversion_rate"] < 2
        ):

            insights.append({

                "type": "warning",

                "title": "Low conversion efficiency",

                "message": (
                    f"Marketing conversion rate is "
                    f"{metrics['conversion_rate']:.2f}%. "
                    "Review landing pages, targeting "
                    "and campaign messaging."
                ),

            })

        elif (
            metrics["conversion_rate"] >= 5
        ):

            insights.append({

                "type": "positive",

                "title": "Healthy conversion rate",

                "message": (
                    f"Marketing conversion rate is "
                    f"{metrics['conversion_rate']:.2f}%."
                ),

            })

    return insights


# ============================================================
# COMPLETE MARKETING ANALYSIS
# ============================================================

def analyze_marketing_intelligence(df):

    # --------------------------------------------------------
    # Prepare dataframe
    # --------------------------------------------------------

    df, columns = (
        prepare_marketing_dataframe(
            df
        )
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    metrics = (
        calculate_marketing_metrics(
            df,
            columns,
        )
    )

    # --------------------------------------------------------
    # Channels
    # --------------------------------------------------------

    channel_data = (
        calculate_channel_analysis(
            df,
            columns,
        )
    )

    # --------------------------------------------------------
    # Campaigns
    # --------------------------------------------------------

    campaign_data = (
        calculate_campaign_analysis(
            df,
            columns,
        )
    )

    # --------------------------------------------------------
    # Trend
    # --------------------------------------------------------

    trend_data = (
        calculate_marketing_trend(
            df,
            columns,
        )
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    classified_campaigns = (
        classify_campaigns(
            campaign_data
        )
    )

    classified_channels = (
        classify_channels(
            channel_data
        )
    )

    # --------------------------------------------------------
    # Top channels
    # --------------------------------------------------------

    top_revenue_channels = (
        get_top_channels(
            classified_channels,
            "revenue",
            10,
        )
    )

    top_roas_channels = (
        get_top_channels(
            classified_channels,
            "roas",
            10,
        )
    )

    # --------------------------------------------------------
    # Top campaigns
    # --------------------------------------------------------

    top_revenue_campaigns = (
        get_top_campaigns(
            classified_campaigns,
            "revenue",
            10,
        )
    )

    top_roi_campaigns = (
        get_top_campaigns(
            classified_campaigns,
            "roi",
            10,
        )
    )

    # --------------------------------------------------------
    # Insights
    # --------------------------------------------------------

    insights = (
        generate_marketing_insights(
            metrics,
            classified_channels,
            classified_campaigns,
        )
    )

    return {

        "columns":
            columns,

        "metrics":
            metrics,

        "channel_data":
            classified_channels,

        "campaign_data":
            classified_campaigns,

        "trend_data":
            trend_data,

        "top_revenue_channels":
            top_revenue_channels,

        "top_roas_channels":
            top_roas_channels,

        "top_revenue_campaigns":
            top_revenue_campaigns,

        "top_roi_campaigns":
            top_roi_campaigns,

        "insights":
            insights,

    }