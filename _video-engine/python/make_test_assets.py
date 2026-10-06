#!/usr/bin/env python3
"""Генерация нейтральных тестовых файлов (без чужих материалов и без сети).

Создаёт:
  1) видео «спикера»: условная фигура, рот двигается в такт голосу, звук - синтез речи;
  2) картинку для B-roll: абстрактный градиент с мягкими фигурами;
  3) текстовый файл со сценарием (то, что произносится) - для проверки качества распознавания.

Голос синтезирует flite или espeak-ng (что найдётся в системе). Только numpy + ffmpeg.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import wave

import numpy as np

SCRIPT = (
    "Welcome to this short demonstration. "
    "Today we show how a small video engine works. "
    "First, the engine reads the video and listens to the sound. "
    "Then it writes down every word with its time. "
    "After that, it builds a plan with three scenes. "
    "The first scene shows the speaker with subtitles. "
    "The second scene shows one big title. "
    "The third scene shows a picture. "
    "At the end, the engine saves one clean video file."
)

W, H, FPS = 1280, 720, 25


def fail(code, message, hint):
    print(json.dumps({"ok": False, "error": {"code": code, "message": message, "hint": hint}}, ensure_ascii=False))
    sys.exit(2)


def synth_speech(text, out_wav):
    """Синтез речи в WAV. Возвращает название движка."""
    tmp = out_wav + ".raw.wav"
    # flite распознаётся запасным движком заметно лучше espeak-ng (проверено замером), поэтому он первый.
    if shutil.which("flite"):
        cmd = ["flite", "-voice", "rms", "-t", text, "-o", tmp]
        engine = "flite"
    elif shutil.which("espeak-ng"):
        cmd = ["espeak-ng", "-v", "en-us", "-s", "135", "-p", "45", "-w", tmp, text]
        engine = "espeak-ng"
    else:
        fail(
            "NO_TTS",
            "Нет программы синтеза речи (flite или espeak-ng) - тестовое видео с голосом создать нечем.",
            "Ubuntu/Debian: sudo apt-get install flite · macOS: brew install flite. "
            "Либо возьмите своё короткое видео с речью и положите в input/.",
        )
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.isfile(tmp):
        fail("TTS_FAILED", f"Синтез речи ({engine}) не сработал.", (r.stderr or "").strip()[:200])
    # 16 кГц моно + полсекунды тишины в начале и конце, чтобы речь не обрезалась на стыках
    r = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "adelay=700,apad=pad_dur=0.9,loudnorm=I=-18:TP=-2:LRA=7",
         "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", out_wav],
        capture_output=True, text=True)
    os.remove(tmp)
    if r.returncode != 0:
        fail("TTS_CONVERT", "Не удалось подготовить звук речи.", r.stderr.strip()[:200])
    return engine


def envelope(wav_path, fps):
    """Громкость по кадрам видео (0..1) - управляет открытием рта."""
    with wave.open(wav_path, "rb") as w:
        rate = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    n_frames = int(math.ceil(len(data) / rate * fps))
    env = np.zeros(n_frames, dtype=np.float32)
    win = int(rate / fps)
    for i in range(n_frames):
        chunk = data[i * win:(i + 1) * win]
        env[i] = float(np.sqrt(np.mean(chunk ** 2))) if len(chunk) else 0.0
    peak = max(float(env.max()), 1e-6)
    env = np.clip(env / (peak * 0.6), 0, 1)
    # лёгкое сглаживание, чтобы рот не дёргался
    k = np.array([0.25, 0.5, 0.25], dtype=np.float32)
    return np.convolve(env, k, mode="same"), len(data) / rate


def ellipse_mask(yy, xx, cy, cx, ry, rx):
    return ((yy - cy) / max(ry, 1)) ** 2 + ((xx - cx) / max(rx, 1)) ** 2 <= 1.0


def make_background():
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    base = np.zeros((H, W, 3), dtype=np.float32)
    base[..., 0] = 28 + 40 * y + 20 * x
    base[..., 1] = 44 + 50 * y
    base[..., 2] = 78 + 70 * (1 - y) + 30 * x
    vig = 1.0 - 0.35 * (((x - 0.5) ** 2 + (y - 0.5) ** 2) * 2.2)
    return np.clip(base * vig[..., None], 0, 255).astype(np.uint8)


def render_video(wav_path, silent_mp4, env):
    bg = make_background()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    n = len(env)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", silent_mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    skin = np.array([226, 184, 150], dtype=np.uint8)
    shirt = np.array([60, 90, 140], dtype=np.uint8)
    dark = np.array([40, 30, 30], dtype=np.uint8)
    mouth_c = np.array([120, 40, 50], dtype=np.uint8)
    for i in range(n):
        t = i / FPS
        sway = math.sin(t * 1.3) * 10
        cx, cy = W * 0.5 + sway, H * 0.42
        f = bg.copy()
        # плечи
        f[ellipse_mask(yy, xx, H * 0.98, cx, 190, 330)] = shirt
        # шея и голова
        f[ellipse_mask(yy, xx, cy + 150, cx, 60, 55)] = skin
        f[ellipse_mask(yy, xx, cy, cx, 150, 120)] = skin
        # волосы (верхняя часть)
        hair = ellipse_mask(yy, xx, cy - 40, cx, 130, 126) & (yy < cy - 70)
        f[hair] = dark
        # глаза (иногда моргают)
        blink = (i % 90) in (0, 1, 2)
        for ex in (-48, 48):
            f[ellipse_mask(yy, xx, cy - 20, cx + ex, 3 if blink else 11, 14)] = dark
        # рот открывается по громкости
        open_h = 3 + 34 * float(env[i])
        f[ellipse_mask(yy, xx, cy + 70, cx, open_h, 34)] = mouth_c
        p.stdin.write(f.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        fail("VIDEO_FAILED", "FFmpeg не смог собрать тестовое видео.", "Запустите npm run doctor.")


def make_image(out_png, variant=0):
    w, h = 1920, 1080
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    img = np.zeros((h, w, 3), dtype=np.float32)
    img[..., 0] = 240 - 120 * x + 20 * y
    img[..., 1] = 120 + 90 * y
    img[..., 2] = 90 + 150 * x
    if variant:
        img = np.roll(img, variant, axis=2)  # другая палитра для 2-й и 3-й картинки
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for cy, cx, r, col, a in [
        (h * (0.30 + 0.12 * variant), w * (0.25 + 0.2 * variant), 260, (255, 235, 200), 0.55),
        (h * 0.68, w * (0.72 - 0.15 * variant), 340, (30, 60, 120), 0.45),
        (h * 0.55, w * 0.40, 150, (255, 255, 255), 0.35),
        (h * 0.20, w * 0.82, 120, (255, 200, 120), 0.5),
    ]:
        d = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
        m = np.clip(1.0 - d / r, 0, 1) ** 0.7 * a
        for c in range(3):
            img[..., c] = img[..., c] * (1 - m) + col[c] * m
    band = np.clip(1.0 - np.abs((xx * 0.6 + yy) % 400 - 200) / 12.0, 0, 1) * 0.10
    img = img * (1 - band[..., None]) + 255 * band[..., None]
    raw = np.clip(img, 0, 255).astype(np.uint8)
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-i", "-",
                        "-frames:v", "1", out_png], input=raw.tobytes(), capture_output=True)
    if r.returncode != 0:
        fail("IMAGE_FAILED", "Не удалось создать тестовую картинку.", r.stderr.decode(errors="ignore")[:200])


def make_music(out_wav, seconds=40, sr=44100):
    """Мягкий синтезированный «пад» (Am-F-C-G): собственная генерация, права ни у кого не нужны."""
    chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (261.63, 329.63, 392.0), (196.0, 246.94, 293.66)]
    n = int(seconds * sr)
    t = np.arange(n, dtype=np.float32) / sr
    out = np.zeros((n, 2), dtype=np.float32)
    seg = 4.0
    for i in range(int(seconds / seg) + 1):
        a, b = int(i * seg * sr), min(n, int((i + 1) * seg * sr))
        if a >= n:
            break
        tt = t[a:b] - t[a]
        env = np.minimum(1.0, tt / 1.2) * np.minimum(1.0, (seg - tt) / 1.2 + 0.0)
        for k, f in enumerate(chords[i % 4]):
            tone = np.sin(2 * np.pi * f * t[a:b]) + 0.3 * np.sin(2 * np.pi * 2 * f * t[a:b])
            pan = 0.35 + 0.15 * k
            out[a:b, 0] += tone * env * (1 - pan) * 0.22
            out[a:b, 1] += tone * env * pan * 0.22
    out *= 0.9 / max(float(np.abs(out).max()), 1e-6)
    pcm = (out * 32767).astype(np.int16)
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video")
    ap.add_argument("--image")
    ap.add_argument("--image2")
    ap.add_argument("--image3")
    ap.add_argument("--music")
    ap.add_argument("--script-out")
    ap.add_argument("--work-dir", required=True)
    a = ap.parse_args()
    os.makedirs(a.work_dir, exist_ok=True)
    result = {"ok": True}

    # Дополнительные файлы создаём только если их ещё нет (ничего не перезаписываем)
    for path, variant in ((a.image, 0), (a.image2, 1), (a.image3, 2)):
        if path and not os.path.exists(path):
            make_image(path, variant)
    if a.music and not os.path.exists(a.music):
        make_music(a.music)

    if a.video and not os.path.exists(a.video):
        wav = os.path.join(a.work_dir, "test-speech.wav")
        silent = os.path.join(a.work_dir, "test-silent.mp4")
        engine = synth_speech(SCRIPT, wav)
        env, dur = envelope(wav, FPS)
        render_video(wav, silent, env)
        r = subprocess.run(
            ["ffmpeg", "-n", "-v", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2", "-shortest",
             "-movflags", "+faststart", a.video],
            capture_output=True, text=True)
        if r.returncode != 0:
            fail("MUX_FAILED", "Не удалось соединить картинку и звук тестового видео.", r.stderr.strip()[:200])
        if a.script_out:
            with open(a.script_out, "w", encoding="utf-8") as f:
                f.write(SCRIPT + "\n")
        os.remove(silent)
        result.update({"tts": engine, "duration": round(dur, 2), "video": a.video})
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
