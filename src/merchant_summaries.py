"""Generate merchant health briefs with a local Ollama model (Llama 3)."""

import json
import importlib
from pathlib import Path

import pandas as pd

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
MODEL = "llama3"
SEGMENT_ORDER = ["Champions", "Rising Stars", "At Risk", "Dormant"]

SYSTEM_PROMPT = """You are a merchant success analyst at an e-commerce marketplace.
Your job is to write a brief, plain-language health summary for a specific merchant,
based only on the structured metrics provided. Do not invent numbers, percentages, or
facts that are not in the input.

Write exactly 3 to 4 sentences. Structure your response as follows:
1. State the merchant's segment and top product category, and characterize their overall
business trajectory in one sentence.
2. Highlight their single strongest metric (the one that reflects what they are doing well).
3. Identify their single most important risk or weakness, using the provided data.
4. Recommend one specific, actionable intervention the platform should take for this merchant.

Keep the language direct and concrete. A merchant success manager should be able to read
this brief in 20 seconds and know exactly what to do."""


def _build_user_message(merchant_row: dict) -> str:
    trajectory = merchant_row.get("trajectory")
    order_change_pct = merchant_row.get("order_change_pct")
    recency_days = merchant_row.get("recency_days")

    traj_str = trajectory if pd.notna(trajectory) else "Unknown (insufficient data)"
    chg_str = (
        f"{float(order_change_pct):+.0f}% order volume change (H1 vs H2)"
        if pd.notna(order_change_pct)
        else "Not available"
    )
    recency_str = (
        f"{float(recency_days):.0f} days since last order"
        if pd.notna(recency_days)
        else "Unknown"
    )

    return f"""Merchant profile:
- Segment: {merchant_row.get('segment', 'Unknown')}
- Top product category: {str(merchant_row.get('top_category', 'unknown')).replace('_', ' ').title()}
- Total GMV: R${float(merchant_row.get('total_gmv', 0)):,.0f}
- Total orders: {int(float(merchant_row.get('order_count', 0)))}
- Average review score: {float(merchant_row.get('avg_review_score', 0)):.2f} / 5.0
- On-time delivery rate: {(1 - float(merchant_row.get('pct_orders_late', 0)))*100:.1f}%
- Average shipping days: {float(merchant_row.get('avg_shipping_days', 0)):.1f} days
- Recency: {recency_str}
- Order volume trajectory: {traj_str} ({chg_str})"""


def _fallback_brief(merchant_row: dict) -> str:
    segment = merchant_row.get("segment", "Unknown segment")
    category = str(merchant_row.get("top_category", "unknown")).replace("_", " ")
    review = float(merchant_row.get("avg_review_score", 0))
    late_rate = float(merchant_row.get("pct_orders_late", 0))
    on_time = 1 - late_rate
    orders = int(float(merchant_row.get("order_count", 0)))
    recency = merchant_row.get("recency_days")
    recency_text = f"{float(recency):.0f} days" if pd.notna(recency) else "unknown"

    return (
        f"This {segment} merchant in {category.title()} has {orders} total orders with an average review score of {review:.2f}. "
        f"Their strongest visible signal is an on-time delivery rate of {on_time:.1%}, while the biggest risk is delayed fulfillment at {late_rate:.1%} late orders. "
        f"They were last active {recency_text} ago, so this looks actionable now. "
        "Recommend a proactive fulfillment benchmark alert with one concrete next step tied to their category baseline."
    )


def _try_generate_with_ollama(user_message: str):
    try:
        ollama = importlib.import_module("ollama")
    except ImportError:
        return None

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            options={"temperature": 0.3, "num_predict": 250},
        )
        return response.message.content.strip()
    except Exception:
        return None


def generate_merchant_brief(merchant_row: dict) -> str:
    """
    Generate a natural-language health brief for a single merchant.
    
    Args:
        merchant_row: dict with keys: seller_id, segment, total_gmv,
            avg_review_score, pct_orders_late, top_category, trajectory
    
    Returns:
        str: 3-4 sentence merchant health brief
    """
    user_message = _build_user_message(merchant_row)
    llm_output = _try_generate_with_ollama(user_message)
    if llm_output:
        return llm_output
    return _fallback_brief(merchant_row)


def generate_sample_briefs(segments_df, n_per_segment=3):
    """
    Generate briefs for a sample of merchants (2-3 per segment).
    
    Returns:
        list[dict]: Each with seller_id, segment, brief text
    """
    required_cols = {
        "seller_id",
        "segment",
        "total_gmv",
        "order_count",
        "avg_review_score",
        "pct_orders_late",
        "avg_shipping_days",
        "recency_days",
        "top_category",
    }
    missing_cols = required_cols - set(segments_df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns for brief generation: {sorted(missing_cols)}")

    if n_per_segment < 1:
        raise ValueError("n_per_segment must be >= 1")

    results = []
    df = segments_df.copy()

    for segment in SEGMENT_ORDER:
        segment_df = df[df["segment"] == segment].copy()
        if segment_df.empty:
            continue

        segment_df = segment_df.sort_values(["total_gmv", "order_count"], ascending=[False, False])
        sample = segment_df.head(n_per_segment)

        for _, row in sample.iterrows():
            row_dict = row.to_dict()
            brief_text = generate_merchant_brief(row_dict)
            results.append(
                {
                    "seller_id": row_dict["seller_id"],
                    "segment": row_dict["segment"],
                    "input_metrics": {
                        "total_gmv": round(float(row_dict.get("total_gmv", 0)), 2),
                        "order_count": int(float(row_dict.get("order_count", 0))),
                        "avg_review_score": round(float(row_dict.get("avg_review_score", 0)), 4),
                        "pct_orders_late": round(float(row_dict.get("pct_orders_late", 0)), 4),
                        "on_time_rate": round(float(1 - row_dict.get("pct_orders_late", 0)), 4),
                        "avg_shipping_days": round(float(row_dict.get("avg_shipping_days", 0)), 2),
                        "recency_days": round(float(row_dict.get("recency_days", 0)), 1),
                        "top_category": str(row_dict.get("top_category", "unknown")),
                        "trajectory": str(row_dict.get("trajectory")) if pd.notna(row_dict.get("trajectory")) else None,
                        "order_change_pct": (
                            round(float(row_dict.get("order_change_pct")), 2)
                            if pd.notna(row_dict.get("order_change_pct"))
                            else None
                        ),
                    },
                    "brief_text": brief_text,
                    "generated_by": f"ollama/{MODEL} (live if available, fallback otherwise)",
                }
            )

    return results


def main():
    """Generate sample briefs from merchant segments and save JSON output."""
    segments_path = PROCESSED_DIR / "merchant_segments.csv"
    trajectory_path = PROCESSED_DIR / "merchant_trajectory.csv"
    output_path = PROCESSED_DIR / "merchant_briefs.json"

    segments_df = pd.read_csv(segments_path)

    if trajectory_path.exists():
        trajectory = pd.read_csv(trajectory_path)[["seller_id", "order_change_pct"]]
        segments_df = segments_df.merge(trajectory, on="seller_id", how="left")

    briefs = generate_sample_briefs(segments_df, n_per_segment=3)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(briefs, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(briefs)} briefs to {output_path}")


if __name__ == "__main__":
    main()
