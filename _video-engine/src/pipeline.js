// Весь конвейер «видео/звук -> final/<имя>.mp4». Используется командами run, demo и watch.
import fs from 'node:fs';
import path from 'node:path';
import { probe, checkInput } from './probe.js';
import { extractAudio } from './audio.js';
import { transcribe } from './transcribe.js';
import { buildPlan, loadHints, loadTheme } from './plan.js';
import { validatePlan, validatePlanFile } from './schema.js';
import { prepareRender, renderPreview, renderVisual } from './render.js';
import { finish, measureDuck } from './finish.js';
import { verifyVideo, printReport } from './verify-output.js';
import { accept, writeReport } from './acceptance.js';
import { faceFocus } from './face.js';
import { DIRS, ROOT, adoptInput, ensureDirs, rel, slugify } from './paths.js';
import { EngineError } from './errors.js';

export function loadConfig() {
  const file = path.join(ROOT, 'engine.config.json');
  const defaults = { theme: 'mebel-inside', format: 'landscape', language: 'auto', engine: 'auto', model: 'small', face: false, music: 'auto', watchIntervalSec: 5 };
  if (!fs.existsSync(file)) return defaults;
  try {
    return { ...defaults, ...JSON.parse(fs.readFileSync(file, 'utf8')) };
  } catch (e) {
    throw new EngineError('CONFIG_BAD_JSON', 'Файл engine.config.json — не корректный JSON', { why: String(e.message).replace(/\s+/g, ' '), fix: 'Исправьте запятые и кавычки или удалите файл — тогда возьмутся настройки по умолчанию.' });
  }
}

