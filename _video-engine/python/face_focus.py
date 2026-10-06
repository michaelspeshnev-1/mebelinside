#!/usr/bin/env python3
"""ОПЦИОНАЛЬНО (OpenCV): где в кадре лицо - нужно для вертикального кадрирования 9:16.

Берёт несколько кадров видео, ищет лицо каскадом Хаара и выдаёт медианный центр.
stdout: одна строка JSON {"ok":true,"found":bool,"focusX":0..1,"focusY":0..1,"samples":N,"hits":K}
Лицо не найдено - found=false, центр кадра (0.5, 0.5): конвейер продолжит работу.
"""
import argparse, json, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--samples", type=int, default=12)
    a = ap.parse_args()
    try:
        import cv2
        import numpy as np
    except Exception as exc:
        print(json.dumps({"ok": False, "error": {"code": "OPENCV_MISSING", "message": f"OpenCV не установлен: {exc}",
              "hint": "Выполните: .venv/bin/pip install -r requirements-optional.txt"}}, ensure_ascii=False))
        return 2
    cap = cv2.VideoCapture(a.video)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if not cap.isOpened() or n <= 0:
        print(json.dumps({"ok": False, "error": {"code": "CV_CANNOT_OPEN", "message": "OpenCV не смог открыть видео.", "hint": "Проверьте файл."}}, ensure_ascii=False))
        return 2
    det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    xs, ys, hits = [], [], 0
    for i in range(a.samples):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(n * (i + 0.5) / a.samples))
        ok, fr = cap.read()
        if not ok:
            continue
        h, w = fr.shape[:2]
        faces = det.detectMultiScale(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY), 1.1, 5, minSize=(max(40, w // 20), max(40, w // 20)))
        if len(faces):
            x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            xs.append((x + fw / 2) / w); ys.append((y + fh / 2) / h); hits += 1
    found = hits >= max(2, a.samples // 4)
    print(json.dumps({"ok": True, "found": bool(found), "focusX": round(float(np.median(xs)), 3) if found else 0.5,
                      "focusY": round(float(np.median(ys)), 3) if found else 0.5, "samples": a.samples, "hits": hits}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
