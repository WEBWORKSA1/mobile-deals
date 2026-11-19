# Mobile.Deals — Winning Concept + Phase-wise Build Prompt

_Last revised: 19 Nov 2026_

## 1. The decision

**Mobile.Deals = "The Mobile Savings Engine."** A live, self-refreshing mobile-deals hub (phones, SIM/eSIM plans, accessories, tablets & wearables across US, CA, UK, EU, AU, IN) wrapped around original money-saving tools. The core conversion is a **free Bill Audit**: the visitor sees an instant savings estimate, then trades their email for a personalized report (lead) and clicks through to the cheapest plan that fits (affiliate CPA).

### Why this beats a plain deals blog

| Option | Verdict | Reason |
|---|---|---|
| Pure deal feed (Slickdeals/OzBargain clone) | Reject | Community giants own it; aggregated headlines alone are thin content and an AdSense rejection risk. |
| Phone spec database (GSMArena clone) | Reject | 20-year incumbents, massive data upkeep, low CPA. |
| **Plan-savings tools + live deal feed + guides** | **Build** | Recurring-bill intent pays the highest CPAs in the niche, tools are original and linkable, the feed supplies freshness and repeat visits. |

Wireless affiliate payouts observed Nov 2026 (FlexOffers/UpPromote listings): Visible $58/activation, T-Mobile $60/activation, Total Wireless $58, Verizon $24–$60, US Mobile ~$30, Mint Mobile ~$20–$30, Cricket $8.

### Revenue model (assumptions, month-12 target: 50,000 sessions/mo, 2.2 pages/session)

| Stream | Assumption | Monthly |
|---|---|---|
| Google AdSense | 110k pageviews × $8–$15 RPM (US-heavy telecom/deals) | $880–$1,650 |
| Plan affiliates | 1.5% of sessions click a plan × 4% activate × $40 avg CPA | ≈ $1,200 |
| Business-line leads | 10 fleet leads × $50 | ≈ $500 |
| Sponsorships | 1–2 placements × $300–$1,000 | $300–$2,000 |
| Donations | 0.05% of sessions × $15 | ≈ $100 |
| **Total** | | **≈ $3,000–$5,450/mo** on $0 hosting |

The single biggest lever is Bill Audit conversion: every +1 point on 5,000 audit users = +50 leads/month.

### Safe path vs bold path
- **Safe (this build):** tools + 12 evergreen guides + live feed + compliance pages. Get AdSense approval first.
- **Bold (after approval):** programmatic pages generated from the Deal Radar (`/phones/iphone-17/`, `/switch-from-verizon/`, per-country plan finders), paid newsletter sponsorships, a weekly YouTube Short per top deal. Higher upside, thin-content risk: only publish a programmatic page when it has ≥5 live deals and ≥250 words of original intro.

## 2. Research basis
41 world-class sites were opened and read (full log in `RESEARCH.md`). Patterns adopted: WhistleOut/Uswitch filters and total-cost sorting; PlanHub "price verified" stamps and refresh counters; dealnews/OzBargain/Pepper alerts, expiry and heat scores; 9to5Toys dark mode and discount-first headlines; SellCell/BankMyCell multi-buyer trade-in comparison; Airalo/Holafly destination-first eSIM flow; Reviews.org/Finder editorial-independence and methodology statements; T-Mobile/Metro bill-credit fine print (turned into our True Cost calculator).

---

## 3. Phase-wise build prompt

Use these phases in order. Each phase ends with a checkable deliverable.

### Phase 1 — Foundation & compliance shell
> Build a static, dependency-free website for the domain **Mobile.Deals** that deploys on GitHub Pages (free plan, `main` branch, repo root). Use relative URLs everywhere so it works on both `webworksa1.github.io/mobile-deals/` and `https://mobile.deals/`.
> - Generator: `scripts/build.py` (Python 3 stdlib only) renders page fragments in `src/pages/*.html` and Markdown guides in `src/guides/*.md` into `*/index.html`, plus `sitemap.xml`, `feed.xml`, `data/search.json`, `404.html`.
> - Every page `<head>` carries the AdSense loader `<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6620975821265271" crossorigin="anonymous"></script>` and `<meta name="google-adsense-account" content="ca-pub-6620975821265271">`. Root `ads.txt`: `google.com, pub-6620975821265271, DIRECT, f08c47fec0942fa0`.
> - Every page starts with a thin top bar: "Contact, if you are interested in this website / domain name / Sponsorship / Advertisement / Partnership" linking to `https://web.works/contact` (link text never shows the URL).
> - All forms post to one inbox through FormSubmit's AJAX endpoint; the address is assembled in JavaScript from an encoded string at submit time, so it never appears in HTML, text or `mailto:` links.
> - Required pages: About (incl. editorial policy + how we make money), Contact (form), Privacy (Google AdSense cookie disclosure, GDPR/CCPA), Terms, Disclosures (affiliate + trademark/copyright: independent, not affiliated with any business named "Mobile Deals"/"MobileDeals" or similar; marks belong to owners).
> - Brand: "Mobile.Deals" (always with the dot). Ink-navy + signal-green palette, coral for "hot". Light/dark mode, mobile drawer nav, site search (Ctrl/⌘+K), cookie notice, schema.org Organization + WebSite + SearchAction.

