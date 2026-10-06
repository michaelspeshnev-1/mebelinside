#!/usr/bin/env python3
"""Локальная транскрипция с таймкодами.

Два движка:
  whisper  - faster-whisper (основной, много языков, нужна папка с моделью)
  sphinx   - pocketsphinx   (запасной, только английский, модель внутри пакета)
  auto     - сначала whisper, если его модели нет - sphinx (только для английского)

Результат записывается в JSON-файл (--out). В stdout печатается одна строка JSON:
  успех:  {"ok": true, "engine": "...", ...}
  ошибка: {"ok": false, "error": {"code": "...", "message": "...", "hint": "..."}}
Код выхода: 0 - успех, 2 - понятная ошибка, 1 - непредвиденная.
"""
import argparse
import json
import os
import re
import sys
import wave

SPHINX_NOISE = {"<s>", "</s>", "<sil>", "[SPEECH]", "++NOISE++", "++noise++", "<unk>"}


class EngineFail(Exception):
    def __init__(self, code, message, hint=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint


def wav_info(path):
    try:
        with wave.open(path, "rb") as w:
            return w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
    except Exception as exc:
        raise EngineFail(
            "BAD_WAV",
            f"Не удалось прочитать звуковой файл: {exc}",
            "Звук должен быть WAV, 16 кГц, моно, 16 бит. Его делает шаг «извлечение звука».",
        )


# ---------------------------------------------------------------- whisper
def find_local_model(model, models_dir):
    """Ищет готовую CTranslate2-модель на диске. Возвращает путь или None."""
    candidates = []
    if os.path.isdir(model):
        candidates.append(model)
    if models_dir:
        candidates.append(os.path.join(models_dir, model))
        candidates.append(os.path.join(models_dir, f"faster-whisper-{model}"))
    for c in candidates:
        if os.path.isfile(os.path.join(c, "model.bin")) and os.path.isfile(os.path.join(c, "config.json")):
            return c
    return None


def run_whisper(wav, language, model, models_dir, allow_download):
    try:
        from faster_whisper import WhisperModel
    except Exception as exc:
        raise EngineFail(
            "WHISPER_NOT_INSTALLED",
            f"Библиотека faster-whisper не загружается: {exc}",
            "Выполните: .venv/bin/pip install -r requirements.txt",
        )

    local = find_local_model(model, models_dir)
    source = local
    if local is None:
        if not allow_download:
            raise EngineFail(
                "WHISPER_MODEL_MISSING",
                f"Модель Whisper «{model}» не найдена в папке models/.",
                "Скачайте её на компьютере с интернетом: python scripts/download-model.py "
                f"{model} и положите папку в models/{model}.",
            )
        os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "8")
        os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "30")
        source = model  # faster-whisper сам скачает по имени (tiny, base, small ...)

    try:
        if local:
            wm = WhisperModel(source, device="cpu", compute_type="int8")
        else:
            os.makedirs(models_dir or ".", exist_ok=True)
            wm = WhisperModel(source, device="cpu", compute_type="int8", download_root=models_dir)
    except Exception as exc:
        raise EngineFail(
            "WHISPER_MODEL_UNAVAILABLE",
            f"Не удалось получить модель Whisper «{model}»: {type(exc).__name__}.",
            "Скорее всего, нет доступа к huggingface.co. Скачайте модель вручную "
            "(scripts/download-model.py) и положите в models/.",
        )

    seg_iter, info = wm.transcribe(
        wav,
        language=None if language in (None, "", "auto") else language,
        word_timestamps=True,
        vad_filter=True,
        beam_size=5,
    )
    segments = []
    for i, s in enumerate(seg_iter):
        words = [
            {"start": round(w.start, 3), "end": round(w.end, 3), "word": w.word.strip()}
            for w in (s.words or [])
            if w.word.strip()
        ]
        segments.append(
            {"id": i, "start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(), "words": words}
        )
    return {
        "engine": "faster-whisper",
        "model": os.path.basename(os.path.normpath(local)) if local else model,
        "language": info.language,
        "segments": segments,
    }


# ---------------------------------------------------------------- sphinx
def run_sphinx(wav, language):
    if language not in (None, "", "auto", "en"):
        raise EngineFail(
            "SPHINX_ENGLISH_ONLY",
            f"Запасной движок pocketsphinx понимает только английский, а запрошен язык «{language}».",
            "Для русского нужна модель Whisper: python scripts/download-model.py small",
        )
    try:
        from pocketsphinx import Decoder
    except Exception as exc:
        raise EngineFail(
            "SPHINX_NOT_INSTALLED",
            f"Библиотека pocketsphinx не загружается: {exc}",
            "Выполните: .venv/bin/pip install -r requirements.txt",
        )

    rate, channels, width, _ = wav_info(wav)
    if (rate, channels, width) != (16000, 1, 2):
        raise EngineFail(
            "BAD_WAV",
            f"Нужен звук 16 кГц, моно, 16 бит, а получено: {rate} Гц, {channels} кан., {width * 8} бит.",
            "Запустите шаг извлечения звука заново.",
        )

    decoder = Decoder(samprate=16000, loglevel="FATAL")
    decoder.start_utt()
    with wave.open(wav, "rb") as w:
        while True:
            chunk = w.readframes(4000)
            if not chunk:
                break
            decoder.process_raw(chunk, False, False)
    decoder.end_utt()

    words = []
    for seg in decoder.seg():
        token = seg.word
        if token in SPHINX_NOISE or token.startswith("++") or token.startswith("["):
            continue
        token = re.sub(r"\(\d+\)$", "", token)  # варианты произношения: the(2)
        if not token:
            continue
        words.append({"start": seg.start_frame / 100.0, "end": (seg.end_frame + 1) / 100.0, "word": token})

    segments = []
    cur = []

    def flush():
        if not cur:
            return
        segments.append(
            {
                "id": len(segments),
                "start": round(cur[0]["start"], 3),
                "end": round(cur[-1]["end"], 3),
                "text": " ".join(x["word"] for x in cur),
                "words": [{**x, "start": round(x["start"], 3), "end": round(x["end"], 3)} for x in cur],
            }
        )
        cur.clear()

    for wd in words:
        if cur:
            gap = wd["start"] - cur[-1]["end"]
            too_long = len(cur) >= 9 or (wd["end"] - cur[0]["start"]) > 4.5
            if gap > 0.45 or too_long:
                flush()
        cur.append(wd)
    flush()

    return {"engine": "pocketsphinx", "model": "en-us (внутри пакета)", "language": "en", "segments": segments}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--language", default="auto")
    ap.add_argument("--engine", default="auto", choices=["auto", "whisper", "sphinx"])
    ap.add_argument("--model", default="small")
    ap.add_argument("--models-dir", default=None)
    ap.add_argument("--allow-download", action="store_true")
    args = ap.parse_args()

    try:
        if not os.path.isfile(args.wav):
            raise EngineFail("NO_WAV", f"Звуковой файл не найден: {args.wav}", "Сначала выполните извлечение звука.")

        result = None
        notes = []
        if args.engine == "whisper":
            result = run_whisper(args.wav, args.language, args.model, args.models_dir, args.allow_download)
        elif args.engine == "sphinx":
            result = run_sphinx(args.wav, args.language)
        else:  # auto
            try:
                result = run_whisper(args.wav, args.language, args.model, args.models_dir, args.allow_download)
            except EngineFail as exc:
                if not exc.code.startswith("WHISPER_"):
                    raise
                notes.append(f"Whisper недоступен ({exc.code}), использован запасной движок pocketsphinx.")
                if args.language not in (None, "", "auto", "en"):
                    raise EngineFail(
                        "NO_ENGINE_FOR_LANGUAGE",
                        f"Для языка «{args.language}» нужна модель Whisper, а её нет. "
                        "Запасной движок понимает только английский.",
                        exc.hint,
                    )
                result = run_sphinx(args.wav, "en")

        result["notes"] = notes
        result["audio"] = os.path.basename(args.wav)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(
            json.dumps(
                {
                    "ok": True,
                    "engine": result["engine"],
                    "model": result["model"],
                    "language": result["language"],
                    "segments": len(result["segments"]),
                    "notes": notes,
                },
                ensure_ascii=False,
            )
        )
        return 0
    except EngineFail as exc:
        print(json.dumps({"ok": False, "error": {"code": exc.code, "message": exc.message, "hint": exc.hint}}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
