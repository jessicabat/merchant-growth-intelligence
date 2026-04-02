# Merchant Growth Intelligence: Project PRD

## Document Purpose

This is the working reference document for the entire project. Every analysis, script, and deliverable should trace back to a section here. When using Claude Code, feed it the relevant section to scope each task.

---

## 1. Project Overview

**Project name:** Merchant Growth Intelligence

**One-liner:** A product data science case study that identifies silently failing e-commerce merchants, models the drivers of merchant success, and recommends product interventions, built using Shopify's own published DS frameworks.

**Core question:** Which merchants are silently failing, and what should a marketplace platform build to save them?

**Why this project exists:** This is a pre-application portfolio project targeting Shopify's Fall 2026 Product Data Science Internship. It is designed to demonstrate product judgment, statistical rigor, and communication quality, the three capabilities Shopify's interview process evaluates. Every deliverable mirrors how Shopify's internal DS team actually operates, based on their published engineering blog posts and frameworks.

**What this is NOT:** This is not a machine learning project, a fraud detection pipeline, or a multi-module technical showcase. It is one coherent product question answered through multiple analytical lenses, culminating in a written decision memo.

---

## 2. Dataset

**Source:** Olist Brazilian E-Commerce Public Dataset (Kaggle)
**Link:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
**License:** CC BY-NC-SA 4.0

This is real commercial data from a Brazilian e-commerce marketplace, anonymized by Olist. It is structurally analogous to Shopify's merchant ecosystem: a platform connecting independent sellers to buyers, with order fulfillment, reviews, and payments flowing through the platform.

### Tables (9 CSV files)

| File | Key columns | Role in project |
|------|-------------|-----------------|
| olist_orders_dataset.csv | order_id, customer_id, order_status, purchase_timestamp, delivered_timestamp, estimated_delivery | Core fact table. Timestamps enable time-based merchant analysis. Delivery gap (actual vs. estimated) is a key feature. |
| olist_order_items_dataset.csv | order_id, product_id, seller_id, price, freight_value | Links orders to sellers. Price and freight are critical for merchant economics. |
| olist_order_reviews_dataset.csv | review_id, order_id, review_score, review_comment_title, review_comment_message | Review scores are the primary quality signal. Review text enables AI-generated summaries. |
| olist_order_payments_dataset.csv | order_id, payment_type, payment_installments, payment_value | Payment behavior (installments, method) enriches merchant profiles. |
| olist_products_dataset.csv | product_id, product_category_name, product_weight_g, product_length/height/width_cm | Category and physical dimensions. Category is a key stratification variable. |
| olist_sellers_dataset.csv | seller_id, seller_zip_code, seller_city, seller_state | Seller geography. Enables regional analysis. |
| olist_customers_dataset.csv | customer_id, customer_unique_id, customer_zip_code, customer_city, customer_state | Buyer geography. Seller-buyer distance is a derived feature. |
| olist_geolocation_dataset.csv | geolocation_zip_code_prefix, lat, lng | Enables distance calculation between seller and buyer. |
| product_category_name_translation.csv | product_category_name, product_category_name_english | Portuguese to English mapping. Apply early in pipeline. |

### Dataset characteristics

- ~100,000 orders across ~3,000 unique sellers
- Date range: September 2016 to October 2018
- Seller volume varies significantly: some sellers have 1 order, top sellers have 2,000+
- Review scores are skewed toward 5 stars (positive skew), with a secondary spike at 1 star
- Delivery delay (actual minus estimated) is the single strongest predictor of negative reviews in prior analyses of this dataset

### Known limitations to acknowledge

- No true "churn" signal (we cannot observe a seller deactivating their account). Proxy: no orders in the final 90 days of the dataset.
- No cost data (margins, ad spend). GMV is observable but profit is not.
- Brazilian marketplace, not North American. Frame findings as transferable patterns, not Shopify-specific numbers.
- Single marketplace, not multi-channel. Shopify merchants sell across channels; Olist sellers sell on one platform.

---

## 3. Analytical Framework

This project follows Shopify's published "Product Success Metrics Framework" from their engineering blog. The framework has four layers, and the project maps to each.

### Layer 1: Start at the End User (the Merchant)

