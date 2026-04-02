"""
Merchant segmentation using RFM analysis + K-means clustering.

See PRD.md Section 4, Part 3 for full specification.

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
        pd.DataFrame with columns: seller_id, recency, frequency, monetary
    """
    # TODO: Implement
    raise NotImplementedError("Implement in notebook 03")


def find_optimal_k(rfm_scaled, k_range=range(2, 9)):
    """
    Run elbow method and silhouette analysis to select optimal k.
    
    Returns:
        dict with 'inertias', 'silhouette_scores', and 'optimal_k'
    """
    # TODO: Implement
    raise NotImplementedError("Implement in notebook 03")


def assign_segments(merchants_df, rfm_scaled, k=4):
    """
    Run K-means with k clusters, then label based on RFM profiles.
    
    Target labels: Champions, Rising Stars, At Risk, Dormant
    
    Returns:
        pd.DataFrame: merchants_df with 'segment' column added
    """
    # TODO: Implement
    raise NotImplementedError("Implement in notebook 03")


def segment_profiles(segmented_df):
    """
    Compute summary statistics per segment for the product recommendations.
    
    For each segment: count, % of total GMV, avg review score, avg delivery
    time, top categories, avg freight ratio.
    
    Returns:
        pd.DataFrame: one row per segment with summary stats
    """
    # TODO: Implement
    raise NotImplementedError("Implement in notebook 03")
