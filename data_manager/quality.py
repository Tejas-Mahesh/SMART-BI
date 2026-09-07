import os

import numpy as np
import pandas as pd
from scipy import stats


# =========================================================
# FILE LOADING
# =========================================================

def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()


def load_dataset_file(file):
    """
    Load CSV / XLSX / XLS into a Pandas DataFrame.
    """

    extension = get_file_extension(file.name)

    if extension == ".csv":
        return pd.read_csv(file)

    if extension in [".xlsx", ".xls"]:
        return pd.read_excel(file)

    raise ValueError("Unsupported file format.")


# =========================================================
# BASIC NORMALIZATION
# =========================================================

def normalize_dataframe(df):
    """
    Basic cleanup without changing the actual business values.
    """

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

    return df


# =========================================================
# COLUMN TYPE DETECTION
# =========================================================

def detect_column_type(series):
    """
    Detect a practical business-friendly column type.
    """

    if pd.api.types.is_bool_dtype(series):
        return "Boolean"

    if pd.api.types.is_integer_dtype(series):
        return "Integer"

    if pd.api.types.is_float_dtype(series):
        return "Decimal"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "Date / DateTime"

    # Try to recognize date-like text
    if series.dtype == "object":
        non_null = series.dropna()

        if len(non_null) > 0:
            converted = pd.to_datetime(
                non_null,
                errors="coerce",
                dayfirst=True
            )

            valid_ratio = converted.notna().mean()

            if valid_ratio >= 0.80:
                return "Date / DateTime"

    return "Text"


# =========================================================
# MISSING VALUE ANALYSIS
# =========================================================

def analyze_missing_values(df):
    results = []

    total_rows = len(df)

    for column in df.columns:

        missing_count = int(df[column].isna().sum())

        if total_rows > 0:
            missing_percentage = (
                missing_count / total_rows
            ) * 100
        else:
            missing_percentage = 0

        if missing_count == 0:
            status = "Good"
            severity = "Good"

        elif missing_percentage >= 30:
            status = "Critical"
            severity = "Critical"

        elif missing_percentage >= 10:
            status = "Warning"
            severity = "Warning"

        else:
            status = "Minor"
            severity = "Warning"

        results.append({
            "column": str(column),
            "missing_count": missing_count,
            "missing_percentage": round(
                missing_percentage,
                2
            ),
            "status": status,
            "severity": severity,
        })

    return results


# =========================================================
# DUPLICATE ANALYSIS
# =========================================================

def analyze_duplicates(df):
    duplicate_count = int(
        df.duplicated().sum()
    )

    total_rows = len(df)

    if total_rows > 0:
        duplicate_percentage = (
            duplicate_count / total_rows
        ) * 100
    else:
        duplicate_percentage = 0

    if duplicate_count == 0:
        status = "Good"
        severity = "Good"

    elif duplicate_percentage >= 10:
        status = "Critical"
        severity = "Critical"

    else:
        status = "Warning"
        severity = "Warning"

    return {
        "count": duplicate_count,
        "percentage": round(
            duplicate_percentage,
            2
        ),
        "status": status,
        "severity": severity,
    }


# =========================================================
# UNIQUE VALUE ANALYSIS
# =========================================================

def analyze_unique_values(df):
    results = []

    for column in df.columns:

        total_values = int(
            df[column].notna().sum()
        )

        unique_values = int(
            df[column].nunique(dropna=True)
        )

        if total_values > 0:
            uniqueness = (
                unique_values / total_values
            ) * 100
        else:
            uniqueness = 0

        results.append({
            "column": str(column),
            "unique_values": unique_values,
            "total_values": total_values,
            "uniqueness_percentage": round(
                uniqueness,
                2
            ),
        })

    return results


# =========================================================
# DATA TYPE ANALYSIS
# =========================================================

def analyze_column_types(df):
    results = []

    for column in df.columns:

        detected_type = detect_column_type(
            df[column]
        )

        results.append({
            "column": str(column),
            "pandas_dtype": str(
                df[column].dtype
            ),
            "detected_type": detected_type,
        })

    return results


# =========================================================
# INVALID VALUE ANALYSIS
# =========================================================

def analyze_invalid_values(df):
    results = []

    for column in df.columns:

        series = df[column]

        detected_type = detect_column_type(
            series
        )

        invalid_count = 0

        # Numeric columns
        if detected_type in ["Integer", "Decimal"]:

            if series.dtype == "object":
                converted = pd.to_numeric(
                    series,
                    errors="coerce"
                )

                invalid_count = int(
                    (
                        series.notna()
                        & converted.isna()
                    ).sum()
                )

        # Date columns
        elif detected_type == "Date / DateTime":

            if not pd.api.types.is_datetime64_any_dtype(
                series
            ):
                converted = pd.to_datetime(
                    series,
                    errors="coerce",
                    dayfirst=True
                )

                invalid_count = int(
                    (
                        series.notna()
                        & converted.isna()
                    ).sum()
                )

        if invalid_count == 0:
            status = "Good"
            severity = "Good"

        elif invalid_count >= 10:
            status = "Critical"
            severity = "Critical"

        else:
            status = "Warning"
            severity = "Warning"

        results.append({
            "column": str(column),
            "invalid_count": invalid_count,
            "status": status,
            "severity": severity,
        })

    return results


