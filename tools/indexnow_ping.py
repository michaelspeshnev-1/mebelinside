#!/usr/bin/env python3
"""IndexNow: сообщить поисковикам (Bing, Яндекс и др.) об изменённых страницах. Только стандартная библиотека.

Запуск на ПК (из корня репозитория), подробности — site-blocks/indexnow/README.md:

    # конкретные адреса (по одному в строке, # — комментарий)
    python3 tools/indexnow_ping.py --urls-file urls.txt
    # адреса прямо в командной строке
    python3 tools/indexnow_ping.py https://mebelinside.ru/ https://mebelinside.ru/belye-kuhni.html
    # весь sitemap.xml сайта (или локальный файл sitemap)
    python3 tools/indexnow_ping.py --sitemap https://mebelinside.ru/sitemap.xml
    # сначала посмотреть, что уйдёт, ничего не отправляя
    python3 tools/indexnow_ping.py --urls-file urls.txt --dry-run
    # проверить, что ключ-файл лежит в корне сайта
    python3 tools/indexnow_ping.py --check-key

Ключ: --key, иначе --key-file, иначе единственный файл <32 hex>.txt в site-blocks/indexnow/.
Host: --host (по умолчанию mebelinside.ru). Адреса чужих доменов отбрасываются.
Ответы: 200 — принято; 202 — принято, ключ ещё проверяется; 400 — неверный запрос;
403 — ключ не найден/не совпал (файл не залит в корень?); 422 — адреса не того host; 429 — слишком часто.
"""
import argparse, json, os, re, sys, urllib.error, urllib.parse, urllib.request

ENDPOINTS = ["https://api.indexnow.org/indexnow", "https://yandex.com/indexnow"]
DEFAULT_HOST = "mebelinside.ru"
KEY_RE = re.compile(r"^[0-9a-fA-F]{8,128}$")
BATCH = 10000  # предел протокола на один POST
UA = {"User-Agent": "Mozilla/5.0 (compatible; mi-indexnow/1.0)"}
HERE = os.path.dirname(os.path.abspath(__file__))
KEY_DIR = os.path.join(os.path.dirname(HERE), "site-blocks", "indexnow")


def load_key(a):
    if a.key:
        key = a.key.strip()
    else:
        path = a.key_file
        if not path:
            cands = [f for f in os.listdir(KEY_DIR) if f.endswith(".txt") and KEY_RE.match(f[:-4])] if os.path.isdir(KEY_DIR) else []
            if len(cands) != 1:
                sys.exit(f"! ключ не найден: укажите --key или --key-file (в {KEY_DIR} найдено файлов-ключей: {len(cands)})")
            path = os.path.join(KEY_DIR, cands[0])
        with open(path, encoding="utf-8") as f:
            key = f.read().strip()
    if not KEY_RE.match(key):
        sys.exit("! ключ должен состоять из 8–128 символов 0-9 a-f")
    return key


def read_lines(path):
    with open(path, encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.lstrip().startswith("#")]


def fetch(url, timeout=25):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.status, r.read()


def sitemap_urls(src, depth=0):
    """URL из sitemap.xml (адрес или локальный файл); sitemapindex раскрывается на один уровень."""
    if re.match(r"^https?://", src):
        st, body = fetch(src)
        if st != 200:
            sys.exit(f"! sitemap {src}: код {st}")
    else:
        with open(src, "rb") as f:
            body = f.read()
    txt = body.decode("utf-8", "replace")
    locs = [l.replace("&amp;", "&") for l in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", txt)]
    if "<sitemapindex" in txt and depth == 0:
        out = []
        for sm in locs:
            out += sitemap_urls(sm, 1)
        return out
    return locs


def clean(urls, host):
    seen, ok, bad = set(), [], []
    for u in urls:
        p = urllib.parse.urlparse(u)
        if p.scheme not in ("http", "https") or p.netloc.lower() != host:
            bad.append(u)
        elif u not in seen:
            seen.add(u)
            ok.append(u)
    return ok, bad


def post(endpoint, payload, timeout=30):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, method="POST",
                                 headers={**UA, "Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")[:300]
    except urllib.error.HTTPError as e:
        return e.code, (e.read() or b"").decode("utf-8", "replace")[:300]
    except Exception as e:  # сеть, таймаут, TLS
        return 0, str(e)


def main():
    ap = argparse.ArgumentParser(description="Отправка URL в IndexNow (Bing, Яндекс и др.)")
    ap.add_argument("urls", nargs="*", help="адреса страниц")
    ap.add_argument("--urls-file", help="файл со списком URL, по одному в строке")
    ap.add_argument("--sitemap", help="адрес или путь к sitemap.xml")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--key")
    ap.add_argument("--key-file")
    ap.add_argument("--key-location", help="URL ключ-файла (по умолчанию https://<host>/<key>.txt)")
    ap.add_argument("--endpoint", action="append", help="свой адрес API (можно несколько); по умолчанию api.indexnow.org и yandex.com")
    ap.add_argument("--dry-run", action="store_true", help="только показать, ничего не отправлять")
    ap.add_argument("--check-key", action="store_true", help="проверить, что ключ-файл доступен на сайте")
    a = ap.parse_args()

    host = a.host.lower().strip().strip("/")
    host = re.sub(r"^https?://", "", host)
    key = load_key(a)
    key_loc = a.key_location or f"https://{host}/{key}.txt"
    print(f"host: {host}\nключ: {key}\nключ-файл: {key_loc}")

    if a.check_key:
        try:
            st, body = fetch(key_loc)
            got = body.decode("utf-8", "replace").strip()
            print(f"код {st}; содержимое {'совпадает' if got == key else 'НЕ совпадает: ' + got[:60]!r}")
            sys.exit(0 if st == 200 and got == key else 1)
        except Exception as e:
            sys.exit(f"! ключ-файл недоступен: {e}")

    urls = list(a.urls)
    if a.urls_file:
        urls += read_lines(a.urls_file)
    if a.sitemap:
        urls += sitemap_urls(a.sitemap)
    urls, bad = clean(urls, host)
    if bad:
        print(f"! отброшено (не {host} или не http/https): {len(bad)}")
        for u in bad[:10]:
            print("   ", u)
    if not urls:
        sys.exit("! нет адресов для отправки (укажите URL, --urls-file или --sitemap)")
    print(f"адресов к отправке: {len(urls)}")
    for u in urls[:20]:
        print("   ", u)
    if len(urls) > 20:
        print(f"    … и ещё {len(urls) - 20}")

    endpoints = a.endpoint or ENDPOINTS
    fails = 0
    for i in range(0, len(urls), BATCH):
        payload = {"host": host, "key": key, "keyLocation": key_loc, "urlList": urls[i:i + BATCH]}
        for ep in endpoints:
            if a.dry_run:
                print(f"[dry-run] POST {ep}: {len(payload['urlList'])} URL")
                continue
            st, txt = post(ep, payload)
            mark = "OK" if st in (200, 202) else "ОШИБКА"
            print(f"{mark} {ep}: код {st} {txt.strip()[:200]}")
            fails += st not in (200, 202)
    if a.dry_run:
        print("[dry-run] пример тела запроса:")
        print(json.dumps({"host": host, "key": key, "keyLocation": key_loc, "urlList": urls[:3]}, ensure_ascii=False, indent=1))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
