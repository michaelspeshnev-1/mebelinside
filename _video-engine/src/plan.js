// Шаг 4: транскрипт + параметры видео -> JSON-план сцен (без нейросетей и платных API).
//
// Раскладка по умолчанию (доли длины ролика, границы подтягиваются к паузам в речи):
//   спикер + субтитры  ->  крупный заголовок  ->  B-roll (картинка)  ->  спикер + субтитры
import fs from 'node:fs';
import path from 'node:path';
import { EngineError } from './errors.js';
import { DIRS, IMAGE_EXT, ROOT, rel } from './paths.js';

export const AUDIO_EXT = ['.mp3', '.m4a', '.wav', '.ogg', '.opus', '.aac', '.flac'];
export const MUSIC_EXT = AUDIO_EXT;
import { PLAN_VERSION, validateHints, validateTheme } from './schema.js';

export const FORMATS = {
  landscape: { width: 1280, height: 720 },
  vertical: { width: 1080, height: 1920 },
  square: { width: 1080, height: 1080 },
};

const STOP = {
  en: new Set('a an the and or but so then this that these those is are was were be been to of in on at for with from by it its as we you i he she they our your their my me us do does did can will just very now first after today'.split(' ')),
  ru: new Set('и в во не что он на я с со как а то все она так его но да ты к у же вы за бы по только ее мне было вот от меня еще нет о из ему теперь когда даже ну вдруг ли если уже или ни быть был него до вас нибудь опять уж вам ведь там потом себя ничего ей может они тут где есть надо ней для мы тебя их чем была сам чтоб без будто чего раз тоже себе под будет ж тогда кто этот того потому этого какой совсем ним здесь этом один почти мой тем чтобы нее сейчас были куда зачем всех никогда можно при наконец два об другой хоть после над больше тот через эти нас про всего них какая много разве три эту моя впрочем хорошо свою этой перед иногда лучше чуть том нельзя такой им более всегда конечно всю между'.split(' ')),
};

const round3 = (x) => Math.round(x * 1000) / 1000;

/** Границы сцен: подтягиваем к паузам между фразами, чтобы не резать слово. */
function snapBoundaries(duration, segments, fractions, minScene) {
  const gaps = [];
  for (let i = 0; i < segments.length - 1; i++) {
    const a = segments[i].end;
    const b = segments[i + 1].start;
    gaps.push({ at: (a + b) / 2, size: b - a });
  }
  const bounds = [0];
  for (const f of fractions) {
    const target = duration * f;
    const prev = bounds[bounds.length - 1];
    const lo = prev + minScene;
    const hi = duration - minScene * (fractions.length - bounds.length + 1);
    let best = null;
    for (const g of gaps) {
      if (g.at < lo || g.at > hi || g.size < 0.12) continue;
      const score = Math.abs(g.at - target) - Math.min(g.size, 1) * 0.5; // чуть любим длинные паузы
      if (!best || score < best.score) best = { at: g.at, score };
    }
    let t = best && Math.abs(best.at - target) < duration * 0.18 ? best.at : target;
    t = Math.min(Math.max(t, lo), Math.max(lo, hi));
    bounds.push(round3(t));
  }
  bounds.push(round3(duration));
  return bounds;
}

function words(text, lang) {
  return text.split(/\s+/).map((w) => w.replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, '')).filter(Boolean);
}

