#!/usr/bin/env python3
"""
Ролик 9:16 по 15 с, рубрика «Спроси Инсайда»: 3D-персонаж, вопрос, реплика по словам,
карточки-факты, финальная карточка ПРОЕКТ (CTA-reels.md). Кадры рисует Pillow -> ffmpeg.

    python tools/make_insaid.py tools/shorts/insaid/i1-srok.json
Результат: media/shorts/insaid/<slug>.mp4 и <slug>-preview.jpg
"""
import json, math, subprocess, sys, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "tools" / "fonts" / "Manrope-Variable.ttf"
MASCOT = ROOT / "media" / "mascot" / "3d" / "final3" / "insaid-3D-final3-alpha.png"  # tools/key_mascot.py
W, H, FPS = 1080, 1920, 30
MAIN, CTA_D = 11.5, 3.5
TOTAL = MAIN + CTA_D
GREEN, INK, WHITE, BRASS = (8, 134, 104), (28, 29, 32), (255, 255, 255), (201, 168, 106)
FF = shutil.which("ffmpeg") or "ffmpeg"
_fc = {}


def font(size, w=800):
    k = (size, w)
    if k not in _fc:
        f = ImageFont.truetype(str(FONT), size)
        try: f.set_variation_by_axes([w])
        except Exception: pass
        _fc[k] = f
    return _fc[k]


def ease(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3


def center(d, t, y, f, fill, cx=W / 2):
    d.text((cx - d.textlength(t, font=f) / 2, y), t, font=f, fill=fill)


def background():
    img = Image.new("RGB", (W, H), GREEN); px = img.load()
    for y in range(H):
        k = max(0, (y - 900) / (H - 900)) ** 1.4 * 0.55
        c = tuple(int(GREEN[i] * (1 - k) + INK[i] * k) for i in range(3))
        for x in range(W): px[x, y] = c
    d = ImageDraw.Draw(img)
    d.rectangle([64, 150, 72, 190], fill=BRASS)
    d.text((88, 150), "МЕБЕЛЬ INSIDE", font=font(32), fill=WHITE)
    return img


def wrap(words, f, maxw, d):
    lines, cur = [], []
    for w in words:
        t = " ".join(cur + [w])
        if cur and d.textlength(t, font=f) > maxw: lines.append(cur); cur = [w]
        else: cur.append(w)
    lines.append(cur); return lines


def draw_wrapped_words(d, lines, f, x0, y0, lh, nshown, fill):
    i = 0
    for r, ln in enumerate(lines):
        x = x0
        for w in ln:
            if i < nshown: d.text((x, y0 + r * lh), w, font=f, fill=fill)
            x += d.textlength(w + " ", font=f); i += 1


def cta_card():
    img = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 10], fill=BRASS); d.rectangle([0, H - 10, W, H], fill=BRASS)
    center(d, "МЕБЕЛЬ INSIDE", 190, font(54), BRASS)
    center(d, "Пятигорск · свой цех с 2009", 266, font(32, 600), WHITE)
    center(d, "Хочешь так же?", 420, font(84), WHITE)
    center(d, "Напиши слово", 530, font(56, 700), WHITE)
    d.rounded_rectangle([110, 640, W - 110, 840], radius=40, fill=GREEN, outline=BRASS, width=5)
    center(d, "ПРОЕКТ", 675, font(124), WHITE)
    center(d, "в комментариях — пришлём", 880, font(40, 600), WHITE)
    center(d, "ссылку на просчёт в директ", 940, font(40, 600), WHITE)
    center(d, "3D-проект бесплатно", 1020, font(44, 800), BRASS)
    center(d, "Шоурум: Кисловодское шоссе, 22, ТЦ «Пазл», 2 этаж", 1090, font(30, 600), WHITE)
    center(d, "mebelinside.ru", 1150, font(52, 800), BRASS)
    return img


