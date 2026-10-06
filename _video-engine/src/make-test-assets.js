// Создаёт нейтральные тестовые файлы: input/test-speaker.mp4 и assets/test-broll.png.
// Существующие файлы НЕ перезаписывает.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { run } from './exec.js';
import { EngineError, explain } from './errors.js';
import { DIRS, PY, PY_DIR, ROOT, ensureDirs, rel } from './paths.js';

export const TEST_VIDEO = path.join(DIRS.input, 'test-speaker.mp4');
export const TEST_AUDIO = path.join(DIRS.input, 'test-voiceover.m4a'); // только голос: для режима «голос + фото»
export const TEST_IMAGE = path.join(DIRS.assets, 'test-broll.png');
export const TEST_IMAGE2 = path.join(DIRS.assets, 'test-broll-2.png');
export const TEST_IMAGE3 = path.join(DIRS.assets, 'test-broll-3.png');
export const TEST_MUSIC = path.join(DIRS.assets, 'test-music.wav');
export const TEST_SCRIPT = path.join(DIRS.assets, 'test-speaker.script.txt');

/** Создаёт недостающие тестовые файлы. Существующие НЕ трогает. */
export async function makeTestAssets({ log = console.log } = {}) {
  ensureDirs();
  fs.mkdirSync(path.join(DIRS.assets, 'broll'), { recursive: true });
  fs.mkdirSync(path.join(DIRS.assets, 'music'), { recursive: true });
  const need = [TEST_VIDEO, TEST_IMAGE, TEST_IMAGE2, TEST_IMAGE3, TEST_MUSIC].filter((f) => !fs.existsSync(f));
  let tts = null;
  if (need.length) {
    if (!fs.existsSync(PY)) {
      throw new EngineError('PY_MISSING', 'Не найдено Python-окружение (.venv)', {
        why: 'Тестовые файлы создаёт небольшой Python-скрипт.',
        fix: 'Выполните: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt',
      });
    }
    const work = fs.mkdtempSync(path.join(DIRS.previews, '.tmp-assets-'));
    try {
      log(`Создаю недостающие тестовые файлы: ${need.map(rel).join(', ')}`);
      const res = await run(PY, [
        path.join(PY_DIR, 'make_test_assets.py'),
        '--video', TEST_VIDEO, '--image', TEST_IMAGE, '--image2', TEST_IMAGE2, '--image3', TEST_IMAGE3,
        '--music', TEST_MUSIC, '--script-out', TEST_SCRIPT, '--work-dir', work,
      ], { env: { PYTHONIOENCODING: 'utf-8' } });
      const last = res.stdout.trim().split('\n').filter(Boolean).pop() || '';
      let payload = null;
      try { payload = JSON.parse(last); } catch { /* не JSON */ }
      if (!payload || !payload.ok) {
        const e = payload?.error;
        throw new EngineError(e?.code || 'TEST_ASSETS_FAILED', e?.message || 'Не удалось создать тестовые файлы', {
          why: 'Скрипт генерации остановился.',
          fix: e?.hint || 'Запустите npm run doctor.',
          details: (res.stderr || '').trim().split('\n').slice(-1)[0],
        });
      }
      tts = payload.tts || null;
    } finally {
      fs.rmSync(work, { recursive: true, force: true });
    }
  }
  if (!fs.existsSync(TEST_AUDIO)) {
    // «Запись голоса»: звук из тестового видео в M4A (имитация голосового из Telegram)
    const r = await run('ffmpeg', ['-n', '-v', 'error', '-i', TEST_VIDEO, '-vn', '-c:a', 'aac', '-b:a', '96k', '-ac', '1', TEST_AUDIO]);
    if (r.code !== 0) throw new EngineError('TEST_AUDIO_FAILED', 'Не удалось создать тестовую запись голоса', { why: 'FFmpeg остановился.', fix: 'Запустите npm run doctor.', details: r.stderr.trim().split('\n')[0] });
    log(`Создан ${rel(TEST_AUDIO)}`);
  }
  if (!need.length) log('Тестовые файлы уже на месте, оставляю как есть.');
  return { video: TEST_VIDEO, audio: TEST_AUDIO, image: TEST_IMAGE, music: TEST_MUSIC, created: need.length > 0, tts };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  makeTestAssets().catch((e) => {
    console.error(explain(e));
    process.exit(1);
  });
}
