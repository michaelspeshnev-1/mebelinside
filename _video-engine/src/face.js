// Опциональный модуль OpenCV: центр лица для вертикального кадрирования. Не нашли - берём центр кадра.
import fs from 'node:fs';
import { run } from './exec.js';
import { PY, PY_DIR } from './paths.js';
import path from 'node:path';

export async function faceFocus(video) {
  if (!fs.existsSync(PY)) return { ok: false, message: 'нет Python-окружения .venv' };
  const res = await run(PY, [path.join(PY_DIR, 'face_focus.py'), '--video', video]);
  try {
    const p = JSON.parse(res.stdout.trim().split('\n').pop());
    return p.ok ? p : { ok: false, message: p.error?.message, hint: p.error?.hint };
  } catch {
    return { ok: false, message: 'модуль лица завершился с ошибкой' };
  }
}
