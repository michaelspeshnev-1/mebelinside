// Шаги 6-7 (картинка): Remotion рисует превью и «чистовую» картинку без звука.
import fs from 'node:fs';
import path from 'node:path';
import { EngineError } from './errors.js';
import { DIRS, ROOT, assertNotSource, rel } from './paths.js';
import { findBrowser } from './browser.js';

const ENTRY = path.join(ROOT, 'remotion', 'index.jsx');
const COMPOSITION_ID = 'Main';

async function loadRemotion() {
  try {
    const [bundler, renderer] = await Promise.all([import('@remotion/bundler'), import('@remotion/renderer')]);
    return { bundle: bundler.bundle, ...renderer };
  } catch (e) {
    throw new EngineError('REMOTION_MISSING', 'Не загружается Remotion', {
      why: 'Пакеты Remotion не установлены или повреждены.',
      fix: 'Выполните в папке проекта: npm ci',
      details: String(e.message).split('\n')[0],
    });
  }
}

/** Готовит всё общее: временную public-папку (ссылки на видео и картинки), сборку, браузер. */
export async function prepareRender(plan) {
  const R = await loadRemotion();
  const stage = path.join(DIRS.renders, `.stage-${plan.name}`);
  fs.rmSync(stage, { recursive: true, force: true });
  const pub = path.join(stage, 'public');
  fs.mkdirSync(pub, { recursive: true });

  const link = (srcAbs, name) => {
    const dst = path.join(pub, name);
    // Сервер Remotion не отдаёт символические ссылки, поэтому: жёсткая ссылка (мгновенно, без копии,
    // оригинал не меняется), а если диски разные - обычная копия.
    try {
      fs.linkSync(srcAbs, dst);
    } catch {
      fs.copyFileSync(srcAbs, dst);
    }
    return name;
  };
  const videoAbs = path.resolve(ROOT, plan.source.video);
  // Если исходник - только звук, картинки со спикером нет: в Remotion видео не передаём
  const videoFile = plan.source.hasVideo === false ? null : link(videoAbs, `source${path.extname(videoAbs)}`);
  const images = {};
  for (const s of plan.scenes) {
    if (s.type === 'broll' && s.images) images[s.id] = s.images.map((img, k) => link(path.resolve(ROOT, img), `broll-${s.id}-${k}${path.extname(img)}`));
  }
  const logoFile = plan.brand?.logo ? link(path.resolve(ROOT, plan.brand.logo), `logo${path.extname(plan.brand.logo)}`) : null;

  let found = findBrowser();
  if (!found && !process.env.REMOTION_BROWSER && !process.env.BROWSER_EXECUTABLE) {
    try {
      await R.ensureBrowser();
      found = findBrowser();
    } catch (e) {
      throw new EngineError('NO_BROWSER', 'Не найден браузер для рисования кадров', {
        why: 'Remotion рисует кадры в headless-Chrome. Ни установленного, ни скачанного не нашлось, а скачать автоматически не вышло.',
        fix: 'Установите Google Chrome или Chromium (или укажите путь: REMOTION_BROWSER=/путь/к/chrome). Затем npm run doctor.',
        details: String(e.message).split('\n')[0],
      });
    }
  }
  if (!found) {
    throw new EngineError('NO_BROWSER', 'Указанный браузер не найден', {
      why: 'Переменная REMOTION_BROWSER указывает на несуществующий файл.',
      fix: 'Проверьте путь или удалите переменную — тогда я поищу браузер сам.',
    });
  }

  let serveUrl;
  try {
    serveUrl = await R.bundle({ entryPoint: ENTRY, publicDir: pub, onProgress: () => {} });
  } catch (e) {
    throw new EngineError('BUNDLE_FAILED', 'Не удалось собрать сцены Remotion', {
      why: 'В файлах папки remotion/ есть ошибка, либо не хватает зависимостей.',
      fix: 'Если вы правили сцены — проверьте последние изменения. Иначе: npm ci и повторить.',
      details: String(e.message).split('\n').slice(0, 3).join(' | '),
    });
  }

  const browserOpts = { browserExecutable: found.path, chromiumOptions: { gl: 'swangle' } };
  const inputProps = { plan, videoFile, images, logoFile };
  const composition = await R.selectComposition({ serveUrl, id: COMPOSITION_ID, inputProps, ...browserOpts });

  return {
    R, stage, serveUrl, inputProps, composition, browserOpts, browser: found,
    cleanup: () => fs.rmSync(stage, { recursive: true, force: true }),
  };
}

