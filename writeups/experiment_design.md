# Experiment Design: Proactive Merchant Health Alerts

## Background

Parts 2 and 4 of this analysis surfaced a consistent finding: delivery reliability is the strongest predictor of merchant decline, and it operates as a leading indicator that review scores miss. 24.2% of merchants with above-average reviews have declining order volume. The regression quantified this: each 10 percentage point increase in late delivery rate costs 0.138 review points (p < 0.001), roughly 4x the effect of raw shipping speed.

The merchants most affected are Rising Stars (999 merchants, 15% of GMV), where 29.3% show declining volume despite healthy reviews. These merchants are still active and still delivering reasonably well, but they're losing momentum for reasons their own metrics wouldn't surface.

This experiment tests whether making that trajectory visible to the merchant can reverse the decline.

## Hypothesis

Merchants who receive proactive fulfillment alerts (showing their on-time delivery trend vs. category peers) will improve their on-time delivery rate by at least 5 percentage points within 30 days, relative to control, without reducing order volume or GMV.

The 5pp MDE is grounded in the data: the gap between declining and growing merchants' late delivery rates in the first half of the dataset was ~2.1pp (6.0% vs 3.9%, from Part 2). A 5pp on-time improvement is ambitious but directionally consistent with what we observe in merchants who sustain growth.

I chose 5pp rather than 2pp because a smaller effect, while potentially real, would be harder to translate into a product recommendation with confidence. If the alerts only move the needle by 2pp, I'd want to understand why before scaling the feature.

## Randomization

**Unit:** Seller-level.

Randomizing at the seller level (not the order level) avoids contamination. If we randomized orders, a single merchant could receive alerts for some orders and not others, which doesn't make sense for a behavioral intervention. The merchant either sees the dashboard or they don't.

**Assignment:** Simple random assignment into treatment (receives alerts) and control (no alerts, existing experience). 50/50 split.

**Stratification:** Stratify by two variables before randomizing:
- **Product category** (top category per merchant). This controls for category-level differences in delivery logistics. A furniture seller and a cosmetics seller have fundamentally different shipping profiles.
- **Merchant segment** (Champions vs. Rising Stars). These groups have different baseline delivery rates and volume, so unstratified randomization could produce imbalanced arms by chance.

I'd want to discuss with the team whether additional stratification (e.g., by seller geography) is worth the added complexity. With only 68 merchants needed, over-stratification could create cells too small to fill.

## Metrics

**Primary metric:** 30-day on-time delivery rate (% of orders delivered on or before the estimated delivery date). Measured at the seller level.

This was chosen over review score because the regression showed late delivery rate has a direct, significant relationship with reviews (p < 0.001), while raw delivery days did not reach significance once late rate was controlled. On-time rate captures the binary "did you keep your promise?" signal that the data says matters most.

**Secondary metric:** 30-day GMV (total order value). This tells us whether improved delivery reliability translates into business outcomes, or whether the alerts just change behavior without impacting revenue.

**Guardrail metrics (should NOT get worse):**
- Average review score. If alerts somehow stress merchants and degrade service quality, reviews would catch it.
- Order cancellation rate. Alerts should not cause merchants to reject orders they're unsure they can fulfill on time.
- Merchant churn (no orders for 30+ days post-experiment). The alerts should not discourage merchants from selling.

## Power Analysis

All calculations use observed variance from the 1,226 eligible merchants (sellers with 10+ orders) in the Olist dataset.

**Primary metric:**
- Baseline on-time delivery rate: mean = 91.98%, sigma = 7.17pp
- MDE: 5pp improvement
- Cohen's d: 0.05 / 0.0717 = 0.697 (medium-to-large effect)
- **Required N per group: 34 merchants (68 total)**
- This is 5.5% of the 1,226 eligible pool. Sample size is not a constraint.

**Power curve across different MDEs:**

| MDE | Required N per group |
|-----|---------------------|
| 3pp | 93 |
| 5pp | 34 |
| 8pp | 14 |
| 10pp | 9 |
| 15pp | 5 |

The 5pp design point sits in a comfortable range. Even if we wanted to detect a smaller 3pp effect, we'd only need 93 per group, still well within the eligible pool.

## Runtime Estimate

The experiment would run **6 weeks total**: 4 weeks of observation to capture the 30-day on-time delivery rate change, plus a 2-week buffer for in-transit orders to resolve and for analysis.

With 1,226 eligible merchants and only 68 needed, we're not waiting to accumulate merchants. We're waiting for the observation window. Even at a conservative 50% enrollment rate (613 merchants), we exceed the required sample on day one. The runtime is observation-limited, not sample-limited.

## The Guardrail Power Problem

This is the finding I want to flag most prominently, because I think it reveals something important about how experiments can fail silently.

**At the planned sample size of 34 merchants per group, the GMV guardrail has only 6.4% statistical power.** That means if the alerts were secretly harming merchants' revenue by 10%, we would fail to detect it 93.6% of the time. The guardrail is effectively decorative.