**Merchant's main goal:** Grow a sustainable, profitable e-commerce business on the platform.

**Merchant subgoals:**
- Acquire new customers and generate repeat purchases
- Maintain high product quality perception (reviews)
- Fulfill orders reliably and on time
- Optimize pricing and freight economics

### Layer 2: Define the Platform's Product Goals

**Platform's main goal:** Increase the number of merchants who achieve sustained success, because merchant success drives platform GMV and retention.

**Platform product subgoals (progressive):**
1. **Make merchants aware** of their performance relative to peers (benchmarking)
2. **Make merchants data-driven** by surfacing actionable metrics in their workflow
3. **Make merchants proactive** by alerting them before problems compound
4. **Make merchants successful** by recommending specific interventions based on their segment

### Layer 3: Define Success Metrics

| Metric type | Metric | Definition | Why it matters |
|-------------|--------|------------|----------------|
| **North star** | Merchant 90-day GMV retention | % of merchants active in month M who are still active 90 days later | Directly measures whether the platform keeps merchants selling |
| **Success: Adoption** | Merchants reached per segment | Count of merchants who would be classified into an actionable segment | Measures whether the segmentation is useful at scale |
| **Success: Quality** | Insight actionability rate | % of product recommendations tied to a measurable lever | Ensures recommendations are specific, not generic |
| **Guardrail** | Merchant satisfaction (avg review score trend) | Trailing 30-day avg review score | Ensures interventions do not degrade buyer experience |
| **Guardrail** | Order volume stability | Monthly order count per merchant | Ensures interventions do not inadvertently reduce volume |
| **Tripwire** | Merchant confusion signal | If a "health dashboard" intervention increases support tickets | Anti-success metric: the product is making things worse |

### Layer 4: Measurement Plan

| Time horizon | What to measure | How |
|--------------|----------------|-----|
| Week 1 (adoption) | Are merchants engaging with insights? | Dashboard view rate, time-on-page |
| Month 1 (behavior change) | Are merchants acting on recommendations? | Shipping time changes, SKU adjustments |
| Month 3 (outcome) | Are merchant success metrics improving? | GMV trend, review score trend, retention |
| Month 6 (sustained impact) | Is the improvement durable? | Cohort retention curves, regression to mean check |

---

## 4. Project Parts and Specifications

### Part 1: Product Brief (Written Deliverable)

**What:** A 1-page document framing the problem in Shopify's language. This is Section 3 above, polished into a standalone brief.

**Format:** Markdown, later rendered on project site.

**Tone:** Write as if you are a Shopify product DS presenting to a product manager. Opinionated, concise, merchant-first.

**This is not optional.** This document is what separates the project from every other Olist notebook on Kaggle. It signals that you understand product DS is about framing, not just analysis.

### Part 2: Challenge the Obvious Metric

**What:** An exploratory analysis that starts with the naive assumption ("low review scores = struggling merchant") and shows why it is wrong or incomplete.

**Objective:** Surface one non-obvious insight that reframes the problem.

**Approach:**
1. Compute naive merchant health: average review score per seller.
2. Compute alternative signals: order frequency trend (increasing/declining over time), delivery reliability (% orders delivered late), freight-to-price ratio, category concentration vs. diversification.
3. Build a simple "merchant trajectory" view: split the dataset into two time periods (first half / second half). Compare each merchant's metrics across periods. Identify merchants whose review scores are stable but whose order volume is declining. These are the "silently failing" merchants that a naive review-score-only view would miss.
4. Quantify the gap: "X% of merchants with review scores above 4.0 show declining order trajectories. A platform relying solely on review scores would miss these merchants entirely."

**Key output:** One clear finding, stated in one sentence, with a supporting visualization. Example: "Delivery reliability, not review score, is the leading indicator of merchant decline. Merchants whose on-time delivery rate drops below 70% see a 40% reduction in order volume within 60 days, regardless of their average review score."

**Technical notes:**
- Use pandas for all data manipulation
- Matplotlib or Plotly for visualizations (Plotly preferred for the project site)
- Keep the notebook clean: markdown headers, minimal code comments, findings stated in prose between code cells

### Part 3: Merchant Segmentation

