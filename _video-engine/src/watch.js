// Автозапуск: следит за папкой input/ и сам делает ролики из новых файлов.
//   npm run watch            - работает постоянно (Ctrl+C - остановить)
//   npm run watch -- --once  - обработать то, что накопилось, и выйти (для расписания)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { runPipeline, loadConfig } from './pipeline.js';
import { parseArgs } from './args.js';
import { AUDIO_INPUT_EXT, DIRS, ROOT, VIDEO_EXT, ensureDirs, rel, slugify } from './paths.js';
import { explain } from './errors.js';

const STATE = path.join(DIRS.brief, '.watch-state.json');
const readState = () => { try { return JSON.parse(fs.readFileSync(STATE, 'utf8')); } catch { return {}; } };
const writeState = (s) => fs.writeFileSync(STATE, JSON.stringify(s, null, 2));
const EXT = new Set([...VIDEO_EXT, ...AUDIO_INPUT_EXT]);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function logger() {
  fs.mkdirSync(path.join(ROOT, 'logs'), { recursive: true });
  const file = path.join(ROOT, 'logs', `watch-${new Date().toISOString().slice(0, 10)}.log`);
  return (...a) => {
    const line = a.join(' ');
    console.log(line);
    fs.appendFileSync(file, `[${new Date().toISOString()}] ${line}\n`);
  };
}

function candidates(opts) {
  const st = readState();
  return fs.readdirSync(DIRS.input)
    .filter((f) => !f.startsWith('.') && EXT.has(path.extname(f).toLowerCase()))
    .filter((f) => (opts.only ? f === opts.only : opts['include-test'] || !f.startsWith('test-')))
    .map((f) => {
      const p = path.join(DIRS.input, f);
      const s = fs.statSync(p);
      return { f, p, size: s.size, mtimeMs: Math.round(s.mtimeMs) };
    })
    .filter((c) => {
      const prev = st[c.f];
      return !(prev && prev.size === c.size && prev.mtimeMs === c.mtimeMs); // уже обработан (успех или ошибка) и файл не менялся
    });
}

/** Файл «устоялся»: размер не меняется между двумя проверками (не копируется прямо сейчас). */
async function settled(c, waitMs) {
  await sleep(waitMs);
  try {
    const s = fs.statSync(c.p);
    return s.size === c.size && Math.round(s.mtimeMs) === c.mtimeMs && s.size > 0;
  } catch { return false; }
}

export async function watch(opts = {}) {
  ensureDirs();
  const cfg = loadConfig();
  const interval = (Number(opts.interval) || cfg.watchIntervalSec || 5) * 1000;
  const log = logger();
  const passthrough = Object.fromEntries(Object.entries(opts).filter(([k]) => !['once', 'include-test', 'interval', 'only', '_'].includes(k)));
  let stop = false;
  process.on('SIGINT', () => { stop = true; log('\nОстанавливаюсь после текущего файла…'); });
  process.on('SIGTERM', () => { stop = true; });

  log(`Слежу за ${rel(DIRS.input)}/ каждые ${interval / 1000} с (формат: ${passthrough.format || cfg.format}, тема: ${passthrough.theme || cfg.theme}). Положите видео или голосовую запись — ролик появится в ${rel(DIRS.final)}/.`);
  do {
    for (const c of candidates(opts)) {
      if (stop) break;
      if (!(await settled(c, Math.min(interval, 4000)))) { log(`… ${c.f} ещё копируется, подожду`); continue; }
      const name = slugify(c.f);
      log(`\n▶ Новый файл: ${c.f} → делаю ролик «${name}»`);
      const st = readState();
      try {
        const res = await runPipeline(c.p, passthrough, { log });
        st[c.f] = { size: c.size, mtimeMs: c.mtimeMs, status: 'done', final: rel(res.final), report: res.reportFile, at: new Date().toISOString() };
        log(`✔ ${c.f} → ${rel(res.final)}`);
      } catch (e) {
        st[c.f] = { size: c.size, mtimeMs: c.mtimeMs, status: 'failed', error: e.title || e.message, at: new Date().toISOString() };
        log(explain(e));
        log(`✖ ${c.f}: не получилось. Исправьте причину и замените файл (или удалите запись из ${rel(STATE)}) — тогда я попробую снова.`);
      }
      writeState(st);
    }
    if (opts.once) break;
    await sleep(interval);
  } while (!stop);
  log('Готово.');
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    await watch(parseArgs(process.argv.slice(2)));
  } catch (e) {
    console.error(explain(e));
    process.exit(1);
  }
}
