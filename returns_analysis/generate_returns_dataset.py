import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "returns_dataset.csv"

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)

NUMBER_OF_RECORDS = 12000

REGIONS = [
    "North",
    "South",
    "East",
    "West",
    "Central",
]

PRODUCTS = [
    {
        "product_id": 101,
        "product_name": "Wireless Headphones",
        "category": "Electronics",
        "base_price": 2499,
        "base_profit": 650,
        "return_factor": 1.20,
    },
    {
        "product_id": 102,
        "product_name": "Smart Watch",
        "category": "Electronics",
        "base_price": 3999,
        "base_profit": 1100,
        "return_factor": 1.35,
    },
    {
        "product_id": 103,
        "product_name": "Bluetooth Speaker",
        "category": "Electronics",
        "base_price": 2999,
        "base_profit": 850,
        "return_factor": 1.10,
    },
    {
        "product_id": 104,
        "product_name": "USB-C Charger",
        "category": "Electronics",
        "base_price": 999,
        "base_profit": 300,
        "return_factor": 0.80,
    },
    {
        "product_id": 105,
        "product_name": "Laptop Backpack",
        "category": "Accessories",
        "base_price": 1799,
        "base_profit": 550,
        "return_factor": 0.90,
    },
    {
        "product_id": 106,
        "product_name": "Running Shoes",
        "category": "Fashion",
        "base_price": 3499,
        "base_profit": 900,
        "return_factor": 1.45,
    },
    {
        "product_id": 107,
        "product_name": "Casual Shirt",
        "category": "Fashion",
        "base_price": 1499,
        "base_profit": 450,
        "return_factor": 1.25,
    },
    {
        "product_id": 108,
        "product_name": "Denim Jeans",
        "category": "Fashion",
        "base_price": 2299,
        "base_profit": 700,
        "return_factor": 1.40,
    },
    {
        "product_id": 109,
        "product_name": "Coffee Maker",
        "category": "Home Appliances",
        "base_price": 4999,
        "base_profit": 1250,
        "return_factor": 0.95,
    },
    {
        "product_id": 110,
        "product_name": "Air Fryer",
        "category": "Home Appliances",
        "base_price": 5999,
        "base_profit": 1500,
        "return_factor": 1.05,
    },
    {
        "product_id": 111,
        "product_name": "Table Lamp",
        "category": "Home",
        "base_price": 1299,
        "base_profit": 380,
        "return_factor": 0.75,
    },
    {
        "product_id": 112,
        "product_name": "Office Chair",
        "category": "Furniture",
        "base_price": 7499,
        "base_profit": 1800,
        "return_factor": 1.15,
    },
    {
        "product_id": 113,
        "product_name": "Study Table",
        "category": "Furniture",
        "base_price": 8999,
        "base_profit": 2200,
        "return_factor": 1.00,
    },
    {
        "product_id": 114,
        "product_name": "Water Bottle",
        "category": "Lifestyle",
        "base_price": 799,
        "base_profit": 220,
        "return_factor": 0.70,
    },
    {
        "product_id": 115,
        "product_name": "Fitness Tracker",
        "category": "Fitness",
        "base_price": 2799,
        "base_profit": 750,
        "return_factor": 1.30,
    },
]


RETURN_REASONS = [
    "Damaged Product",
    "Wrong Product",
    "Product Not as Expected",
    "Size/Fit Issue",
    "Quality Issue",
    "Late Delivery",
    "Changed Mind",
    "Duplicate Order",
    "Defective Product",
    "Other",
]


RETURN_REASON_WEIGHTS = [
    0.12,
    0.08,
    0.16,
    0.15,
    0.13,
    0.08,
    0.10,
    0.05,
    0.09,
    0.04,
]


RETURN_STATUS = [
    "Returned",
    "Refunded",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86399)

    return start_date + timedelta(
        days=random_days,
        seconds=random_seconds,
    )


def generate_customer_id():
    return random.randint(10001, 13000)


def calculate_return_probability(product, region, month):
    """
    Generates realistic differences between products, regions,
    and months.
    """

    probability = 0.075

    # Product-specific return tendency
    probability *= product["return_factor"]

    # Fashion tends to have higher return rates
    if product["category"] == "Fashion":
        probability += 0.035

    # Electronics can have quality/defect returns
    if product["category"] == "Electronics":
        probability += 0.015

    # Regional variation
    regional_adjustment = {
        "North": 0.005,
        "South": 0.000,
        "East": 0.010,
        "West": -0.005,
        "Central": 0.008,
    }

    probability += regional_adjustment.get(region, 0)

    # Seasonal effect
    if month in [10, 11, 12]:
        probability += 0.015

    if month in [6, 7]:
        probability += 0.008

    return min(max(probability, 0.03), 0.25)


