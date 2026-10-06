// Проверка готового MP4: ffprobe (параметры) + полное декодирование + осмысленность картинки и звука.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { run } from './exec.js';
import { EngineError, explain } from './errors.js';
import { ROOT } from './paths.js';

/** Идём по «коробкам» MP4 и проверяем, что moov (оглавление) стоит перед mdat: ролик стартует без полной загрузки. */
function faststart(file) {
  const fd = fs.openSync(file, 'r');
  try {
    const size = fs.fstatSync(fd).size;
    let pos = 0;
    const order = [];
    const hdr = Buffer.alloc(16);
    while (pos + 8 <= size && order.length < 12) {
      fs.readSync(fd, hdr, 0, 16, pos);
      let len = hdr.readUInt32BE(0);
      const type = hdr.toString('latin1', 4, 8);
      if (len === 1) len = Number(hdr.readBigUInt64BE(8));
      order.push(type);
      if (len < 8) break;
      pos += len;
    }
    return order.indexOf('moov') !== -1 && order.indexOf('moov') < order.indexOf('mdat');
  } finally {
    fs.closeSync(fd);
  }
}

export async function verifyVideo(file, expect = {}) {
  const checks = [];
  const add = (name, ok, detail = '') => checks.push({ name, ok, detail });

  if (!fs.existsSync(file)) {
    throw new EngineError('VERIFY_NO_FILE', `Файл для проверки не найден: ${file}`, { why: 'Нечего проверять.', fix: 'Сначала создайте ролик: npm run demo' });
  }
  add('файл не пустой', fs.statSync(file).size > 10000, `${(fs.statSync(file).size / 1e6).toFixed(2)} МБ`);

  // 1. ffprobe
  const pr = await run('ffprobe', ['-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', file]);
  if (pr.code !== 0) {
    add('ffprobe читает файл', false, pr.stderr.trim().split('\n')[0]);
    return { ok: false, checks };
  }
  const j = JSON.parse(pr.stdout);
  const v = j.streams.filter((s) => s.codec_type === 'video');
  const a = j.streams.filter((s) => s.codec_type === 'audio');
  const dur = Number(j.format.duration);
  add('ffprobe читает файл', true, `контейнер ${j.format.format_name.split(',')[0]}, ${dur.toFixed(2)} с`);
  add('одна видеодорожка H.264, yuv420p (обычный диапазон)', v.length === 1 && v[0].codec_name === 'h264' && v[0].pix_fmt === 'yuv420p', v[0] ? `${v[0].codec_name}, ${v[0].pix_fmt}, ${v[0].color_range || '?'}, ${v[0].color_space || '?'}` : 'нет видео');
  add('одна звуковая дорожка AAC', a.length === 1 && a[0].codec_name === 'aac', a[0] ? `${a[0].codec_name}, ${a[0].sample_rate} Гц, ${a[0].channels} кан.` : 'нет звука');
  const fps = v[0] ? eval(v[0].avg_frame_rate) : 0; // «30/1» -> 30
  if (expect.width) add(`размер ${expect.width}×${expect.height}`, v[0]?.width === expect.width && v[0]?.height === expect.height, `${v[0]?.width}×${v[0]?.height}`);
  if (expect.fps) add(`частота кадров ${expect.fps}`, Math.abs(fps - expect.fps) < 0.01, `${fps}`);
  if (expect.duration) add(`длительность ≈ ${expect.duration.toFixed(2)} с (±0.15)`, Math.abs(dur - expect.duration) <= 0.15, `${dur.toFixed(2)} с`);
  if (v[0] && a[0]) {
    const dv = Number(v[0].duration), da = Number(a[0].duration);
    add('звук и картинка одной длины (±0.15 с)', Math.abs(dv - da) <= 0.15, `видео ${dv.toFixed(2)} с, звук ${da.toFixed(2)} с`);
  }
  add('faststart (moov перед данными)', faststart(file), '');

  // 2. Полное декодирование обеих дорожек: любая битая вставка даст ошибку
  const dec = await run('ffmpeg', ['-v', 'error', '-xerror', '-i', file, '-f', 'null', '-']);
  add('полное декодирование без ошибок', dec.code === 0 && dec.stderr.trim() === '', dec.stderr.trim().split('\n')[0] || 'ошибок нет');

  // 3. Число кадров совпадает с ожиданием
  const fc = await run('ffprobe', ['-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', file]);
  const frames = parseInt(fc.stdout.trim(), 10);
  if (expect.duration && expect.fps) {
    const want = Math.round(expect.duration * expect.fps);
    add(`кадров ≈ ${want} (±2)`, Math.abs(frames - want) <= 2, `${frames}`);
  } else add('кадры декодируются', frames > 0, `${frames}`);

  // 4. Картинка не чёрная и сцены различаются
  const times = (expect.sceneMids && expect.sceneMids.length ? expect.sceneMids : [dur * 0.2, dur * 0.5, dur * 0.8]).filter((t) => t < dur);
  const hashes = [];
  const lumas = [];
  for (const t of times) {
    const f = await run('ffmpeg', ['-v', 'error', '-ss', String(t), '-i', file, '-frames:v', '1', '-vf', 'scale=64:36,format=gray', '-f', 'rawvideo', '-']);
    const buf = Buffer.from(f.stdout, 'latin1');
    // stdout прочитан как строка - для надёжности считаем яркость отдельным запросом
    const sig = await run('ffmpeg', ['-v', 'error', '-ss', String(t), '-i', file, '-frames:v', '1', '-vf', 'signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-', '-f', 'null', '-']);
    const m = sig.stdout.match(/YAVG=([\d.]+)/);
    lumas.push(m ? Number(m[1]) : 0);
    hashes.push(crypto.createHash('md5').update(buf).digest('hex'));
  }
  add('кадры сцен не чёрные и не белые', lumas.every((y) => y > 12 && y < 245), lumas.map((y) => y.toFixed(0)).join(' / '));
  add('сцены визуально различаются', new Set(hashes).size === hashes.length, `${new Set(hashes).size} разных из ${hashes.length}`);

  // 5. Звук не пустой
  const vol = await run('ffmpeg', ['-v', 'info', '-i', file, '-vn', '-af', 'volumedetect', '-f', 'null', '-']);
  const mean = Number((vol.stderr.match(/mean_volume: (-?[\d.]+) dB/) || [])[1]);
  const max = Number((vol.stderr.match(/max_volume: (-?[\d.]+) dB/) || [])[1]);
  add('звук слышен и не клиппирует', mean > -45 && max <= 0, `средняя ${mean} дБ, пик ${max} дБ`);

  return { ok: checks.every((c) => c.ok), checks, duration: dur, frames };
}

export function printReport(rep, log = console.log) {
  for (const c of rep.checks) log(`  ${c.ok ? '✔' : '✖'} ${c.name}${c.detail ? `  [${c.detail}]` : ''}`);
  log(rep.ok ? '  ИТОГ: файл исправен.' : '  ИТОГ: есть проблемы, файл НЕ считается готовым.');
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const file = args.find((x) => !x.startsWith('--'));
  const pi = args.indexOf('--plan');
  let expect = {};
  try {
    if (pi >= 0) {
      const plan = JSON.parse(fs.readFileSync(args[pi + 1], 'utf8'));
      expect = { width: plan.output.width, height: plan.output.height, fps: plan.output.fps, duration: plan.source.duration, sceneMids: plan.scenes.map((s) => (s.start + s.end) / 2) };
    }
    if (!file) throw new EngineError('VERIFY_ARGS', 'Не указан файл для проверки', { why: 'Нужно имя MP4.', fix: 'Пример: npm run verify -- final/demo.mp4 --plan brief/demo.plan.json' });
    const rep = await verifyVideo(path.resolve(ROOT, file), expect);
    printReport(rep);
    process.exit(rep.ok ? 0 : 1);
  } catch (e) {
    console.error(explain(e));
    process.exit(1);
  }
}
