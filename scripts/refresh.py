#!/usr/bin/env python3
"""Refresh live data for Mobile.Deals (Python 3 stdlib only).

- Reads public RSS/Atom deal feeds listed in data/feeds.json, keeps mobile items only,
  tags region/category, extracts price + community heat, de-duplicates and keeps
  21 days / 240 items in data/deals.json. Headlines link to the original source.
- Reads YouTube channel feeds in data/channels.json into data/videos.json.
Failures are logged and skipped; existing data is never wiped.
"""
import datetime as dt
import email.utils
import hashlib
import html
import json
import pathlib
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
NOW = dt.datetime.now(dt.timezone.utc)
UA = "Mozilla/5.0 (compatible; MobileDealsBot/1.0; +https://mobile.deals/about/)"
KEEP_DAYS, MAX_ITEMS, PER_FEED = 21, 240, 25

GATE = re.compile(
    r"\b(iphones?|galaxy\s?(s|z|a)\s?\d+\w*|galaxy\s?(fold|flip|buds|watch|tab)\w*|pixel\s?(\d+\w*|buds|watch|tablet)|oneplus|motorola|moto\s?g|razr|"
    r"xiaomi|redmi|poco|nothing phone|smartphones?|phones?|handys?|cell ?phones?|mobiles?|sim|e-?sims?|prepaid|airpods|earbuds|"
    r"magsafe|power ?banks?|apple watch|smartwatch|ipad|forfaits?|tarifs?|5g)\b", re.I)
STRONG = re.compile(r"\b(iphones?|galaxy\s?(s|z|a)\s?\d+\w*|pixel\s?\d+\w*|oneplus|smartphone|sim|e-?sim|prepaid|phone plan|cell ?phone)\b", re.I)
EXCLUDE = re.compile(r"(^\[(ios|android|pc|mac|ps\d|xbox|switch|steam)\b)|\b(app store|game pass|laptop|macbook|monitor|television|\d{2,3}\s?(inch|\")\s?tv|"
                     r"vacuum|lego|mattress|air fryer|sofa|headphone stand|phone ?case for ps|mobile game)\b", re.I)


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.5"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def clean(s):
    s = html.unescape(html.unescape(s or ""))
    s = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_date(s):
    if not s:
        return NOW
    try:
        d = email.utils.parsedate_to_datetime(s)
    except Exception:
        try:
            d = dt.datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
        except Exception:
            return NOW
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return min(d.astimezone(dt.timezone.utc), NOW)


