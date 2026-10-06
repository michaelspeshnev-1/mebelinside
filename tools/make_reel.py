#!/usr/bin/env python3
"""
Сборка рилс из своего видео: обрезка, вертикаль 9:16 (1080×1920), надписи по
сценарию, сжатие до размера, который принимают Telegram, MAX и Instagram.

Запуск (на ПК, где лежит видео):
    pip install imageio-ffmpeg pillow
    python tools/make_reel.py reels/r1-shkaf-pantograf.json "D:\\путь\\к\\видео.mp4"

Сценарий — JSON рядом (см. reels/*.json): откуда и сколько резать, надписи
с таймингом. Результат — reels/out/<имя>.mp4, до ~20 МБ.
"""
import json
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "tools" / "fonts" / "Manrope-Variable.ttf"
W, H, PAD = 1080, 1920, 34


def render_text(t, path):
    """Надпись — прозрачная картинка 1080×1920: белый текст на полупрозрачной плашке.

    Рисуем Pillow, а не drawtext: в части сборок ffmpeg (в том числе в pip-пакете
    imageio-ffmpeg) фильтра drawtext нет, а наложение картинки работает везде.
    """
    from PIL import Image, ImageDraw, ImageFont

    size = t.get("size", 64)
    font = ImageFont.truetype(str(FONT), size)
    try:
        font.set_variation_by_axes([700])   # жирное начертание вариативного шрифта
    except Exception:
        pass
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    lines = t["text"].split("\n")
    line_h = int(size * 1.35)
    widths = [draw.textlength(line, font=font) for line in lines]
    box_w, box_h = int(max(widths)) + 2 * PAD, line_h * len(lines) + 2 * PAD - int(size * 0.2)
    top = {"top": int(H * 0.11), "center": (H - box_h) // 2, "bottom": int(H * 0.70)}[t.get("pos", "bottom")]
    left = (W - box_w) // 2
    draw.rounded_rectangle([left, top, left + box_w, top + box_h], radius=28, fill=(0, 0, 0, 150))
    for i, (line, w) in enumerate(zip(lines, widths)):
        draw.text(((W - w) / 2, top + PAD + i * line_h), line, font=font, fill=(255, 255, 255, 255))
    img.save(path)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    spec_path, src = Path(sys.argv[1]), sys.argv[2]
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out_dir = ROOT / "reels" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (spec_path.stem + ".mp4")
    tmp = out_dir / (spec_path.stem + "_texts")
    tmp.mkdir(exist_ok=True)

    inputs, chain, last = [], [], "base"
    chain.append(
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1,fps=30[base]"
    )
    for i, t in enumerate(spec["texts"]):
        png = tmp / f"{i:02d}.png"
        render_text(t, png)
        inputs += ["-i", str(png)]
        nxt = f"v{i}"
        chain.append(f"[{last}][{i + 1}:v]overlay=0:0:enable='between(t,{t['from']},{t['to']})'[{nxt}]")
        last = nxt

    cmd = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
        "-ss", str(spec.get("start", 0)), "-t", str(spec["duration"]), "-i", src,
        *inputs,
        "-filter_complex", ";".join(chain), "-map", f"[{last}]",
        "-c:v", "libx264", "-preset", "medium", "-b:v", "4500k", "-maxrate", "5500k",
        "-bufsize", "9000k", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    ]
    if spec.get("mute"):
        cmd += ["-an"]
    else:
        cmd += ["-map", "0:a?", "-c:a", "aac", "-b:a", "128k", "-ac", "2"]
    cmd.append(str(out))
    subprocess.run(cmd, check=True)
    size = out.stat().st_size / 1024 / 1024
    print(f"Готово: {out} ({size:.1f} МБ)")
    if size > 20:
        print("Больше 20 МБ: для MAX уменьшите duration или -b:v в скрипте.")


if __name__ == "__main__":
    main()
