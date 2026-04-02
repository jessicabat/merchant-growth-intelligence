"""
AI-generated merchant health briefs using Claude API.

See PRD.md Section 4, Part 6 for specification.

Usage:
    python src/merchant_summaries.py

Input:
    data/processed/merchant_segments.csv

Output:
    data/processed/merchant_briefs.json

Requires:
    ANTHROPIC_API_KEY environment variable (or .env file)
"""

import os
import json
import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

SYSTEM_PROMPT = """You are a product data scientist at an e-commerce platform. Given structured 
merchant metrics, write a 3-4 sentence health brief that:
1. States the merchant's segment and primary category
2. Highlights their strongest metric and biggest risk
3. Recommends a specific, actionable intervention

Be concise and opinionated. Write as if this brief will appear in a merchant health dashboard 
that a product manager reviews weekly."""


def generate_merchant_brief(merchant_row: dict) -> str:
    """
    Generate a natural-language health brief for a single merchant.
    
    Args:
        merchant_row: dict with keys: seller_id, segment, total_gmv,
            avg_review_score, pct_orders_late, top_category, trajectory
    
    Returns:
        str: 3-4 sentence merchant health brief
    """
    # TODO: Implement with Anthropic SDK
    # Use claude-sonnet-4-20250514
    raise NotImplementedError("Implement in notebook 06")


def generate_sample_briefs(segments_df, n_per_segment=3):
    """
    Generate briefs for a sample of merchants (2-3 per segment).
    
    Returns:
        list[dict]: Each with seller_id, segment, brief text
    """
    # TODO: Implement
    raise NotImplementedError("Implement in notebook 06")
