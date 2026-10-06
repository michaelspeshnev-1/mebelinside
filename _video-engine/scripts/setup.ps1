# Установка для Windows: npm run setup  (или правый клик -> Выполнить в PowerShell)
$ErrorActionPreference = 'Continue'
Set-Location (Join-Path $PSScriptRoot '..')
function Ok($m){ Write-Host "OK  $m" -ForegroundColor Green }
function Bad($m){ Write-Host "ОШИБКА  $m" -ForegroundColor Red }
Write-Host "== 1/5 Проверяю программы"
$miss = @()
$nodeOk = $false
if (Get-Command node -ErrorAction SilentlyContinue) { $v=[int]((node -p "process.versions.node.split('.')[0]")); if($v -ge 20){Ok "Node.js $(node -v)"; $nodeOk=$true} }
if(-not $nodeOk){ Bad "Нужен Node.js 20+"; $miss += "winget install OpenJS.NodeJS.LTS" }
foreach($t in 'ffmpeg','ffprobe'){ if(Get-Command $t -ErrorAction SilentlyContinue){Ok $t}else{Bad "Не найден $t"; if($miss -notcontains "winget install Gyan.FFmpeg"){$miss += "winget install Gyan.FFmpeg"}} }
$py = $null
foreach($c in 'python','py'){ if(Get-Command $c -ErrorAction SilentlyContinue){ $o = & $c --version 2>&1; if("$o" -match 'Python 3'){ $py=$c; Ok "$o"; break } } }
if(-not $py){ Bad "Не найден Python 3"; $miss += "winget install Python.Python.3.12" }
if($miss.Count -gt 0){
  Write-Host "`nУстановите недостающее (каждая строка — отдельная команда в PowerShell), потом ЗАКРОЙТЕ и снова откройте окно и запустите установку:" -ForegroundColor Yellow
  $miss | ForEach-Object { Write-Host "  $_" }
  exit 1
}
Write-Host "== 2/5 Пакеты Node"
npm ci; if($LASTEXITCODE -ne 0){ Bad "npm ci не удался"; exit 1 }
Write-Host "== 3/5 Python-окружение"
if(-not (Test-Path .venv)){ & $py -m venv .venv; if($LASTEXITCODE -ne 0){ Bad "не удалось создать .venv"; exit 1 } }
.\.venv\Scripts\python.exe -m pip install --quiet --upgrade pip
.\.venv\Scripts\python.exe -c "import pathlib;pathlib.Path('.venv/req-win.txt').write_text(''.join(l for l in open('requirements.txt',encoding='utf-8') if not l.lower().startswith('pocketsphinx')),encoding='utf-8')"
.\.venv\Scripts\pip.exe install -r .venv\req-win.txt; if($LASTEXITCODE -ne 0){ Bad "pip install не удался"; exit 1 }
# запасной движок pocketsphinx: на Windows готовой сборки нет, он не обязателен (основной - Whisper)
.\.venv\Scripts\pip.exe install --only-binary=:all: pocketsphinx==5.1.1 2>$null
if($LASTEXITCODE -ne 0){ Write-Host "Запасной движок pocketsphinx на Windows не ставится - это нормально, работает Whisper." -ForegroundColor Yellow }
$global:LASTEXITCODE = 0
Write-Host "== 4/5 Модель Whisper (~460 МБ, один раз)"
if(Test-Path models\small\model.bin){ Ok "модель уже на месте" } else { .\.venv\Scripts\python.exe scripts\download-model.py small; if($LASTEXITCODE -ne 0){ Write-Host "Модель не скачалась. Будет запасное английское распознавание. Повтор: .\.venv\Scripts\python.exe scripts\download-model.py small" -ForegroundColor Yellow } }
Write-Host "== 5/5 Диагностика"
node src/doctor.js
Write-Host "`nДальше:  npm run demo   |   npm run watch   |   powershell -File scripts\install-autostart.ps1"