# =========================================================
# OUTLIER ANALYSIS
# =========================================================

def analyze_outliers(df):
    results = []

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns

    total_outliers = 0

    for column in numeric_columns:

        series = df[column].dropna()

        if len(series) < 4:
            outlier_count = 0

        else:

            # IQR method
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)

            iqr = q3 - q1

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outlier_count = int(
                (
                    (series < lower_bound)
                    |
                    (series > upper_bound)
                ).sum()
            )

        total_outliers += outlier_count

        if outlier_count == 0:
            status = "Good"
            severity = "Good"

        elif outlier_count >= 10:
            status = "High"
            severity = "Warning"

        else:
            status = "Detected"
            severity = "Warning"

        results.append({
            "column": str(column),
            "outlier_count": outlier_count,
            "status": status,
            "severity": severity,
        })

    return {
        "columns": results,
        "total": total_outliers,
    }


# =========================================================
# COLUMN NAME ANALYSIS
# =========================================================

def analyze_column_names(df):
    results = []

    seen = {}

    for column in df.columns:

        name = str(column)

        problems = []

        if name.strip() == "":
            problems.append(
                "Empty column name"
            )

        if name != name.strip():
            problems.append(
                "Leading or trailing spaces"
            )

        normalized = name.lower()

        if normalized in seen:
            problems.append(
                "Duplicate column name"
            )

        seen[normalized] = True

        if problems:
            status = "Warning"
            severity = "Warning"
        else:
            status = "Good"
            severity = "Good"

        results.append({
            "column": name,
            "issues": problems,
            "status": status,
            "severity": severity,
        })

    return results


# =========================================================
# DATASET SUMMARY
# =========================================================

def get_dataset_summary(df):
    missing_total = int(
        df.isna().sum().sum()
    )

    duplicate_total = int(
        df.duplicated().sum()
    )

    numeric_columns = len(
        df.select_dtypes(
            include=np.number
        ).columns
    )

    text_columns = len(
        df.select_dtypes(
            include=["object", "string"]
        ).columns
    )

    date_columns = 0

    for column in df.columns:
        if detect_column_type(
            df[column]
        ) == "Date / DateTime":
            date_columns += 1

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_values": missing_total,
        "duplicate_rows": duplicate_total,
        "numeric_columns": numeric_columns,
        "text_columns": text_columns,
        "date_columns": date_columns,
    }


# =========================================================
# QUALITY SCORE
# =========================================================

def calculate_quality_score(
    df,
    missing_analysis,
    duplicate_analysis,
    invalid_analysis,
    outlier_analysis
):
    """
    Calculate a 0-100 business-friendly quality score.

    Missing values:
        35 points

    Duplicates:
        20 points

    Invalid values:
        25 points

    Outliers:
        20 points
    """

    total_rows = len(df)

    if total_rows == 0:
        return 0

    # -----------------------------------------------------
    # Missing score
    # -----------------------------------------------------

    total_missing = sum(
        item["missing_count"]
        for item in missing_analysis
    )

    total_cells = (
        len(df)
        * len(df.columns)
    )

    if total_cells > 0:
        missing_ratio = (
            total_missing
            / total_cells
        )
    else:
        missing_ratio = 0

    missing_score = (
        35
        * max(
            0,
            1 - missing_ratio
        )
    )

    # -----------------------------------------------------
    # Duplicate score
    # -----------------------------------------------------

    duplicate_ratio = (
        duplicate_analysis["count"]
        / total_rows
    )

    duplicate_score = (
        20
        * max(
            0,
            1 - duplicate_ratio
        )
    )

    # -----------------------------------------------------
    # Invalid score
    # -----------------------------------------------------

    total_invalid = sum(
        item["invalid_count"]
        for item in invalid_analysis
    )

    invalid_ratio = (
        total_invalid
        / total_rows
    )

    invalid_score = (
        25
        * max(
            0,
            1 - invalid_ratio
        )
    )

    # -----------------------------------------------------
    # Outlier score
    # -----------------------------------------------------

    outlier_count = outlier_analysis["total"]

    outlier_ratio = (
        outlier_count
        / total_rows
    )

    outlier_score = (
        20
        * max(
            0,
            1 - min(
                outlier_ratio,
                1
            )
        )
    )

    score = (
        missing_score
        + duplicate_score
        + invalid_score
        + outlier_score
    )

    return round(
        max(
            0,
            min(
                score,
                100
            )
        ),
        2
    )


# =========================================================
# QUALITY LEVEL
# =========================================================

def get_quality_level(score):

    if score >= 90:
        return {
            "label": "Excellent",
            "class": "excellent",
        }

    if score >= 75:
        return {
            "label": "Good",
            "class": "good",
        }

    if score >= 50:
        return {
            "label": "Needs Improvement",
            "class": "warning",
        }

    return {
        "label": "Poor",
        "class": "critical",
    }


