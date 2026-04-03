# Decision Memo: Proactive Merchant Health Alerts

## Context

This analysis examined ~3,000 sellers on a real e-commerce marketplace to understand what drives merchant success and failure. The goal was to answer a product question: which merchants are silently failing, and what should the platform build to help them?

The dataset (Olist Brazilian E-Commerce, 100k orders, 2016-2018) is structurally similar to Shopify's merchant ecosystem: a platform connecting independent sellers to buyers, with fulfillment, reviews, and payments flowing through the platform. The findings are framed as transferable patterns, not Shopify-specific numbers.

## Key Findings

**1. Review scores are a lagging indicator, not a leading one.** 24.2% of merchants with review scores above 4.0 have declining order volume. When I tested whether early-period late delivery rate or early-period review score better predicted merchant decline, late delivery rate was significant (p = 0.028) and review score was not (p = 0.267). A platform that monitors merchant health through reviews alone would miss nearly one in four at-risk merchants. This was the finding that reframed the rest of the analysis: the right metric to watch is delivery reliability, not review scores.

**2. Rising Stars are the highest-leverage segment for intervention.** The segmentation identified four merchant tiers: Champions (645 merchants, 80.9% of GMV), Rising Stars (999 merchants, 15%), At Risk (748, 1.2%), and Dormant (568, 2.9%). Of these, Rising Stars have the most urgent combination of signals: 29.3% are declining, but they're still active (28-day median recency), still delivering reasonably well (5.0% late rate), and still receiving solid reviews (4.29). They sit at the inflection point between growth and decline, which means there's still time to intervene. Champions are more valuable individually, but their decline rate is lower (15.4%) and their problems are different (operational strain at scale, not silent stalling).

**3. Delivery promise-keeping matters 4x more than shipping speed.** The regression showed that each 10 percentage point increase in late delivery rate reduces average review scores by 0.138 points (p < 0.001, 95% CI: [-0.173, -0.103]). That's roughly 4x the per-unit effect of raw shipping days (-0.035 points per day). Even more telling: once late rate is controlled, the average number of days a delivery is late becomes non-significant (p = 0.93). Buyers care about whether the promise was kept, not how late it was. The product implication is that fulfillment tooling should focus on helping merchants set accurate delivery estimates and meet them, not just on reducing absolute shipping time.

## Recommendation

Build a proactive merchant health alert system that surfaces fulfillment benchmarks to Rising Star merchants before their delivery reliability degrades into visible decline.

The core feature: a weekly notification showing the merchant's on-time delivery rate trend over the last 30 days, benchmarked against the median for their product category. When a merchant's rate drops below the category median, the alert escalates with a specific suggestion (e.g., "Your on-time rate dropped to 82% this month. Merchants in health_beauty with rates above 90% fulfill 2 days faster on average. Consider adjusting your estimated delivery windows.").

I'd start with Rising Stars because the data shows this is where the funnel leaks most: merchants with solid fundamentals who are declining for reasons they can't see in their own metrics. Over time, the same alert infrastructure could extend to Champions (where the late rate is highest at 6.9%) and to At Risk merchants as part of a broader onboarding flow.

## Proposed Validation

Test this with a randomized experiment. The experiment design is detailed in [experiment_design.md](../docs/experiment_design.md), but the key parameters are:

- Randomize at the seller level, stratified by product category and segment
- Primary metric: 30-day on-time delivery rate improvement (5pp MDE)
- Required sample: 34 merchants per group (68 total), from a pool of 1,226 eligible sellers
- Runtime: 6 weeks (observation-limited, not sample-limited)
- GMV guardrail measured at the order level, not the merchant level

The guardrail measurement is worth calling out. The power analysis revealed that merchant-level GMV is too noisy to detect a 10% decrease at the planned sample size (would need 2,101 per group, 3.4x the eligible pool). At the primary sample size of 34 per group, GMV guardrail power is only 6.4%, which is effectively random. Switching to order-level GMV measurement solves this: the eligible sellers generate ~3,812 orders/month, reaching the required 1,233 orders per group in under 4 weeks.

Ship decision: primary metric significant at p < 0.05, no guardrail degradation beyond 1 standard deviation. Kill decision: any guardrail degrades at p < 0.10, or primary metric flat/negative at full power.

## Risks and Open Questions

**The dataset is a proxy, not the real thing.** Olist is a Brazilian marketplace, not a North American SaaS commerce platform. The patterns (delivery reliability as a leading indicator, the "silently failing" cohort) are structurally plausible for any merchant ecosystem, but the specific coefficients (0.138 points per 10pp late rate) would need to be validated on Shopify's own data before informing product decisions.

**I can't distinguish supply-side from demand-side decline.** A merchant with declining order volume could be pulling back (listing fewer products, shipping less frequently) or losing demand (fewer buyers finding them). The Olist dataset doesn't include storefront traffic or search impression data, so I can't tell which. The intervention I'm recommending (making the decline visible to the merchant) is a reasonable first step regardless, but the root cause matters for what comes next.

**The experiment assumes merchants will act on the alerts.** The power analysis shows we can detect a 5pp on-time improvement if it exists. But whether merchants actually change their fulfillment behavior in response to a weekly benchmark notification is an open question. If the ITT effect is flat but per-protocol analysis (merchants who opened the alert) shows an effect, the intervention concept works but the delivery mechanism needs iteration.

**I don't know what Shopify's current merchant health infrastructure looks like.** There may already be fulfillment dashboards, alert systems, or merchant success programs that address parts of this. If I were starting on the team, understanding the existing tooling would be my first question before recommending net-new features.

---

*Analysis based on the Olist Brazilian E-Commerce dataset (Kaggle, CC BY-NC-SA 4.0). Framework adapted from Shopify's published engineering blog posts on product success measurement and data science foundations. Full code and methodology: [https://github.com/jessicabat/merchant-growth-intelligence].*