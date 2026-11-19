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

## One-time setup (as WEBWORKSA1)
1. **Add the auto-refresh workflow:** open [this pre-filled new-file link](https://github.com/WEBWORKSA1/mobile-deals/new/main?filename=.github/workflows/refresh.yml&value=name%3A%20Auto-refresh%20%26%20build%0A%0Aon%3A%0A%20%20push%3A%0A%20%20%20%20branches%3A%20%5Bmain%5D%0A%20%20%20%20paths-ignore%3A%0A%20%20%20%20%20%20-%20%27README.md%27%0A%20%20%20%20%20%20-%20%27PROMPT.md%27%0A%20%20%20%20%20%20-%20%27RESEARCH.md%27%0A%20%20schedule%3A%0A%20%20%20%20-%20cron%3A%20%2717%20%2A%2F6%20%2A%20%2A%20%2A%27%0A%20%20workflow_dispatch%3A%0A%0Apermissions%3A%0A%20%20contents%3A%20write%0A%20%20pages%3A%20write%0A%0Aconcurrency%3A%0A%20%20group%3A%20refresh-build%0A%20%20cancel-in-progress%3A%20false%0A%0Ajobs%3A%0A%20%20refresh%3A%0A%20%20%20%20runs-on%3A%20ubuntu-latest%0A%20%20%20%20timeout-minutes%3A%2015%0A%20%20%20%20steps%3A%0A%20%20%20%20%20%20-%20uses%3A%20actions%2Fcheckout%40v4%0A%0A%20%20%20%20%20%20-%20uses%3A%20actions%2Fsetup-python%40v5%0A%20%20%20%20%20%20%20%20with%3A%0A%20%20%20%20%20%20%20%20%20%20python-version%3A%20%273.12%27%0A%0A%20%20%20%20%20%20-%20name%3A%20Refresh%20live%20deals%20and%20videos%0A%20%20%20%20%20%20%20%20run%3A%20python%20scripts%2Frefresh.py%0A%20%20%20%20%20%20%20%20continue-on-error%3A%20true%0A%0A%20%20%20%20%20%20-%20name%3A%20Build%20site%0A%20%20%20%20%20%20%20%20run%3A%20python%20scripts%2Fbuild.py%0A%0A%20%20%20%20%20%20-%20name%3A%20Commit%20and%20push%20changes%0A%20%20%20%20%20%20%20%20run%3A%20%7C%0A%20%20%20%20%20%20%20%20%20%20git%20config%20user.name%20%22mobile-deals-bot%22%0A%20%20%20%20%20%20%20%20%20%20git%20config%20user.email%20%2241898282%2Bgithub-actions%5Bbot%5D%40users.noreply.github.com%22%0A%20%20%20%20%20%20%20%20%20%20git%20add%20-A%0A%20%20%20%20%20%20%20%20%20%20if%20git%20diff%20--cached%20--quiet%3B%20then%0A%20%20%20%20%20%20%20%20%20%20%20%20echo%20%22No%20changes%20to%20commit%22%0A%20%20%20%20%20%20%20%20%20%20%20%20exit%200%0A%20%20%20%20%20%20%20%20%20%20fi%0A%20%20%20%20%20%20%20%20%20%20git%20commit%20-m%20%22Auto-refresh%3A%20deals%2C%20videos%20and%20pages%20%28%24%28date%20-u%20%2B%27%25Y-%25m-%25d%20%25H%3A%25M%20UTC%27%29%29%22%0A%20%20%20%20%20%20%20%20%20%20for%20i%20in%201%202%203%3B%20do%0A%20%20%20%20%20%20%20%20%20%20%20%20git%20pull%20--rebase%20-X%20theirs%20origin%20main%20%26%26%20git%20push%20%26%26%20exit%200%0A%20%20%20%20%20%20%20%20%20%20%20%20sleep%205%0A%20%20%20%20%20%20%20%20%20%20done%0A%20%20%20%20%20%20%20%20%20%20exit%201%0A%0A%20%20%20%20%20%20-%20name%3A%20Request%20GitHub%20Pages%20rebuild%0A%20%20%20%20%20%20%20%20env%3A%0A%20%20%20%20%20%20%20%20%20%20GH_TOKEN%3A%20%24%7B%7B%20github.token%20%7D%7D%0A%20%20%20%20%20%20%20%20run%3A%20gh%20api%20-X%20POST%20%22repos%2F%24%7B%7B%20github.repository%20%7D%7D%2Fpages%2Fbuilds%22%20%3E%2Fdev%2Fnull%202%3E%261%20%26%26%20echo%20%22Pages%20build%20requested%22%20%7C%7C%20echo%20%22Pages%20not%20enabled%20yet%3B%20skipped%22%0A) and click **Commit changes** twice. (The same file is kept at `scripts/refresh-workflow.yml`.) The first run builds every page and commits it within about a minute.
2. **Turn on Pages:** [Settings → Pages](https://github.com/WEBWORKSA1/mobile-deals/settings/pages) → Source **Deploy from a branch** → `main` / `/ (root)` → Save. Live at `https://webworksa1.github.io/mobile-deals/`.
3. **Custom domain:** point `mobile.deals` DNS to GitHub Pages (A records 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153), then enter `mobile.deals` under Settings → Pages → Custom domain and tick Enforce HTTPS.
4. **Forms:** submit the Contact form once on the live site; FormSubmit emails a one-time activation link to the site inbox. Click it and every form is live.
5. **AdSense:** add the site in AdSense; turn on Auto ads and the Privacy & messaging GDPR message for EEA/UK visitors.

## Trademark & copyright
Mobile.Deals is an independent publication, not affiliated with any carrier, manufacturer, retailer, or any business using "Mobile Deals", "MobileDeals" or a similar name. Product and company names are trademarks of their respective owners, used for identification only. Deal headlines link to their original publishers. Original text, tools, code and design © 2026 Mobile.Deals. All rights reserved.
