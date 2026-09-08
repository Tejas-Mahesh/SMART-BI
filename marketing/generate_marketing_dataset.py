
import random
from datetime import datetime

import numpy as np
import pandas as pd


# ============================================================
# SMART BI
# MARKETING DATASET GENERATOR
# ============================================================

random.seed(42)
np.random.seed(42)


# ============================================================
# CONFIGURATION
# ============================================================

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

OUTPUT_FILE = "marketing_dataset.csv"


# ============================================================
# CAMPAIGN CONFIGURATION
# ============================================================

CAMPAIGNS = [
    {
        "campaign": "Google Search - Brand",
        "channel": "Google Ads",
        "base_spend": 18000,
        "ctr": 0.055,
        "conversion_rate": 0.095,
        "revenue_per_conversion": 420,
    },
    {
        "campaign": "Google Search - Generic",
        "channel": "Google Ads",
        "base_spend": 24000,
        "ctr": 0.035,
        "conversion_rate": 0.060,
        "revenue_per_conversion": 360,
    },
    {
        "campaign": "Google Shopping",
        "channel": "Google Ads",
        "base_spend": 21000,
        "ctr": 0.042,
        "conversion_rate": 0.072,
        "revenue_per_conversion": 390,
    },
    {
        "campaign": "Facebook Retargeting",
        "channel": "Facebook",
        "base_spend": 14500,
        "ctr": 0.031,
        "conversion_rate": 0.075,
        "revenue_per_conversion": 340,
    },
    {
        "campaign": "Facebook Prospecting",
        "channel": "Facebook",
        "base_spend": 19000,
        "ctr": 0.021,
        "conversion_rate": 0.042,
        "revenue_per_conversion": 310,
    },
    {
        "campaign": "Instagram Reels",
        "channel": "Instagram",
        "base_spend": 12500,
        "ctr": 0.028,
        "conversion_rate": 0.048,
        "revenue_per_conversion": 325,
    },
    {
        "campaign": "Instagram Influencer",
        "channel": "Instagram",
        "base_spend": 16000,
        "ctr": 0.034,
        "conversion_rate": 0.055,
        "revenue_per_conversion": 350,
    },
    {
        "campaign": "YouTube Product Video",
        "channel": "YouTube",
        "base_spend": 22000,
        "ctr": 0.018,
        "conversion_rate": 0.038,
        "revenue_per_conversion": 370,
    },
    {
        "campaign": "YouTube Brand Awareness",
        "channel": "YouTube",
        "base_spend": 17500,
        "ctr": 0.014,
        "conversion_rate": 0.030,
        "revenue_per_conversion": 330,
    },
    {
        "campaign": "Email - Weekly Promotion",
        "channel": "Email",
        "base_spend": 4500,
        "ctr": 0.085,
        "conversion_rate": 0.115,
        "revenue_per_conversion": 290,
    },
    {
        "campaign": "Email - Product Launch",
        "channel": "Email",
        "base_spend": 6500,
        "ctr": 0.095,
        "conversion_rate": 0.135,
        "revenue_per_conversion": 410,
    },
    {
        "campaign": "Affiliate - Partners",
        "channel": "Affiliate",
        "base_spend": 9000,
        "ctr": 0.038,
        "conversion_rate": 0.070,
        "revenue_per_conversion": 380,
    },
]


# ============================================================
# MONTHLY SEASONALITY
# ============================================================

MONTH_MULTIPLIERS = {
    1: 0.88,
    2: 0.92,
    3: 0.97,
    4: 1.00,
    5: 1.03,
    6: 1.06,
    7: 1.02,
    8: 1.08,
    9: 1.12,
    10: 1.18,
    11: 1.32,
    12: 1.42,
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_date_range(start_date, end_date):
    return pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
    )


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


# ============================================================
# GENERATE DATA
# ============================================================

dates = random_date_range(
    START_DATE,
    END_DATE,
)

rows = []


