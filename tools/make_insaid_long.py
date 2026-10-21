#!/usr/bin/env python3
"""
Длинный ролик 9:16 (40–60 с) с Инсайдом-ведущим: вопрос, затем сцены (заголовок + реплика по словам),
финальная карточка ПРОЕКТ. Тот же стиль, что у tools/make_insaid.py (импортирует его функции).

    python tools/make_insaid_long.py tools/shorts/insaid/w2-cena.json
JSON: slug, header (вверху в сценах), question (str с \\n), q_dur, scenes[{dur, title, text}], music, music_vol.
Результат: media/shorts/w2/<slug>.mp4 и <slug>-preview.jpg
"""
import json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_insaid as mi
from make_insaid import W, H, FPS, GREEN, INK, WHITE, BRASS, font, ease, center, wrap, draw_wrapped_words

ROOT = mi.ROOT


def main():
    s = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    outdir = ROOT / "media" / "shorts" / "w2"; outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"{s['slug']}.mp4"
    q_dur = s.get("q_dur", 3.5)
    scenes = s["scenes"]
    main_d = q_dur + sum(sc["dur"] for sc in scenes)
    total = main_d + mi.CTA_D
    bg = mi.background(); md = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    im0 = Image.open(mi.MASCOT).convert("RGBA"); im0 = im0.crop(im0.getchannel("A").getbbox())
    MH = 860; MWd = int(im0.width * MH / im0.height); mas = im0.resize((MWd, MH), Image.LANCZOS)
    bf = font(50, 700); tf = font(46, 800); lh = 70
    bx0, bx1, by0 = 70, 1010, 520
    prep = []; t0 = q_dur
    for sc in scenes:
        words = sc["text"].split(); lines = wrap(words, bf, 800, md)
        step = max(0.18, min(0.30, (sc["dur"] - 1.4) / max(len(words), 1)))
        prep.append(dict(t0=t0, t1=t0 + sc["dur"], words=words, lines=lines, step=step, title=sc.get("title", "")))
        t0 += sc["dur"]
    cta_bg = mi.cta_card()
    music = ROOT / s["music"] if s.get("music") else None
    cmd = [mi.FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if music:
        cmd += ["-stream_loop", "-1", "-i", str(music), "-af",
                f"atrim=0:{total},volume={s.get('music_vol', 0.95)},afade=t=in:st=0:d=0.6,afade=t=out:st={total-1.5}:d=1.5,"
                "aformat=sample_rates=44100:channel_layouts=stereo"]
    else:
        cmd += ["-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=44100:cl=stereo"]
    cmd += ["-t", str(total), "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(total * FPS); previews = {}
    pv_t = [q_dur - 0.5] + [pp["t1"] - 0.8 for pp in prep[:3]] + [main_d + 2]
    pv_i = {int(t * FPS) for t in pv_t}
    for fi in range(n):
        t = fi / FPS
        if t >= main_d:
            u = t - main_d
            fr = cta_bg.copy().convert("RGBA")
            sc_ = 0.62 * (1 + 0.012 * math.sin(u * 6)); mw, mh = int(MWd * sc_), int(MH * sc_)
            m = mas.resize((mw, mh), Image.LANCZOS).rotate(math.sin(u * 4) * 2.5, resample=Image.BICUBIC, center=(mw // 2, mh))
            fr.alpha_composite(m, (W // 2 - mw // 2, H - mh - 30))
            fr = fr.convert("RGB")
            if u < 0.4: fr = Image.blend(Image.new("RGB", (W, H), INK), fr, ease(u / 0.4))
        else:
            fr = bg.copy().convert("RGBA")
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            talking = False
            if t < q_dur:
                qa = ease((t - 0.2) / 0.5)
                center(d, "СПРОСИ ИНСАЙДА", 260, font(46), BRASS + (int(255 * qa),))
                d.rectangle([W / 2 - 90, 322, W / 2 + 90, 325], fill=BRASS + (int(255 * qa),))
                qy = 380 + int((1 - qa) * 30)
                for i, l in enumerate(s["question"].split("\n")):
                    center(d, l, qy + i * 100, font(86), WHITE + (int(255 * qa),))
            else:
                center(d, s["header"], 250, font(40), BRASS)
                d.rectangle([W / 2 - 90, 308, W / 2 + 90, 311], fill=BRASS)
                pp = next(x for x in prep if x["t0"] <= t < x["t1"])
                lt = t - pp["t0"]
                ba = ease(lt / 0.35) * ease((pp["t1"] - t) / 0.25)
                by1 = by0 + (88 if pp["title"] else 40) + lh * len(pp["lines"]) + 10
                sh = int((1 - ease(lt / 0.35)) * 40)
                d.rounded_rectangle([bx0, by0 + sh, bx1, by1 + sh], radius=40, fill=WHITE + (int(250 * ba),))
                d.polygon([(x, y + sh) for x, y in [(250, by1 - 2), (400, by1 - 2), (230, by1 + 50)]], fill=WHITE + (int(250 * ba),))
                ty = by0 + 30 + sh
                if pp["title"]:
                    d.text((bx0 + 50, ty), pp["title"], font=tf, fill=GREEN + (255,)); ty += 62
                nsh = int((lt - 0.5) / pp["step"]) + 1 if lt >= 0.5 else 0
                draw_wrapped_words(d, pp["lines"], bf, bx0 + 50, ty, lh, nsh, INK + (255,))
                talking = 0.5 <= lt < 0.5 + pp["step"] * len(pp["words"]) + 0.3
            fr = Image.alpha_composite(fr, ov)
            ma = ease(t / 0.6)
            bob = math.sin(t * 2.2) * 10; ang = math.sin(t * 1.6) * 2.2
            sc_ = ma * (1.0 + (0.018 * math.sin(t * 13) if talking else 0))
            if sc_ > 0.02:
                mw, mh = int(MWd * sc_), int(MH * sc_)
                m = mas.resize((mw, mh), Image.LANCZOS).rotate(ang, resample=Image.BICUBIC, center=(mw // 2, mh))
                fr.alpha_composite(m, (40 + (MWd - mw) // 2, int(H - mh - 30 - bob)))
            fr = fr.convert("RGB")
        if fi in pv_i: previews[fi] = fr.copy()
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    keys = sorted(previews)
    strip = Image.new("RGB", (360 * len(keys), 640))
    for j, k in enumerate(keys): strip.paste(previews[k].resize((360, 640)), (360 * j, 0))
    strip.save(outdir / f"{s['slug']}-preview.jpg", quality=88)
    print(out, round(out.stat().st_size / 1048576, 1), "МБ", round(total, 1), "с")


if __name__ == "__main__":
    main()
