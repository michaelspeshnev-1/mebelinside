# -*- coding: utf-8 -*-
"""Контактные листы карточек для согласования (6 шт. на лист) + media/cards/SOGLASOVANIE.md.
Запуск: python make_contact_sheets.py <папка content-bot>"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
BOT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "media", "cards")
cards = json.load(open(os.path.join(HERE, "cards.json"), encoding="utf-8"))
BG = json.load(open(os.path.join(HERE, "soglasovanie-bg.json"), encoding="utf-8"))
F = ImageFont.truetype(os.path.join(BOT, "assets/fonts/Manrope-Variable.ttf"), 19)
FB = ImageFont.truetype(os.path.join(BOT, "assets/fonts/Manrope-Variable.ttf"), 21)
try: FB.set_variation_by_axes([700])
except Exception: pass
def fit(t, f, w=480):
    while d_.textlength(t, font=f) > w and len(t) > 4:
        t = t[:-2].rstrip() + "…" if not t.endswith("…") else t[:-2] + "…"
    return t
d_ = ImageDraw.Draw(Image.new("RGB", (10, 10)))
T = 480; CAP = 84; GAP = 20
for k in range(0, len(cards), 6):
    chunk = cards[k:k + 6]
    sh = Image.new("RGB", (3 * T + 4 * GAP, 2 * (T + CAP) + 3 * GAP), "white")
    d = ImageDraw.Draw(sh)
    for i, c in enumerate(chunk):
        im = Image.open(os.path.join(OUT, c["id"] + ".jpg")).convert("RGB").resize((T, T), Image.LANCZOS)
        x = GAP + (i % 3) * (T + GAP); y = GAP + (i // 3) * (T + CAP + GAP)
        sh.paste(im, (x, y))
        dd, mm = c["id"][8:10], c["id"][5:7]
        d.text((x, y + T + 6), fit(f"{dd}.{mm}  ·  {c['title']}", FB), font=FB, fill=(28, 29, 32))
        d.text((x, y + T + 42), fit("фон: " + BG[c["id"]]["short"], F), font=F, fill=(90, 86, 78))
    rows_used = 1 if len(chunk) <= 3 else 2
    sh = sh.crop((0, 0, sh.width, rows_used * (T + CAP + GAP) + GAP))
    sh.save(os.path.join(OUT, f"SOGLASOVANIE-list-{k // 6 + 1}.jpg"), quality=88)
rows = ["# Лист согласования карточек 19.10–28.11 (на согласовании у Михаила)", "",
        "Контактные листы: `SOGLASOVANIE-list-1.jpg` … `-5.jpg` (по 6 карточек). Статус всех — **на согласовании**; в бот и Metricool новые карточки не заливались.",
        "Пометка **новый фон** — фон заменён в этой правке; «[?]» — не уверены, что фон подходит.", "",
        "| № | Дата | Тема | Что на фоне | Статус |", "|---|---|---|---|---|"]
for n, c in enumerate(cards, 1):
    b = BG[c["id"]]
    rows.append(f"| {n} | {c['id'][8:10]}.{c['id'][5:7]} | {c['title']} | {b['long']} | на согласовании |")
open(os.path.join(OUT, "SOGLASOVANIE.md"), "w", encoding="utf-8").write("\n".join(rows) + "\n")