/** Заголовок из речи: самая «содержательная» фраза в окне сцены, без служебных слов по краям. */
function makeHeadline(segments, from, to, lang) {
  const stop = STOP[lang] || STOP.en;
  const inWin = segments.filter((s) => s.end > from && s.start < to);
  const pool = inWin.length ? inWin : segments;
  let best = null;
  for (const s of pool) {
    const w = words(s.text, lang);
    const content = w.filter((x) => !stop.has(x.toLowerCase())).length;
    const score = content - Math.abs(w.length - 6) * 0.15;
    if (w.length >= 2 && (!best || score > best.score)) best = { w, score };
  }
  if (!best) return 'Главная мысль';
  let w = best.w;
  while (w.length > 2 && stop.has(w[0].toLowerCase())) w = w.slice(1);
  w = w.slice(0, 6);
  while (w.length > 2 && stop.has(w[w.length - 1].toLowerCase())) w = w.slice(0, -1);
  const s = w.join(' ');
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/** Группы слов для субтитров: короткие строки, читаемые за раз. */
export function makeCaptions(segments, maxWords = 5, maxSec = 2.8) {
  const flat = [];
  for (const s of segments) {
    let ws = s.words && s.words.length ? s.words : null;
    if (!ws) {
      const parts = words(s.text);
      const step = (s.end - s.start) / Math.max(parts.length, 1);
      ws = parts.map((p, i) => ({ word: p, start: s.start + i * step, end: s.start + (i + 1) * step }));
    }
    for (const w of ws) flat.push({ text: String(w.word).trim(), start: w.start, end: w.end, segEnd: s.end });
  }
  const groups = [];
  let cur = [];
  const flush = () => {
    if (!cur.length) return;
    groups.push({
      start: round3(cur[0].start),
      end: round3(cur[cur.length - 1].end),
      text: cur.map((x) => x.text).join(' '),
      words: cur.map((x) => ({ start: round3(x.start), end: round3(x.end), text: x.text })),
    });
    cur = [];
  };
  for (const w of flat) {
    if (!w.text) continue;
    if (cur.length) {
      const gap = w.start - cur[cur.length - 1].end;
      if (gap > 0.5 || cur.length >= maxWords || w.end - cur[0].start > maxSec) flush();
    }
    cur.push(w);
  }
  flush();
  // чтобы субтитры не налезали друг на друга и не мигали
  for (let i = 0; i < groups.length; i++) {
    const g = groups[i];
    if (g.end - g.start < 0.4) g.end = round3(g.start + 0.4);
    const next = groups[i + 1];
    if (next && g.end > next.start) g.end = round3(Math.max(g.start + 0.05, next.start));
    for (const w of g.words) {
      w.end = Math.min(w.end, g.end);
      w.start = Math.min(w.start, w.end);
    }
  }
  return groups;
}


const isImg = (f) => !f.startsWith('.') && IMAGE_EXT.includes(path.extname(f).toLowerCase());

/** Фото для B-roll: подсказка > assets/broll/ > картинки прямо в assets/ (test-* берём только для демо). */
export function findBrollImages(hint, { allowTest = false } = {}) {
  if (hint) {
    const list = (Array.isArray(hint) ? hint : [hint]).map((h) => path.resolve(ROOT, h)).filter((a) => fs.existsSync(a));
    return list.map(rel);
  }
  const fromDir = (dir, filterTest) =>
    fs.existsSync(dir)
      ? fs.readdirSync(dir).filter((f) => isImg(f) && !(filterTest && !allowTest && f.startsWith('test-'))).sort().map((f) => rel(path.join(dir, f)))
      : [];
  const own = fromDir(path.join(DIRS.assets, 'broll'), false);
  return own.length ? own : fromDir(DIRS.assets, true);
}

/** Музыка: --music <файл> | auto (первый трек из assets/music/) | none. */
export function findMusic(spec) {
  if (!spec || spec === 'none' || spec === false) return null;
  if (spec !== 'auto') {
    const abs = path.resolve(ROOT, spec);
    if (!fs.existsSync(abs)) {
      throw new EngineError('MUSIC_NOT_FOUND', `Музыка не найдена: ${spec}`, { why: 'Файл не существует.', fix: 'Положите трек (mp3, m4a, wav) в assets/music/ и укажите путь, либо уберите --music.' });
    }
    return rel(abs);
  }
  const dir = path.join(DIRS.assets, 'music');
  if (!fs.existsSync(dir)) return null;
  const f = fs.readdirSync(dir).filter((x) => !x.startsWith('.') && MUSIC_EXT.includes(path.extname(x).toLowerCase())).sort()[0];
  return f ? rel(path.join(dir, f)) : null;
}

export function findLogo() {
  const f = ['logo.png', 'logo.svg', 'logo.webp', 'logo.jpg'].find((n) => fs.existsSync(path.join(DIRS.assets, n)));
  return f ? rel(path.join(DIRS.assets, f)) : null;
}

export function loadTheme(name = 'mebel-inside') {
  const file = path.join(ROOT, 'theme', `${name}.json`);
  if (!fs.existsSync(file)) {
    const have = fs.existsSync(path.join(ROOT, 'theme')) ? fs.readdirSync(path.join(ROOT, 'theme')).filter((f) => f.endsWith('.json')).map((f) => f.replace(/\.json$/, '')) : [];
    throw new EngineError('THEME_NOT_FOUND', `Тема «${name}» не найдена`, { why: 'Файла темы нет в папке theme/.', fix: `Доступные темы: ${have.join(', ') || 'нет'}. Укажите --theme <имя> или поправьте engine.config.json.` });
  }
  let parsed;
  try { parsed = JSON.parse(fs.readFileSync(file, 'utf8')); } catch (e) {
    throw new EngineError('THEME_BAD_JSON', `Файл темы ${rel(file)} — не корректный JSON`, { why: String(e.message).replace(/\s+/g, ' '), fix: 'Исправьте запятые и кавычки.' });
  }
  return validateTheme(parsed, rel(file));
}

export function loadHints(name) {
  const file = path.join(DIRS.brief, `${name}.hints.json`);
  if (!fs.existsSync(file)) return { hints: {}, file: null };
  let parsed;
  try {
    parsed = JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    throw new EngineError('HINTS_BAD_JSON', `Файл подсказок ${rel(file)} — не корректный JSON`, {
      why: String(e.message).replace(/\s+/g, ' '),
      fix: 'Исправьте синтаксис (запятые, кавычки) или удалите файл: он необязателен.',
    });
  }
  return { hints: validateHints(parsed, rel(file)), file };
}

/** Раскладка сцен. Видео: спикер -> заголовок -> B-roll -> спикер [-> CTA]. Только звук: фото -> заголовок -> фото... [-> CTA]. */
function layoutFor(duration, hasVideo) {
  const cta = duration >= 15;
  if (hasVideo) {
    if (duration >= 12) return { types: cta ? ['speaker', 'title', 'broll', 'speaker', 'cta'] : ['speaker', 'title', 'broll', 'speaker'], fractions: cta ? [0.28, 0.46, 0.68] : [0.3, 0.5, 0.72], ctaSec: 3.5 };
    return { types: ['speaker', 'title', 'broll'], fractions: [0.4, 0.7], ctaSec: 0 };
  }
  if (duration >= 12) return { types: cta ? ['broll', 'title', 'broll', 'broll', 'cta'] : ['broll', 'title', 'broll', 'broll'], fractions: cta ? [0.25, 0.42, 0.62] : [0.25, 0.45, 0.7], ctaSec: 3.5 };
  return { types: ['broll', 'title', 'broll'], fractions: [0.4, 0.7], ctaSec: 0 };
}

/**
 * @param info    результат probe()
 * @param transcript  результат транскрипции
 * @param opts    { name, format, size, fps, hints, theme, music, videoRel, allowTest }
 */
export function buildPlan(info, transcript, opts) {
  const duration = round3(info.duration);
  if (duration < 4) {
    throw new EngineError('TOO_SHORT_FOR_PLAN', 'Ролик слишком короткий для трёх сцен', {
      why: `Длина ${duration} с, а на три сцены нужно хотя бы 4 с.`,
      fix: 'Возьмите запись от 6 секунд.',
    });
  }
  const hasVideo = Boolean(info.video);
  const lang = transcript.language || 'en';
  const segments = transcript.segments;
  const hints = opts.hints || {};
  const theme = opts.theme || loadTheme('default');

  const fmt = opts.format || 'landscape';
  const size = opts.size || FORMATS[fmt];
  if (!size) {
    throw new EngineError('BAD_FORMAT', `Неизвестный формат «${opts.format}»`, {
      why: 'Поддерживаются только готовые форматы.',
      fix: `Выберите один из: ${Object.keys(FORMATS).join(', ')} — или задайте размер: --size 1280x720.`,
    });
  }
  const orient = size.height > size.width ? 'vertical' : 'landscape';

  const { types, fractions, ctaSec } = layoutFor(duration, hasVideo);
  // CTA занимает последние секунды, остальные границы считаем по речи до неё
  const body = types.filter((t) => t !== 'cta');
  const bodyEnd = ctaSec ? round3(duration - ctaSec) : duration;
  const minScene = duration >= 12 ? 2.5 : 1;
  const b = snapBoundaries(bodyEnd, segments, fractions.slice(0, body.length - 1), minScene);
  if (ctaSec) b.push(duration);

  const images = findBrollImages(hints.broll, { allowTest: opts.allowTest });
  const brollCount = types.filter((t) => t === 'broll').length;
  // Фото делим между B-roll-сценами поровну; фото меньше сцен - картинки повторяются по кругу
  const share = (k) => {
    if (!images.length) return [];
    const per = Math.max(1, Math.floor(images.length / brollCount));
    const slice = images.slice(k * per, k === brollCount - 1 ? undefined : (k + 1) * per);
    return (slice.length ? slice : [images[k % images.length]]).slice(0, 12);
  };

  const headline = hints.title || makeHeadline(segments, b[types.indexOf('title')], b[types.indexOf('title') + 1], lang);
  const scenes = [];
  let brollK = 0;
  types.forEach((type, i) => {
    const base = { id: `scene-${i + 1}`, type, start: b[i], end: b[i + 1] };
    if (type === 'speaker') scenes.push({ ...base, focusX: 0.5, focusY: 0.5, subtitles: true });
    else if (type === 'title') scenes.push({ ...base, title: headline, ...(hints.subtitle ? { subtitle: hints.subtitle } : {}), backdrop: hasVideo ? 'video' : 'gradient', ...(hasVideo ? { focusX: 0.5 } : {}) });
    else if (type === 'broll') {
      const imgs = share(brollK++);
      scenes.push({ ...base, ...(imgs.length ? { images: imgs } : {}), ...(hints.brollLabel && brollK === 1 ? { label: hints.brollLabel } : {}), subtitles: true });
    } else {
      scenes.push({ ...base, title: hints.cta || theme.cta.title || theme.brand.name || 'Свяжитесь с нами', ...(hints.ctaText || theme.cta.text ? { text: hints.ctaText || theme.cta.text } : {}), ...(theme.brand.site ? { site: theme.brand.site } : {}), ...(theme.brand.phone ? { phone: theme.brand.phone } : {}) });
    }
  });

  const warnings = [];
  if (!images.length) warnings.push('Фото для B-roll не найдены — вместо них градиент. Положите снимки работ в assets/broll/ и пересоберите план.');
  if (transcript.engine === 'pocketsphinx') {
    warnings.push('Речь распознана запасным движком pocketsphinx (только английский, возможны ошибки в словах). Для точных субтитров положите модель Whisper в models/ (см. README).');
  }
  if (!hasVideo) warnings.push('Исходник — только звук: ролик собран из ваших фото, спикера в кадре нет.');

  const music = findMusic(opts.music);
  const logo = findLogo();
  const plan = {
    version: PLAN_VERSION,
    name: opts.name,
    language: lang,
    source: hasVideo
      ? { video: opts.videoRel, hasVideo: true, duration, width: info.video.width, height: info.video.height, fps: info.video.fps || 30 }
      : { video: opts.videoRel, hasVideo: false, duration },
    output: { width: size.width, height: size.height, fps: opts.fps || 30 },
    style: {
      accent: hints.accent || theme.colors.accent,
      background: hints.background || theme.colors.background,
      text: theme.colors.text,
      safeZone: theme.safeZone[orient],
    },
    brand: { ...theme.brand, ...(logo ? { logo } : {}) },
    audio: { ...(music ? { music } : {}), ...theme.audio },
    scenes,
    captions: makeCaptions(segments),
  };
  return { plan, warnings };
}
