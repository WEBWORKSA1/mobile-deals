#!/usr/bin/env python3
"""Mobile.Deals static site generator (Python 3 stdlib only).

Renders src/pages/*.html and src/guides/*.md into the site root, plus
sitemap.xml, feed.xml, data/search.json and data/radar.json.
"""
import datetime as dt
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://mobile.deals/"
BRAND = "Mobile.Deals"
ADSENSE = "ca-pub-6620975821265271"
CONTACT_URL = "https://web.works/contact"
NOW = dt.datetime.now(dt.timezone.utc)
VER = NOW.strftime("%Y%m%d%H%M")
CAT_LABEL = {"phones": "Phones", "plans": "Plans & SIMs", "accessories": "Accessories", "wearables": "Tablets & wearables"}


def esc(s):
    return html.escape(str(s or ""), quote=True)


def load(rel, default):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return default


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def parse_iso(s):
    try:
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return NOW


def human(d):
    return d.strftime("%b %-d, %Y, %H:%M UTC")


# ---------------------------------------------------------------- data
DEALS = load("data/deals.json", {"items": []})
ITEMS = sorted(DEALS.get("items", []), key=lambda x: x.get("date", ""), reverse=True)
VIDEOS = load("data/videos.json", {"items": []})
CHANNELS = load("data/channels.json", [])
PLANS = load("data/plans.json", {"plans": []})
UPDATED = parse_iso(DEALS.get("updated") or NOW.isoformat())

WORDS = {"pro": "Pro", "max": "Max", "xl": "XL", "plus": "Plus", "ultra": "Ultra", "fe": "FE", "edge": "Edge",
         "fold": "Fold", "flip": "Flip", "air": "Air", "mini": "Mini", "lite": "Lite", "+": "+"}


def tidy(s):
    return " ".join(WORDS.get(w.lower(), w.upper() if re.fullmatch(r"[a-z]\d+\w*", w, re.I) else w.capitalize())
                    for w in s.split())


MODEL_RULES = [
    (re.compile(r"\biphone\s?(\d{2}e?)(?:\s?(pro max|pro|plus|air|mini))?", re.I),
     lambda m: "iPhone " + m.group(1).lower() + (" " + tidy(m.group(2)) if m.group(2) else "")),
    (re.compile(r"\biphone air\b", re.I), lambda m: "iPhone Air"),
    (re.compile(r"\bgalaxy\s?z\s?(fold|flip)\s?(\d{1,2})", re.I), lambda m: "Galaxy Z " + tidy(m.group(1)) + m.group(2)),
    (re.compile(r"\bgalaxy\s?(s\d{2})(?:\s?(ultra|\+|plus|fe|edge))?", re.I),
     lambda m: "Galaxy " + m.group(1).upper() + (("+" if m.group(2) in ("+",) or (m.group(2) or "").lower() == "plus" else " " + tidy(m.group(2))) if m.group(2) else "")),
    (re.compile(r"\bgalaxy\s?(a\d{2})\b", re.I), lambda m: "Galaxy " + m.group(1).upper()),
    (re.compile(r"\bpixel\s?(\d{1,2}a?)(?:\s?(pro xl|pro fold|pro|fold))?\b", re.I),
     lambda m: "Pixel " + m.group(1).lower() + (" " + tidy(m.group(2)) if m.group(2) else "")),
    (re.compile(r"\boneplus\s?(nord\s?\w+|\d{2}r?)\b", re.I), lambda m: "OnePlus " + tidy(m.group(1))),
    (re.compile(r"\bnothing phone\s?\(?(\d\w?)\)?", re.I), lambda m: "Nothing Phone (" + m.group(1) + ")"),
    (re.compile(r"\b(?:motorola|moto)\s?(razr\s?\w*|edge\s?\d{2,4}\w*|g\d{2,3}\w*)", re.I), lambda m: "Motorola " + tidy(m.group(1))),
    (re.compile(r"\bredmi note\s?(\d{1,2})(?:\s?(pro\+?|pro))?", re.I), lambda m: "Redmi Note " + m.group(1) + (" " + tidy(m.group(2)) if m.group(2) else "")),
    (re.compile(r"\bpoco\s?([xfm]\d\w*)", re.I), lambda m: "POCO " + m.group(1).upper()),
]


