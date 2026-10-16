"""Текстовые задачи через Gemini API — чтобы не тратить лимиты Claude на массовую работу.

Ключ — в переменной окружения GEMINI_API_KEY (ключ из AI Studio; подписка Gemini Pro ≠ API-ключ).
Примеры:
  python tools/gemini_text.py -p "Перепиши в 3 вариантах" -f texts/draft.md -o out.md
  python tools/gemini_text.py -p "Сделай alt-тексты для списка фото" -f list.txt
Подходит для: черновики постов, alt-тексты, переписывание описаний, сжатие и очистка текстов.
Не подходит: решения по сайту, факты о компании без проверки (проверять по BACKLOG/ROADMAP).
"""
import argparse, json, os, sys, urllib.error, urllib.parse, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prompt", required=True, help="что сделать")
ap.add_argument("-f", "--file", help="файл с исходным текстом")
ap.add_argument("-o", "--out", help="куда сохранить ответ (иначе — в консоль)")
ap.add_argument("--model", default=os.environ.get("GEMINI_MODEL", "gemini-flash-latest"))
a = ap.parse_args()

key = os.environ.get("GEMINI_API_KEY", "")
if not key:
    sys.exit("Нет GEMINI_API_KEY в окружении (ключ из aistudio.google.com/apikey)")

text = a.prompt
if a.file:
    text += "\n\n---\n" + open(a.file, encoding="utf-8").read()
url = f"https://generativelanguage.googleapis.com/v1beta/models/{a.model}:generateContent?key={urllib.parse.quote(key)}"
body = json.dumps({"contents": [{"parts": [{"text": text}]}], "generationConfig": {"temperature": 0.6}}).encode()
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    sys.exit(f"Gemini {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")
out = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"]).strip()
if a.out:
    open(a.out, "w", encoding="utf-8").write(out)
    print(f"сохранено: {a.out} ({len(out)} знаков)")
else:
    print(out)
