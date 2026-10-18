#!/usr/bin/env python3
"""Пачка: просветлить и поправить экспозицию фото мебели (без нейросети, без лимитов).

Что делает: аккуратный баланс белого, подъём теней (сильнее для тёмных кадров), лёгкий контраст и цвет,
резкость, ужимает до 1600 px по длинной стороне, JPG ~84 %. Оригиналы не трогает.
Цвет фасада не меняет (баланс белого ограничен ±3 %, автоконтраст не используется).

Примеры:
  python tools/foto_prosvetlit.py D:\\photos\\vhod D:\\photos\\gotovo
  python tools/foto_prosvetlit.py vhod gotovo --sila 1.5      # сильнее просветлить
  python tools/foto_prosvetlit.py vhod gotovo --bez-resize     # не уменьшать размер
Результат: рядом с готовыми файлами лежит _sravnenie.jpg — «до | после» для быстрой проверки глазами.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def retouch(im, sila=1.0):
    a = np.asarray(im).astype(np.float32) / 255
    mean_lum = float(a.mean())
    # авто-сила: чем темнее кадр, тем больше поднимаем тени (0.10 … 0.28)
    base = float(np.clip((0.50 - mean_lum) * 0.9 + 0.10, 0.10, 0.28))
    lift = base * sila
    m = a.reshape(-1, 3).mean(0)
    gain = np.clip(m.mean() / m, 0.97, 1.03)
    a = a * gain
    lum = a.mean(2, keepdims=True)
    a = a + lift * (1 - lum) ** 2 * (1 - a)
    a = np.clip(a, 0, 1)
    out = Image.fromarray((a * 255).astype("uint8"))
    out = ImageEnhance.Contrast(out).enhance(1.02)
    out = ImageEnhance.Color(out).enhance(1.03)
    out = out.filter(ImageFilter.UnsharpMask(radius=1.4, percent=60, threshold=3))
    return out, mean_lum, lift


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap =argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="папка с исходными фото")
    ap.add_argument("dst", help="папка для готовых (создастся)")
    ap.add_argument("--sila", type=float, default=1.0, help="множитель силы просветления (1.0 по умолчанию)")
    ap.add_argument("--bez-resize", action="store_true", help="не уменьшать до 1600 px")
    ap.add_argument("--kachestvo", type=int, default=84, help="качество JPG")
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(args.src) if os.path.splitext(f)[1].lower() in EXT)
    if not files:
        sys.exit("В папке нет фото: " + args.src)
    os.makedirs(args.dst, exist_ok=True)

    thumbs = []
    for f in files:
        im = ImageOps.exif_transpose(Image.open(os.path.join(args.src, f))).convert("RGB")
        orig = im.copy()
        if not args.bez_resize:
            im.thumbnail((1600, 1600), Image.LANCZOS)
        out, lum, lift = retouch(im, args.sila)
        name = os.path.splitext(f)[0] + ".jpg"
        path = os.path.join(args.dst, name)
        out.save(path, quality=args.kachestvo, optimize=True)
        print(f"{f}: яркость {lum:.2f} -> подъём теней {lift:.2f}, {out.size[0]}x{out.size[1]}, {os.path.getsize(path)//1024} КБ")
        o, n = orig.copy(), out.copy()
        o.thumbnail((260, 340))
        n.thumbnail((260, 340))
        thumbs.append((o, n))

    # контрольный лист «до | после»
    W, H = 270, 350
    cols = 2
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (2 * W + 20) + 10, rows * H + 10), "white")
    for i, (o, n) in enumerate(thumbs):
        x = 10 + (i % cols) * (2 * W + 20)
        y = 10 + (i // cols) * H
        sheet.paste(o, (x, y))
        sheet.paste(n, (x + W, y))
    sheet.save(os.path.join(args.dst, "_sravnenie.jpg"), quality=80)
    print(f"Готово: {len(files)} шт. Проверьте {os.path.join(args.dst, '_sravnenie.jpg')} (слева до, справа после).")


if __name__ == "__main__":
    main()
