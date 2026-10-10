#!/usr/bin/env python3
"""Полные списки из audit.csv (tools/seo_audit.py печатает только первые 25 строк каждого списка).

Запуск на ПК после `python3 tools/seo_audit.py https://mebelinside.ru`:
    python3 tools/audit_export.py audit.csv > audit-spiski.md
Результат — Markdown для zalivka/22a, 22b, 22 (раздел «30–45»).
"""
import csv
import sys
from collections import defaultdict

path = sys.argv[1] if len(sys.argv) > 1 else "audit.csv"
with open(path, encoding="utf-8-sig") as f:
    rows = [r for r in csv.DictReader(f) if r["status"] == "200"]


def show(title, items):
    print(f"\n## {title}: {len(items)}\n")
    for x in items:
        print(f"- {x}")


show("Нет title / description (R63)",
     [f"{r['url']} — title: «{r['title']}», H1: «{r['h1']}»"
      for r in rows if not r["title"] or not r["description"]])
show("H1 не один (R62)", [f"{r['h1_count']}× {r['url']}" for r in rows if r["h1_count"] != "1"])

for field in ("title", "h1"):
    groups = defaultdict(list)
    for r in rows:
        if r[field]:
            groups[r[field]].append(r["url"])
    dup = {k: v for k, v in groups.items() if len(v) > 1}
    print(f"\n## Дубли {field} (R64): {len(dup)} групп\n")
    for k, urls in dup.items():
        print(f"- «{k}»")
        for u in urls:
            print(f"  - {u}")

bad = ("30–45", "30-45", "30 – 45", "30—45")
show("«30–45 дней» в title / description / H1 (R27)",
     [f"{r['url']} — " + ", ".join(fl for fl in ("title", "description", "h1") if any(b in r[fl] for b in bad))
      for r in rows if any(b in r[fl] for fl in ("title", "description", "h1") for b in bad)])
