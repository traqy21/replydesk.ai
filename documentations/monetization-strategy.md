# Replydesk AI — Monetization Strategy

## Primary Model: SaaS Subscription

| Plan | Price | Includes |
|------|-------|----------|
| Free | $0/month | 10 generations/day, basic tools (Client Reply, Task Summary) |
| Pro | $9–15/month | 50+ generations/day, all tools, history, export, priority support |
| Team | $29–49/month | Multiple users, shared templates, admin panel, analytics |

## Secondary Revenue Streams

### 1. Pay-Per-Use Credits
- Sell credit packs for users who don't want a subscription
- Example: 100 generations for $5
- Low friction, good for casual or occasional users

### 2. White-Label / Agency Licensing
- VA agencies brand the tool as their own
- Custom domain, logo, team management
- Price: $99–199/month per agency

### 3. Prompt Marketplace
- Power users create and sell custom prompt templates
- Platform takes 20–30% commission
- Example: "Real Estate Email Pack" for $5

### 4. Affiliate / Referral Program
- Existing users earn $3–5 credit per referral who upgrades to Pro
- Low acquisition cost, high trust channel

## Go-To-Market Strategy

1. Launch on Product Hunt for free exposure
2. Post in VA Facebook groups and Reddit (r/VirtualAssistant, r/freelance)
3. Offer 14-day free trial of Pro plan
4. Create a 2-minute demo video (Loom) showing real use cases
5. Partner with VA training programs for tool recommendations

## Revenue Projections

| Users (Pro) | Monthly Revenue | Estimated Costs | Net Profit |
|-------------|-----------------|-----------------|------------|
| 50 | $600 | ~$50 | ~$550 |
| 100 | $1,200 | ~$80 | ~$1,120 |
| 250 | $3,000 | ~$150 | ~$2,850 |
| 500 | $6,000 | ~$300 | ~$5,700 |
| 1,000 | $12,000 | ~$600 | ~$11,400 |

Costs include AWS hosting (~$30 base) + OpenAI API usage (scales with users).

## Implementation Requirements

- [ ] Stripe integration for payments
- [ ] Plan-based rate limits (free: 10/day, pro: 50+/day)
- [ ] Landing page with pricing and demo
- [ ] Terms of service and privacy policy
- [ ] Email onboarding sequence (welcome, tips, upgrade nudge)
- [ ] Usage analytics to track engagement and conversion

## Recommended Approach

1. Ship the free tier now with current features
2. Build an audience and collect feedback
3. Gate premium features (export, templates, higher limits) behind Pro
4. Add Stripe once you have 20+ active free users showing interest
5. Iterate pricing based on conversion data
