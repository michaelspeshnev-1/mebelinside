// Диагностика: проверяет всё нужное для работы и объясняет проблемы человеческим языком.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { run } from './exec.js';
import { DIRS, PY, ROOT } from './paths.js';
import { findBrowser } from './browser.js';

const require = createRequire(import.meta.url);

const osName = () => {
  const p = process.platform;
  if (p === 'darwin') return 'macOS';
  if (p === 'win32') return 'Windows';
  try {
    const m = fs.readFileSync('/etc/os-release', 'utf8').match(/PRETTY_NAME="(.+)"/);
    return m ? m[1] : 'Linux';
  } catch { return 'Linux'; }
};

const installHint = {
  ffmpeg: 'Ubuntu/Debian: sudo apt-get install ffmpeg · macOS: brew install ffmpeg · Windows: winget install Gyan.FFmpeg',
  node: 'Установите Node.js 20 или новее: https://nodejs.org (или nvm).',
};

/** Каждая проверка возвращает {level: ok|warn|fail, name, detail, why?, fix?}. level=warn не мешает работе. */
export async function runChecks() {
  const out = [];
  const add = (level, name, detail = '', why = '', fix = '') => out.push({ level, name, detail, why, fix });

  add('ok', 'Система', `${osName()}, ${os.arch()}, ${os.cpus().length} ядер, ${(os.totalmem() / 1e9).toFixed(1)} ГБ памяти`);

  const major = Number(process.versions.node.split('.')[0]);
  major >= 20
    ? add('ok', 'Node.js', `v${process.versions.node}`)
    : add('fail', 'Node.js', `v${process.versions.node}`, 'Remotion требует Node.js 20 или новее.', installHint.node);

  if (os.totalmem() < 3.5e9) add('warn', 'Оперативная память', `${(os.totalmem() / 1e9).toFixed(1)} ГБ`, 'Рендер Remotion в Chrome любит память; на слабом компьютере может падать.', 'Закройте другие программы или уменьшите размер ролика: --size 960x540.');

  // FFmpeg / ffprobe
  for (const t of ['ffmpeg', 'ffprobe']) {
    try {
      const r = await run(t, ['-version']);
      const v = (r.stdout.match(/version (\S+)/) || [])[1];
      r.code === 0 ? add('ok', t, `версия ${v}`) : add('fail', t, 'не запускается', 'Программа есть, но не работает.', installHint.ffmpeg);
    } catch {
      add('fail', t, 'не найден', 'Движок без неё не сможет читать и собирать видео.', installHint.ffmpeg);
    }
  }
  try {
    const e = await run('ffmpeg', ['-hide_banner', '-encoders']);
    const has = (n) => new RegExp(`\\s${n}\\s`).test(e.stdout);
    has('aac') ? add('ok', 'FFmpeg: звук AAC', 'есть') : add('fail', 'FFmpeg: звук AAC', 'нет', 'Без AAC итоговый MP4 не получит звук.', installHint.ffmpeg);
    has('libx264') ? add('ok', 'FFmpeg: видео H.264 (libx264)', 'есть') : add('fail', 'FFmpeg: видео H.264 (libx264)', 'нет', 'Remotion кодирует картинку в H.264.', 'Поставьте полную сборку FFmpeg (apt install ffmpeg / brew install ffmpeg).');
  } catch { /* уже сообщили выше */ }

  // Python
  if (!fs.existsSync(PY)) {
    add('fail', 'Python-окружение (.venv)', 'нет', 'В нём живёт распознавание речи.', 'python3 -m venv .venv && .venv/bin/pip install -r requirements.txt');
  } else {
    const v = await run(PY, ['--version']);
    add('ok', 'Python-окружение (.venv)', (v.stdout || v.stderr).trim());
    const probeCode = `
import importlib,json
r={}
for m in ["faster_whisper","pocketsphinx","numpy","cv2"]:
    try:
        mod=importlib.import_module(m); r[m]=getattr(mod,"__version__","ok")
    except Exception as e: r[m]=None
print(json.dumps(r))`;
    const p = await run(PY, ['-c', probeCode]);
    let mods = {};
    try { mods = JSON.parse(p.stdout.trim()); } catch { /* пусто */ }
    mods.faster_whisper ? add('ok', 'faster-whisper (Python)', `v${mods.faster_whisper}`) : add('fail', 'faster-whisper (Python)', 'не загружается', 'Это основной движок распознавания.', '.venv/bin/pip install -r requirements.txt');
    mods.pocketsphinx ? add('ok', 'pocketsphinx (запасной движок)', mods.pocketsphinx === 'ok' ? 'установлен' : `v${mods.pocketsphinx}`) : add('warn', 'pocketsphinx (запасной движок)', 'нет', 'Без него при отсутствии модели Whisper распознавания не будет.', '.venv/bin/pip install -r requirements.txt');
    mods.cv2 ? add('ok', 'OpenCV (необязательно)', `v${mods.cv2} — лицо и вертикальное кадрирование доступны`) : add('warn', 'OpenCV (необязательно)', 'не установлен', 'Нужен только для --face (вертикальное кадрирование по лицу).', '.venv/bin/pip install -r requirements-optional.txt');
  }

  // Модель Whisper
  const modelDirs = fs.existsSync(DIRS.models) ? fs.readdirSync(DIRS.models).filter((d) => fs.existsSync(path.join(DIRS.models, d, 'model.bin'))) : [];
  modelDirs.length
    ? add('ok', 'Модель Whisper в models/', modelDirs.join(', '))
    : add('warn', 'Модель Whisper в models/', 'не найдена', 'Без неё работает только запасной английский движок (больше ошибок, нет русского).', 'На компьютере с интернетом: .venv/bin/python scripts/download-model.py small');

  // Node-пакеты
  for (const pkg of ['remotion', '@remotion/bundler', '@remotion/renderer', '@remotion/cli', 'react', 'react-dom', 'ajv']) {
    try {
      const v = JSON.parse(fs.readFileSync(path.join(ROOT, 'node_modules', pkg, 'package.json'), 'utf8')).version;
      add('ok', `пакет ${pkg}`, `v${v}`);
    } catch {
      add('fail', `пакет ${pkg}`, 'не установлен', 'Папка node_modules неполная.', 'В папке проекта выполните: npm ci');
    }
  }

  // Браузер
  const b = findBrowser();
  b ? add('ok', 'Браузер для Remotion', `${b.source}: ${b.path}`) : add('warn', 'Браузер для Remotion', 'не найден', 'Remotion попробует скачать свой при первом рендере (нужен интернет).', 'Или установите Google Chrome / укажите REMOTION_BROWSER=/путь/к/chrome');

  // Диск и папки
  try {
    const s = fs.statfsSync(ROOT);
    const free = (s.bavail * s.bsize) / 1e9;
    free > 2 ? add('ok', 'Свободное место', `${free.toFixed(1)} ГБ`) : add('warn', 'Свободное место', `${free.toFixed(1)} ГБ`, 'Видео занимает много места.', 'Освободите диск или очистите renders/ и previews/.');
  } catch { /* не критично */ }
  for (const [name, dir] of Object.entries(DIRS)) {
    if (name === 'models') continue;
    try {
      fs.mkdirSync(dir, { recursive: true });
      fs.accessSync(dir, fs.constants.W_OK);
    } catch {
      add('fail', `папка ${name}/`, 'нет доступа на запись', 'Движок не сможет сохранять результаты.', 'Проверьте права на папку проекта.');
    }
  }
  const inputs = fs.existsSync(DIRS.input) ? fs.readdirSync(DIRS.input).filter((f) => !f.startsWith('.')) : [];
  add('ok', 'Папка input/', inputs.length ? `${inputs.length} файл(ов): ${inputs.slice(0, 4).join(', ')}` : 'пока пусто — положите туда видео (или npm run make-test-assets)');

  // Необязательно: синтез речи для тестовых файлов
  const tts = [];
  for (const t of ['flite', 'espeak-ng']) { try { await run(t, ['--version']); tts.push(t); } catch { /* нет */ } }
  tts.length ? add('ok', 'Синтез речи для тестовых файлов (необязательно)', tts.join(', ')) : add('warn', 'Синтез речи для тестовых файлов (необязательно)', 'нет', 'Нужен только для npm run make-test-assets.', 'Ubuntu: sudo apt-get install flite · macOS: brew install flite');
  return out;
}

export function printChecks(checks, log = console.log) {
  const icon = { ok: '✔', warn: '⚠', fail: '✖' };
  for (const c of checks) {
    log(`${icon[c.level]} ${c.name}${c.detail ? ` — ${c.detail}` : ''}`);
    if (c.level !== 'ok') {
      if (c.why) log(`    Почему важно: ${c.why}`);
      if (c.fix) log(`    Что сделать:  ${c.fix}`);
    }
  }
  const fails = checks.filter((c) => c.level === 'fail').length;
  const warns = checks.filter((c) => c.level === 'warn').length;
  log('');
  log(fails ? `ИТОГ: ${fails} критичных проблем(ы) — без исправления движок не заработает.` : warns ? `ИТОГ: работать можно, но есть замечания (${warns}) — они не критичны, но стоит прочитать.` : 'ИТОГ: всё в порядке.');
  return fails === 0;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const ok = printChecks(await runChecks());
  process.exit(ok ? 0 : 1);
}
