#!/usr/bin/env python3
"""Живой технический аудит сайта по sitemap.xml -> CSV (только стандартная библиотека).

Запуск (на ПК с доступом к сайту):
    python3 tools/seo_audit.py https://mebelinside.ru --out audit.csv [--limit 50] [--delay 0.3]

Для каждого URL: код ответа, цепочка редиректов, canonical, robots meta, title, description,
число H1, слов в тексте, типы JSON-LD, картинок без alt, ссылка на внутренние редиректящие URL.
Плюс отчёт в stdout: robots.txt, sitemap (URL не 200 / редиректы / canonical не равен себе),
дубли title и H1, цепочки >1 редиректа. Позиции и трафик скрипт не знает.
"""
import argparse, csv, re, sys, time, urllib.parse, urllib.request, urllib.error
from html.parser import HTMLParser
from collections import Counter

UA = {"User-Agent": "Mozilla/5.0 (compatible; mi-seo-audit/1.0)"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def fetch(url, timeout=25):
    """Один запрос без автоследования редиректам. -> (status, headers, body, location)."""
    req = urllib.request.Request(url, headers=UA)
    try:
        r = OPENER.open(req, timeout=timeout)
        return r.status, r.headers, r.read(), None
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location") if e.headers else None
        body = b""
        try:
            body = e.read()
        except Exception:
            pass
        return e.code, e.headers, body, loc
    except Exception as e:  # сеть, таймаут, TLS
        return 0, {}, str(e).encode(), None


def follow(url, max_hops=8):
    chain = []
    cur = url
    for _ in range(max_hops):
        st, hd, body, loc = fetch(cur)
        if st in (301, 302, 303, 307, 308) and loc:
            nxt = urllib.parse.urljoin(cur, loc)
            chain.append((st, cur))
            if nxt == cur or any(nxt == c for _, c in chain):
                return chain, 0, hd, b"", "loop"
            cur = nxt
            continue
        return chain, st, hd, body, cur
    return chain, 0, {}, b"", "too_many_redirects"


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.h1 = 0
        self.h1_text = ""
        self.in_h1 = False
        self.meta = {}
        self.canonical = ""
        self.jsonld = []
        self.in_jsonld = False
        self.imgs = 0
        self.imgs_no_alt = 0
        self.links = []
        self.words = 0
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1 += 1
            self.in_h1 = True
        elif tag == "meta" and a.get("name"):
            self.meta[a["name"].lower()] = a.get("content", "")
        elif tag == "link" and "canonical" in (a.get("rel") or "").lower():
            self.canonical = a.get("href", "")
        elif tag == "script":
            if (a.get("type") or "").lower() == "application/ld+json":
                self.in_jsonld = True
                self.jsonld.append("")
            self.skip += 1
        elif tag == "style":
            self.skip += 1
        elif tag == "img":
            self.imgs += 1
            if not (a.get("alt") or "").strip():
                self.imgs_no_alt += 1
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        elif tag == "script":
            self.in_jsonld = False
            self.skip = max(0, self.skip - 1)
        elif tag == "style":
            self.skip = max(0, self.skip - 1)

    def handle_data(self, d):
        if self.in_title:
            self.title += d
        if self.in_jsonld and self.jsonld:
            self.jsonld[-1] += d
        if self.skip:
            return
        if self.in_h1:
            self.h1_text += d
        self.words += len(d.split())


def ld_types(blocks):
    out = []
    for b in blocks:
        out += re.findall(r'"@type"\s*:\s*"([^"]+)"', b)
    return sorted(set(out))


def sitemap_urls(base):
    st, _, body, _ = fetch(base.rstrip("/") + "/sitemap.xml")
    if st != 200:
        print(f"! sitemap.xml: код {st}", file=sys.stderr)
        return []
    txt = body.decode("utf-8", "replace")
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", txt)
    if "<sitemapindex" in txt:
        urls = []
        for sm in locs:
            s2, _, b2, _ = fetch(sm)
            if s2 == 200:
                urls += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", b2.decode("utf-8", "replace"))
        return urls
    return locs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--out", default="audit.csv")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--delay", type=float, default=0.3)
    a = ap.parse_args()
    base = a.base.rstrip("/")
    host = urllib.parse.urlparse(base).netloc

    st, _, body, _ = fetch(base + "/robots.txt")
    print(f"== robots.txt: код {st}")
    if st == 200:
        print(body.decode("utf-8", "replace")[:3000])

    urls = sitemap_urls(base)
    if a.limit:
        urls = urls[: a.limit]
    print(f"== URL в sitemap: {len(urls)}")

    rows, internal_redirect_targets = [], Counter()
    for i, u in enumerate(urls, 1):
        chain, status, hd, body, final = follow(u)
        p = Page()
        if status == 200 and body:
            try:
                p.feed(body.decode("utf-8", "replace"))
            except Exception:
                pass
        for h in p.links:
            full = urllib.parse.urljoin(u, h)
            if urllib.parse.urlparse(full).netloc == host:
                internal_redirect_targets[full.split("#")[0]] += 1
        rows.append({
            "url": u, "status": status, "hops": len(chain),
            "redirect_chain": " > ".join(f"{s}:{c}" for s, c in chain),
            "final": final if status else final,
            "canonical": p.canonical,
            "canonical_ok": (p.canonical.rstrip("/") == u.rstrip("/")) if p.canonical else "",
            "robots": p.meta.get("robots", ""),
            "title": " ".join(p.title.split()), "title_len": len(" ".join(p.title.split())),
            "description": p.meta.get("description", ""),
            "desc_len": len(p.meta.get("description", "")),
            "h1_count": p.h1, "h1": " ".join(p.h1_text.split()),
            "words": p.words, "jsonld": ",".join(ld_types(p.jsonld)),
            "imgs": p.imgs, "imgs_no_alt": p.imgs_no_alt,
        })
        if i % 25 == 0:
            print(f"  {i}/{len(urls)}", file=sys.stderr)
        time.sleep(a.delay)

    with open(a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["url"])
        w.writeheader()
        w.writerows(rows)

    # внутренние ссылки, ведущие на URL с редиректом (проверяем только те, что в sitemap-прогоне уже редиректят)
    redir_urls = {r["url"] for r in rows if r["hops"]}
    bad_links = {u: n for u, n in internal_redirect_targets.items() if u in redir_urls}

    def lst(title, items, n=25):
        print(f"\n== {title}: {len(items)}")
        for x in items[:n]:
            print("  ", x)

    lst("не 200", [(r["status"], r["url"]) for r in rows if r["status"] != 200])
    lst("в sitemap, но с редиректом (в sitemap нужны конечные URL)", [r["url"] for r in rows if r["hops"]])
    lst("цепочки >1 редиректа", [r["redirect_chain"] for r in rows if r["hops"] > 1])
    lst("canonical не совпадает с URL", [(r["url"], r["canonical"]) for r in rows if r["canonical"] and not r["canonical_ok"]])
    lst("нет canonical", [r["url"] for r in rows if r["status"] == 200 and not r["canonical"]])
    lst("noindex в sitemap", [r["url"] for r in rows if "noindex" in r["robots"].lower()])
    lst("нет title / description", [r["url"] for r in rows if r["status"] == 200 and (not r["title"] or not r["description"])])
    lst("H1 не один", [(r["h1_count"], r["url"]) for r in rows if r["status"] == 200 and r["h1_count"] != 1])
    lst("тонкие (<150 слов)", [(r["words"], r["url"]) for r in rows if r["status"] == 200 and r["words"] < 150])
    lst("внутренние ссылки на редиректящие URL", [f"{n}× {u}" for u, n in bad_links.items()])
    for field in ("title", "h1"):
        c = Counter(r[field] for r in rows if r["status"] == 200 and r[field])
        lst(f"дубли {field}", [f"{n}× {t[:90]}" for t, n in c.items() if n > 1])
    print(f"\nCSV: {a.out}")


if __name__ == "__main__":
    main()
