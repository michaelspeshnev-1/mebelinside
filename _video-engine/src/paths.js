// Все пути проекта в одном месте + защита исходников от перезаписи.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { EngineError } from './errors.js';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

export const DIRS = {
  input: path.join(ROOT, 'input'),
  transcript: path.join(ROOT, 'transcript'),
  brief: path.join(ROOT, 'brief'),
  assets: path.join(ROOT, 'assets'),
  previews: path.join(ROOT, 'previews'),
  renders: path.join(ROOT, 'renders'),
  final: path.join(ROOT, 'final'),
  models: path.join(ROOT, 'models'),
};

export const PY = process.platform === 'win32'
  ? path.join(ROOT, '.venv', 'Scripts', 'python.exe')
  : path.join(ROOT, '.venv', 'bin', 'python');
export const PY_DIR = path.join(ROOT, 'python');

export const VIDEO_EXT = ['.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'];
export const AUDIO_INPUT_EXT = ['.m4a', '.mp3', '.wav', '.ogg', '.opus', '.aac', '.flac'];
export const IMAGE_EXT = ['.png', '.jpg', '.jpeg', '.webp'];

export function ensureDirs() {
  for (const d of Object.values(DIRS)) fs.mkdirSync(d, { recursive: true });
}

export function rel(p) {
  return path.relative(ROOT, p) || '.';
}

/** Имя для файлов результата: только буквы/цифры/дефис. */
export function slugify(name) {
  const base = name
    .replace(/\.[^.]+$/, '')
    .normalize('NFKD')
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '')
    .toLowerCase();
  return base || 'video';
}

export function isInside(child, parent) {
  const r = path.relative(parent, child);
  return r === '' || (!r.startsWith('..') && !path.isAbsolute(r));
}

/** Запрещает записывать результат внутрь input/ (исходники неприкосновенны). */
export function assertNotSource(outPath) {
  const abs = path.resolve(outPath);
  if (isInside(abs, DIRS.input)) {
    throw new EngineError('WRITE_TO_INPUT', 'Попытка записать результат в папку input/', {
      why: 'Папка input/ хранит ваши исходники, движок никогда в неё не пишет.',
      fix: 'Результаты создаются в transcript/, brief/, previews/, renders/ и final/ автоматически.',
      details: abs,
    });
  }
  return abs;
}

/**
 * Находит входной файл: путь как есть либо имя внутри input/.
 * Если файл лежит вне input/, КОПИРУЕТ его в input/ (оригинал не трогаем,
 * существующие файлы не перезаписываем).
 */
export function adoptInput(arg) {
  const candidates = [path.resolve(arg), path.join(DIRS.input, arg)];
  const found = candidates.find((c) => fs.existsSync(c) && fs.statSync(c).isFile());
  if (!found) {
    const have = fs.existsSync(DIRS.input)
      ? fs.readdirSync(DIRS.input).filter((f) => [...VIDEO_EXT, ...AUDIO_INPUT_EXT].includes(path.extname(f).toLowerCase()))
      : [];
    throw new EngineError('INPUT_NOT_FOUND', `Файл не найден: ${arg}`, {
      why: 'Нет файла с таким именем ни по указанному пути, ни в папке input/.',
      fix: have.length
        ? `Сейчас в input/ лежат: ${have.join(', ')}. Укажите одно из них.`
        : 'Положите видео в папку input/ и запустите команду снова. Для проверки можно создать тестовое: npm run make-test-assets',
    });
  }
  if (isInside(found, DIRS.input)) return found;

  const ext = path.extname(found);
  const stem = path.basename(found, ext);
  let target = path.join(DIRS.input, `${stem}${ext}`);
  let n = 2;
  while (fs.existsSync(target)) {
    const same = fs.statSync(target).size === fs.statSync(found).size;
    if (same) return target; // уже копировали раньше
    target = path.join(DIRS.input, `${stem}-${n++}${ext}`);
  }
  fs.copyFileSync(found, target, fs.constants.COPYFILE_EXCL);
  return target;
}
