#!/usr/bin/env bash
# Автозапуск наблюдателя при входе в систему (macOS LaunchAgent / Linux systemd --user).
#   bash scripts/install-autostart.sh            - установить
#   bash scripts/install-autostart.sh --print    - только показать, что будет создано
#   bash scripts/install-autostart.sh --remove   - убрать автозапуск
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NODE="$(command -v node)"
MODE="${1:-install}"
LABEL="ru.mebelinside.video-engine"

mac_plist() { cat <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>$NODE</string><string>$ROOT/src/watch.js</string></array>
  <key>WorkingDirectory</key><string>$ROOT</string>
  <key>EnvironmentVariables</key><dict><key>PATH</key><string>$(dirname "$NODE"):/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$ROOT/logs/launchd.out.log</string>
  <key>StandardErrorPath</key><string>$ROOT/logs/launchd.err.log</string>
</dict></plist>
PLIST
}
linux_unit() { cat <<UNIT
[Unit]
Description=Мебель Inside: автомонтаж роликов из папки input/
[Service]
WorkingDirectory=$ROOT
ExecStart=$NODE $ROOT/src/watch.js
Restart=always
RestartSec=10
Environment=PATH=$(dirname "$NODE"):/usr/local/bin:/usr/bin:/bin
[Install]
WantedBy=default.target
UNIT
}

mkdir -p "$ROOT/logs"
case "$(uname)" in
  Darwin)
    PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
    case "$MODE" in
      --print) mac_plist ;;
      --remove) launchctl unload "$PLIST" 2>/dev/null || true; rm -f "$PLIST"; echo "Автозапуск убран." ;;
      *) mkdir -p "$HOME/Library/LaunchAgents"; mac_plist > "$PLIST"; launchctl unload "$PLIST" 2>/dev/null || true; launchctl load "$PLIST"; echo "Готово: наблюдатель запустится сам при входе в систему и уже работает. Логи: $ROOT/logs/" ;;
    esac ;;
  Linux)
    UNIT="$HOME/.config/systemd/user/mebel-video-engine.service"
    case "$MODE" in
      --print) linux_unit ;;
      --remove) systemctl --user disable --now mebel-video-engine 2>/dev/null || true; rm -f "$UNIT"; echo "Автозапуск убран." ;;
      *) mkdir -p "$(dirname "$UNIT")"; linux_unit > "$UNIT"; systemctl --user daemon-reload; systemctl --user enable --now mebel-video-engine; echo "Готово: наблюдатель запущен и стартует при входе. Логи: journalctl --user -u mebel-video-engine, $ROOT/logs/" ;;
    esac ;;
  *) echo "Эта система не поддерживается скриптом (Windows: создайте задачу в Планировщике с командой: node src/watch.js)"; exit 1 ;;
esac
