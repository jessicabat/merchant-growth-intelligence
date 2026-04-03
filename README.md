# Merchant Growth Intelligence

**Which e-commerce merchants are silently failing, and what should the platform build to save them?**

A product data science case study analyzing merchant success patterns on a real e-commerce marketplace, identifying at-risk merchants before their metrics visibly decline, and recommending product interventions backed by statistical evidence.

## Key Finding

24.2% of merchants with above-average review scores have declining order volume. Delivery reliability is the leading indicator of merchant decline. Late delivery rate significantly predicts trajectory (p = 0.028), but early-period review score does not (p = 0.267). A platform monitoring merchant health through reviews alone would miss nearly one in four at-risk merchants.

## About

The analysis follows Shopify's published Product Success Metrics Framework (user-goals-first, layered metric design, experiment-backed recommendations) and is structured to demonstrate the three capabilities their interview process evaluates: product judgment, statistical rigor, and communication quality. Every deliverable is built around a single coherent product question, and each analysis feeds into the next.

## Project Site

[https://jessicabat.github.io/merchant-growth-intelligence/](https://jessicabat.github.io/merchant-growth-intelligence/)

## Project Structure

```
├── PRD.md                      # Full project specification
├── data/
│   ├── raw/                    # Olist CSVs (gitignored)
│   └── processed/              # Cleaned merchant features (gitignored)
├── notebooks/
│   ├── 01_data_cleaning.ipynb          # Join 9 Olist tables, translate categories, build merchant_features.csv
│   ├── 02_challenge_the_metric.ipynb   # Merchant trajectory analysis, late rate vs. review score t-tests
│   ├── 03_segmentation.ipynb           # RFM features, K-means (k=4), elbow and silhouette validation
│   ├── 04_regression.ipynb             # OLS (statsmodels), SHAP values, VIF diagnostics, GMV model
│   ├── 05_power_analysis.ipynb         # TTestIndPower, power curves, merchant vs. order-level guardrail
│   └── 06_ai_summaries.ipynb          # Llama 3 8B via Ollama, merchant health briefs for all 4 segments
├── writeups/
│   ├── product_brief.md
│   ├── experiment_design.md
│   └── decision_memo.md
├── src/
│   ├── merchant_features.py
│   ├── merchant_segments.py
│   └── merchant_summaries.py
└── docs/                       # Project website (GitHub Pages)
    ├── index.html              # Product brief page (non-technical audience)
    └── technical.html          # Technical deep dive (DS reviewers)
```

## Setup

```bash
git clone https://github.com/jessicabat/merchant-growth-intelligence.git
cd merchant-growth-intelligence
pip install -r requirements.txt

# Download data from:
# https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
# Unzip into data/raw/
```

For AI summaries (notebook 06), Ollama must be running locally with Llama 3 pulled:

```bash
ollama serve &
ollama pull llama3
```

## Dataset

[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): ~100,000 real orders across ~3,000 sellers on a Brazilian e-commerce marketplace (2016-2018). Structurally similar to Shopify's merchant ecosystem: independent sellers, platform-mediated fulfillment, reviews, and payments.

## Deliverables

| Deliverable | Audience | Location |
|-------------|----------|----------|
| Product Brief | Product reviewers | [docs/product_brief.md](writeups/product_brief.md) |
| Experiment Design | Technical reviewers | [docs/experiment_design.md](writeups/experiment_design.md) |
| Decision Memo | All reviewers | [docs/decision_memo.md](writeups/decision_memo.md) |
| Technical Notebooks | Technical reviewers | [notebooks/](notebooks/) |
| Project Website | All reviewers | [jessicabat.github.io/merchant-growth-intelligence](https://jessicabat.github.io/merchant-growth-intelligence/) |

## Tech Stack

pandas, statsmodels (OLS regression), scikit-learn (K-means segmentation), SHAP (feature importance), Plotly (visualization), Ollama with Llama 3 8B (AI merchant briefs)

## Analytical Approach

1. **Challenge the obvious metric** - Identify the 24.2% of high-rated merchants with declining volume and test which early signals actually predict trajectory
2. **Segment merchants** - RFM-based K-means clustering (k=4, silhouette-validated) into Champions, Rising Stars, At Risk, and Dormant tiers with product recommendations per segment
3. **Model drivers of success** - OLS regression with statsmodels identifying the highest-leverage product levers (delivery reliability over raw shipping speed, 0.138 review points per 10pp late rate)
4. **Design an experiment** - Full experiment design for a proactive merchant health alert feature, including a power analysis that surfaces the GMV guardrail measurement problem
5. **Generate AI insights** - Llama 3 8B health briefs for merchants across all four segments, demonstrating reflexive AI tool use
6. **Recommend and defend** - Decision memo synthesizing findings into a clear product recommendation with proposed validation approach