def radar(items):
    counts = {}
    for it in items:
        seen = set()
        for rx, fn in MODEL_RULES:
            for m in rx.finditer(it.get("title", "")):
                name = fn(m).strip()
                if name in seen:
                    continue
                seen.add(name)
                c = counts.setdefault(name, {"model": name, "count": 0, "link": it.get("link"), "date": it.get("date", "")})
                c["count"] += 1
                if it.get("date", "") > c["date"]:
                    c["date"], c["link"] = it.get("date", ""), it.get("link")
    out = sorted(counts.values(), key=lambda c: (-c["count"], c["model"]))
    return out[:24]


RADAR = radar(ITEMS)


def deal_of_day(items):
    recent = [i for i in items if (NOW - parse_iso(i.get("date"))).days <= 3]
    pool = recent or items
    if not pool:
        return None
    return sorted(pool, key=lambda i: (i.get("heat", 0), i.get("date", "")), reverse=True)[0]


# ---------------------------------------------------------------- components
ICON = {
    "search": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    "moon": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "star": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/></svg>',
    "share": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="m8.2 10.8 7.6-4.6M8.2 13.2l7.6 4.6"/></svg>',
    "logo": '<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="9" y="3" width="14" height="26" rx="4"/><path d="M13 13l3 6 3-6" /><circle cx="16" cy="25" r="1"/></svg>',
}


def deal_card(it, featured=False):
    cat = it.get("cat", "phones")
    d = parse_iso(it.get("date"))
    price = f'<span class="price">{esc(it["price"])}</span>' if it.get("price") else ""
    heat = f'<span class="heat">Hot {int(it["heat"])}&deg;</span>' if it.get("heat", 0) > 0 else ""
    link = esc(it.get("link", "#"))
    title = esc(it.get("title", ""))
    cls = "deal-card featured card" if featured else "deal-card card"
    return (f'<article class="{cls}" data-region="{esc(it.get("region"))}" data-cat="{esc(cat)}" '
            f'data-date="{esc(it.get("date"))}" data-heat="{int(it.get("heat", 0))}" data-id="{esc(it.get("id"))}">'
            f'<div class="deal-top"><span class="tag t-{esc(cat)}">{esc(CAT_LABEL.get(cat, cat.title()))}</span>'
            f'<span class="region-badge">{esc(it.get("region"))}</span><time datetime="{esc(it.get("date"))}">{d.strftime("%b %-d")}</time></div>'
            f'<h3 class="deal-title"><a href="{link}" target="_blank" rel="nofollow noopener">{title}</a></h3>'
            f'<div class="deal-meta">{price}<span class="src">via {esc(it.get("source"))}</span>{heat}</div>'
            f'<div class="deal-actions"><a class="btn btn-sm btn-primary" href="{link}" target="_blank" rel="nofollow noopener">Get deal <span aria-hidden="true">&#8599;</span></a>'
            f'<button class="icon-btn save-btn" type="button" data-save="{esc(it.get("id"))}" aria-pressed="false" aria-label="Save deal">{ICON["star"]}</button>'
            f'<button class="icon-btn" type="button" data-share="{link}" data-title="{title}" aria-label="Share deal">{ICON["share"]}</button></div></article>')


def radar_html(n):
    rows = RADAR[:n]
    if not rows:
        return '<p class="muted">The radar fills up as new deals arrive.</p>'
    top = rows[0]["count"] or 1
    lis = "".join(
        f'<li><a href="{esc(r["link"])}" target="_blank" rel="nofollow noopener"><span class="rk">{i + 1}</span>'
        f'<span class="model">{esc(r["model"])}</span><span class="bar"><i style="width:{max(8, round(r["count"] / top * 100))}%"></i></span>'
        f'<span class="count">{r["count"]} deal{"s" if r["count"] != 1 else ""}</span></a></li>'
        for i, r in enumerate(rows))
    return f'<ol class="radar card">{lis}</ol>'