export async function runPipeline(inputArg, opts = {}, { log = console.log } = {}) {
  ensureDirs();
  const cfg = { ...loadConfig(), ...Object.fromEntries(Object.entries(opts).filter(([, v]) => v !== undefined)) };
  let step = 0;
  const STEPS = 8;
  const say = (t) => log(`\n[${++step}/${STEPS}] ${t}`);
  const t0 = Date.now();
  const input = adoptInput(inputArg);
  const name = slugify(cfg.name || path.basename(input));
  const P = (d, ext) => path.join(DIRS[d], `${name}${ext}`);
  const allowTest = Boolean(cfg['use-test-assets']) || path.basename(input).startsWith('test-') || name === 'demo';
  let size;
  if (cfg.size) {
    const m = String(cfg.size).match(/^(\d{2,4})x(\d{2,4})$/);
    if (!m) throw new EngineError('BAD_SIZE', `Размер «${cfg.size}» не понят`, { why: 'Нужен формат ШИРИНАxВЫСОТА.', fix: 'Например: --size 1280x720' });
    size = { width: +m[1], height: +m[2] };
  }

  say(`Проверяю файл: ${rel(input)}`);
  const info = await probe(input);
  for (const w of checkInput(info)) log(`  ⚠ ${w}`);
  log(info.video ? `  видео ${info.video.width}×${info.video.height}, ${info.video.fps} к/с, ${info.duration.toFixed(2)} с, звук: ${info.audio.codec}` : `  только звук (${info.audio.codec}), ${info.duration.toFixed(2)} с — соберу ролик из фото, без спикера в кадре`);
  fs.writeFileSync(P('brief', '.probe.json'), JSON.stringify(info, null, 2));

  let plan;
  let transcript = null;
  let planFile = P('brief', '.plan.json');
  if (cfg.plan) {
    say('Беру готовый план (расшифровка пропущена)');
    planFile = path.resolve(ROOT, cfg.plan);
    plan = validatePlanFile(planFile);
    step += 2;
    log('  план прошёл проверку');
    const tj = path.join(DIRS.transcript, `${plan.name}.json`);
    if (fs.existsSync(tj)) transcript = JSON.parse(fs.readFileSync(tj, 'utf8'));
  } else {
    say('Извлекаю звук');
    const wav = await extractAudio(input, P('transcript', '.wav'));
    log(`  ${rel(wav)}`);

    say('Распознаю речь (локально, с таймкодами слов)');
    transcript = await transcribe(wav, P('transcript', '.json'), { language: cfg.language, engine: cfg.engine, model: cfg.model, allowDownload: false });
    log(`  движок: ${transcript.engine}, язык: ${transcript.language}, фраз: ${transcript.segments.length}`);
    for (const n of transcript.notes || []) log(`  ⚠ ${n}`);

    say('Строю JSON-план сцен');
    const theme = loadTheme(cfg.theme);
    const { hints } = loadHints(name);
    let face = null;
    if (cfg.face && info.video) {
      face = await faceFocus(input);
      log(face.ok ? `  лицо: ${face.found ? `найдено (x=${face.focusX}, y=${face.focusY})` : 'не найдено, центр кадра'}` : `  ⚠ OpenCV недоступен (${face.message}) — центр кадра. ${face.hint || ''}`);
    }
    const built = buildPlan(info, transcript, { name, format: cfg.format, size, fps: cfg.fps ? Number(cfg.fps) : 30, hints, theme, music: cfg.music === 'none' ? 'none' : cfg.music, videoRel: rel(input), allowTest });
    plan = built.plan;
    if (face?.ok && face.found) for (const s of plan.scenes) if (s.type === 'speaker' || s.type === 'title') { s.focusX = face.focusX; if ('focusY' in s) s.focusY = face.focusY; }
    for (const w of built.warnings) log(`  ⚠ ${w}`);
    validatePlan(plan);
    fs.writeFileSync(planFile, JSON.stringify(plan, null, 2));
    log(`  ${rel(planFile)} — ${plan.scenes.length} сцен: ${plan.scenes.map((s) => s.type).join(' → ')}; тема «${theme.name}», ${plan.output.width}×${plan.output.height}`);
    log('  план прошёл проверку (AJV + правила таймингов)');
  }
  if (cfg['plan-only']) { log('\nОстановился после плана (--plan-only). Правьте файл и запускайте с --plan.'); return { plan, planFile }; }

  const ctx = await prepareRender(plan);
  try {
    say(cfg['no-preview'] || cfg['finish-only'] ? 'Превью пропущено' : 'Remotion: превью и кадры сцен');
    if (!cfg['no-preview'] && !cfg['finish-only']) {
      const preview = await renderPreview(ctx, plan, { log });
      log(`  ${rel(preview.video)} и ${preview.stills.length} стоп-кадра(ов) в previews/`);
    }
    say('Remotion: чистовая картинка');
    let visual;
    if (cfg['finish-only']) {
      const existing = path.join(DIRS.renders, `${plan.name}.visual.mp4`);
      if (!fs.existsSync(existing)) throw new EngineError('NO_VISUAL', 'Нет готовой картинки для финиша', { why: `Файла ${rel(existing)} нет: рендер ещё не делался.`, fix: 'Запустите без --finish-only.' });
      visual = { video: existing, rel: rel(existing), frames: ctx.composition.durationInFrames };
      log(`  беру готовую картинку ${visual.rel} (--finish-only)`);
    } else {
      visual = await renderVisual(ctx, plan, { log });
    }
    log(`  ${visual.rel}: ${visual.frames} кадров`);
    say('FFmpeg: звук, музыка, громкость, итоговый MP4');
    const final = await finish(plan, visual.video, { log });

    log('\nПроверяю результат (ffprobe + полное декодирование)…');
    const rep = await verifyVideo(final, { width: plan.output.width, height: plan.output.height, fps: plan.output.fps, duration: plan.source.duration, sceneMids: plan.scenes.map((s) => (s.start + s.end) / 2) });
    printReport(rep, log);
    const wav = path.join(DIRS.transcript, `${plan.name}.wav`);
    const duck = plan.audio?.music && transcript && fs.existsSync(wav) ? await measureDuck(plan, wav, transcript.segments.map((s) => [s.start, s.end])) : null;
    const acc = accept({ plan, transcript, verifyRep: rep, duck });
    const reportFile = writeReport(plan, acc, { engine: transcript?.engine });
    log(`\nПриёмка (смысл / картинка / техника): ${acc.ok ? 'автопроверки пройдены' : 'ЕСТЬ ПРОВАЛЫ'}${acc.manual.length ? `, посмотреть глазами: ${acc.manual.length}` : ''} → ${reportFile}`);
    for (const f of acc.failed) log(`  ✖ ${f.name}${f.detail ? ` — ${f.detail}` : ''}`);
    if (!rep.ok || !acc.ok) throw new EngineError('VERIFY_FAILED', 'Итоговый файл не прошёл приёмку', { why: 'Одна из проверок выше провалена.', fix: `Не публикуйте этот файл. Подробности: ${reportFile}. Затем npm run doctor.` });
    log(`\n✔ Готово за ${((Date.now() - t0) / 1000).toFixed(0)} с: ${rel(final)}`);
    return { final, plan, planFile, report: rep, acceptance: acc, reportFile };
  } finally {
    ctx.cleanup();
  }
}