function progressPrinter(label, log) {
  let last = -10;
  return ({ progress }) => {
    const pct = Math.floor(progress * 100);
    if (pct >= last + 10) {
      last = pct - (pct % 10);
      log(`  ${label}: ${pct}%`);
    }
  };
}

function wrapRenderError(e, what) {
  if (e instanceof EngineError) return e;
  const msg = String(e?.message || e);
  if (/ENOSPC/.test(msg)) return e;
  return new EngineError('RENDER_FAILED', `Не удалось отрисовать ${what}`, {
    why: 'Remotion остановился с ошибкой во время рендера.',
    fix: 'Запустите npm run doctor (проверит браузер и память). Если на компьютере мало памяти — закройте другие программы или уменьшите размер: --size 960x540.',
    details: msg.split('\n').slice(0, 2).join(' | '),
  });
}

/** Быстрый черновик (половинный размер, каждый 2-й кадр) + стоп-кадр середины каждой сцены. */
export async function renderPreview(ctx, plan, { log = console.log } = {}) {
  const { R, serveUrl, inputProps, composition, browserOpts } = ctx;
  const outVideo = assertNotSource(path.join(DIRS.previews, `${plan.name}-preview.mp4`));
  const tmp = outVideo.replace(/\.mp4$/, '.partial.mp4');
  try {
    await R.renderMedia({
      composition, serveUrl, inputProps, ...browserOpts,
      codec: 'h264', outputLocation: tmp, muted: true, scale: 0.5, everyNthFrame: 2, crf: 30, pixelFormat: 'yuv420p',
      concurrency: Math.max(1, Math.min(4, Math.floor((await import('node:os')).cpus().length))),
      onProgress: progressPrinter('превью', log),
    });
    fs.renameSync(tmp, outVideo);
  } catch (e) {
    fs.rmSync(tmp, { force: true });
    throw wrapRenderError(e, 'превью');
  }

  const stills = [];
  const fps = composition.fps;
  for (let i = 0; i < plan.scenes.length; i++) {
    const s = plan.scenes[i];
    const frame = Math.min(composition.durationInFrames - 1, Math.round(((s.start + s.end) / 2) * fps));
    const out = assertNotSource(path.join(DIRS.previews, `${plan.name}-scene-${i + 1}-${s.type}.png`));
    try {
      await R.renderStill({ composition, serveUrl, inputProps, ...browserOpts, frame, output: out, imageFormat: 'png' });
    } catch (e) {
      throw wrapRenderError(e, `кадр сцены №${i + 1}`);
    }
    stills.push(out);
  }
  return { video: outVideo, stills };
}

/** Чистовая картинка без звука (звук добавит FFmpeg из оригинала). */
export async function renderVisual(ctx, plan, { log = console.log } = {}) {
  const { R, serveUrl, inputProps, composition, browserOpts } = ctx;
  const out = assertNotSource(path.join(DIRS.renders, `${plan.name}.visual.mp4`));
  const tmp = out.replace(/\.mp4$/, '.partial.mp4');
  try {
    await R.renderMedia({
      composition, serveUrl, inputProps, ...browserOpts,
      codec: 'h264', outputLocation: tmp, muted: true, crf: 16, pixelFormat: 'yuv420p',
      concurrency: Math.max(1, (await import('node:os')).cpus().length),
      onProgress: progressPrinter('рендер', log),
    });
    fs.renameSync(tmp, out);
  } catch (e) {
    fs.rmSync(tmp, { force: true });
    throw wrapRenderError(e, 'видео');
  }
  return { video: out, frames: composition.durationInFrames, fps: composition.fps, rel: rel(out) };
}
