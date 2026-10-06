// Ошибки, которые объясняются человеческим языком: что случилось, почему, что делать.

export class EngineError extends Error {
  constructor(code, title, { why = '', fix = '', details = '' } = {}) {
    super(title);
    this.name = 'EngineError';
    this.code = code;
    this.title = title;
    this.why = why;
    this.fix = fix;
    this.details = details;
  }
}

function block(title, why, fix, tail, list) {
  const lines = [`✖ ${title}`];
  if (why) lines.push(`  Почему: ${why}`);
  if (list) lines.push(`  Что именно не так:${list}`);
  if (fix) lines.push(`  Что сделать: ${fix}`);
  if (tail) lines.push(`  (${tail})`);
  return lines.join('\n');
}

const INSTALL_HINT = {
  ffmpeg:
    'Ubuntu/Debian: sudo apt-get install ffmpeg · macOS: brew install ffmpeg · Windows: winget install Gyan.FFmpeg',
  ffprobe:
    'ffprobe ставится вместе с FFmpeg. Ubuntu/Debian: sudo apt-get install ffmpeg · macOS: brew install ffmpeg',
};

export function toolMissing(tool) {
  return new EngineError('TOOL_MISSING', `Программа «${tool}» не найдена`, {
    why: 'Она нужна движку, но её нет в системе или она не прописана в PATH.',
    fix: INSTALL_HINT[tool] || `Установите «${tool}» и повторите.`,
    details: `tool=${tool}`,
  });
}

/** Превращает любую ошибку в понятный текст. */
export function explain(err) {
  if (err instanceof EngineError) {
    // Многострочные подробности (список проблем плана) выводим отдельным блоком, однострочные - в скобках.
    const multi = err.details.includes('\n');
    return block(err.title, err.why, err.fix, `код: ${err.code}${err.details && !multi ? `; ${err.details}` : ''}`, multi ? err.details : '');
  }
  if (err && err.code === 'ENOENT') {
    return block('Не найден файл или программа', 'Система не нашла то, что движок пытался открыть.', 'Проверьте путь и запустите npm run doctor.', String(err.message));
  }
  if (err && err.code === 'EACCES') {
    return block('Нет прав доступа', 'Система не разрешила читать или писать этот файл.', 'Проверьте права на папку проекта.', String(err.message));
  }
  if (err && err.code === 'ENOSPC') {
    return block('Закончилось место на диске', 'Видео занимает много места, а свободного не осталось.', 'Освободите место (папки renders/ и previews/ можно очистить) и повторите.', String(err.message));
  }
  const msg = err && err.message ? err.message : String(err);
  return block('Непредвиденная ошибка', 'Это не похоже ни на одну из известных проблем.', 'Запустите npm run doctor — он проверит окружение. Если не поможет, покажите этот текст целиком.', msg.split('\n')[0]);
}
