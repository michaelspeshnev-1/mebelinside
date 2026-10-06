// Шаг 3: локальная транскрипция с таймкодами (Python: faster-whisper / pocketsphinx).
import fs from 'node:fs';
import path from 'node:path';
import { run } from './exec.js';
import { EngineError } from './errors.js';
import { DIRS, PY, PY_DIR, assertNotSource } from './paths.js';

export async function transcribe(wavPath, outJson, { language = 'auto', engine = 'auto', model = 'small', allowDownload = true } = {}) {
  assertNotSource(outJson);
  if (!fs.existsSync(PY)) {
    throw new EngineError('PY_MISSING', 'Не найдено Python-окружение (.venv)', {
      why: 'Распознавание речи работает в отдельном Python-окружении, а его нет.',
      fix: 'Выполните: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt',
    });
  }
  const args = [
    path.join(PY_DIR, 'transcribe.py'),
    '--wav', wavPath,
    '--out', outJson,
    '--language', language,
    '--engine', engine,
    '--model', model,
    '--models-dir', DIRS.models,
  ];
  if (allowDownload) args.push('--allow-download');

  const res = await run(PY, args, { env: { PYTHONIOENCODING: 'utf-8' } });
  const lastLine = res.stdout.trim().split('\n').filter(Boolean).pop() || '';
  let payload = null;
  try {
    payload = JSON.parse(lastLine);
  } catch {
    /* не JSON */
  }
  if (!payload || !payload.ok) {
    const e = payload?.error;
    if (e) {
      throw new EngineError(e.code, e.message, { why: 'Распознавание речи остановилось.', fix: e.hint || '' });
    }
    throw new EngineError('TRANSCRIBE_CRASH', 'Распознавание речи неожиданно завершилось', {
      why: 'Python-скрипт упал, не объяснив причину.',
      fix: 'Запустите npm run doctor, затем повторите. Если не помогло, покажите подробности ниже.',
      details: (res.stderr || res.stdout).trim().split('\n').slice(-1)[0],
    });
  }
  const data = JSON.parse(fs.readFileSync(outJson, 'utf8'));
  if (!data.segments.length) {
    throw new EngineError('NO_SPEECH', 'Речь в видео не обнаружена', {
      why: `Движок «${data.engine}» не нашёл слов. Возможно, голос слишком тихий, есть сильный шум или язык выбран неверно.`,
      fix: 'Проверьте громкость и язык (--language ru или --language en). Для русского нужна модель Whisper.',
    });
  }
  return data;
}
