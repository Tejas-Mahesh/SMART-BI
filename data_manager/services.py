import os

import pandas as pd


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
}


def get_file_extension(filename):
    """
    Return the lowercase file extension.
    """

    return os.path.splitext(
        filename
    )[1].lower()


def validate_file_extension(filename):
    """
    Check whether the uploaded file type is supported.
    """

    extension = get_file_extension(filename)

    return extension in SUPPORTED_EXTENSIONS


def load_uploaded_file(file):
    """
    Read CSV or Excel file using Pandas.
    """

    extension = get_file_extension(
        file.name
    )

    if extension == ".csv":

        df = pd.read_csv(file)

    elif extension in [".xlsx", ".xls"]:

        df = pd.read_excel(file)

    else:

        raise ValueError(
            "Unsupported file format."
        )

    return df


def normalize_dataframe(df):
    """
    Basic normalization without changing
    the original uploaded file.
    """

    df = df.copy()

    # Remove completely empty rows
    df = df.dropna(
        how="all"
    )

    # Remove completely empty columns
    df = df.dropna(
        axis=1,
        how="all"
    )

    # Convert column names to strings
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    return df


def detect_column_types(df):
    """
    Detect basic Pandas data types.
    """

    column_types = {}

    for column in df.columns:

        dtype = str(
            df[column].dtype
        )

        if pd.api.types.is_integer_dtype(
            df[column]
        ):
            data_type = "Integer"

        elif pd.api.types.is_float_dtype(
            df[column]
        ):
            data_type = "Decimal"

        elif pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):
            data_type = "Date / DateTime"

        elif pd.api.types.is_bool_dtype(
            df[column]
        ):
            data_type = "Boolean"

        else:
            data_type = "Text"

        column_types[str(column)] = {
            "dtype": dtype,
            "type": data_type,
        }

    return column_types


def get_dataset_statistics(df):
    """
    Generate basic dataset statistics.
    """

    return {
        "rows": int(
            len(df)
        ),

        "columns": int(
            len(df.columns)
        ),

        "missing_values": int(
            df.isna().sum().sum()
        ),

        "duplicate_rows": int(
            df.duplicated().sum()
        ),

        "memory_usage": int(
            df.memory_usage(
                deep=True
            ).sum()
        ),
    }


def get_preview_records(df, limit=10):
    """
    Return first rows in JSON-friendly format.
    """

    preview = df.head(
        limit
    ).copy()

    preview = preview.astype(
        object
    )

    preview = preview.where(
        pd.notna(preview),
        None
    )

    return preview.to_dict(
        orient="records"
    )


def analyze_uploaded_file(file):
    """
    Complete analysis pipeline for an uploaded file.
    """

    df = load_uploaded_file(
        file
    )

    df = normalize_dataframe(
        df
    )

    statistics = get_dataset_statistics(
        df
    )

    column_types = detect_column_types(
        df
    )

    preview = get_preview_records(
        df
    )

    columns = [
        str(column)
        for column in df.columns
    ]

    return {
        "dataframe": df,
        "statistics": statistics,
        "column_types": column_types,
        "columns": columns,
        "preview": preview,
    }