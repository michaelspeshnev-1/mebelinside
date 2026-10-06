#!/usr/bin/env python3
"""Скачивание модели Whisper (faster-whisper) в папку models/.

Запускайте на компьютере, который выходит в интернет (нужен доступ к huggingface.co):

    .venv/bin/python scripts/download-model.py small

Размеры (чем больше, тем точнее и медленнее):
    tiny (~75 МБ), base (~140 МБ), small (~460 МБ, хороший баланс), medium (~1.5 ГБ)
Для русского языка берите не меньше small.
"""
import os
import sys

MODELS = {"tiny", "base", "small", "medium", "large-v3"}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "small"
    if name not in MODELS:
        print(f"Неизвестная модель «{name}». Доступно: {', '.join(sorted(MODELS))}")
        return 2
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(root, "models", name)
    try:
        from huggingface_hub import snapshot_download
    except Exception as exc:
        print(f"Не найдена библиотека huggingface_hub ({exc}). Выполните: .venv/bin/pip install -r requirements.txt")
        return 2
    print(f"Скачиваю модель «{name}» в {target} ...")
    try:
        snapshot_download(repo_id=f"Systran/faster-whisper-{name}", local_dir=target)
    except Exception as exc:
        print(f"Не удалось скачать: {type(exc).__name__}: {exc}")
        print("Скорее всего, нет интернета или сайт huggingface.co закрыт сетью/файрволом.")
        print("Скачайте папку Systran/faster-whisper-%s вручную на другом компьютере и положите в models/%s/" % (name, name))
        return 1
    ok = os.path.isfile(os.path.join(target, "model.bin"))
    print("Готово." if ok else "Скачивание завершилось, но model.bin не найден — повторите.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
