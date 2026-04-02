# Product Brief: Merchant Growth Intelligence

## The Problem

A marketplace platform's health depends on merchant retention. When merchants fail, the platform loses GMV. The intuitive approach is to monitor merchant review scores and intervene when they drop. But the data shows this misses a significant portion of the problem.

In an analysis of ~3,000 sellers on a real e-commerce marketplace, 24.2% of merchants with review scores above 4.0 had declining order volume. Their reviews looked fine. Their businesses were quietly shrinking. A platform relying on review scores as the merchant health signal would miss nearly one in four at-risk merchants.

The question this project tries to answer: can we identify these merchants earlier and recommend what the platform should build to help them?

## Start at the End User

Following Shopify's published product success framework, I started by defining what merchants are trying to achieve, not what the platform wants from them.

**Merchant's main goal:** Build a sustainable, growing business on the platform.

**Merchant subgoals:**
- Acquire customers and generate repeat purchases
- Maintain buyer trust through reliable fulfillment and product quality
- Keep shipping economics viable (freight costs proportional to product value)
- Understand how their business is performing relative to peers

I don't have direct merchant interview data to validate these, which is a limitation. In a real product setting, I'd want to talk to 5-10 merchants in each segment before finalizing this hierarchy. For this analysis, I derived the subgoals from what the data shows actually predicts merchant success and failure.

## Platform Product Goals

**Platform's main goal:** Increase the number of merchants who achieve sustained growth, because merchant success is what drives platform GMV.

The analysis revealed a merchant lifecycle that moves through four stages: At Risk merchants who never gain traction (748 sellers, 1.2% of GMV), Rising Stars who are building momentum but haven't broken through (999 sellers, 15% of GMV), Champions who drive the bulk of revenue (645 sellers, 80.9% of GMV), and Dormant merchants who have left (568 sellers, 100% churned).

The platform's product goals map to this lifecycle progressively:

1. **Help new merchants reach traction** (At Risk to Rising Star). These merchants have the highest review scores (4.67) but only 2 median orders. The barrier is discoverability, not quality.
2. **Prevent Rising Stars from stalling** (the core intervention). 29.3% of Rising Stars are declining. The regression identified delivery reliability as the strongest lever: each 10pp increase in late delivery rate costs 0.138 review points. These merchants need visibility into their own trajectory before the decline becomes irreversible.
3. **Protect Champions at scale** (retention). Champions have the highest late rate of any active segment (6.9%) because fulfillment strain increases with volume. Losing even a small percentage of Champions has outsized GMV impact.
4. **Learn from Dormant merchants** (prevention). 52.8% of Dormant sellers were already declining before they went inactive. Their early patterns can serve as warning signals for current merchants.

## Success Metrics

| Type | Metric | Definition | Why this metric |
|------|--------|------------|-----------------|
| **North star** | Merchant 90-day retention | % of merchants active in month M who place at least one order 90 days later | Directly measures whether the platform keeps merchants selling. Chosen over GMV because a merchant who stops selling generates zero future value regardless of their past revenue. |
| **Success** | Segment transition rate | % of Rising Stars who reach Champion-level volume (65+ orders) within 6 months | Measures whether interventions actually move merchants up the lifecycle, not just prevent decline. |
| **Success** | Alert engagement rate | % of merchants who view a fulfillment benchmark alert within 7 days of receiving it | Measures whether the intervention reaches merchants. If engagement is low, the problem is delivery mechanics, not the insight itself. |
| **Guardrail** | Average review score | Trailing 30-day mean review score across treated merchants | Ensures interventions don't degrade the buyer experience. If alerts stress merchants into rushing fulfillment and quality drops, reviews would catch it. |
| **Guardrail** | Order-level GMV | Mean order value for treated merchants vs. control | Ensures the intervention doesn't reduce revenue. Measured at the order level because the power analysis showed merchant-level GMV is too noisy to detect a 10% decrease at feasible sample sizes (would need 2,101 per group; only 1,226 eligible). |
| **Tripwire** | Merchant support tickets | Volume of support tickets from treated merchants post-intervention | Anti-success metric. If a merchant health dashboard confuses merchants or creates anxiety, support volume would increase. Any significant increase should trigger a pause. |

## Measurement Plan

| Time horizon | What to measure | What it tells us |
|-------------|----------------|------------------|
| **Week 1** | Alert open rate, time on dashboard | Are merchants seeing the intervention at all? If open rate is below 30%, the delivery mechanism needs work before we can evaluate the content. |
| **Month 1** | On-time delivery rate change (treatment vs. control) | Is behavior changing? This is the primary experiment metric. We need a 5pp improvement at p < 0.05 to consider shipping. |
| **Month 3** | Review score trend, GMV trend, segment transitions | Are the behavioral changes translating to outcomes? A merchant who ships on time more often should see reviews stabilize and volume grow. If on-time rate improves but GMV doesn't, the theory of change is incomplete. |
| **Month 6** | Retention rate, regression to mean check | Is the improvement durable? Early effects often fade (novelty effect). Compare 6-month retention curves for treatment vs. control to see if the intervention has lasting impact. |

The Month 3 and Month 6 measurements are where I have the least certainty. The Olist dataset covers about two years, which gives some ability to observe long-term merchant trajectories, but a real experiment would need to be designed with these longer time horizons in mind from the start. I'd want to discuss with the team what Shopify's typical experiment observation windows look like for merchant-facing interventions, since the right cadence probably depends on how quickly merchants typically respond to new platform features.

---

*This framework is adapted from Shopify's published ["A Data Scientist's Guide to Measuring Product Success"](https://shopify.engineering/a-data-scientist-s-guide-to-measuring-product-success) (2022) and ["Data Science & Engineering Foundations"](https://shopify.engineering/shopifys-data-science-engineering-foundations) (2020). I structured this analysis to follow the same user-goals-first approach their team describes.*