Here's why: merchant-level GMV is extremely noisy. Log-GMV has a standard deviation of 1.22. To detect a 10% decrease with 80% power, we'd need **2,101 merchants per group**, which is 3.4x the entire eligible pool. It's not feasible at the merchant level.

**The fix:** Measure the GMV guardrail at the order level rather than the merchant level.

Individual order values have lower variance (sigma = 0.916 in log scale) than merchant-level aggregates, and there are far more of them. The eligible sellers generate approximately 3,812 orders per month. At the order level, we need ~1,233 orders per group to detect a 10% GMV decrease at 80% power, which accumulates in under 4 weeks.

So the final design has an intentional asymmetry:
- **Primary metric (on-time rate):** measured at the seller level, N = 34/group
- **GMV guardrail:** measured at the order level, N = ~1,233 orders/group

I initially expected all metrics to operate at the same unit of analysis. Running the power calculation showed me why that assumption breaks down when metric variance differs dramatically. This is something I'd want to discuss with more experienced team members. Are there standard practices for handling this asymmetry at Shopify? I imagine this comes up regularly in experiments where the randomization unit is at a higher level than some of the metrics.

## Decision Criteria

**Ship if:** On-time delivery rate improves by 5pp+ at p < 0.05, AND no guardrail metric (order-level GMV, review score, cancellation rate, churn) degrades by more than 1 standard deviation from its baseline.

**Iterate if:** On-time rate is trending positive (point estimate > 0) but not significant at p < 0.05. This could mean the effect is real but smaller than 5pp, or we need more observation time. I'd extend the observation window to 60 days before making a call.

**Kill if:** Any guardrail metric degrades significantly (p < 0.10, using a more lenient threshold for harm detection). Or if the primary metric point estimate is negative or flat at full observation time.

The asymmetric significance thresholds (0.05 for ship, 0.10 for kill) are intentional. I want to be more cautious about shipping a harmful feature than about missing a real improvement. A false negative (failing to detect a real benefit) means we iterate. A false positive on the guardrail (failing to detect real harm) means we hurt merchants.

## Risks and Mitigations

**1. Novelty effect.** Merchants might engage with the alerts in week 1 and ignore them by week 4. Mitigation: measure the primary metric at both 30 and 60 days. If the 30-day effect is significant but the 60-day effect is not, the improvement isn't durable and we should not ship.

**2. Alert fatigue.** Too many notifications could annoy merchants or cause them to disengage from the platform entirely. Mitigation: cap alert frequency at once per week. If we see the merchant churn guardrail trending upward in the treatment group (even non-significantly), pause enrollment and investigate.

**3. Selection bias in treatment response.** Only already-engaged merchants might respond to alerts, meaning the ITT (intent-to-treat) effect is diluted by non-responders. Mitigation: run ITT as the primary analysis (all assigned merchants, whether they opened the alert or not). Run per-protocol analysis (only merchants who viewed the alert) as a sensitivity check. If ITT is flat but per-protocol shows an effect, the intervention works but needs better delivery mechanics, not a different intervention.

**4. Spillover.** Treatment merchants who improve their fulfillment might shift carrier capacity away from control merchants in the same region. This is unlikely at N=34 per group but worth monitoring. Mitigation: check whether control group on-time rates decrease during the experiment. If they do, the treatment effect estimate is biased upward.

## Open Questions

These are things I'd want to ask the team before finalizing this design:

- What does Shopify's current merchant communication infrastructure look like? Would these alerts be in-app notifications, emails, or embedded in the merchant admin dashboard? The delivery mechanism affects engagement rates and therefore the expected effect size.
- Is there precedent for experiments where the guardrail metric uses a different unit of analysis than the primary metric? I've justified the asymmetry statistically, but I'd want to know if there are organizational norms around this.
- Should we restrict the experiment to Rising Stars only (where the need is clearest), or include Champions (where the late rate is actually higher)? Restricting to Rising Stars makes the product story cleaner but reduces the eligible pool from 1,226 to 536.
- The 5pp MDE is my best judgment given the data. Would the product team ship a feature that moved on-time rates by only 2-3pp? If yes, we'd need to increase sample size to 93/group. If the team's bar is higher (e.g., 8pp+), we could run a smaller experiment.

## Summary

| Parameter | Value |
|-----------|-------|
| Primary metric | On-time delivery rate (seller-level) |
| MDE | 5 percentage points |
| Required N | 34 per group, 68 total |
| Eligible pool | 1,226 merchants |
| Runtime | 6 weeks |
| GMV guardrail | Order-level (not merchant-level) |
| GMV guardrail N | ~1,233 orders per group |
| Primary power | 80% |
| GMV guardrail power | 80% (at order level); 6.4% if measured at merchant level |

Full power analysis code and visualizations: [notebooks/05_power_analysis.ipynb](../notebooks/05_power_analysis.ipynb)