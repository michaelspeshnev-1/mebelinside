#!/usr/bin/env bash
# Установка «одной командой» (macOS и Linux): npm run setup  или  bash scripts/setup.sh
# Ничего не ставит в систему без вашего ведома: только внутрь папки проекта (node_modules, .venv).
# Системные программы (Node.js, FFmpeg, Python) скрипт НЕ устанавливает, а подсказывает команду.
set -u
cd "$(dirname "$0")/.."
red() { printf '\033[31m%s\033[0m\n' "$*"; }
ok()  { printf '\033[32m✔\033[0m %s\n' "$*"; }
miss=0

echo "== 1/5 Проверяю системные программы"
if command -v node >/dev/null && [ "$(node -p 'process.versions.node.split(".")[0]')" -ge 20 ]; then ok "Node.js $(node -v)"; else red "✖ Нужен Node.js 20+"; miss=1; fi
for t in ffmpeg ffprobe python3; do
  if command -v "$t" >/dev/null; then ok "$t"; else red "✖ Не найден $t"; miss=1; fi
done
if [ "$miss" = 1 ]; then
  echo
  echo "Поставьте недостающее и запустите снова:"
  echo "  macOS:  brew install node python ffmpeg"
  echo "  Ubuntu: sudo apt-get install nodejs npm python3 python3-venv ffmpeg   (Node 20+: https://nodejs.org)"
  exit 1
fi
[ "${1:-}" = "--check" ] && { echo "Проверка пройдена (режим --check: дальше не иду)."; exit 0; }

echo "== 2/5 Пакеты Node (точные версии из package-lock.json)"
npm ci || { red "✖ npm ci не удался (нет интернета?)"; exit 1; }

echo "== 3/5 Python-окружение .venv и точные версии из requirements.txt"
[ -d .venv ] || python3 -m venv .venv || { red "✖ не удалось создать .venv (на Ubuntu: sudo apt-get install python3-venv)"; exit 1; }
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/pip install -r requirements.txt || { red "✖ pip install не удался"; exit 1; }

echo "== 4/5 Модель Whisper для точных субтитров (≈460 МБ, один раз)"
if [ -f models/small/model.bin ]; then ok "модель уже на месте"; else
  .venv/bin/python scripts/download-model.py small || echo "⚠ Модель не скачалась. Движок будет работать на запасном (английском) распознавании. Повторить: .venv/bin/python scripts/download-model.py small"
fi

echo "== 5/5 Диагностика"
node src/doctor.js
echo
echo "Дальше:  npm run demo      (проверочный ролик)"
echo "         npm run watch     (автоматически делать ролики из папки input/)"
echo "         bash scripts/install-autostart.sh   (запускать наблюдатель при входе в систему)"