def plan_total(p, lines=1):
    m = (p.get("multi") or {}).get(str(lines))
    base = m if m is not None else p["price"] * lines
    if p.get("perGB"):
        base += p["perGB"] * 3 * lines
    return base


def plan_card(p, lines=1):
    data = "Unlimited data" if p["data"] >= 999 else ("Pay per GB ($%d/GB)" % p["perGB"] if p.get("perGB") else f'{p["data"]}GB data')
    total = plan_total(p, lines)
    gb = 50 if p["data"] >= 999 else (3 if p.get("perGB") else p["data"])
    feats = [data, "Hotspot included" if p.get("hotspot") else "No hotspot listed", p.get("term", ""), p.get("perks", "")]
    lis = "".join(f"<li>{esc(f)}</li>" for f in feats if f)
    price = ("$%g" % p["price"])
    return (f'<article class="card plan-card"><div class="plan-top"><div><p class="plan-carrier">{esc(p["carrier"])}</p>'
            f'<h3 class="plan-name">{esc(p["plan"])}</h3></div><span class="net">{esc(p["network"])}</span></div>'
            f'<p class="plan-price"><b>{price}</b><span>/mo per line</span></p><ul class="plan-feats">{lis}</ul>'
            f'<p class="plan-total">24-mo total, {lines} line: <b>${total * 24:,.0f}</b> &middot; ${total / lines / gb:.2f}/GB</p>'
            f'<p class="plan-best">Best for: {esc(p.get("best", ""))}</p>'
            f'<a class="btn btn-primary btn-sm btn-block" href="{esc(p["url"])}" data-aff="{esc(p.get("aff", ""))}" target="_blank" rel="nofollow noopener sponsored">See plan <span aria-hidden="true">&#8599;</span></a></article>')


def plans_cards():
    ps = sorted(PLANS.get("plans", []), key=lambda p: plan_total(p))
    return "".join(plan_card(p) for p in ps)


def guide_cards(guides, n=None):
    gs = guides[:n] if n else guides
    return "".join(
        f'<a class="card guide-card" href="{{{{ROOT}}}}guides/{g["slug"]}/" data-reveal><span class="tag t-{esc(g["category"].lower())}">{esc(g["category"])}</span>'
        f'<h3>{esc(g["title"])}</h3><p>{esc(g["description"])}</p><span class="meta">{esc(g["read"])} min read</span></a>' for g in gs)


def videos_grid(n):
    items = VIDEOS.get("items", [])
    ok = set(VIDEOS.get("channels_ok", []))
    if items:
        rel = [v for v in items if v.get("rel")] or items
        return "".join(
            f'<article class="card video-card"><button class="yt-lite" type="button" data-id="{esc(v["id"])}" aria-label="Play: {esc(v["title"])}">'
            f'<img src="https://i.ytimg.com/vi/{esc(v["id"])}/hqdefault.jpg" alt="" loading="lazy" width="480" height="360"><span class="play"></span></button>'
            f'<h3>{esc(v["title"])}</h3><p class="meta">{esc(v["channel"])} &middot; {parse_iso(v.get("date")).strftime("%b %-d, %Y")}</p></article>'
            for v in rel[:n])
    chans = [c for c in CHANNELS if not ok or c["id"] in ok][: max(1, min(n, 6))]
    return "".join(
        f'<article class="card video-card"><button class="yt-lite yt-list" type="button" data-list="UU{esc(c["id"][2:])}" aria-label="Play latest videos from {esc(c["name"])}">'
        f'<span class="yt-ph"><b>{esc(c["name"])}</b><small>Latest uploads</small></span><span class="play"></span></button>'
        f'<h3>Latest from {esc(c["name"])}</h3><p class="meta">Playlist &middot; updates automatically</p></article>' for c in chans)


HONEYPOT = '<div class="hp" aria-hidden="true"><label>Leave this empty<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div>'
CONSENT = ('<label class="check consent"><input type="checkbox" name="consent" value="yes" required>'
           '<span>I agree to the <a href="{{ROOT}}privacy/">Privacy Policy</a> and to be contacted about this request.</span></label>')


