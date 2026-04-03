"""
Merchant-level feature engineering pipeline.

Reads raw Olist CSVs and produces a single merchant_features.csv with one row
per seller, containing all features needed for segmentation, regression, and
the challenge-the-metric analysis.

Usage:
    python src/merchant_features.py

Output:
    data/processed/merchant_features.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
MIDPOINT = pd.Timestamp("2017-09-07")


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
    required_tables = {
        "orders", "items", "reviews", "payments", "products", "sellers", "category_translation"
    }
    missing = required_tables - set(tables.keys())
    if missing:
        raise ValueError(f"Missing required input tables: {sorted(missing)}")

    orders = tables["orders"].copy()
    items = tables["items"].copy()
    reviews = tables["reviews"].copy()
    payments = tables["payments"].copy()
    products = tables["products"].copy()
    sellers = tables["sellers"].copy()
    cat_trans = tables["category_translation"].copy()

    # Translate product category names to English, fallback to "unknown".
    cat_map = cat_trans.set_index("product_category_name")["product_category_name_english"].to_dict()
    products["product_category_name_english"] = products["product_category_name"].map(cat_map).fillna("unknown")

    # Parse order timestamps needed for delivery metrics.
    ts_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in ts_cols:
        if col in orders.columns:
            orders[col] = pd.to_datetime(orders[col], errors="coerce")

    # Keep delivered orders with complete timestamps required for timing features.
    orders_delivered = orders[orders["order_status"] == "delivered"].copy()
    orders_delivered = orders_delivered.dropna(
        subset=[
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ]
    )

    orders_delivered["shipping_days"] = (
        (orders_delivered["order_delivered_customer_date"] - orders_delivered["order_purchase_timestamp"])
        .dt.total_seconds() / 86400
    )
    orders_delivered["delivery_delay_days"] = (
        (orders_delivered["order_delivered_customer_date"] - orders_delivered["order_estimated_delivery_date"])
        .dt.total_seconds() / 86400
    )
    orders_delivered = orders_delivered[orders_delivered["shipping_days"] > 0].copy()
    orders_delivered["is_late"] = orders_delivered["delivery_delay_days"] > 0

    # Deduplicate reviews at order level by keeping the most recent review row.
    reviews["review_creation_date"] = pd.to_datetime(reviews["review_creation_date"], errors="coerce")
    reviews_deduped = (
        reviews
        .sort_values("review_creation_date", ascending=False)
        .drop_duplicates("order_id", keep="first")
        [["order_id", "review_score"]]
    )

    # Aggregate payment installments to one row per order.
    payments_agg = (
        payments
        .groupby("order_id")
        .agg(
            total_payment_value=("payment_value", "sum"),
            max_installments=("payment_installments", "max"),
            payment_type=("payment_type", lambda x: x.mode().iloc[0] if not x.mode().empty else pd.NA),
        )
        .reset_index()
    )

    df = items.merge(
        orders_delivered[
            [
                "order_id",
                "customer_id",
                "order_purchase_timestamp",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
                "shipping_days",
                "delivery_delay_days",
                "is_late",
            ]
        ],
        on="order_id",
        how="inner",
    )
    df = df.merge(reviews_deduped, on="order_id", how="left")
    df = df.merge(payments_agg, on="order_id", how="left")
    df = df.merge(
        products[
            [
                "product_id",
                "product_category_name_english",
                "product_weight_g",
                "product_length_cm",
                "product_height_cm",
                "product_width_cm",
            ]
        ],
        on="product_id",
        how="left",
    )
    df = df.merge(
        sellers[["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"]],
        on="seller_id",
        how="left",
    )

    df["freight_ratio"] = np.where(df["price"] > 0, df["freight_value"] / df["price"], np.nan)
    return df


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
    required_cols = {
        "seller_id",
        "order_id",
        "order_purchase_timestamp",
        "shipping_days",
        "delivery_delay_days",
        "is_late",
        "review_score",
        "price",
        "freight_value",
        "freight_ratio",
        "product_id",
        "product_category_name_english",
    }
    missing_cols = required_cols - set(order_items_df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns in order_items_df: {sorted(missing_cols)}")

    df = order_items_df.copy()
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")
    dataset_end = df["order_purchase_timestamp"].max()

    # One seller-order row avoids double counting when an order has multiple items from the same seller.
    seller_orders = (
        df.sort_values("order_purchase_timestamp")
        .drop_duplicates(["seller_id", "order_id"], keep="first")
    )

    orders_agg = (
        seller_orders
        .groupby("seller_id")
        .agg(
            order_count=("order_id", "nunique"),
            first_order_date=("order_purchase_timestamp", "min"),
            last_order_date=("order_purchase_timestamp", "max"),
            avg_shipping_days=("shipping_days", "mean"),
            avg_delivery_delay_days=("delivery_delay_days", "mean"),
            pct_orders_late=("is_late", "mean"),
            avg_review_score=("review_score", "mean"),
            review_count=("review_score", "count"),
        )
        .reset_index()
    )

    items_agg = (
        df
        .groupby("seller_id")
        .agg(
            total_gmv=("price", "sum"),
            total_freight=("freight_value", "sum"),
            avg_price=("price", "mean"),
            avg_freight_value=("freight_value", "mean"),
            avg_freight_ratio=("freight_ratio", "mean"),
            num_skus=("product_id", "nunique"),
            num_categories=("product_category_name_english", "nunique"),
            top_category=(
                "product_category_name_english",
                lambda x: x.mode().iloc[0] if not x.mode().empty else "unknown",
            ),
            item_count=("order_item_id", "count"),
        )
        .reset_index()
    )
    items_agg["total_gmv_with_freight"] = items_agg["total_gmv"] + items_agg["total_freight"]

    merchant_features = orders_agg.merge(items_agg, on="seller_id", how="inner")
    merchant_features["recency_days"] = (
        (dataset_end - merchant_features["last_order_date"]).dt.total_seconds() / 86400
    ).round(1)
    merchant_features["tenure_days"] = (
        (dataset_end - merchant_features["first_order_date"]).dt.total_seconds() / 86400
    ).round(1)
    merchant_features["orders_per_month"] = (
        merchant_features["order_count"] / (merchant_features["tenure_days"] / 30).clip(lower=1)
    ).round(3)
    merchant_features["is_churned"] = merchant_features["recency_days"] > 90

    seller_geo = (
        df[["seller_id", "seller_city", "seller_state"]]
        .dropna(subset=["seller_id"])
        .drop_duplicates("seller_id")
    )
    merchant_features = merchant_features.merge(seller_geo, on="seller_id", how="left")

    float_cols = merchant_features.select_dtypes(include=["float64", "float32"]).columns
    merchant_features[float_cols] = merchant_features[float_cols].round(4)
    return merchant_features


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
    required_cols = {
        "order_id",
        "seller_id",
        "order_purchase_timestamp",
        "is_late",
        "price",
        "review_score",
    }
    missing_cols = required_cols - set(order_items_df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns for trajectory features: {sorted(missing_cols)}")

    df = order_items_df.copy()
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")

    h1_items = df[df["order_purchase_timestamp"] <= MIDPOINT]
    h2_items = df[df["order_purchase_timestamp"] > MIDPOINT]

    h1_cnt = h1_items.groupby("seller_id")["order_id"].nunique().rename("h1_orders")
    h2_cnt = h2_items.groupby("seller_id")["order_id"].nunique().rename("h2_orders")
    h1_gmv = h1_items.groupby("seller_id")["price"].sum().rename("h1_gmv")
    h2_gmv = h2_items.groupby("seller_id")["price"].sum().rename("h2_gmv")
    h1_pct_late = h1_items.groupby("seller_id")["is_late"].mean().rename("h1_pct_late")
    h2_pct_late = h2_items.groupby("seller_id")["is_late"].mean().rename("h2_pct_late")
    h1_avg_review = h1_items.groupby("seller_id")["review_score"].mean().rename("h1_avg_review")
    h2_avg_review = h2_items.groupby("seller_id")["review_score"].mean().rename("h2_avg_review")

    traj = pd.concat(
        [h1_cnt, h2_cnt, h1_gmv, h2_gmv, h1_pct_late, h2_pct_late, h1_avg_review, h2_avg_review],
        axis=1,
    )
    traj = traj[(traj["h1_orders"] > 0) & (traj["h2_orders"] > 0)].copy().reset_index()

    traj["order_change_pct"] = (traj["h2_orders"] - traj["h1_orders"]) / traj["h1_orders"] * 100
    traj["gmv_change_pct"] = (traj["h2_gmv"] - traj["h1_gmv"]) / traj["h1_gmv"] * 100
    traj["review_change"] = traj["h2_avg_review"] - traj["h1_avg_review"]

    traj["trajectory"] = pd.cut(
        traj["order_change_pct"],
        bins=[-np.inf, -20, 20, np.inf],
        labels=["Declining", "Stable", "Growing"],
    )
    traj["gmv_trajectory"] = pd.cut(
        traj["gmv_change_pct"],
        bins=[-np.inf, -20, 20, np.inf],
        labels=["Declining", "Stable", "Growing"],
    )
    traj["review_trajectory"] = pd.cut(
        traj["review_change"],
        bins=[-np.inf, -0.2, 0.2, np.inf],
        labels=["Declining", "Stable", "Improving"],
    )
    traj["is_declining"] = traj["trajectory"] == "Declining"

    merged = merchant_df.merge(
        traj[
            [
                "seller_id",
                "trajectory",
                "order_change_pct",
                "gmv_change_pct",
                "h1_orders",
                "h2_orders",
                "h1_pct_late",
                "h2_pct_late",
                "h1_avg_review",
                "h2_avg_review",
                "gmv_trajectory",
                "review_trajectory",
                "is_declining",
            ]
        ],
        on="seller_id",
        how="left",
    )
    return merged


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
