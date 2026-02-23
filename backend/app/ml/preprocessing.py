"""Data preprocessing pipeline for Navi Mumbai real estate data.

Handles cleaning, normalization, and feature engineering for the
raw CSV dataset. Designed to handle messy real-world data with
missing values, inconsistent formatting, and outliers.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from app.core.logging import logger


# Valid Navi Mumbai locations (canonical names)
VALID_LOCATIONS: List[str] = [
    "Airoli",
    "Belapur",
    "CBD Belapur",
    "Ghansoli",
    "Kharghar",
    "Kopar Khairane",
    "Nerul",
    "Panvel",
    "Sanpada",
    "Ulwe",
    "Vashi",
    "Juinagar",
    "Rabale",
    "Taloja",
]

# Location name normalization mapping
LOCATION_ALIASES: Dict[str, str] = {
    "airoli": "Airoli",
    "belapur": "Belapur",
    "cbd belapur": "CBD Belapur",
    "ghansoli": "Ghansoli",
    "kharghar": "Kharghar",
    "kopar khairane": "Kopar Khairane",
    "nerul": "Nerul",
    "panvel": "Panvel",
    "sanpada": "Sanpada",
    "ulwe": "Ulwe",
    "vashi": "Vashi",
    "juinagar": "Juinagar",
    "rabale": "Rabale",
    "taloja": "Taloja",
}


def normalize_location(location: Optional[str]) -> Optional[str]:
    """Normalize location name to canonical form.

    Args:
        location: Raw location string, possibly with inconsistent casing
            or extra whitespace.

    Returns:
        Canonical location name, or None if unrecognizable.
    """
    if pd.isna(location) or not str(location).strip():
        return None
    cleaned = str(location).strip().lower()
    return LOCATION_ALIASES.get(cleaned, None)


def clean_price(price_val) -> Optional[float]:
    """Parse and clean price values from various formats.

    Handles formats like '₹24426717', '24456626 INR', plain integers,
    and negative values (treated as invalid).

    Args:
        price_val: Raw price value (string, int, or float).

    Returns:
        Cleaned price as float, or None if invalid.
    """
    if pd.isna(price_val):
        return None
    price_str = str(price_val).strip()
    # Remove currency symbols and text
    price_str = re.sub(r"[₹,INR\s]", "", price_str)
    try:
        price = float(price_str)
        # Reject negative or zero prices
        if price <= 0:
            return None
        return price
    except ValueError:
        return None


def clean_bhk(bhk_val) -> Optional[int]:
    """Parse BHK configuration to integer.

    Handles formats like '2BHK', '2', '3BHK', etc.

    Args:
        bhk_val: Raw BHK value.

    Returns:
        BHK count as integer, or None if invalid.
    """
    if pd.isna(bhk_val):
        return None
    bhk_str = str(bhk_val).strip().upper()
    # Remove 'BHK' suffix
    bhk_str = bhk_str.replace("BHK", "").strip()
    try:
        bhk = int(float(bhk_str))
        if 1 <= bhk <= 6:
            return bhk
        return None
    except ValueError:
        return None


def clean_floor(floor_val) -> Optional[int]:
    """Parse floor value handling 'Ground' and other formats.

    Args:
        floor_val: Raw floor value.

    Returns:
        Floor number as integer (Ground = 0), or None if invalid.
    """
    if pd.isna(floor_val):
        return None
    floor_str = str(floor_val).strip().lower()
    if floor_str == "ground":
        return 0
    try:
        floor = int(float(floor_str))
        if 0 <= floor <= 100:
            return floor
        return None
    except ValueError:
        return None


def clean_yes_no(val) -> Optional[int]:
    """Convert yes/no strings to binary (1/0).

    Args:
        val: Raw yes/no value.

    Returns:
        1 for yes, 0 for no, None if missing.
    """
    if pd.isna(val):
        return None
    cleaned = str(val).strip().lower()
    if cleaned in ("yes", "y", "1", "true"):
        return 1
    if cleaned in ("no", "n", "0", "false"):
        return 0
    return None


def preprocess_dataset(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean and preprocess the raw real estate dataset.

    Applies all cleaning steps: location normalization, price cleaning,
    BHK parsing, outlier removal, and missing value imputation.

    Args:
        df: Raw DataFrame loaded from CSV.

    Returns:
        A tuple of (cleaned DataFrame, preprocessing stats dict).
    """
    stats = {
        "original_rows": len(df),
        "columns": list(df.columns),
    }
    logger.info(f"Starting preprocessing: {len(df)} rows, {len(df.columns)} columns")

    # Standardize column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    logger.info(f"Columns: {list(df.columns)}")

    # 1. Clean Location
    df["location"] = df["location"].apply(normalize_location)
    location_nulls = df["location"].isna().sum()
    df = df.dropna(subset=["location"]).copy()
    logger.info(f"Location: dropped {location_nulls} rows with invalid locations")

    # 2. Clean Area (remove negative and extreme outliers)
    df["area_sqft"] = pd.to_numeric(df["area_sqft"], errors="coerce")
    df = df[df["area_sqft"] > 100]  # Minimum realistic area
    df = df[df["area_sqft"] < 10000]  # Maximum realistic area
    logger.info(f"Area filter: {len(df)} rows remaining")

    # 3. Clean Price
    df["actual_price"] = df["actual_price"].apply(clean_price)
    df = df.dropna(subset=["actual_price"])
    logger.info(f"Price filter: {len(df)} rows remaining")

    # 4. Clean BHK
    df["bhk"] = df["bhk"].apply(clean_bhk)
    # Impute missing BHK based on area (rough heuristic)
    median_bhk = df["bhk"].median()
    df["bhk"] = df["bhk"].fillna(median_bhk).astype(int)

    # 5. Clean Bathrooms
    df["bathrooms"] = pd.to_numeric(df["bathrooms"], errors="coerce")
    df["bathrooms"] = df["bathrooms"].clip(1, 6)
    median_bath = df["bathrooms"].median()
    df["bathrooms"] = df["bathrooms"].fillna(median_bath).astype(int)

    # 6. Clean Floor
    df["floor"] = df["floor"].apply(clean_floor)
    median_floor = df["floor"].median()
    df["floor"] = df["floor"].fillna(median_floor).astype(int)

    # 7. Clean Total Floors
    df["total_floors"] = pd.to_numeric(df["total_floors"], errors="coerce")
    df["total_floors"] = df["total_floors"].clip(1, 80)
    median_total_floors = df["total_floors"].median()
    df["total_floors"] = df["total_floors"].fillna(median_total_floors).astype(int)

    # 8. Clean Age of Property
    df["age_of_property"] = pd.to_numeric(df["age_of_property"], errors="coerce")
    df["age_of_property"] = df["age_of_property"].clip(0, 50)
    median_age = df["age_of_property"].median()
    df["age_of_property"] = df["age_of_property"].fillna(median_age)

    # 9. Clean Parking and Lift
    df["parking"] = df["parking"].apply(clean_yes_no)
    df["parking"] = df["parking"].fillna(0).astype(int)

    df["lift"] = df["lift"].apply(clean_yes_no)
    df["lift"] = df["lift"].fillna(0).astype(int)

    # 10. Remove price outliers using IQR method
    q1 = df["actual_price"].quantile(0.01)
    q99 = df["actual_price"].quantile(0.99)
    initial_count = len(df)
    df = df[(df["actual_price"] >= q1) & (df["actual_price"] <= q99)]
    logger.info(
        f"Price outlier removal: {initial_count - len(df)} rows removed, "
        f"{len(df)} remaining"
    )

    # 11. Compute price per sqft for validation
    df["price_per_sqft"] = df["actual_price"] / df["area_sqft"]

    # Remove unrealistic price_per_sqft
    df = df[df["price_per_sqft"] > 2000]
    df = df[df["price_per_sqft"] < 50000]

    # Drop the helper column
    df = df.drop(columns=["price_per_sqft"])

    # Reset index
    df = df.reset_index(drop=True)

    stats["cleaned_rows"] = len(df)
    stats["rows_removed"] = stats["original_rows"] - stats["cleaned_rows"]
    stats["locations"] = sorted(df["location"].unique().tolist())
    stats["location_counts"] = df["location"].value_counts().to_dict()

    logger.info(
        f"Preprocessing complete: {stats['cleaned_rows']} rows "
        f"({stats['rows_removed']} removed)"
    )
    logger.info(f"Locations: {stats['locations']}")

    return df, stats


def get_feature_columns() -> List[str]:
    """Return the list of feature columns used for model training."""
    return [
        "location",
        "area_sqft",
        "bhk",
        "bathrooms",
        "floor",
        "total_floors",
        "age_of_property",
        "parking",
        "lift",
    ]


def get_target_column() -> str:
    """Return the target column name."""
    return "actual_price"
