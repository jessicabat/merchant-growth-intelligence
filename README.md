# Merchant Growth Intelligence

**Which e-commerce merchants are silently failing, and what should the platform build to save them?**

A product data science case study analyzing merchant success patterns on a real e-commerce marketplace, identifying at-risk merchants before their metrics visibly decline, and recommending product interventions backed by statistical evidence.

Built using Shopify's published Product Success Metrics Framework.

## Key Finding

> [Replace with your core insight from Part 2 after analysis, e.g.: "Delivery reliability, not review score, is the leading indicator of merchant decline. X% of merchants with above-average review scores are silently losing order volume due to fulfillment issues that a review-based health metric would miss entirely."]

## Project Structure

```
├── PRD.md                      # Full project specification
├── data/
│   ├── raw/                    # Olist CSVs (gitignored)
│   └── processed/              # Cleaned merchant features (gitignored)
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_challenge_the_metric.ipynb
│   ├── 03_segmentation.ipynb
│   ├── 04_regression.ipynb
│   ├── 05_power_analysis.ipynb
│   └── 06_ai_summaries.ipynb
├── docs/
│   ├── product_brief.md
│   ├── experiment_design.md
│   └── decision_memo.md
├── src/
│   ├── merchant_features.py
│   ├── merchant_segments.py
│   └── merchant_summaries.py
└── site/                       # Project website (GitHub Pages)
```

## Setup

```bash
# Clone and install
git clone https://github.com/jessicabat/merchant-growth-intelligence.git
cd merchant-growth-intelligence
pip install -r requirements.txt


# download from:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
# Unzip into data/raw/
```

## Dataset

[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): ~100,000 real orders across ~3,000 sellers on a Brazilian e-commerce marketplace (2016-2018). Includes orders, products, reviews, payments, sellers, and geolocation data.

## Deliverables

| Deliverable | Audience | Location |
|-------------|----------|----------|
| Product Brief | Product reviewers | [docs/product_brief.md](docs/product_brief.md) |
| Experiment Design | Technical reviewers | [docs/experiment_design.md](docs/experiment_design.md) |
| Decision Memo | All reviewers | [docs/decision_memo.md](docs/decision_memo.md) |
| Technical Notebooks | Technical reviewers | [notebooks/](notebooks/) |
| Project Website | All reviewers | [Link TBD] |

## Tech Stack

pandas, statsmodels (OLS regression), scikit-learn (K-means segmentation), SHAP (feature importance), Plotly (visualization)

## Analytical Approach

1. **Challenge the obvious metric** - Show why review scores alone miss silently failing merchants
2. **Segment merchants** - RFM-based clustering into actionable tiers with product recommendations
3. **Model drivers of success** - OLS regression identifying the highest-leverage product interventions
4. **Design an experiment** - Full experiment design doc for a merchant health alert feature
5. **Generate AI insights** - LLM-powered merchant health briefs demonstrating reflexive AI use
6. **Recommend and defend** - Decision memo synthesizing findings into a clear product recommendation