def main():
    s = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    outdir = ROOT / "media" / "shorts" / "insaid"; outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"{s['slug']}.mp4"
    bg = background(); md = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    im0 = Image.open(MASCOT).convert("RGBA"); im0 = im0.crop(im0.getchannel("A").getbbox())
    MH = 860; MWd = int(im0.width * MH / im0.height); mas = im0.resize((MWd, MH), Image.LANCZOS)
    words = s["answer"].split(); bf = font(50, 700)
    lines = wrap(words, bf, 800, md); lh = 72
    bx0, bx1, by0 = 70, 1010, 660
    by1 = by0 + 88 + lh * len(lines)
    tail = [(250, by1 - 2), (400, by1 - 2), (230, by1 + 50)]
    t_word0, step = 2.0, 0.27
    facts = s["facts"]; fact_t0, fact_dt = 6.0, 1.7
    cta_bg = cta_card()

    cmd = [FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-t", str(TOTAL), "-i", "anullsrc=r=44100:cl=stereo",
           "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
           "-shortest", "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(TOTAL * FPS); previews = {}
    for fi in range(n):
        t = fi / FPS
        if t >= MAIN:
            u = t - MAIN
            fr = cta_bg.copy().convert("RGBA")
            sc = 0.62 * (1 + 0.012 * math.sin(u * 6)); mw, mh = int(MWd * sc), int(MH * sc)
            m = mas.resize((mw, mh), Image.LANCZOS).rotate(math.sin(u * 4) * 2.5, resample=Image.BICUBIC, center=(mw // 2, mh))
            fr.alpha_composite(m, (W // 2 - mw // 2, H - mh - 30))
            fr = fr.convert("RGB")
            if u < 0.4: fr = Image.blend(Image.new("RGB", (W, H), INK), fr, ease(u / 0.4))
        else:
            fr = bg.copy().convert("RGBA")
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            qa = ease((t - 0.2) / 0.5)
            center(d, "СПРОСИ ИНСАЙДА", 260, font(46), BRASS + (int(255 * qa),))
            d.rectangle([W / 2 - 90, 322, W / 2 + 90, 325], fill=BRASS + (int(255 * qa),))
            qy = 360 + int((1 - qa) * 30)
            for i, l in enumerate(s["question"].split("\n")):
                center(d, l, qy + i * 100, font(86), WHITE + (int(255 * qa),))
            ba = ease((t - 1.2) / 0.4); n_sh = 0
            if ba > 0:
                sh = int((1 - ba) * 40)
                d.rounded_rectangle([bx0, by0 + sh, bx1, by1 + sh], radius=40, fill=WHITE + (int(250 * ba),))
                d.polygon([(x, y + sh) for x, y in tail], fill=WHITE + (int(250 * ba),))
                n_sh = int((t - t_word0) / step) + 1 if t >= t_word0 else 0
                draw_wrapped_words(d, lines, bf, bx0 + 50, by0 + 44 + sh, lh, n_sh, INK + (255,))
            talking = t_word0 <= t < t_word0 + step * len(words) + 0.3
            fr = Image.alpha_composite(fr, ov)
            fo = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(fo)
            f = font(44, 800)
            for i, ft in enumerate(facts):
                st = fact_t0 + i * fact_dt
                if t < st: continue
                a = ease((t - st) / 0.35)
                cy = 1090 + i * 250 + int((1 - a) * 40); x0 = 620
                d.rounded_rectangle([x0, cy, 1030, cy + 200], radius=30, fill=INK + (int(235 * a),),
                                    outline=BRASS + (int(255 * a),), width=3)
                ls = wrap(ft.replace("2 года", "2 года").split(" "), f, 390, d); ty = cy + 100 - len(ls) * 28
                for r, ln in enumerate(ls):
                    center(d, " ".join(ln), ty + r * 56, f, WHITE + (int(255 * a),), cx=(x0 + 1030) / 2)
            fr = Image.alpha_composite(fr, fo)
            ma = ease(t / 0.6)
            bob = math.sin(t * 2.2) * 10
            ang = math.sin(t * 1.6) * 2.2
            sc = ma * (1.0 + (0.018 * math.sin(t * 13) if talking else 0))
            if sc > 0.02:
                mw, mh = int(MWd * sc), int(MH * sc)
                m = mas.resize((mw, mh), Image.LANCZOS).rotate(ang, resample=Image.BICUBIC, center=(mw // 2, mh))
                fr.alpha_composite(m, (40 + (MWd - mw) // 2, int(H - mh - 30 - bob)))
            fr = fr.convert("RGB")
        if fi in (int(5.0 * FPS), int(9.5 * FPS), int((MAIN + 2) * FPS)): previews[fi] = fr.copy()
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    keys = sorted(previews)
    strip = Image.new("RGB", (540 * len(keys), 960))
    for j, k in enumerate(keys): strip.paste(previews[k].resize((540, 960)), (540 * j, 0))
    strip.save(outdir / f"{s['slug']}-preview.jpg", quality=88)
    print(out, round(out.stat().st_size / 1048576, 1), "МБ")


if __name__ == "__main__":
    main()