**What:** RFM-based (Recency, Frequency, Monetary) segmentation of sellers into actionable tiers, with product recommendations for each tier.

**Approach:**
1. Compute RFM metrics per seller:
   - **Recency:** Days since last order (relative to dataset end date: Oct 2018)
   - **Frequency:** Total order count across the dataset
   - **Monetary:** Total GMV (sum of price + freight across all order items)
2. Standardize and cluster using K-means (k=4, validated with elbow method and silhouette score).
3. Label clusters based on RFM profiles. Target labels:
   - **Champions:** High GMV, recent activity, high frequency
   - **Rising Stars:** Growing trajectory, moderate volume
   - **At Risk:** Historically active, recent decline
   - **Dormant:** Low activity, low recency
4. For each segment, compute summary statistics: avg GMV, avg review score, avg delivery time, top categories, avg freight-to-price ratio.
5. **Write one paragraph per segment** with a specific product recommendation.

**Output format for each segment:**

> **[Segment Name]** (N merchants, X% of total GMV)
>
> Profile: [2-3 sentence description of this merchant type]
>
> Key risk/opportunity: [The single most important thing about this segment]
>
> Product recommendation: [What the platform should build or surface for this segment, and why]

**Technical notes:**
- sklearn for K-means
- scipy for silhouette validation
- The product recommendations are the deliverable, not the cluster visualization. The visualization supports the recommendation; it does not replace it.

### Part 4: Drivers of Merchant Success (Regression)

**What:** OLS regression identifying which operational factors most strongly predict merchant success, framed as product levers.

**Dependent variable:** Merchant average review score (continuous, 1-5). Secondary model: merchant GMV (log-transformed for normality).

**Independent variables:**
| Feature | Source | Hypothesis |
|---------|--------|------------|
| avg_shipping_days | orders (delivered - purchased) | Longer shipping reduces satisfaction |
| delivery_delay_days | orders (delivered - estimated) | Late deliveries hurt more than slow ones |
| pct_orders_late | orders | Consistency matters more than average |
| avg_price | order_items | Higher price = higher expectations |
| avg_freight_ratio | order_items (freight / price) | High freight ratio signals poor economics |
| num_skus | order_items (distinct products) | Diversification signal |
| num_categories | products | Category breadth |
| order_count | orders | Volume / experience proxy |
| seller_state | sellers | Regional effects |

**Approach:**
1. Build a merchant-level feature table (one row per seller, aggregated from order-level data).
2. Filter to sellers with 10+ orders (exclude merchants with too few data points for reliable aggregation).
3. Run OLS with statsmodels (not sklearn). statsmodels provides interpretable p-values, confidence intervals, and diagnostic statistics that product teams actually use.
4. Compute SHAP values on a parallel sklearn model for feature importance visualization.
5. Run diagnostic checks: VIF for multicollinearity, residual plots for heteroscedasticity, Cook's distance for influential observations.

**Key output:** 2-3 findings framed as product levers. Example: "Each additional day of delivery delay beyond the estimated date reduces average review score by 0.15 points (p < 0.001, 95% CI: [-0.18, -0.12]). This effect is 3x larger than the effect of price. The highest-leverage product intervention is fulfillment tooling, not pricing tools."

**Technical notes:**
- statsmodels.api.OLS for the primary model
- shap library for SHAP values
- Report R-squared, F-statistic, and key coefficients with confidence intervals
- Acknowledge limitations: OLS identifies association, not causation. Frame appropriately.

### Part 5: Experiment Design Document

**What:** A written experiment design for a product intervention informed by Parts 2-4. This is a design doc, not a simulated experiment.

**Why a design doc and not a simulation:** Running a fake A/B test with synthetic treatment effects is less impressive than demonstrating that you understand why experiments exist in product development, what can go wrong, and how to make a ship/no-ship decision. Shopify's interview process explicitly tests experiment design reasoning.

**Product intervention to test:** "Proactive Merchant Health Alerts" -- a feature that surfaces fulfillment benchmarks and peer comparisons to merchants whose delivery reliability is trending downward, before their review scores degrade.

**Design doc structure:**

1. **Hypothesis:** Merchants who receive proactive fulfillment alerts will improve their on-time delivery rate by at least 5 percentage points within 30 days, relative to control, without reducing order volume.

