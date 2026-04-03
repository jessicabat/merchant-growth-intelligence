"""
Merchant segmentation using RFM analysis + K-means clustering.

Usage:
    python src/merchant_segments.py

Input:
    data/processed/merchant_features.csv

Output:
    data/processed/merchant_segments.csv (features + segment labels)
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from pathlib import Path

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"


def compute_rfm(merchants_df):
    """
    Extract RFM (Recency, Frequency, Monetary) features from merchant data.
    
    - Recency: recency_days (already computed in merchant_features)
    - Frequency: order_count
    - Monetary: total_gmv
    
    Returns:
        tuple[pd.DataFrame, np.ndarray, StandardScaler]:
            - rfm_df with seller_id and transformed RFM columns
            - standardized feature matrix used for clustering
            - fitted scaler (for centroid back-transforms)
    """
    required_cols = {"seller_id", "recency_days", "order_count", "total_gmv"}
    missing_cols = required_cols - set(merchants_df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns for RFM: {sorted(missing_cols)}")

    rfm_df = merchants_df[["seller_id", "recency_days", "order_count", "total_gmv"]].dropna().copy()
    rfm_df["log_frequency"] = np.log1p(rfm_df["order_count"])
    rfm_df["log_monetary"] = np.log1p(rfm_df["total_gmv"])

    rfm_features = ["recency_days", "log_frequency", "log_monetary"]
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_df[rfm_features])
    return rfm_df, rfm_scaled, scaler


def find_optimal_k(rfm_scaled, k_range=range(2, 9)):
    """
    Run elbow method and silhouette analysis to select optimal k.
    
    Returns:
        dict with 'inertias', 'silhouette_scores', and 'optimal_k'
    """
    if len(rfm_scaled) == 0:
        raise ValueError("rfm_scaled is empty")

    inertias = []
    silhouette_scores = []

    for k in k_range:
        if k < 2:
            raise ValueError("k must be at least 2 for silhouette analysis")
        if k >= len(rfm_scaled):
            raise ValueError("Each k must be smaller than number of samples")

        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(rfm_scaled)
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(rfm_scaled, labels))

    optimal_k = list(k_range)[int(np.argmax(silhouette_scores))]
    return {
        "k_values": list(k_range),
        "inertias": inertias,
        "silhouette_scores": silhouette_scores,
        "optimal_k": optimal_k,
    }


def assign_segments(merchants_df, rfm_scaled, k=4):
    """
    Run K-means with k clusters, then label based on RFM profiles.
    
    Target labels: Champions, Rising Stars, At Risk, Dormant
    
    Returns:
        pd.DataFrame: merchants_df with 'segment' column added
    """
    required_cols = {"recency_days", "order_count", "total_gmv"}
    missing_cols = required_cols - set(merchants_df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns for segmentation: {sorted(missing_cols)}")

    valid_mask = merchants_df[["recency_days", "order_count", "total_gmv"]].notna().all(axis=1)
    valid_idx = merchants_df.index[valid_mask]
    if len(valid_idx) != len(rfm_scaled):
        raise ValueError(
            "Length mismatch: rfm_scaled must align with merchants rows where "
            "recency_days/order_count/total_gmv are non-null"
        )

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(rfm_scaled)

    centers = pd.DataFrame(
        kmeans.cluster_centers_,
        columns=["recency_z", "log_frequency_z", "log_monetary_z"],
    )
    centers["score_champion"] = (
        -centers["recency_z"] + centers["log_frequency_z"] + centers["log_monetary_z"]
    )
    centers["score_dormant"] = (
        centers["recency_z"] - centers["log_frequency_z"] - centers["log_monetary_z"]
    )

    champion_cluster = int(centers["score_champion"].idxmax())
    dormant_cluster = int(centers["score_dormant"].idxmax())
    remaining_clusters = [c for c in centers.index if c not in {champion_cluster, dormant_cluster}]

    # Remaining clusters are split into growth potential vs early risk by activity level.
    rising_cluster = int(
        centers.loc[remaining_clusters, ["log_frequency_z", "log_monetary_z"]]
        .mean(axis=1)
        .idxmax()
    )
    at_risk_cluster = int([c for c in remaining_clusters if c != rising_cluster][0])

    cluster_to_segment = {
        champion_cluster: "Champions",
        rising_cluster: "Rising Stars",
        at_risk_cluster: "At Risk",
        dormant_cluster: "Dormant",
    }

    segmented = merchants_df.copy()
    segmented["cluster"] = np.nan
    segmented["segment"] = pd.Series(pd.NA, index=segmented.index, dtype="object")

    segmented.loc[valid_idx, "cluster"] = cluster_labels
    segmented.loc[valid_idx, "segment"] = [cluster_to_segment[c] for c in cluster_labels]
    segmented["cluster"] = segmented["cluster"].astype("Int64")
    return segmented


def segment_profiles(segmented_df):
    """
    Compute summary statistics per segment for the product recommendations.
    
    For each segment: count, % of total GMV, avg review score, avg delivery
    time, top categories, avg freight ratio.
    
    Returns:
        pd.DataFrame: one row per segment with summary stats
    """
    if "segment" not in segmented_df.columns:
        raise ValueError("segment_profiles requires a 'segment' column")

    segment_order = ["Champions", "Rising Stars", "At Risk", "Dormant"]
    working = segmented_df[segmented_df["segment"].notna()].copy()
    if working.empty:
        return pd.DataFrame()

    total_sellers = len(working)
    total_gmv = working["total_gmv"].sum() if "total_gmv" in working.columns else np.nan
    rows = []

    for segment in segment_order:
        group = working[working["segment"] == segment]
        if group.empty:
            continue

        top_categories = ""
        if "top_category" in group.columns:
            top_categories = ", ".join(group["top_category"].value_counts().head(3).index.tolist())

        row = {
            "segment": segment,
            "seller_count": len(group),
            "seller_share": len(group) / total_sellers,
            "gmv_share": (group["total_gmv"].sum() / total_gmv) if total_gmv and not np.isnan(total_gmv) else np.nan,
            "median_gmv": group["total_gmv"].median() if "total_gmv" in group.columns else np.nan,
            "median_orders": group["order_count"].median() if "order_count" in group.columns else np.nan,
            "median_recency_days": group["recency_days"].median() if "recency_days" in group.columns else np.nan,
            "avg_review_score": group["avg_review_score"].mean() if "avg_review_score" in group.columns else np.nan,
            "avg_delivery_days": group["avg_shipping_days"].mean() if "avg_shipping_days" in group.columns else np.nan,
            "avg_freight_ratio": group["avg_freight_ratio"].mean() if "avg_freight_ratio" in group.columns else np.nan,
            "pct_orders_late": group["pct_orders_late"].mean() if "pct_orders_late" in group.columns else np.nan,
            "top_categories": top_categories,
        }

        if "is_declining" in group.columns:
            with_traj = group.dropna(subset=["is_declining"])
            row["pct_declining_trajectory"] = with_traj["is_declining"].mean() if len(with_traj) > 0 else np.nan

        rows.append(row)

    profile_df = pd.DataFrame(rows)
    if not profile_df.empty:
        profile_df["segment"] = pd.Categorical(profile_df["segment"], categories=segment_order, ordered=True)
        profile_df = profile_df.sort_values("segment").reset_index(drop=True)
    return profile_df
