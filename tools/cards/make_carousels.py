# -*- coding: utf-8 -*-
"""Карусели 1080x1350 для Instagram/Facebook/TikTok photo-mode «Мебель Inside».
Фото берутся с Google Диска (D:\\Google Drive\\Мебель), обрабатываются локально (tools/foto_prosvetlit.retouch)
и кладутся в media/carousels/<имя>/ только уже со слайдовым оформлением.
Запуск: python tools/cards/make_carousels.py [имя ...]
"""
import os, sys, importlib.util
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(ROOT, "tools", "fonts")
SANS = os.path.join(FONTS, "Manrope-Variable.ttf")
SERIF = os.environ.get("MI_SERIF", r"C:\Users\Елисей\content-bot\assets\fonts\PlayfairDisplay-Variable.ttf")
LOGO = os.environ.get("MI_LOGO", r"C:\Users\Елисей\content-bot\assets\logo.png")
DRIVE = r"D:\Google Drive\Мебель"
OUT = os.path.join(ROOT, "media", "carousels")

INK = (28, 29, 32); GREEN = (8, 134, 104); GREEN_D = (15, 92, 67); BRASS = (201, 168, 106)
PAPER = (251, 249, 244); MUTED = (72, 69, 62); WHITE = (255, 255, 255)
W, H = 1080, 1350; M = 84

spec = importlib.util.spec_from_file_location("fp", os.path.join(ROOT, "tools", "foto_prosvetlit.py"))
fp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fp)


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


def block(d, x, y, text, f, fill, maxw, lh):
    for ln in wrap(d, text, f, maxw):
        d.text((x, y), ln, font=f, fill=fill); y += lh
    return y


def tracked(d, xy, text, f, fill, tr=4):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + tr


def photo(path, focus=(0.5, 0.5), retouch=True, zoom=1.0):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if retouch:
        im.thumbnail((2000, 2000), Image.LANCZOS)
        im = fp.retouch(im, 1.0)[0]
    s = max(W / im.width, H / im.height) * zoom
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x = int((im.width - W) * focus[0]); y = int((im.height - H) * focus[1])
    return im.crop((x, y, x + W, y + H))


def gradient(im, y0, y1, a0, a1, color=INK):
    ov = Image.new("RGBA", im.size, color + (0,))
    px = ov.load()
    for y in range(y0, min(y1, H)):
        a = int(a0 + (a1 - a0) * (y - y0) / max(1, y1 - y0))
        for x in range(W):
            px[x, y] = color + (a,)
    for y in range(y1, H):
        for x in range(W):
            px[x, y] = color + (a1,)
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def footer(d, im, n, total, dark=True):
    col = BRASS
    logo = Image.open(LOGO).convert("RGBA").resize((44, 44), Image.LANCZOS)
    im.paste(logo, (M, H - 80), logo)
    tracked(d, (M + 60, H - 70), "MEBELINSIDE.RU", font(SANS, 20, 700), col, 3)
    t = f"{n} / {total}"
    f = font(SANS, 22, 700)
    d.text((W - M - d.textlength(t, font=f), H - 68), t, font=f, fill=col)


def s_cover(a, kicker, title, sub, focus=(0.5, 0.5), n=1, total=8):
    im = photo(a["src"], focus, a.get("retouch", True))
    im = gradient(im, 300, 1000, 0, 215)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 12), fill=GREEN); d.rectangle((0, 12, W, 15), fill=BRASS)
    tracked(d, (M, 700), kicker.upper(), font(SANS, 26, 700), BRASS, 5)
    y = block(d, M, 750, title, font(SERIF, 78, 700), WHITE, W - 2 * M, 90)
    d.rectangle((M, y + 14, M + 100, y + 17), fill=BRASS)
    block(d, M, y + 44, sub, font(SANS, 32, 600), (235, 232, 224), W - 2 * M, 44)
    footer(d, im, n, total)
    return im


def s_photo(a, title, sub, n, total, focus=(0.5, 0.5), zoom=1.0):
    im = photo(a["src"], focus, a.get("retouch", True), zoom)
    plate_top = 1010
    im = gradient(im, plate_top - 120, plate_top, 0, 235)
    d = ImageDraw.Draw(im)
    d.rectangle((0, plate_top, W, H), fill=INK)
    d.rectangle((M, plate_top + 1, M + 90, plate_top + 4), fill=BRASS)
    d.rectangle((0, 0, W, 12), fill=GREEN); d.rectangle((0, 12, W, 15), fill=BRASS)
    y = block(d, M, plate_top + 34, title, font(SANS, 52, 800), WHITE, W - 2 * M, 62)
    block(d, M, y + 6, sub, font(SANS, 30, 500), (214, 210, 200), W - 2 * M, 40)
    footer(d, im, n, total)
    return im