# ---------------------------------------------------------------- markdown
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)

    def link(m):
        url = m.group(2)
        ext = url.startswith("http")
        return f'<a href="{url}"' + (' target="_blank" rel="noopener"' if ext else "") + f">{m.group(1)}</a>"
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, s)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def markdown(md):
    """Return (html, toc, faq)."""
    lines = md.strip("\n").split("\n")
    out, toc, faq = [], [], []
    i, in_faq, h2count = 0, False, 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("## "):
            t = ln[3:].strip()
            in_faq = t.lower() == "faq"
            h2count += 1
            if h2count == 3:
                out.append('<div class="ad-slot" data-slot="guideMid"></div>')
            sid = slugify(t)
            toc.append((sid, t))
            out.append(f'<h2 id="{sid}">{inline(t)}</h2>')
            i += 1
            continue
        if ln.startswith("### "):
            q = ln[4:].strip()
            if in_faq:
                i += 1
                ans = []
                while i < len(lines) and lines[i].strip() and not lines[i].startswith("#"):
                    ans.append(lines[i].strip())
                    i += 1
                a = " ".join(ans)
                faq.append((q, a))
                out.append(f'<details class="faq"><summary>{inline(q)}</summary><div><p>{inline(a)}</p></div></details>')
                continue
            out.append(f"<h3>{inline(q)}</h3>")
            i += 1
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[2:]]
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
            continue
        if re.match(r"^(- |\d+\. )", ln):
            ordered = bool(re.match(r"^\d+\. ", ln))
            items = []
            while i < len(lines) and re.match(r"^(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i]).strip())
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        if ln.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith("> "):
                buf.append(lines[i][2:].strip())
                i += 1
            out.append(f'<div class="callout">{inline(" ".join(buf))}</div>')
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||- |\d+\. |> )", lines[i]):
            buf.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out), toc, faq


def front(text, start, end):
    m = re.match(rf"^\s*{re.escape(start)}\s*\n(.*?)\n\s*{re.escape(end)}\s*\n?", text, re.S)
    meta = {}
    if not m:
        return meta, text
    for ln in m.group(1).split("\n"):
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip()] = v.strip().strip('"') if v.strip().startswith('"') and v.strip().endswith('"') else v.strip()
    return meta, text[m.end():]


def load_guides():
    gs = []
    for f in sorted((ROOT / "src/guides").glob("*.md")):
        meta, body = front(f.read_text(encoding="utf-8"), "---", "---")
        meta["slug"] = f.stem
        meta["body"] = body
        meta.setdefault("category", "Guides")
        meta.setdefault("read", "5")
        meta.setdefault("date", NOW.date().isoformat())
        gs.append(meta)
    order = ["how-to-choose-a-phone-plan", "free-phone-bill-credits-explained", "phone-trade-in-guide", "best-time-to-buy-a-phone",
             "travel-esim-guide", "prepaid-vs-postpaid"]
    gs.sort(key=lambda g: (order.index(g["slug"]) if g["slug"] in order else 99, g["title"]))
    return gs


# ---------------------------------------------------------------- layout
NAV = [("deals", "deals/", "Deals"), ("plans", "plans/", "Plans"), ("phones", "phones/", "Phones"),
       ("trade-in", "trade-in/", "Trade-in"), ("esim", "esim/", "eSIM"), ("guides", "guides/", "Guides"), ("videos", "videos/", "Videos")]
MORE = [("business", "business/", "Business quote"), ("support", "support/", "Support us"), ("contests", "contests/", "Contests"),
        ("advertise", "advertise/", "Advertise & partner"), ("careers", "careers/", "Careers"), ("about", "about/", "About"), ("contact", "contact/", "Contact")]


