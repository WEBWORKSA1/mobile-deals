# Mobile.Deals

The Mobile Savings Engine — live mobile deals, plan finder, free bill audit, trade-in and eSIM tools. Static site, auto-refreshed every 6 hours by GitHub Actions, hosted free on GitHub Pages (`main` branch, root).

- Concept + phase-wise build prompt: [`PROMPT.md`](PROMPT.md)
- 41-site research log: [`RESEARCH.md`](RESEARCH.md)

## How it works

| Part | Where |
|---|---|
| Page bodies | `src/pages/*.html` (front matter in the first HTML comment) |
| Guides | `src/guides/*.md` |
| Generator | `scripts/build.py` → `index.html`, `*/index.html`, `sitemap.xml`, `feed.xml`, `data/search.json`, `404.html` |
| Live data | `scripts/refresh.py` → `data/deals.json`, `data/videos.json`, `data/radar.json` |
| Plans | `data/plans.json` (edit prices + `checked` date) |
| Settings | `assets/js/config.js` (affiliate URLs, donation links, ad slot IDs, contest prize) |
| Automation | `.github/workflows/refresh.yml` (push, every 6 h, manual) |

Local build: `python3 scripts/refresh.py && python3 scripts/build.py`

## One-time setup
1. **Pages:** Settings → Pages → Deploy from a branch → `main` / root.
2. **Custom domain:** point `mobile.deals` DNS to GitHub Pages (A records 185.199.108.153, .109.153, .110.153, .111.153), then add the domain in Settings → Pages.
3. **Forms:** the first form submission triggers a one-time FormSubmit activation email to the site inbox — confirm it once.
4. **AdSense:** add the site in AdSense; turn on Auto ads and the Privacy & messaging GDPR message for EEA/UK visitors.

## Trademark & copyright
Mobile.Deals is an independent publication, not affiliated with any carrier, manufacturer, retailer, or any business using "Mobile Deals", "MobileDeals" or a similar name. Product and company names are trademarks of their respective owners, used for identification only. Deal headlines link to their original publishers. Original text, tools, code and design © 2026 Mobile.Deals. All rights reserved.