def s_text(num, title, sub, n, total, kicker=None, note=None):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 12), fill=GREEN); d.rectangle((0, 12, W, 15), fill=BRASS)
    if kicker:
        tracked(d, (M, 150), kicker.upper(), font(SANS, 26, 700), BRASS, 5)
    if num:
        d.ellipse((M, 330, M + 190, 520), fill=GREEN)
        f = font(SERIF, 112, 700); tw = d.textlength(str(num), font=f)
        d.text((M + 95 - tw / 2, 353), str(num), font=f, fill=PAPER)
        ty = 590
    else:
        ty = 420
    y = block(d, M, ty, title, font(SERIF, 88, 700), INK, W - 2 * M, 102)
    d.rectangle((M, y + 14, M + 100, y + 17), fill=BRASS)
    y = block(d, M, y + 54, sub, font(SANS, 44, 600), MUTED, W - 2 * M, 62)
    if note:
        block(d, M, y + 30, note, font(SANS, 34, 500), MUTED, W - 2 * M, 48)
    footer(d, im, n, total)
    return im


def s_cta(lines, big, sub, n, total, detail=None):
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    d.rectangle((40, 40, W - 40, H - 40), outline=BRASS, width=2)
    logo = Image.open(LOGO).convert("RGBA").resize((96, 96), Image.LANCZOS)
    im.paste(logo, (M + 10, 170), logo)
    tracked(d, (M + 130, 200), "МЕБЕЛЬ INSIDE", font(SANS, 30, 800), BRASS, 5)
    y = block(d, M + 10, 380, lines, font(SERIF, 70, 700), WHITE, W - 2 * M - 20, 84)
    d.rectangle((M + 10, y + 14, M + 110, y + 17), fill=BRASS)
    y = block(d, M + 10, y + 56, big, font(SANS, 64, 800), BRASS, W - 2 * M - 20, 78)
    y = block(d, M + 10, y + 24, sub, font(SANS, 32, 500), (225, 221, 211), W - 2 * M - 20, 46)
    if detail:
        block(d, M + 10, y + 30, detail, font(SANS, 28, 500), (190, 186, 176), W - 2 * M - 20, 40)
    footer(d, im, n, total)
    return im