def parse_feed(raw):
    """Return list of dicts: title, link, date, source."""
    out = []
    try:
        root = ET.fromstring(raw)
        for it in root.iter("item"):
            src = it.find("source")
            out.append({"title": clean(it.findtext("title")), "link": (it.findtext("link") or "").strip(),
                        "date": parse_date(it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date")),
                        "source": clean(src.text) if src is not None and src.text else ""})
        A = "{http://www.w3.org/2005/Atom}"
        for e in root.iter(A + "entry"):
            link = ""
            for l in e.findall(A + "link"):
                if l.get("rel", "alternate") == "alternate":
                    link = l.get("href", "")
            out.append({"title": clean(e.findtext(A + "title")), "link": link,
                        "date": parse_date(e.findtext(A + "published") or e.findtext(A + "updated")), "source": ""})
        return out
    except ET.ParseError:
        text = raw.decode("utf-8", "replace")
        for block in re.findall(r"<item\b.*?</item>", text, re.S | re.I):
            t = re.search(r"<title[^>]*>(.*?)</title>", block, re.S | re.I)
            l = re.search(r"<link[^>]*>(.*?)</link>", block, re.S | re.I)
            p = re.search(r"<pubDate[^>]*>(.*?)</pubDate>", block, re.S | re.I)
            if t and l:
                out.append({"title": clean(t.group(1)), "link": clean(l.group(1)), "date": parse_date(clean(p.group(1)) if p else ""), "source": ""})
        return out


def categorize(t):
    tl = t.lower()
    if re.search(r"\b(airpods|earbuds|buds|magsafe|charger|charging|gan\d?|power ?bank|cable|cases?|screen protector|stand|mount|adapter|headphones)\b", tl) \
            and not re.search(r"\b(sim|e-?sim|prepaid|plan)\b", tl):
        return "accessories"
    if re.search(r"\b(sim|e-?sims?|prepaid|plans?|unlimited|postpaid|mvno|tarifs?|forfaits?|vertrag|\d+\s?gb\s?(/|per|a)\s?(mo|month)|/mo\b|/month|per month|lines?)\b", tl):
        return "plans"
    if re.search(r"\b(ipad|tablets?|galaxy tab|watch|smartwatch|fitbit|wearables?)\b", tl):
        return "wearables"
    return "phones"


PRICE = re.compile(r"((?:A\$|C\$|NZ\$|US\$|Rs\.?\s?|[$£€₹])\s?\d[\d,]*(?:\.\d{1,2})?|\d[\d.,]*\s?€)")


def norm(t):
    return re.sub(r"[^a-z0-9]+", "", t.lower())[:80]


def refresh_deals():
    feeds = json.loads((ROOT / "data/feeds.json").read_text(encoding="utf-8"))
    store_p = ROOT / "data/deals.json"
    store = json.loads(store_p.read_text(encoding="utf-8")) if store_p.exists() else {"items": []}
    items = {norm(i["title"]): i for i in store.get("items", [])}
    ok = []
    for f in feeds:
        try:
            entries = parse_feed(fetch(f["url"]))
        except Exception as e:  # noqa: BLE001
            print(f"[skip] {f['name']} {f['url'][:60]}: {e}", file=sys.stderr)
            continue
        kept = 0
        for e in sorted(entries, key=lambda x: x["date"], reverse=True):
            title, link = e["title"], e["link"]
            if not title or not link.startswith("http"):
                continue
            heat = 0
            m = re.match(r"^\s*(-?\d{1,5})\s?°\s*[-–]\s*(.+)$", title)
            if m:
                heat, title = int(m.group(1)), m.group(2).strip()
            source = e.get("source") or f["name"]
            if f["name"] == "Google News":
                parts = title.rsplit(" - ", 1)
                if len(parts) == 2 and len(parts[1]) < 60:
                    title, source = parts[0].strip(), e.get("source") or parts[1].strip()
            if not GATE.search(title) or (EXCLUDE.search(title) and not STRONG.search(title)):
                continue
            if (NOW - e["date"]).days > KEEP_DAYS:
                continue
            key = norm(title)
            if not key:
                continue
            pm = PRICE.search(title)
            rec = {"id": hashlib.sha1((link or title).encode()).hexdigest()[:12], "title": title[:220], "link": link,
                   "source": source[:60], "region": f["region"], "cat": categorize(title), "date": e["date"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "price": pm.group(1).strip() if pm else "", "heat": heat}
            if key in items:
                old = items[key]
                old["heat"] = max(old.get("heat", 0), heat)
                continue
            items[key] = rec
            kept += 1
            if kept >= PER_FEED:
                break
        ok.append(f["name"])
        print(f"[ok] {f['name']} ({f['region']}): +{kept}")
    cutoff = (NOW - dt.timedelta(days=KEEP_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    fresh = sorted((i for i in items.values() if i.get("date", "") >= cutoff), key=lambda i: i["date"], reverse=True)[:MAX_ITEMS]
    if ok:
        store = {"updated": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "runs": int(store.get("runs", 0)) + 1,
                 "sources_ok": sorted(set(ok)), "items": fresh}
        store_p.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"deals: {len(fresh)} kept, {len(ok)}/{len(feeds)} feeds ok")


PHONE = re.compile(r"\b(iphone|galaxy|pixel|phone|smartphone|android|oneplus|xiaomi|nothing|motorola|samsung|ios|foldable|fold|flip|apple)\b", re.I)


def refresh_videos():
    chans = json.loads((ROOT / "data/channels.json").read_text(encoding="utf-8"))
    vids, ok = [], []
    Y, A, M = "{http://www.youtube.com/xml/schemas/2015}", "{http://www.w3.org/2005/Atom}", "{http://search.yahoo.com/mrss/}"
    for c in chans:
        try:
            root = ET.fromstring(fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={c['id']}"))
        except Exception as e:  # noqa: BLE001
            print(f"[skip] video {c['name']}: {e}", file=sys.stderr)
            continue
        ok.append(c["id"])
        for e in list(root.iter(A + "entry"))[:10]:
            vid = e.findtext(Y + "videoId") or ""
            link = ""
            for l in e.findall(A + "link"):
                link = l.get("href", link)
            if not vid or "/shorts/" in link:
                continue
            title = clean(e.findtext(A + "title"))
            vids.append({"id": vid, "title": title[:160], "channel": c["name"], "date": parse_date(e.findtext(A + "published")).strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "rel": bool(PHONE.search(title))})
    if ok:
        vids.sort(key=lambda v: (v["rel"], v["date"]), reverse=True)
        out = {"updated": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "channels_ok": ok, "items": vids[:36]}
        (ROOT / "data/videos.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"videos: {len(vids)} from {len(ok)}/{len(chans)} channels")


if __name__ == "__main__":
    refresh_deals()
    refresh_videos()