### Phase 2 — Original tools (AdSense-safe value)
> Ship these client-side tools (vanilla JS in `assets/js/tools.js`), each pre-rendered with explanatory copy so crawlers see content:
> 1. **Plan Finder** (`/plans/`): filter by budget, data (5/15/20/unlimited), lines (1–6, uses real multi-line pricing where known), network, hotspot; sort by price, cost per GB, 24-month total. Data in `data/plans.json` with source URL and "last checked" date per plan.
> 2. **Data Usage Calculator**: hours/day of video, social, music, calls, browsing → GB/month → recommended tier.
> 3. **True Cost Calculator** (`/phones/`): "free phone" bill-credit deal vs unlocked phone + cheaper plan over 12/24/36 months, incl. cost of leaving early.
> 4. **Is-this-a-good-deal checker**: MSRP, offer price, months since launch, new/refurb → verdict.
> 5. **Trade-in Value Estimator** (`/trade-in/`): brand, launch price, age, storage, condition → value range, then a "get real offers" lead form.
> 6. **Travel eSIM vs roaming calculator** (`/esim/`).

### Phase 3 — Lead-generation engine (dedicated section `/save/`)
> - **Free Bill Audit**: 3-step wizard with progress bar → step 1 carrier, monthly bill, lines; step 2 data use + needs → instant annual-savings figure and the top 3 matching plans (commitment first) → step 3 short form (name, email, optional phone, consent) that sends the full audit inputs as hidden fields.
> - **Business lines quote** (`/business/`): 5+ lines, fleet/BYOD questions — the highest-value lead.
> - **Deal alerts** signup on deals page, footer and home; **trade-in offers** form; **submit a deal** form.
> - Conversion rules: one primary CTA per screen, show value before asking, ≤4 required fields, honeypot anti-spam, inline success state, no fake testimonials or fake scarcity.

### Phase 4 — Live content & self-updating automation
> - `scripts/refresh.py` pulls public RSS feeds from deal communities and publishers (9to5Toys, 9to5Google deals, Slickdeals, dealnews, OzBargain Mobile, HotUKDeals, mydealz, Dealabs, RedFlagDeals, Google News regional queries), keeps only mobile items (keyword gates + exclusions), tags region/category, extracts price and community heat, de-duplicates, keeps 21 days / 240 items in `data/deals.json`. Headlines link to the original source; descriptions are never copied.
> - It also reads YouTube channel feeds (phone reviewers) into `data/videos.json`; pages use privacy-enhanced lite embeds.
> - Derived data: **Deal Radar** (most-discussed models), **Deal of the Day**, refresh counters, sitemap `lastmod`.
> - `.github/workflows/refresh.yml`: on push, every 6 hours, and manual dispatch → refresh → build → commit to `main` (GitHub Pages redeploys automatically).

### Phase 5 — Guides & video (approval-grade content)
> Write 12 original guides (600–900 words, FAQ section → FAQPage schema): choosing a plan, bill credits decoded, prepaid vs postpaid, MVNOs, unlocked phones, trade-in, refurbished checklist, best time to buy, travel eSIM, family-plan math, business plans, switching carriers. Each links to the relevant tool. `/videos/` shows the latest phone-review videos.

### Phase 6 — Monetization layers
> - AdSense Auto ads via the head tag; optional manual units appear only when slot IDs are set in `assets/js/config.js` (no empty boxes).
> - Affiliate links: plan cards read optional affiliate URLs from `config.js` and add `rel="sponsored nofollow"`.
> - `/support/`: donation tiers (operations, promotions & marketing, hiring talent, contests & prizes) with planned allocation; payment links configurable, pledge form as fallback.
> - `/contests/`: monthly skill-based "Deal Hunter" contest with live countdown, entry form and official rules (no purchase necessary).
> - `/advertise/`: sponsorship, advertising and partnership packages + inquiry form + brand deal submission.
> - `/careers/`: open roles (deal hunters, writers, video creators, moderators, partnerships) + application form.

### Phase 7 — SEO, performance, accessibility
> Unique title/description per page, canonical to `https://mobile.deals/…`, Open Graph, JSON-LD (Article, FAQPage, BreadcrumbList), XML sitemap, RSS, robots.txt, semantic landmarks, keyboard focus states, `prefers-reduced-motion`, lazy images, no layout-shifting ad containers, Lighthouse ≥90.

### Phase 8 — Deploy & verify
> Push to `WEBWORKSA1/mobile-deals` `main`; enable Pages (Deploy from branch → main → / root); run the workflow once; verify: AdSense tag and top bar on every page, inbox address absent from every file, forms submit, workflow commits, live URL loads.

### Phase 9 — Expansion roadmap
> Country plan finders (CA, UK, AU, IN), per-model deal pages, price-history charts from accumulated `deals.json`, email digest via newsletter tool, community voting on deals, AI "ask a plan question" assistant, Spanish/French/Hindi editions.