2. **Randomization unit:** Seller-level. Randomize at the seller level, not the order level, to avoid contamination.

3. **Stratification:** Stratify by product category and current merchant tier (from Part 3 segmentation) to ensure balanced assignment.

4. **Primary metric:** 30-day change in on-time delivery rate (percentage of orders delivered on or before estimated date).

5. **Secondary metric:** 30-day GMV change (to measure whether improved fulfillment translates to business outcomes).

6. **Guardrail metrics:**
   - Average review score (should not decrease)
   - Order cancellation rate (should not increase)
   - Merchant churn rate (should not increase; alerts should not discourage merchants)

7. **Power analysis:** Using variance from the actual Olist data, calculate the minimum sample size needed to detect a 5 percentage point improvement in on-time delivery rate at 80% power and alpha = 0.05. Use statsmodels.stats.power.TTestIndPower. Report the required N per group and the implied experiment runtime given the seller volume in the dataset.

8. **Runtime estimate:** Based on the power analysis, estimate how many weeks the experiment would need to run to accumulate sufficient data.

9. **Decision criteria:**
   - **Ship:** Primary metric significant at p < 0.05 AND no guardrail metric degrades beyond 1 standard deviation
   - **Iterate:** Primary metric trending positive but not significant; extend runtime or refine targeting
   - **Kill:** Any guardrail metric degrades significantly, or primary metric is flat/negative at full power

10. **Risks and mitigations:**
    - Novelty effect: merchants engage with alerts initially but stop. Mitigation: measure at 30 and 60 days.
    - Alert fatigue: too many alerts cause merchants to ignore them. Mitigation: cap alert frequency.
    - Selection bias: only engaged merchants respond. Mitigation: ITT (intent-to-treat) analysis as primary; per-protocol as sensitivity.

**Technical notes:**
- The power analysis is the only code in this section. Everything else is written prose.
- Write this as a standalone Markdown document that could be handed to a product manager.

### Part 6: AI-Generated Merchant Briefs

**What:** A lightweight script that takes structured merchant metrics and generates a natural-language health summary using an LLM API.