def choose_return_reason(product):
    """
    Makes return reasons somewhat dependent on category.
    """

    category = product["category"]

    if category == "Fashion":
        reasons = [
            "Size/Fit Issue",
            "Product Not as Expected",
            "Quality Issue",
            "Changed Mind",
        ]

        weights = [
            0.35,
            0.25,
            0.20,
            0.20,
        ]

        return random.choices(reasons, weights=weights, k=1)[0]

    if category == "Electronics":
        reasons = [
            "Defective Product",
            "Damaged Product",
            "Quality Issue",
            "Wrong Product",
            "Product Not as Expected",
        ]

        weights = [
            0.25,
            0.20,
            0.20,
            0.15,
            0.20,
        ]

        return random.choices(reasons, weights=weights, k=1)[0]

    return random.choices(
        RETURN_REASONS,
        weights=RETURN_REASON_WEIGHTS,
        k=1,
    )[0]


# ============================================================
# DATA GENERATION
# ============================================================

def generate_returns_data():

    records = []

    for i in range(1, NUMBER_OF_RECORDS + 1):

        return_date = random_date(
            START_DATE,
            END_DATE,
        )

        product = random.choice(PRODUCTS)
        region = random.choice(REGIONS)

        customer_id = generate_customer_id()

        order_id = 500000 + i
        return_id = 900000 + i

        quantity = random.choices(
            [1, 2, 3, 4, 5],
            weights=[0.60, 0.25, 0.10, 0.04, 0.01],
            k=1,
        )[0]

        # Small random price variation
        price_multiplier = random.uniform(0.90, 1.10)

        unit_price = product["base_price"] * price_multiplier

        revenue = unit_price * quantity

        # Slightly random profit
        profit = (
            product["base_profit"]
            * quantity
            * random.uniform(0.85, 1.15)
        )

        probability = calculate_return_probability(
            product,
            region,
            return_date.month,
        )

        is_returned = random.random() < probability

        if is_returned:

            return_amount = revenue * random.uniform(
                0.75,
                1.00,
            )

            profit_affected = profit * random.uniform(
                0.70,
                1.00,
            )

            return_reason = choose_return_reason(product)

            return_status = random.choice(
                RETURN_STATUS
            )

        else:

            return_amount = 0
            profit_affected = 0

            return_reason = "No Return"
            return_status = "Not Returned"

        records.append(
            {
                "return_id": return_id,
                "order_id": order_id,
                "customer_id": customer_id,
                "product_id": product["product_id"],
                "product_name": product["product_name"],
                "category": product["category"],
                "region": region,
                "return_date": return_date.strftime(
                    "%d-%m-%Y"
                ),
                "quantity": quantity,
                "revenue": round(revenue, 2),
                "return_amount": round(
                    return_amount,
                    2,
                ),
                "profit": round(profit, 2),
                "profit_affected": round(
                    profit_affected,
                    2,
                ),
                "return_reason": return_reason,
                "return_status": return_status,
            }
        )

    df = pd.DataFrame(records)

    return df


# ============================================================
# VALIDATION / SUMMARY
# ============================================================

def print_summary(df):

    print("\n" + "=" * 70)
    print("SMART BI - RETURNS DATASET")
    print("=" * 70)

    print(f"\nOutput file:")
    print(OUTPUT_FILE)

    print(f"\nTotal records: {len(df):,}")

    returned_count = (
        df["return_status"]
        .isin(["Returned", "Refunded"])
        .sum()
    )

    total_records = len(df)

    return_rate = (
        returned_count / total_records * 100
        if total_records > 0
        else 0
    )

    print(f"Returned records: {returned_count:,}")
    print(f"Return rate: {return_rate:.2f}%")

    print(
        f"Revenue affected: "
        f"₹{df['return_amount'].sum():,.2f}"
    )

    print(
        f"Profit affected: "
        f"₹{df['profit_affected'].sum():,.2f}"
    )

    print("\nReturn Reasons:")
    print(
        df[
            df["return_reason"] != "No Return"
        ]["return_reason"]
        .value_counts()
        .to_string()
    )

    print("\nReturns by Region:")

    region_returns = (
        df.assign(
            is_return=df["return_status"].isin(
                ["Returned", "Refunded"]
            )
        )
        .groupby("region")["is_return"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    print(region_returns.to_string())

    print("\nReturns by Category:")

    category_summary = (
        df.assign(
            is_return=df["return_status"].isin(
                ["Returned", "Refunded"]
            )
        )
        .groupby("category")
        .agg(
            total=("is_return", "count"),
            returns=("is_return", "sum"),
        )
    )

    category_summary["return_rate"] = (
        category_summary["returns"]
        / category_summary["total"]
        * 100
    )

    category_summary = category_summary.sort_values(
        "return_rate",
        ascending=False,
    )

    print(category_summary.to_string())

    print("\nFirst 5 records:")
    print(df.head().to_string())

    print("\n" + "=" * 70)
    print("DATASET GENERATED SUCCESSFULLY")
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    dataframe = generate_returns_data()

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print_summary(dataframe)