def collage(slides, path):
    th = 360; tw = int(th * W / H)
    cols = 4; rows = (len(slides) + cols - 1) // cols
    S = Image.new("RGB", (cols * (tw + 16) + 16, rows * (th + 16) + 16), (60, 60, 60))
    for i, s in enumerate(slides):
        t = s.copy(); t.thumbnail((tw, th), Image.LANCZOS)
        S.paste(t, (16 + (i % cols) * (tw + 16), 16 + (i // cols) * (th + 16)))
    S.save(path, quality=88)


def save(name, slides):
    d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
    for i, s in enumerate(slides, 1):
        s.save(os.path.join(d, f"{i:02d}.jpg"), quality=90, optimize=True, subsampling=0)
    collage(slides, os.path.join(d, "_preview.jpg"))
    print(name, len(slides), "slides")


KIT = os.path.join(DRIVE, "Производство", "Сборка-Монтаж", "Амид кухня Нежнова")
KIT = os.path.join(DRIVE, "Производство", "Сборка-Монтаж", os.listdir(os.path.join(DRIVE, "Производство", "Сборка-Монтаж"))[0]) if not os.path.isdir(KIT) else KIT
WARD = None
for sub in os.listdir(os.path.join(DRIVE, "Шкафы")):
    if "Эмаль" in sub and "Балка" in sub:
        WARD = os.path.join(DRIVE, "Шкафы", sub)
K = lambda stamp: os.path.join(KIT, f"IMG_20260801_{stamp}.jpg")
Wd = lambda pref: next(os.path.join(WARD, f) for f in sorted(os.listdir(WARD)) if f.lower().endswith(".png") and pref in f)


def build_checklist():
    T = 8
    s = [
        s_cover({"src": K("110236")}, "Чек-лист", "Принимаете кухню? Проверьте 5 точек", "Пока монтажники ещё на объекте. Сохраните, чтобы не забыть.", (0.5, 0.5), 1, T),
        s_text(1, "Ящик", "Выдвиньте на полный выдвиг. Должен идти плавно, без перекоса.", 2, T, "Точка 1 из 5"),
        s_text(2, "Зазоры между фасадами", "Одинаковые по всей кухне, не только на уровне глаз.", 3, T, "Точка 2 из 5"),
        s_text(3, "Столешница", "По уровню, без завала в сторону мойки.", 4, T, "Точка 3 из 5"),
        s_text(4, "Торцы и кромка", "Без сколов и отслоений, особенно у мойки и варочной панели.", 5, T, "Точка 4 из 5"),
        s_photo({"src": K("110151")}, "5. Шов у мойки", "Сплошной, без щели, в которую может попасть вода.", 6, T, (0.5, 0.35)),
        s_text(None, "Нашли недочёт?", "Это гарантийный случай. Гарантия 2 года по договору.", 7, T, "Что дальше", "Фиксируйте замечания сразу при приёмке."),
        s_cta("Хотите кухню, которую приятно принимать?", "Напишите ПРОЕКТ", "в комментариях или в личные сообщения — пришлём ссылку на просчёт.", 8, T, "Расчёт и 3D-проект бесплатны."),
    ]
    save("chek-list-priemki-kuhni", s)


def build_montazh():
    T = 8
    s = [
        s_cover({"src": K("110236")}, "Реальный объект", "Монтаж кухни: как выглядит день установки", "Кадры одного проекта, без постановки.", (0.5, 0.45), 1, T),
        s_photo({"src": K("110229")}, "Нижние шкафы и столешница на местах", "Столешница ещё закрыта защитной плёнкой.", 2, T, (0.5, 0.5)),
        s_photo({"src": K("110151")}, "Мойка врезана в столешницу", "Шов у мойки — первое, что смотрим при приёмке.", 3, T, (0.5, 0.4)),
        s_photo({"src": K("110257")}, "Верхний ряд — единой линией", "Фасады навесных шкафов выставлены по одной линии.", 4, T, (0.5, 0.35)),
        s_photo({"src": K("110354")}, "Внутри верхнего модуля — полка", "Корпус виден изнутри, пока фасад не закрыт.", 5, T, (0.5, 0.5)),
        s_photo({"src": K("110431")}, "Ниша под вытяжку", "Шкаф у вытяжки встроен в общий ряд.", 6, T, (0.5, 0.4)),
        s_text(None, "Что дальше", "Регулировка фасадов и приёмка по 5 пунктам.", 7, T, "После монтажа", "Ящик · зазоры · столешница · кромка · шов у мойки."),
        s_cta("Приходите посмотреть материалы и фасады вживую", "Шоурум в Пятигорске", "Кисловодское шоссе, 22, ТЦ «Пазл», 2 этаж. Пн–Сб, 10:00–18:00.", 8, T, "Телефон: +7 928 951-63-42"),
    ]
    save("montazh-kuhni-den-ustanovki", s)


def build_shkaf():
    T = 8
    s = [
        s_cover({"src": Wd("012627bc"), "retouch": False}, "Заглянем внутрь", "Что внутри шкафа до потолка?", "Реальный проект: белый глянец в спальне.", (0.5, 0.4), 1, T),
        s_photo({"src": Wd("bbc51005"), "retouch": False}, "Штанга и полки над ней", "Одежда на плечиках — и верхняя полка для сезонного.", 2, T, (0.5, 0.3)),
        s_photo({"src": Wd("1d784a6d"), "retouch": False}, "Полки и выдвижные ящики", "Разные секции под разные вещи.", 3, T, (0.5, 0.4)),
        s_photo({"src": Wd("54daeb8a"), "retouch": False}, "Открытые полки и ящики", "Бельё и мелочи — в ящиках, остальное на виду.", 4, T, (0.5, 0.5)),
        s_photo({"src": Wd("af7cc77e"), "retouch": False}, "Антресоль — до потолка", "Верхний ярус использован полностью.", 5, T, (0.5, 0.3)),
        s_photo({"src": Wd("45365a33"), "retouch": False}, "Вертикальный профиль вместо ручки", "Фасад гладкий, ничего не цепляется.", 6, T, (0.5, 0.45)),
        s_photo({"src": Wd("a6b1a48d"), "retouch": False}, "Зеркальные дверцы по центру", "Зеркало встроено в фасад шкафа.", 7, T, (0.5, 0.4)),
        s_cta("Хотите так же — под вашу комнату?", "+7 928 951-63-42", "Позвоните — обсудим размеры и наполнение. Расчёт и 3D-проект бесплатны.", 8, T, "Или напишите нам в мессенджер."),
    ]
    save("chto-vnutri-shkafa", s)


if __name__ == "__main__":
    want = set(sys.argv[1:])
    for nm, fn in (("checklist", build_checklist), ("montazh", build_montazh), ("shkaf", build_shkaf)):
        if not want or nm in want:
            fn()
