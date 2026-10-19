# -*- coding: utf-8 -*-
"""Графические карточки для информационных постов «Мебель Inside».
Палитра сайта: --mi-ink #1C1D20, --mi-brass #C9A86A, --mi-cream #F1EBDD, --mi-green #15795C / #0F5C43.
Шрифты и знак — из репозитория content-bot (assets/), те же, что в плашке бота.
Безопасная зона: бот кадрирует Telegram в 4:3 и клеит снизу плашку с темой, поэтому весь текст
лежит в y=140..800, а футер (y>=960) виден только в ВК/MAX/ОК/Instagram.
Запуск: python make_cards.py <папка content-bot> <выходная папка> [id ...]
"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BOT = sys.argv[1]; OUT = sys.argv[2]; ONLY = set(sys.argv[3:])
HERE = os.path.dirname(os.path.abspath(__file__))
SERIF = os.path.join(BOT, "assets/fonts/PlayfairDisplay-Variable.ttf")
SANS = os.path.join(BOT, "assets/fonts/Manrope-Variable.ttf")
LOGO = os.path.join(BOT, "assets/logo.png")
INK = (28, 29, 32); BRASS = (168, 134, 70); BRASS_L = (201, 168, 106); CREAM = (241, 235, 221)
PAPER = (251, 249, 244); GREEN = (21, 121, 92); GREEN_D = (15, 92, 67); MUTED = (72, 69, 62)
W = H = 1080; X0 = 96; X1 = W - 96
SAFE_BOTTOM = 805


def font(path, size, weight):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def tracked(d, xy, text, f, fill, tr=3):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + tr


def draw_block(d, x, y, text, f, fill, maxw, lh):
    for ln in wrap(d, text, f, maxw):
        d.text((x, y), ln, font=f, fill=fill); y += lh
    return y


ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def cover(path):
    im = Image.open(path).convert("RGB"); w, h = im.size
    s = max(W / w, H / h); im = im.resize((int(w * s) + 1, int(h * s) + 1), Image.LANCZOS)
    x = (im.width - W) // 2; y = (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def base(card):
    if card.get("bg"):
        # реальное фото наших работ под полупрозрачной подложкой цвета бренда
        photo = cover(os.path.join(ROOT, card["bg"]))
        veil = Image.new("RGB", (W, H), PAPER)
        im = Image.blend(photo, veil, card.get("veil", 0.74))
    else:
        im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 14), fill=GREEN_D)
    d.rectangle((0, 14, W, 18), fill=BRASS_L)
    tracked(d, (X0, 142), card["kicker"].upper(), font(SANS, 24, 700), BRASS, 4)
    ts = card.get("tsize", 58)
    y = draw_block(d, X0, 188, card["title"], font(SERIF, ts, 700), INK, X1 - X0, int(ts * 1.16))
    d.rectangle((X0, y + 10, X0 + 90, y + 13), fill=BRASS_L)
    logo = Image.open(LOGO).convert("RGBA").resize((56, 56), Image.LANCZOS)
    im.paste(logo, (X0, 986), logo)
    tracked(d, (X0 + 74, 1000), "MEBELINSIDE.RU", font(SANS, 22, 700), BRASS, 3)
    tracked(d, (X1 - 300, 1002), "ПЯТИГОРСК · КМВ", font(SANS, 20, 600), MUTED, 3)
    return im, d, y + 42


def badge(d, cx, cy, r, label, f):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREEN_D)
    tw = d.textlength(label, font=f)
    d.text((cx - tw / 2, cy - f.size * 0.62), label, font=f, fill=PAPER)


def l_list(d, y, rows, card):
    fh = font(SANS, 33, 800); fb = font(SANS, 26, 600); fn = font(SERIF, 30, 700)
    gap = card.get("gap", 22)
    for i, (head, sub) in enumerate(rows, 1):
        top = y
        badge(d, X0 + 28, y + 24, 26, str(i), fn)
        yy = draw_block(d, X0 + 82, y, head, fh, INK, X1 - X0 - 82, 40)
        if sub:
            yy = draw_block(d, X0 + 82, yy + 2, sub, fb, MUTED, X1 - X0 - 82, 33)
        y = max(yy, top + 56) + gap
    return y


def l_table(d, y, rows, card):
    fl = font(SANS, 31, 700); fr = font(SERIF, 36, 700); fs = font(SANS, 22, 500)
    rh = card.get("rh", 90)
    d.line((X0, y, X1, y), fill=BRASS_L, width=2)
    for row in rows:
        left, right = row[0], row[1]; note = row[2] if len(row) > 2 else ""
        ly = wrap(d, left, fl, 470)
        ty = y + (rh - (len(ly) * 38 + (28 if note else 0))) // 2
        for ln in ly:
            d.text((X0, ty), ln, font=fl, fill=INK); ty += 38
        if note:
            d.text((X0, ty), note, font=fs, fill=MUTED)
        rw = d.textlength(right, font=fr)
        d.text((X1 - rw, y + (rh - 44) // 2), right, font=fr, fill=GREEN_D)
        y += rh
        d.line((X0, y, X1, y), fill=BRASS_L, width=2)
    return y


def l_steps(d, y, rows, card):
    fh = font(SANS, 33, 800); fb = font(SANS, 26, 600); fn = font(SERIF, 30, 700)
    x = X0 + 28; ys = []
    for head, sub in rows:
        ys.append(y)
        yy = draw_block(d, X0 + 82, y, head, fh, INK, X1 - X0 - 82, 40)
        if sub:
            yy = draw_block(d, X0 + 82, yy + 2, sub, fb, MUTED, X1 - X0 - 82, 33)
        y = max(yy, y + 56) + card.get("gap", 34)
    d.line((x, ys[0] + 24, x, ys[-1] + 24), fill=BRASS_L, width=3)
    for i, yy in enumerate(ys, 1):
        badge(d, x, yy + 24, 26, str(i), fn)
    return y


def l_compare(d, y, rows, card):
    a, b = card["cols"]; cw = (X1 - X0 - 28) // 2
    fh = font(SERIF, 34, 700); fb = font(SANS, 25, 700)
    for k, (name, col) in enumerate(((a, GREEN_D), (b, BRASS))):
        x = X0 + k * (cw + 28)
        d.rounded_rectangle((x, y, x + cw, y + 70), 14, fill=col)
        tw = d.textlength(name, font=fh)
        d.text((x + (cw - tw) / 2, y + 14), name, font=fh, fill=PAPER)
    y += 90; ybot = y
    for k in (0, 1):
        x = X0 + k * (cw + 28); yy = y
        for r in rows:
            if not r[k]:
                continue
            yy = draw_block(d, x + 6, yy, "· " + r[k], fb, INK, cw - 12, 33) + 14
        ybot = max(ybot, yy)
    return ybot


def l_big(d, y, rows, card):
    fb = font(SANS, 33, 700); fs = font(SANS, 27, 600)
    for head, sub in rows:
        yy = draw_block(d, X0 + 28, y, head, fb, INK, X1 - X0 - 28, 42)
        d.rounded_rectangle((X0, y + 2, X0 + 8, yy - 6), 3, fill=GREEN)
        if sub:
            yy = draw_block(d, X0 + 28, yy + 2, sub, fs, MUTED, X1 - X0 - 28, 34)
        y = yy + card.get("gap", 26)
    return y


LAY = {"list": l_list, "table": l_table, "steps": l_steps, "compare": l_compare, "big": l_big}


def main():
    cards = json.load(open(os.path.join(HERE, "cards.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    for c in cards:
        if ONLY and c["id"] not in ONLY:
            continue
        im, d, y = base(c)
        yend = LAY[c["layout"]](d, y, c["rows"], c)
        if c.get("foot"):
            ff = font(SANS, 26, 700)
            lines = wrap(d, c["foot"], ff, X1 - X0 - 40)
            hh = 34 * len(lines) + 36
            d.rounded_rectangle((X0, yend + 6, X1, yend + 6 + hh), 14, fill=(241, 235, 221))
            ty = yend + 6 + 18
            for ln in lines:
                d.text((X0 + 20, ty), ln, font=ff, fill=GREEN_D); ty += 34
            yend += 6 + hh
        flag = "  !! ЗА БЕЗОПАСНОЙ ЗОНОЙ (y>%d)" % SAFE_BOTTOM if yend > SAFE_BOTTOM else ""
        print(c["id"], "y_end=%d%s" % (yend, flag))
        pass
        im.save(os.path.join(OUT, c["id"] + ".jpg"), quality=92)


main()
