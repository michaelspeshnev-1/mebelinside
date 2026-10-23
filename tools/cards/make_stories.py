# -*- coding: utf-8 -*-
"""Instagram Stories 1080x1920 «Мебель Inside» (неделя 1: 26.10–01.11). Безопасная зона: текст в y=250..1670.
Фото — из тех же исходников, что и карусели (make_carousels.py). Запуск: python tools/cards/make_stories.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_carousels as mc
from make_carousels import (font, block, tracked, INK, GREEN, BRASS, PAPER, MUTED, WHITE, SANS, SERIF, LOGO, M)
from PIL import Image, ImageDraw, ImageOps

SW, SH = 1080, 1920
OUT = os.path.join(mc.ROOT, "media", "stories", "w1")


def photo_full(path, focus=(0.5, 0.5), retouch=True):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if retouch:
        im.thumbnail((2400, 2400), Image.LANCZOS)
        im = mc.fp.retouch(im, 1.0)[0]
    s = max(SW / im.width, SH / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x = int((im.width - SW) * focus[0]); y = int((im.height - SH) * focus[1])
    return im.crop((x, y, x + SW, y + SH))


def veil(im, y0, y1, a0, a1):
    ov = Image.new("RGBA", im.size, INK + (0,)); px = ov.load()
    for y in range(SH):
        a = a0 if y < y0 else a1 if y > y1 else int(a0 + (a1 - a0) * (y - y0) / (y1 - y0))
        for x in range(SW):
            px[x, y] = INK + (a,)
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def brand(d, im, y=1590):
    logo = Image.open(LOGO).convert("RGBA").resize((52, 52), Image.LANCZOS)
    im.paste(logo, (M, y), logo)
    tracked(d, (M + 70, y + 12), "MEBELINSIDE.RU", font(SANS, 24, 700), BRASS, 4)


def pill(d, x, y, w, h, text, f, fill=None, outline=BRASS, color=WHITE):
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=fill, outline=outline, width=3)
    tw = d.textlength(text, font=f)
    d.text((x + (w - tw) / 2, y + (h - f.size) / 2 - 4), text, font=f, fill=color)


def s1_poll():
    im = photo_full(mc.Wd("54daeb8a"), (0.5, 0.5), False)
    im = veil(im, 600, 1100, 0, 200)
    d = ImageDraw.Draw(im)
    tracked(d, (M, 780), "ЧТО ВЫБРАЛИ БЫ ВЫ?", font(SANS, 30, 700), BRASS, 5)
    y = block(d, M, 840, "В шкафу — открытые полки или ящики?", font(SERIF, 84, 700), WHITE, SW - 2 * M, 100)
    d.rectangle((M, y + 16, M + 100, y + 19), fill=BRASS)
    pill(d, M, y + 80, 430, 110, "Полки", font(SANS, 44, 800), fill=None)
    pill(d, SW - M - 430, y + 80, 430, 110, "Ящики", font(SANS, 44, 800))
    brand(d, im)
    return im


def s2_project():
    im = Image.new("RGB", (SW, SH), INK); d = ImageDraw.Draw(im)
    d.rectangle((40, 250, SW - 40, 1670), outline=BRASS, width=2)
    logo = Image.open(LOGO).convert("RGBA").resize((110, 110), Image.LANCZOS)
    im.paste(logo, (M + 20, 600), logo)
    tracked(d, (M + 150, 640), "МЕБЕЛЬ INSIDE", font(SANS, 32, 800), BRASS, 5)
    y = block(d, M + 20, 880, "Хотите такую мебель — под ваш размер?", font(SERIF, 84, 700), WHITE, SW - 2 * M - 40, 100)
    d.rectangle((M + 20, y + 16, M + 120, y + 19), fill=BRASS)
    y = block(d, M + 20, y + 70, "Напишите ПРОЕКТ в директ", font(SANS, 70, 800), BRASS, SW - 2 * M - 40, 86)
    block(d, M + 20, y + 30, "Пришлём ссылку на просчёт. 3D-проект бесплатный.", font(SANS, 38, 500), (225, 221, 211), SW - 2 * M - 40, 54)
    return im


def s3_call():
    im = Image.new("RGB", (SW, SH), INK); d = ImageDraw.Draw(im)
    d.rectangle((40, 250, SW - 40, 1670), outline=BRASS, width=2)
    tracked(d, (M + 20, 620), "ПОЗВОНИТЕ ИЛИ ЗАХОДИТЕ", font(SANS, 30, 700), BRASS, 5)
    y = block(d, M + 20, 700, "+7 928 951-63-42", font(SERIF, 96, 700), WHITE, SW - 2 * M - 40, 112)
    d.rectangle((M + 20, y + 16, M + 120, y + 19), fill=BRASS)
    y = block(d, M + 20, y + 80, "Шоурум в Пятигорске", font(SANS, 58, 800), BRASS, SW - 2 * M - 40, 72)
    y = block(d, M + 20, y + 20, "Кисловодское шоссе, 22, ТЦ «Пазл», 2 этаж", font(SANS, 40, 600), (235, 232, 224), SW - 2 * M - 40, 56)
    block(d, M + 20, y + 14, "Пн–Сб, 10:00–18:00", font(SANS, 40, 600), (235, 232, 224), SW - 2 * M - 40, 56)
    brand(d, im)
    return im


def s4_tip():
    im = photo_full(mc.K("110151"), (0.5, 0.4))
    im = veil(im, 600, 1050, 0, 200)
    d = ImageDraw.Draw(im)
    tracked(d, (M, 800), "СОВЕТ ПРИ ПРИЁМКЕ КУХНИ", font(SANS, 30, 700), BRASS, 5)
    y = block(d, M, 860, "Первым смотрите шов у мойки", font(SERIF, 84, 700), WHITE, SW - 2 * M, 100)
    d.rectangle((M, y + 16, M + 100, y + 19), fill=BRASS)
    block(d, M, y + 56, "Он должен быть сплошным, без щели, в которую может попасть вода.", font(SANS, 40, 600), (235, 232, 224), SW - 2 * M, 56)
    brand(d, im)
    return im


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    sl = [s1_poll(), s2_project(), s3_call(), s4_tip()]
    names = ["01-opros-polki-yashchiki", "02-napishite-proekt", "03-pozvonite-showroom", "04-sovet-shov-u-moyki"]
    for s, n in zip(sl, names):
        s.save(os.path.join(OUT, n + ".jpg"), quality=90, optimize=True, subsampling=0)
    th = 640; tw = int(th * SW / SH)
    S = Image.new("RGB", (4 * (tw + 16) + 16, th + 32), (60, 60, 60))
    for i, s in enumerate(sl):
        t = s.copy(); t.thumbnail((tw, th), Image.LANCZOS); S.paste(t, (16 + i * (tw + 16), 16))
    S.save(os.path.join(OUT, "_preview.jpg"), quality=88)
    print("ok", names)