for date in dates:

    month_multiplier = MONTH_MULTIPLIERS[date.month]

    # Weekday effect
    if date.weekday() >= 5:
        weekday_multiplier = 0.82
    else:
        weekday_multiplier = 1.00

    for campaign_config in CAMPAIGNS:

        campaign = campaign_config["campaign"]
        channel = campaign_config["channel"]

        # ----------------------------------------------------
        # RANDOM DAILY VARIATION
        # ----------------------------------------------------

        random_multiplier = np.random.normal(
            loc=1.0,
            scale=0.10,
        )

        random_multiplier = clamp(
            random_multiplier,
            0.70,
            1.35,
        )

        overall_multiplier = (
            month_multiplier
            * weekday_multiplier
            * random_multiplier
        )

        # ----------------------------------------------------
        # SPEND
        # ----------------------------------------------------

        daily_base_spend = (
            campaign_config["base_spend"] / 30
        )

        spend = (
            daily_base_spend
            * overall_multiplier
            * np.random.uniform(0.85, 1.15)
        )

        spend = max(spend, 100)

        # ----------------------------------------------------
        # IMPRESSIONS
        # ----------------------------------------------------

        # Approximate CPM based on channel
        if channel == "Google Ads":
            cpm = 18
        elif channel == "Facebook":
            cpm = 9
        elif channel == "Instagram":
            cpm = 8
        elif channel == "YouTube":
            cpm = 13
        elif channel == "Email":
            cpm = 4
        else:
            cpm = 10

        impressions = (
            spend / cpm * 1000
        )

        impressions *= np.random.uniform(
            0.85,
            1.15,
        )

        impressions = int(max(impressions, 100))

        # ----------------------------------------------------
        # CLICKS
        # ----------------------------------------------------

        ctr = campaign_config["ctr"]

        ctr_variation = np.random.normal(
            1.0,
            0.08,
        )

        effective_ctr = ctr * ctr_variation

        effective_ctr = clamp(
            effective_ctr,
            0.005,
            0.15,
        )

        clicks = int(
            impressions * effective_ctr
        )

        clicks = max(clicks, 1)

        # ----------------------------------------------------
        # LEADS
        # ----------------------------------------------------

        lead_rate = np.random.uniform(
            0.25,
            0.55,
        )

        leads = int(
            clicks * lead_rate
        )

        leads = max(leads, 1)

        # ----------------------------------------------------
        # CONVERSIONS
        # ----------------------------------------------------

        conversion_rate = (
            campaign_config["conversion_rate"]
        )

        conversion_variation = np.random.normal(
            1.0,
            0.10,
        )

        effective_conversion_rate = (
            conversion_rate
            * conversion_variation
        )

        effective_conversion_rate = clamp(
            effective_conversion_rate,
            0.01,
            0.25,
        )

        conversions = int(
            clicks * effective_conversion_rate
        )

        conversions = max(
            conversions,
            0,
        )

        # Make sure conversions don't exceed leads
        conversions = min(
            conversions,
            leads,
        )

        # ----------------------------------------------------
        # CUSTOMERS
        # ----------------------------------------------------

        repeat_customer_factor = np.random.uniform(
            0.72,
            0.92,
        )

        customers = int(
            conversions * repeat_customer_factor
        )

        customers = max(
            customers,
            0,
        )

        # ----------------------------------------------------
        # REVENUE
        # ----------------------------------------------------

        revenue_per_conversion = (
            campaign_config[
                "revenue_per_conversion"
            ]
        )

        revenue = (
            conversions
            * revenue_per_conversion
        )

        # Random order value variation
        revenue *= np.random.uniform(
            0.90,
            1.15,
        )

        # Additional seasonal boost
        revenue *= (
            0.92
            + (month_multiplier * 0.08)
        )

        revenue = max(
            revenue,
            0,
        )

        # ----------------------------------------------------
        # PROFIT
        # ----------------------------------------------------

        # Marketing + product/service cost
        product_cost_rate = np.random.uniform(
            0.48,
            0.62,
        )

        product_cost = (
            revenue * product_cost_rate
        )

        marketing_cost = spend

        profit = (
            revenue
            - product_cost
            - marketing_cost
        )

        # ----------------------------------------------------
        # CUSTOMER ID
        # ----------------------------------------------------

        if customers > 0:

            customer_id = (
                f"CUST-{random.randint(10000, 99999)}"
            )

        else:

            customer_id = ""

        # ----------------------------------------------------
        # SAVE ROW
        # ----------------------------------------------------

        rows.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "campaign": campaign,
                "channel": channel,
                "spend": round(spend, 2),
                "revenue": round(revenue, 2),
                "impressions": impressions,
                "clicks": clicks,
                "leads": leads,
                "conversions": conversions,
                "customer_id": customer_id,
                "profit": round(profit, 2),
            }
        )


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(rows)


# ============================================================
# CLEAN DATA TYPES
# ============================================================

df["date"] = pd.to_datetime(
    df["date"]
)

numeric_columns = [
    "spend",
    "revenue",
    "impressions",
    "clicks",
    "leads",
    "conversions",
    "profit",
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )


# ============================================================
# SORT DATA
# ============================================================

df = df.sort_values(
    by=[
        "date",
        "channel",
        "campaign",
    ]
).reset_index(drop=True)


# ============================================================
# SAVE CSV
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
)


# ============================================================
# DISPLAY SUMMARY
# ============================================================

print()
print("=" * 70)
print("SMART BI - MARKETING DATASET GENERATED")
print("=" * 70)

print(f"File       : {OUTPUT_FILE}")
print(f"Rows       : {len(df):,}")
print(f"Columns    : {len(df.columns)}")
print(
    f"Date Range : "
    f"{df['date'].min().date()} "
    f"to "
    f"{df['date'].max().date()}"
)

print()
print("Channels:")
print(
    df["channel"]
    .value_counts()
    .to_string()
)

print()
print("Campaigns:")
print(
    df["campaign"]
    .value_counts()
    .to_string()
)

print()
print("Financial Summary:")

print(
    f"Total Spend   : "
    f"${df['spend'].sum():,.2f}"
)

print(
    f"Total Revenue : "
    f"${df['revenue'].sum():,.2f}"
)

print(
    f"Total Profit   : "
    f"${df['profit'].sum():,.2f}"
)

total_spend = df["spend"].sum()
total_revenue = df["revenue"].sum()

if total_spend > 0:

    roi = (
        (total_revenue - total_spend)
        / total_spend
        * 100
    )

    roas = (
        total_revenue
        / total_spend
    )

else:

    roi = 0
    roas = 0


print(
    f"Overall ROI    : "
    f"{roi:.2f}%"
)

print(
    f"Overall ROAS   : "
    f"{roas:.2f}x"
)

print()
print("First 5 Rows:")
print(
    df.head().to_string(
        index=False
    )
)

print()
print("=" * 70)
print("Dataset generation completed successfully.")
print("=" * 70)