def header(nav):
    def a(k, href, label):
        cur = ' aria-current="page"' if k == nav else ""
        return f'<a href="{{{{ROOT}}}}{href}"{cur}>{label}</a>'
    main = "".join(a(*x) for x in NAV)
    more = "".join(a(*x) for x in MORE)
    return f'''<div class="topbar"><div class="container"><a href="{CONTACT_URL}" target="_blank" rel="noopener">Contact, if you are interested in this website / domain name / Sponsorship / Advertisement / Partnership <span aria-hidden="true">&rarr;</span></a></div></div>
<header class="site-header"><div class="container header-inner">
<a class="logo" href="{{{{ROOT}}}}" aria-label="{BRAND} home"><span class="logo-mark">{ICON["logo"]}</span><span class="logo-text">Mobile<b>.Deals</b></span></a>
<nav class="main-nav" id="mainNav" aria-label="Main">{main}<details class="more"><summary>More</summary><div class="more-menu">{more}</div></details>
<a class="btn btn-primary btn-sm nav-cta" href="{{{{ROOT}}}}save/">Free Bill Audit</a></nav>
<div class="header-actions"><button class="icon-btn" id="searchOpen" type="button" aria-label="Search (Ctrl+K)">{ICON["search"]}</button>
<button class="icon-btn" id="themeToggle" type="button" aria-label="Toggle dark mode">{ICON["moon"]}</button>
<a class="btn btn-primary btn-sm hide-md" href="{{{{ROOT}}}}save/">Free Bill Audit</a>
<button class="icon-btn nav-toggle" id="navToggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mainNav">{ICON["menu"]}</button></div>
</div></header>'''