# =========================================================
# QUALITY ISSUES
# =========================================================

def build_quality_issues(
    missing_analysis,
    duplicate_analysis,
    invalid_analysis,
    outlier_analysis
):
    issues = []

    # Missing values
    for item in missing_analysis:

        if item["missing_count"] > 0:

            issues.append({
                "category": "Missing Values",
                "column": item["column"],
                "issue": (
                    f'{item["missing_count"]} missing '
                    f'value(s) '
                    f'({item["missing_percentage"]}%)'
                ),
                "severity": item["severity"],
            })

    # Duplicates
    if duplicate_analysis["count"] > 0:

        issues.append({
            "category": "Duplicates",
            "column": "Dataset",
            "issue": (
                f'{duplicate_analysis["count"]} duplicate '
                f'row(s) detected'
            ),
            "severity": duplicate_analysis[
                "severity"
            ],
        })

    # Invalid values
    for item in invalid_analysis:

        if item["invalid_count"] > 0:

            issues.append({
                "category": "Invalid Values",
                "column": item["column"],
                "issue": (
                    f'{item["invalid_count"]} invalid '
                    f'value(s) detected'
                ),
                "severity": item["severity"],
            })

    # Outliers
    for item in outlier_analysis["columns"]:

        if item["outlier_count"] > 0:

            issues.append({
                "category": "Outliers",
                "column": item["column"],
                "issue": (
                    f'{item["outlier_count"]} statistical '
                    f'outlier(s) detected'
                ),
                "severity": item["severity"],
            })

    return issues


# =========================================================
# RECOMMENDATIONS
# =========================================================

def build_quality_recommendations(
    missing_analysis,
    duplicate_analysis,
    invalid_analysis,
    outlier_analysis
):
    recommendations = []

    # Missing
    missing_columns = [
        item
        for item in missing_analysis
        if item["missing_count"] > 0
    ]

    if missing_columns:
        recommendations.append({
            "title": "Handle missing values",
            "description": (
                "Review columns containing missing values "
                "before performing advanced analytics."
            ),
            "severity": "Warning",
        })

    # Duplicates
    if duplicate_analysis["count"] > 0:
        recommendations.append({
            "title": "Remove duplicate records",
            "description": (
                "Duplicate rows may cause revenue, order "
                "and customer metrics to be overstated."
            ),
            "severity": "Critical",
        })

    # Invalid
    invalid_columns = [
        item
        for item in invalid_analysis
        if item["invalid_count"] > 0
    ]

    if invalid_columns:
        recommendations.append({
            "title": "Fix invalid values",
            "description": (
                "Review numeric and date columns containing "
                "values that cannot be interpreted correctly."
            ),
            "severity": "Critical",
        })

    # Outliers
    if outlier_analysis["total"] > 0:
        recommendations.append({
            "title": "Review statistical outliers",
            "description": (
                "Outliers may represent genuine business "
                "events or data-entry problems."
            ),
            "severity": "Warning",
        })

    # No issues
    if not recommendations:
        recommendations.append({
            "title": "Dataset is ready",
            "description": (
                "No major data-quality problems were detected. "
                "The dataset can proceed to analytics."
            ),
            "severity": "Good",
        })

    return recommendations


# =========================================================
# COMPLETE QUALITY ANALYSIS
# =========================================================

def analyze_data_quality(file):
    """
    Main entry point for the Data Quality module.
    """

    df = load_dataset_file(file)

    df = normalize_dataframe(df)

    summary = get_dataset_summary(df)

    missing_analysis = analyze_missing_values(
        df
    )

    duplicate_analysis = analyze_duplicates(
        df
    )

    unique_analysis = analyze_unique_values(
        df
    )

    type_analysis = analyze_column_types(
        df
    )

    invalid_analysis = analyze_invalid_values(
        df
    )

    outlier_analysis = analyze_outliers(
        df
    )

    column_name_analysis = analyze_column_names(
        df
    )

    quality_score = calculate_quality_score(
        df,
        missing_analysis,
        duplicate_analysis,
        invalid_analysis,
        outlier_analysis
    )

    quality_level = get_quality_level(
        quality_score
    )

    issues = build_quality_issues(
        missing_analysis,
        duplicate_analysis,
        invalid_analysis,
        outlier_analysis
    )

    recommendations = build_quality_recommendations(
        missing_analysis,
        duplicate_analysis,
        invalid_analysis,
        outlier_analysis
    )

    return {
        "dataframe": df,
        "summary": summary,
        "quality_score": quality_score,
        "quality_level": quality_level,
        "missing_analysis": missing_analysis,
        "duplicate_analysis": duplicate_analysis,
        "unique_analysis": unique_analysis,
        "type_analysis": type_analysis,
        "invalid_analysis": invalid_analysis,
        "outlier_analysis": outlier_analysis,
        "column_name_analysis": column_name_analysis,
        "issues": issues,
        "recommendations": recommendations,
    }