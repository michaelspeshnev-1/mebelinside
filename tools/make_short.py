#!/usr/bin/env python3
"""
Вертикальный ролик 9:16 (Shorts / TikTok / Reels) из готового видео: хук, подписи,
финальный призыв, фирменные цвета сайта (--mi-ink / --mi-brass / --mi-cream).

    python tools/make_short.py tools/shorts/s1-vanna.json

Сценарий JSON: src, start, dur, texts[{from,to,text,kind: hook|cap}], cta{...}.
Результат: media/shorts/<имя>.mp4 (H.264 + тихая AAC-дорожка, ~1080x1920, 30 fps).
Надписи рисует Pillow (drawtext есть не во всех сборках ffmpeg).
"""
import json, subprocess, sys, shutil, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "tools" / "fonts" / "Manrope-Variable.ttf"
W, H = 1080, 1920
INK, BRASS, CREAM, GREEN = (28, 29, 32), (201, 168, 106), (241, 235, 221), (21, 121, 92)
FF = shutil.which("ffmpeg") or "ffmpeg"


def font(size, wght=800):
    f = ImageFont.truetype(str(FONT), size)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f


def tag_layer(path):
    """Градиенты сверху/снизу + бренд-метка. Один раз на весь ролик."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = img.load()
    for y in range(H):
        a = 0
        if y < 520: a = int(170 * (1 - y / 520) ** 1.6)
        elif y > H - 760: a = int(190 * ((y - (H - 760)) / 760) ** 1.6)
        if a:
            for x in range(W): px[x, y] = INK + (a,)
    d = ImageDraw.Draw(img)
    d.rectangle([64, 196, 64 + 8, 196 + 40], fill=BRASS)
    d.text((88, 196), "МЕБЕЛЬ INSIDE", font=font(32, 800), fill=CREAM)
    img.save(path)


def text_layer(path, text, kind):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    size = 84 if kind == "hook" else 58
    f = font(size, 800); lines = text.split("\n"); lh = int(size * 1.22)
    ws = [d.textlength(l, font=f) for l in lines]
    pad = 40; bw = int(max(ws)) + 2 * pad + 22; bh = lh * len(lines) + 2 * pad - int(size * .15)
    x0 = 64 if kind == "hook" else (W - bw) // 2
    y0 = 330 if kind == "hook" else 1090
    fill = INK + (215,) if kind == "cap" else INK + (200,)
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=26, fill=fill)
    d.rounded_rectangle([x0, y0, x0 + 14, y0 + bh], radius=7, fill=BRASS)
    for i, (l, w) in enumerate(zip(lines, ws)):
        hot = "**" in l
        l = l.replace("**", "")
        d.text((x0 + pad + 22, y0 + pad - int(size * .1) + i * lh), l, font=f, fill=BRASS if hot else CREAM)
    img.save(path)


def cta_layer(path, cta):
    img = Image.new("RGBA", (W, H), INK + (255,)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=BRASS); d.rectangle([0, H - 14, W, H], fill=BRASS)
    def center(t, y, f, fill):
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=fill)
    center("МЕБЕЛЬ INSIDE", 360, font(58, 800), BRASS)
    center("Пятигорск · свой цех с 2009", 440, font(34, 600), CREAM)
    y = 640
    for l in cta["lines"]:
        center(l, y, font(76, 800), CREAM); y += 100
    d.rounded_rectangle([140, y + 50, W - 140, y + 250], radius=40, fill=BRASS)
    center(cta["word"], y + 82, font(110, 800), INK)
    center(cta["word_sub"], y + 205, font(30, 700), INK) if False else None
    y += 330
    for l in cta["foot"]:
        center(l, y, font(40, 600), CREAM); y += 62
    center("mebelinside.ru", y + 40, font(52, 800), BRASS)
    img.save(path)


def main():
    spec_path = Path(sys.argv[1]); s = json.loads(spec_path.read_text(encoding="utf-8"))
    out = ROOT / "media" / "shorts" / s.get("outdir", "") / (spec_path.stem + ".mp4"); out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="short_")); dur = s["dur"]; cta_d = 3.5; total = dur + cta_d
    tag_layer(tmp / "tag.png"); cta_layer(tmp / "cta.png", s["cta"])
    speed = s.get("speed", 1)
    ins = ["-ss", str(s["start"]), "-t", str(dur * speed), "-i", s["src"],
           "-loop", "1", "-framerate", "30", "-t", str(dur), "-i", str(tmp / "tag.png")]
    flt = [f"[0:v]setpts=PTS/{speed},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,"
           f"eq=contrast=1.06:saturation=1.08,format=yuv420p[v0]", "[v0][1:v]overlay=0:0[v1]"]
    last = "v1"; n = 2
    for i, t in enumerate(s["texts"]):
        p = tmp / f"t{i}.png"; text_layer(p, t["text"], t.get("kind", "cap"))
        ins += ["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", str(p)]
        a, b = t["from"], t["to"]
        flt.append(f"[{n}:v]format=rgba,fade=t=in:st={a}:d=0.3:alpha=1,fade=t=out:st={b-0.3}:d=0.3:alpha=1[x{i}]")
        flt.append(f"[{last}][x{i}]overlay=0:0:enable='between(t,{a},{b})'[o{i}]"); last = f"o{i}"; n += 1
    flt.append(f"[{last}]null[main]")
    ins += ["-loop", "1", "-framerate", "30", "-t", str(cta_d), "-i", str(tmp / "cta.png")]
    flt.append(f"[{n}:v]format=yuv420p,fade=t=in:st=0:d=0.4,setsar=1[cta]")
    flt.append("[main][cta]concat=n=2:v=1:a=0[v]")
    music = s.get("music")
    if music:
        ins += ["-i", str(ROOT / music)]
        flt.append(f"[{n+1}:a]atrim=0:{total},volume={s.get('music_vol', 0.5)},afade=t=in:st=0:d=0.6,"
                   f"afade=t=out:st={total-1.5}:d=1.5,aformat=sample_rates=44100:channel_layouts=stereo[a]")
        amap = "[a]"
    else:
        ins += ["-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=44100:cl=stereo"]
        amap = f"{n+1}:a"
    cmd = [FF, "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[v]", "-map", amap,
           "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
           "-c:a", "aac", "-b:a", "96k", "-shortest", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    print(out, round(out.stat().st_size / 1048576, 1), "МБ")


if __name__ == "__main__":
    main()
