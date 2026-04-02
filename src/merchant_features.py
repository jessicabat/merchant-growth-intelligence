"""
Merchant-level feature engineering pipeline.

Reads raw Olist CSVs and produces a single merchant_features.csv with one row
per seller, containing all features needed for segmentation, regression, and
the challenge-the-metric analysis.

Usage:
    python src/merchant_features.py

Output:
    data/processed/merchant_features.csv

See PRD.md Section 4, Parts 2-4 for feature specifications.
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"


def load_raw_tables():
    """Load and return all raw Olist tables as a dict of DataFrames."""
    tables = {
        "orders": pd.read_csv(RAW_DIR / "olist_orders_dataset.csv", parse_dates=[
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ]),
        "items": pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv"),
        "reviews": pd.read_csv(RAW_DIR / "olist_order_reviews_dataset.csv"),
        "payments": pd.read_csv(RAW_DIR / "olist_order_payments_dataset.csv"),
        "products": pd.read_csv(RAW_DIR / "olist_products_dataset.csv"),
        "sellers": pd.read_csv(RAW_DIR / "olist_sellers_dataset.csv"),
        "customers": pd.read_csv(RAW_DIR / "olist_customers_dataset.csv"),
        "geolocation": pd.read_csv(RAW_DIR / "olist_geolocation_dataset.csv"),
        "category_translation": pd.read_csv(RAW_DIR / "product_category_name_translation.csv"),
    }
    return tables


def clean_and_merge(tables):
    """
    Clean raw tables and produce an order-level merged DataFrame.
    
    Key cleaning steps:
    - Translate product categories to English
    - Filter to delivered orders only
    - Compute delivery_delay_days (actual - estimated)
    - Compute shipping_days (delivered - purchased)
    - Compute freight_ratio (freight_value / price)
    
    Returns:
        pd.DataFrame: Order-item level data with all fields needed for aggregation
    """
    # TODO: Implement cleaning pipeline
    # See PRD.md Section 2 for table details and Section 4 Part 2 for derived fields
    raise NotImplementedError("Implement in notebook 01, then refactor here")


def build_merchant_features(order_items_df):
    """
    Aggregate order-item data to merchant (seller) level.
    
    Output columns (see PRD.md Section 4, Part 4 for full spec):
    - seller_id
    - order_count
    - total_gmv (sum of price + freight)
    - avg_review_score
    - avg_shipping_days
    - avg_delivery_delay_days
    - pct_orders_late (% orders delivered after estimated date)
    - avg_price
    - avg_freight_ratio
    - num_skus (distinct products)
    - num_categories
    - seller_state
    - first_order_date
    - last_order_date
    - recency_days (days from last order to dataset end)
    
    Returns:
        pd.DataFrame: One row per seller
    """
    # TODO: Implement aggregation
    raise NotImplementedError("Implement in notebook 01, then refactor here")


def add_trajectory_features(merchant_df, order_items_df):
    """
    Add time-based trajectory features for Part 2 (challenge the metric).
    
    Split each merchant's orders into first half / second half of their tenure.
    Compare metrics across periods to identify trajectory:
    - gmv_trajectory: 'growing', 'stable', 'declining'
    - volume_trajectory: 'growing', 'stable', 'declining'
    - review_trajectory: 'improving', 'stable', 'declining'
    
    Returns:
        pd.DataFrame: merchant_df with trajectory columns added
    """
    # TODO: Implement trajectory logic
    raise NotImplementedError("Implement in notebook 02, then refactor here")


def main():
    """Run the full feature pipeline."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Loading raw tables...")
    tables = load_raw_tables()
    
    print("Cleaning and merging...")
    order_items = clean_and_merge(tables)
    
    print("Building merchant features...")
    merchants = build_merchant_features(order_items)
    
    print("Adding trajectory features...")
    merchants = add_trajectory_features(merchants, order_items)
    
    output_path = PROCESSED_DIR / "merchant_features.csv"
    merchants.to_csv(output_path, index=False)
    print(f"Saved {len(merchants)} merchants to {output_path}")
    
    # Sanity checks
    print(f"\nSanity checks:")
    print(f"  Merchants: {len(merchants):,}")
    print(f"  Avg orders per merchant: {merchants['order_count'].mean():.1f}")
    print(f"  Avg review score: {merchants['avg_review_score'].mean():.2f}")
    print(f"  Merchants with 10+ orders: {(merchants['order_count'] >= 10).sum():,}")


if __name__ == "__main__":
    main()