def footer():
    return f'''<footer class="site-footer"><div class="container">
<div class="footer-top"><div class="footer-brand"><a class="logo" href="{{{{ROOT}}}}"><span class="logo-mark">{ICON["logo"]}</span><span class="logo-text">Mobile<b>.Deals</b></span></a>
<p>The Mobile Savings Engine. Live deals, honest math, free tools.</p><p class="micro">Deals refreshed {human(UPDATED)} &middot; {len(ITEMS)} live deals</p></div>
<form class="form footer-form" data-form="newsletter" data-subject="Newsletter signup — Mobile.Deals" data-success="You're subscribed. Welcome aboard!">
<label class="field"><span>Weekly best mobile deals, free</span><span class="inline-input"><input type="email" name="email" required placeholder="you@example.com" autocomplete="email"><button class="btn btn-primary" type="submit">Subscribe</button></span></label>
{HONEYPOT}<input type="hidden" name="consent" value="yes (newsletter signup)"><p class="micro">No spam. Unsubscribe anytime. See our <a href="{{{{ROOT}}}}privacy/">Privacy Policy</a>.</p><p class="form-status" role="status" aria-live="polite"></p></form></div>
<div class="footer-cols">
<div><h2>Tools</h2><a href="{{{{ROOT}}}}save/">Free Bill Audit</a><a href="{{{{ROOT}}}}plans/">Plan Finder</a><a href="{{{{ROOT}}}}plans/#data-calculator">Data Calculator</a><a href="{{{{ROOT}}}}phones/#true-cost">True Cost Calculator</a><a href="{{{{ROOT}}}}phones/#deal-check">Good-Deal Checker</a><a href="{{{{ROOT}}}}trade-in/">Trade-in Estimator</a><a href="{{{{ROOT}}}}esim/">eSIM vs Roaming</a></div>
<div><h2>Explore</h2><a href="{{{{ROOT}}}}deals/">Live deals</a><a href="{{{{ROOT}}}}deals/#alerts">Deal alerts</a><a href="{{{{ROOT}}}}phones/#radar">Deal Radar</a><a href="{{{{ROOT}}}}guides/">Guides</a><a href="{{{{ROOT}}}}videos/">Videos</a><a href="{{{{ROOT}}}}business/">Business quote</a><a href="{{{{ROOT}}}}feed.xml">RSS feed</a></div>
<div><h2>Get involved</h2><a href="{{{{ROOT}}}}support/">Support us</a><a href="{{{{ROOT}}}}contests/">Monthly contest</a><a href="{{{{ROOT}}}}advertise/">Advertise & partner</a><a href="{{{{ROOT}}}}careers/">Careers</a><a href="{{{{ROOT}}}}deals/#alerts">Submit a deal</a></div>
<div><h2>Company</h2><a href="{{{{ROOT}}}}about/">About & editorial policy</a><a href="{{{{ROOT}}}}contact/">Contact</a><a href="{{{{ROOT}}}}privacy/">Privacy Policy</a><a href="{{{{ROOT}}}}terms/">Terms of Use</a><a href="{{{{ROOT}}}}disclosure/">Disclosures</a><a href="{CONTACT_URL}" target="_blank" rel="noopener">Buy or sponsor this site</a></div>
</div>
<div class="footer-legal"><p><strong>Independent:</strong> Mobile.Deals is not affiliated with any carrier, manufacturer, retailer, or any business using the name “Mobile Deals”, “MobileDeals” or similar. Product and company names are trademarks of their respective owners, used for identification only. Some links are affiliate links; we may earn a commission at no cost to you. Deal headlines link to and belong to their original publishers. Prices change frequently; confirm with the seller.</p>
<p>&copy; <span data-year>2026</span> Mobile.Deals. All rights reserved. Original content, tools and design are protected by copyright.</p></div>
</div></footer>
<div class="cookie-bar" id="cookieBar" hidden><p>We use cookies for ads (Google AdSense) and to remember your preferences. <a href="{{{{ROOT}}}}privacy/">Learn more</a>.</p><button class="btn btn-primary btn-sm" id="cookieAccept" type="button">Got it</button></div>
<dialog class="search-dialog" id="searchDialog" aria-label="Search Mobile.Deals"><form method="dialog" class="search-box"><input id="searchInput" type="search" placeholder="Search deals, plans, guides, tools…" autocomplete="off" aria-label="Search"><button class="btn btn-ghost btn-sm" value="close">Esc</button></form><ul id="searchResults" class="search-results"></ul></dialog>
<div class="toast" id="toast" role="status" aria-live="polite"></div>'''


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def faq_schema(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def page(title, desc, path, nav, body, crumbs=None, schemas=None, og_type="website"):
    depth = 0 if path in ("", "404.html") else path.rstrip("/").count("/") + 1
    root = "../" * depth
    schemas = list(schemas or [])
    pairs = [(strip_tags(q), strip_tags(a)) for q, a in re.findall(r'<details class="faq"[^>]*><summary>(.*?)</summary><div>(.*?)</div></details>', body, re.S)]
    if pairs and not any(s.get("@type") == "FAQPage" for s in schemas):
        schemas.append(faq_schema(pairs))
    crumb_html = ""
    if crumbs:
        trail = [("Home", "")] + crumbs
        crumb_html = '<nav class="crumbs container" aria-label="Breadcrumb">' + " <span>/</span> ".join(
            (f'<a href="{{{{ROOT}}}}{u}">{esc(n)}</a>' if k < len(trail) - 1 else f'<span aria-current="page">{esc(n)}</span>')
            for k, (n, u) in enumerate(trail)) + "</nav>"
        schemas.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": k + 1, "name": n, "item": SITE + u} for k, (n, u) in enumerate(trail)]})
    needs_plans = any(x in body for x in ('id="planFinder"', 'id="audit"', 'id="quickSave"'))
    plans_json = ('<script type="application/json" id="plansData">' + json.dumps(PLANS.get("plans", [])) + "</script>") if needs_plans else ""
    base = ('<script>(function(){var p=location.pathname,b=p.indexOf("/mobile-deals/")===0?"/mobile-deals/":"/";'
            'document.write(\'<base href="\'+b+\'">\');})();</script>') if path == "404.html" else ""
    canon = SITE + ("" if path == "404.html" else path)
    doc = f'''<!doctype html>
<html lang="en" data-root="{root}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{base}<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta name="google-adsense-account" content="{ADSENSE}">
<meta name="theme-color" content="#0b1220">
<meta name="robots" content="{"noindex" if path == "404.html" else "index,follow,max-image-preview:large"}">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canon}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}">
<link rel="icon" href="{{{{ROOT}}}}assets/img/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="{{{{ROOT}}}}manifest.webmanifest">
<link rel="alternate" type="application/rss+xml" title="{BRAND}" href="{{{{ROOT}}}}feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap">
<link rel="stylesheet" href="{{{{ROOT}}}}assets/css/site.css?v={VER}">
<script>document.documentElement.classList.add("js");try{{var t=localStorage.getItem("md-theme");if(t)document.documentElement.setAttribute("data-theme",JSON.parse(t));}}catch(e){{}}</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE}" crossorigin="anonymous"></script>
{"".join(jsonld(s) for s in schemas)}
</head>
<body data-nav="{nav}">
<a class="skip" href="#main">Skip to content</a>
{header(nav)}
<main id="main">{crumb_html}{body}</main>
{footer()}
{plans_json}
<script src="{{{{ROOT}}}}assets/js/config.js?v={VER}" defer></script>
<script src="{{{{ROOT}}}}assets/js/site.js?v={VER}" defer></script>
<script src="{{{{ROOT}}}}assets/js/tools.js?v={VER}" defer></script>
</body>
</html>
'''
    return doc.replace("{{ROOT}}", root)


# ---------------------------------------------------------------- render
def fill(body, guides):
    dod = deal_of_day(ITEMS)
    rep = {
        "{{HONEYPOT}}": HONEYPOT, "{{CONSENT}}": CONSENT,
        "{{UPDATED}}": UPDATED.strftime("%b %-d, %H:%M UTC"),
        "{{STATS_DEALS}}": str(len(ITEMS)),
        "{{STATS_SOURCES}}": str(max(1, len(set(DEALS.get("sources_ok", [])) or {i.get("source") for i in ITEMS}))),
        "{{PLANS_COUNT}}": str(len(PLANS.get("plans", []))),
        "{{PLANS_CHECKED}}": dt.date.fromisoformat(PLANS.get("checked", NOW.date().isoformat())).strftime("%b %-d, %Y"),
        "{{ALL_DEALS}}": "".join(deal_card(i) for i in ITEMS) or '<p class="muted">New deals are on the way. Check back shortly.</p>',
        "{{DEAL_OF_DAY}}": deal_card(dod, featured=True) if dod else "",
        "{{PLANS_CARDS}}": plans_cards(),
        "{{GUIDES_GRID}}": guide_cards(guides),
    }
    for k, v in rep.items():
        body = body.replace(k, v)
    body = re.sub(r"\{\{LATEST_DEALS:(\d+)\}\}", lambda m: "".join(deal_card(i) for i in ITEMS[: int(m.group(1))]), body)
    body = re.sub(r"\{\{RADAR:(\d+)\}\}", lambda m: radar_html(int(m.group(1))), body)
    body = re.sub(r"\{\{GUIDES_GRID:(\d+)\}\}", lambda m: guide_cards(guides, int(m.group(1))), body)
    body = re.sub(r"\{\{VIDEOS_GRID:(\d+)\}\}", lambda m: videos_grid(int(m.group(1))), body)
    return body


def build():
    guides = load_guides()
    urls, search = [], []
    home_schema = [
        {"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": SITE, "logo": SITE + "assets/img/favicon.svg"},
        {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE,
         "potentialAction": {"@type": "SearchAction", "target": SITE + "deals/?q={search_term_string}", "query-input": "required name=search_term_string"}},
    ]
    for f in sorted((ROOT / "src/pages").glob("*.html")):
        meta, body = front(f.read_text(encoding="utf-8"), "<!--", "-->")
        path = meta.get("path", "")
        crumbs = [(meta["crumb"], path)] if meta.get("crumb") else None
        out = page(meta["title"], meta["description"], path, meta.get("nav", ""), fill(body, guides), crumbs,
                   home_schema if path == "" else None)
        write("404.html" if path == "404.html" else (path + "index.html"), out)
        if path != "404.html":
            urls.append((path, NOW.date().isoformat(), "daily" if path in ("", "deals/", "phones/", "videos/") else "weekly"))
            search.append({"t": meta["title"].split(" — ")[0], "u": path, "d": meta["description"], "k": "page"})

    for idx, g in enumerate(guides):
        body_html, toc, faq = markdown(g["body"])
        related = [x for x in guides if x["slug"] != g["slug"]]
        related = ([x for x in related if x["category"] == g["category"]] + [x for x in related if x["category"] != g["category"]])[:3]
        toc_html = "".join(f'<li><a href="#{sid}">{esc(t)}</a></li>' for sid, t in toc)
        date = dt.date.fromisoformat(g["date"])
        body = f'''<article class="section pt0"><div class="container guide-layout">
<div class="guide-main"><header class="guide-head"><span class="tag t-{esc(g["category"].lower())}">{esc(g["category"])}</span>
<h1>{esc(g["title"])}</h1><p class="lead">{esc(g["description"])}</p>
<p class="meta">Updated <time datetime="{g["date"]}">{date.strftime("%B %-d, %Y")}</time> &middot; {esc(g["read"])} min read &middot; By the Mobile.Deals team</p></header>
<div class="prose">{body_html}</div>
<div class="ad-slot" data-slot="guideEnd"></div>
<div class="cta-band small"><div><p class="kicker">Free &middot; 60 seconds</p><h2>See what you could save</h2><p class="muted">Run the Bill Audit on your actual bill.</p></div><a class="btn btn-primary btn-lg" href="{{{{ROOT}}}}save/">Start my Bill Audit</a></div>
</div>
<aside class="guide-side"><div class="card toc-card"><h2 class="h4">On this page</h2><ol class="toc">{toc_html}</ol></div>
<div class="card"><h2 class="h4">Free tools</h2><ul class="tool-links"><li><a href="{{{{ROOT}}}}save/">Free Bill Audit</a></li><li><a href="{{{{ROOT}}}}plans/">Plan Finder</a></li><li><a href="{{{{ROOT}}}}phones/#true-cost">True Cost Calculator</a></li><li><a href="{{{{ROOT}}}}trade-in/">Trade-in Estimator</a></li><li><a href="{{{{ROOT}}}}esim/">eSIM vs Roaming</a></li></ul></div></aside>
</div></article>
<section class="section section-alt"><div class="container"><h2>Keep reading</h2><div class="grid grid-3">{guide_cards(related)}</div></div></section>'''
        path = f"guides/{g['slug']}/"
        schemas = [{"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["description"],
                    "datePublished": g["date"], "dateModified": g["date"], "author": {"@type": "Organization", "name": "Mobile.Deals team"},
                    "publisher": {"@type": "Organization", "name": BRAND, "logo": {"@type": "ImageObject", "url": SITE + "assets/img/favicon.svg"}},
                    "mainEntityOfPage": SITE + path}]
        if faq:
            schemas.append(faq_schema([(q, strip_tags(inline(a))) for q, a in faq]))
        write(path + "index.html", page(g["title"], g["description"], path, "guides", body,
                                         [("Guides", "guides/"), (g["title"].split(":")[0], path)], schemas, "article"))
        urls.append((path, g["date"], "monthly"))
        search.append({"t": g["title"], "u": path, "d": g["description"], "k": "guide"})

    for it in ITEMS[:150]:
        search.append({"t": it["title"], "u": it["link"], "d": f'{it.get("region")} · {it.get("source")}', "k": "deal"})
    write("data/search.json", json.dumps(search, ensure_ascii=False, separators=(",", ":")))
    write("data/radar.json", json.dumps({"updated": NOW.isoformat(), "models": RADAR}, ensure_ascii=False, indent=1))

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, d, f in urls:
        sm.append(f"<url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod><changefreq>{f}</changefreq></url>")
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")

    rss = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0"><channel>', f"<title>{BRAND}</title>", f"<link>{SITE}</link>",
           "<description>Mobile savings guides and tools from Mobile.Deals</description>", f"<lastBuildDate>{NOW.strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>"]
    for g in guides:
        d = dt.datetime.fromisoformat(g["date"] + "T12:00:00+00:00")
        rss.append(f"<item><title>{esc(g['title'])}</title><link>{SITE}guides/{g['slug']}/</link><guid>{SITE}guides/{g['slug']}/</guid>"
                   f"<pubDate>{d.strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate><description>{esc(g['description'])}</description></item>")
    rss.append("</channel></rss>")
    write("feed.xml", "\n".join(rss) + "\n")
    print(f"Built {len(urls)} pages, {len(guides)} guides, {len(ITEMS)} deals, {len(RADAR)} radar models.")


if __name__ == "__main__":
    build()