**Purpose:** Demonstrates "use AI tools reflexively as part of your fundamental workflow" (direct quote from Shopify's JD).

**Approach:**
1. For a sample of 10-15 merchants (2-3 from each segment), compile a structured input: seller_id, segment, GMV, review_avg, on_time_delivery_pct, top_category, trajectory (improving/stable/declining).
2. Send to Claude API (Sonnet) with a system prompt that produces a 3-4 sentence merchant health brief.
3. Include the prompt, the structured input, and the output in the project deliverables.

**Example output:**
> "This merchant is a Rising Star in the Electronics category. Their GMV grew 28% over the last quarter, but their on-time delivery rate of 64% is well below the category median of 78%. If delivery reliability does not improve, this merchant is likely to transition to At Risk within 60 days. Priority intervention: surface fulfillment partner recommendations."

**Technical notes:**
- Use the Anthropic Python SDK (anthropic library)
- Keep the prompt simple and reproducible
- This is a supporting element, not the centerpiece. Do not over-engineer it.

### Part 7: Decision Memo (Written Deliverable)

**What:** A 1-2 page written document synthesizing Parts 2-6 into a clear recommendation to "Shopify's product team."

**Structure:**
1. **Context** (2-3 sentences): What we analyzed and why.
2. **Key findings** (3 bullet points, each 2-3 sentences): The non-obvious insight from Part 2, the segment-level opportunities from Part 3, the highest-leverage product lever from Part 4.
3. **Recommendation** (1 paragraph): What to build, for which merchants, and why.
4. **Proposed validation** (1 paragraph): How to test the recommendation (reference the experiment design from Part 5).
5. **Risks and open questions** (3-4 items): What we do not know and what would need to be true for this recommendation to work.

**Tone:** Opinionated but honest. State your recommendation clearly. Acknowledge uncertainty. Do not hedge everything into meaninglessness.

**This is the capstone deliverable.** A Shopify DS hiring manager reading this should think: "This person already communicates like one of our product data scientists."

---

## 5. Tech Stack

| Component | Tool | Why this tool |
|-----------|------|---------------|
| Data manipulation | pandas | Industry standard, sufficient for 100k rows |
| Statistical modeling | statsmodels | Interpretable coefficients, p-values, CIs. Product teams use these, not sklearn metrics. |
| Feature importance | shap | SHAP values for storytelling |
| Segmentation | sklearn (KMeans) | Standard, well-documented |
| Power analysis | statsmodels.stats.power | Integrated with the rest of the stats stack |
| Visualization | plotly | Interactive charts for the project site. matplotlib as fallback for static plots. |
| AI summaries | anthropic (Claude Sonnet) | Demonstrates AI integration. |
| Project site | Static HTML/CSS or simple framework | Clean, fast, no framework overhead. GitHub Pages for hosting. |
| Version control | Git + GitHub | Professional portfolio standard |

**What is intentionally excluded:**
- **dbt / DuckDB:** These are data engineering tools. You are targeting Product DS. Including them signals track confusion.
- **Streamlit:** An interactive dashboard adds build time without adding analytical value. A polished static site with Plotly charts embedded is faster to build and more aligned with how Shopify DS communicates (written memos, not dashboards).
- **Complex ML models:** No XGBoost, no neural nets, no ensemble methods. OLS + K-means + SHAP is the right toolkit for product analytics. Shopify's DS philosophy is "fall in love with the problem, not the tools."

---

## 6. Deliverables and Project Site Structure

The project site has two entry points for two audiences.

### Entry Point 1: Product Brief (for product-minded reviewers)

Page flow:
1. Problem framing (Part 1 product brief)
2. The non-obvious insight (Part 2 key finding, with one visualization)
3. Merchant segments and recommendations (Part 3 segment summaries)
4. What to build and how to test it (Part 7 decision memo, referencing Part 5)

This page should be readable in 5 minutes. No code. Clean prose, 2-3 embedded visualizations, and the decision memo.

### Entry Point 2: Technical Deep Dive (for technical reviewers)

Page flow:
1. Data pipeline and cleaning decisions
2. Exploratory analysis with code walkthrough
3. Regression methodology, diagnostics, and outputs
4. Segmentation methodology and validation
5. Experiment design with power analysis code
6. AI summary implementation

This page can be longer. Include code snippets, statistical outputs, and methodology notes. Link to the full GitHub repo.

### GitHub Repository Structure

```
merchant-growth-intelligence/
  PRD.md
  README.md
  data/
    raw/                       # Olist CSVs go here (gitignored)
    processed/                 # Cleaned outputs
    download_data.py
  notebooks/
    01_data_cleaning.ipynb
    02_challenge_the_metric.ipynb
    03_segmentation.ipynb
    04_regression.ipynb
    05_power_analysis.ipynb
    06_ai_summaries.ipynb
  docs/
    product_brief.md
    experiment_design.md
    decision_memo.md
  src/
    merchant_features.py
    merchant_segments.py
    merchant_summaries.py
  site/
    index.html
    technical.html
    assets/
  requirements.txt
```

---

## 7. Build Plan

### Week 1: Data + Discovery + Segmentation

**Days 1-2: Setup and data pipeline**
- Download Olist dataset
- Write data cleaning notebook (handle nulls, translate categories, compute derived fields)
- Build merchant-level feature table (merchant_features.py)
- Validate: row counts, null checks, distribution sanity checks

**Days 3-4: Challenge the metric (Part 2)**
- Compute naive merchant health (avg review score)
- Compute alternative signals (delivery reliability, order trajectory, freight ratio)
- Split data into time periods, compare merchant trajectories
- Identify the "silently failing" cohort
- Write up the key finding

**Days 5-7: Segmentation (Part 3)**
- Compute RFM metrics per seller
- Run K-means (k=4), validate with elbow + silhouette
- Label clusters, compute segment profiles
- Write product recommendation paragraphs for each segment

### Week 2: Regression + Experiment + Deliverables

**Days 8-9: Regression (Part 4)**
- Run OLS regression on review score and GMV
- SHAP values for feature importance
- Diagnostics: VIF, residual plots, Cook's distance
- Write up 2-3 product lever findings

**Day 10: Experiment design (Part 5)**
- Write the experiment design document
- Run the power analysis using actual data variance
- Compute required sample size and runtime estimate

**Day 11: AI summaries (Part 6)**
- Build merchant_summaries.py
- Generate briefs for 10-15 sample merchants
- Include prompt and outputs in deliverables

**Days 12-14: Written deliverables + project site**
- Write the product brief (Part 1)
- Write the decision memo (Part 7)
- Build the project site (two entry points)
- Polish README
- Final review: read every written deliverable aloud for clarity

---

## 8. Quality Checklist (Pre-Submission)

### Analytical quality
- [ ] Every finding includes a specific number, not just a direction
- [ ] Regression reports coefficients, p-values, confidence intervals, and R-squared
- [ ] Segmentation is validated with silhouette score
- [ ] Power analysis uses actual data variance
- [ ] Limitations are explicitly stated

### Product quality
- [ ] Product brief follows Shopify's published framework
- [ ] Every segment recommendation is specific and actionable
- [ ] Decision memo takes a clear position
- [ ] Experiment design includes guardrails and kill criteria

### Communication quality
- [ ] Project site product page is readable in 5 minutes
- [ ] No jargon without explanation
- [ ] Visualizations have titles, axis labels, and a one-sentence takeaway
- [ ] README includes the project's core finding in the first paragraph

### Code quality
- [ ] Notebooks run end-to-end without errors
- [ ] requirements.txt is complete and pinned
- [ ] Data download script works
- [ ] No API keys committed to the repo

### Shopify alignment signals
- [ ] "Use AI tools reflexively" is demonstrated
- [ ] Written deliverables include opinions and recommendations
- [ ] Analysis challenges an assumption
- [ ] The project reads like an internal Shopify product review

---

## 9. Claude Code Usage Guide

Feed Claude Code the relevant PRD section as context for each task. Be specific about inputs and outputs. Example:

```
"Read Part 4 of my PRD (regression section). I have a merchant-level feature
table at data/processed/merchant_features.csv with these columns: [list].
Write an OLS regression script using statsmodels that predicts avg_review_score.
Include VIF checks, residual plots, and SHAP values."
```

### What to do yourself (not Claude Code)
- Write the product brief (Part 1). This is your voice and your product thinking.
- Write the decision memo (Part 7). Same reason.
- Write the experiment design reasoning (Part 5). The power analysis code can be Claude Code; the written reasoning should be yours.
- Write the segment recommendation paragraphs (Part 3). These demonstrate your product judgment.

---

## 10. How This Maps to Shopify's JD

| JD requirement | Where it appears |
|---------------|-----------------|
| "Search for objective truth through analysis to challenge assumptions and judgements" | Part 2: Challenge the Obvious Metric |
| "Apply analytical, statistical, and technical skills to drive insights that inform business actions and product decisions" | Parts 3, 4, 7 |
| "Regression" | Part 4: OLS with statsmodels |
| "Segmentation" | Part 3: RFM + K-means |
| "Experimentation" | Part 5: Experiment Design Document |
| "Use AI tools reflexively as part of your fundamental workflow" | Part 6: AI Merchant Briefs |
| "You take ownership of the projects you work on" | End-to-end project, sole author |
| "You take pride in creating simple solutions to complex problems" | OLS + K-means, clean written deliverables |
| "Constant learner" | Studied Shopify's published DS frameworks and applied them |
| "Care deeply about making commerce better for everyone" | Entire project framed around merchant success |

---

## 11. Interview Preparation Notes

**Life Story connection:** "I built credit scoring models at Khan Bank and for my FlowScore project. That experience taught me that scoring and segmentation are only useful if they lead to action. So for this project, I deliberately focused on the product recommendations, not just the model outputs."

**If asked about experiment design:** Walk through Part 5 in detail. The power analysis uses real data variance. The guardrails and kill criteria show you understand that experiments protect users, not just measure effects.

**If asked 'why not a more complex model?':** "Shopify's DS team says 'fall in love with the problem, not the tools.' OLS gives me interpretable coefficients that a product manager can act on."

**If asked about limitations:** You have them documented (Section 2). The proxy churn definition, the Brazilian market context, and the OLS causation caveat are all pre-addressed.
