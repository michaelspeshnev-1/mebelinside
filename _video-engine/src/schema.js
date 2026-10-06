// Проверка JSON-плана ДО рендера: структура (AJV) + смысловые правила (тайминги, файлы).
// Все сообщения - человеческим языком: какое поле, что не так, как исправить.
import fs from 'node:fs';
import path from 'node:path';
import Ajv from 'ajv';
import { EngineError } from './errors.js';
import { ROOT } from './paths.js';

export const PLAN_VERSION = 1;
export const SCENE_TYPES = ['speaker', 'title', 'broll', 'cta'];

const num = { type: 'number' };
const time = { type: 'number', minimum: 0 };
const color = { type: 'string', pattern: '^#[0-9a-fA-F]{6}$' };

export const planSchema = {
  $id: 'mini-video-engine/plan-v1',
  type: 'object',
  additionalProperties: false,
  required: ['version', 'name', 'source', 'output', 'style', 'scenes', 'captions'],
  properties: {
    version: { const: PLAN_VERSION },
    name: { type: 'string', minLength: 1, maxLength: 80, pattern: '^[\\p{L}\\p{N}._-]+$' },
    language: { type: 'string' },
    source: {
      type: 'object',
      additionalProperties: false,
      required: ['video', 'duration'],
      properties: {
        video: { type: 'string', minLength: 1 },
        hasVideo: { type: 'boolean' }, // false: исходник - только звук (голос + фото)
        duration: { type: 'number', exclusiveMinimum: 0 },
        width: { type: 'integer', minimum: 16 },
        height: { type: 'integer', minimum: 16 },
        fps: { type: 'number', exclusiveMinimum: 0, maximum: 240 },
      },
    },
    output: {
      type: 'object',
      additionalProperties: false,
      required: ['width', 'height', 'fps'],
      properties: {
        width: { type: 'integer', minimum: 64, maximum: 4096 },
        height: { type: 'integer', minimum: 64, maximum: 4096 },
        fps: { type: 'integer', minimum: 12, maximum: 60 },
      },
    },
    style: {
      type: 'object',
      additionalProperties: false,
      required: ['accent', 'background'],
      properties: {
        accent: color,
        background: color,
        text: color,
        safeZone: {
          type: 'object',
          additionalProperties: false,
          required: ['top', 'bottom', 'side'],
          properties: { top: { type: 'number', minimum: 0, maximum: 40 }, bottom: { type: 'number', minimum: 0, maximum: 40 }, side: { type: 'number', minimum: 0, maximum: 30 } },
        },
      },
    },
    brand: {
      type: 'object',
      additionalProperties: false,
      properties: {
        name: { type: 'string', maxLength: 60 },
        site: { type: 'string', maxLength: 80 },
        phone: { type: 'string', maxLength: 40 },
        tagline: { type: 'string', maxLength: 120 },
        logo: { type: 'string' },
      },
    },
    audio: {
      type: 'object',
      additionalProperties: false,
      required: ['gainDb', 'thresholdDb', 'ratio', 'attackMs', 'releaseMs'],
      properties: {
        music: { type: 'string', minLength: 1 },
        gainDb: { type: 'number', minimum: -60, maximum: 0 },
        thresholdDb: { type: 'number', minimum: -60, maximum: 0 },
        ratio: { type: 'number', minimum: 1, maximum: 20 },
        attackMs: { type: 'number', minimum: 0.01, maximum: 2000 },
        releaseMs: { type: 'number', minimum: 0.01, maximum: 9000 },
      },
    },
    scenes: {
      type: 'array',
      minItems: 3,
      maxItems: 200,
      items: {
        type: 'object',
        oneOf: [
          {
            type: 'object',
            additionalProperties: false,
            required: ['id', 'type', 'start', 'end'],
            properties: {
              id: { type: 'string', minLength: 1 },
              type: { const: 'speaker' },
              start: time,
              end: time,
              focusX: { type: 'number', minimum: 0, maximum: 1 },
              focusY: { type: 'number', minimum: 0, maximum: 1 },
              subtitles: { type: 'boolean' },
            },
          },
          {
            type: 'object',
            additionalProperties: false,
            required: ['id', 'type', 'start', 'end', 'title'],
            properties: {
              id: { type: 'string', minLength: 1 },
              type: { const: 'title' },
              start: time,
              end: time,
              title: { type: 'string', minLength: 1, maxLength: 90 },
              subtitle: { type: 'string', maxLength: 140 },
              backdrop: { enum: ['video', 'gradient'] },
              focusX: { type: 'number', minimum: 0, maximum: 1 },
            },
          },
          {
            type: 'object',
            additionalProperties: false,
            required: ['id', 'type', 'start', 'end'],
            properties: {
              id: { type: 'string', minLength: 1 },
              type: { const: 'broll' },
              start: time,
              end: time,
              images: { type: 'array', minItems: 1, maxItems: 12, items: { type: 'string', minLength: 1 } },
              label: { type: 'string', maxLength: 90 },
              subtitles: { type: 'boolean' },
            },
          },
          {
            type: 'object',
            additionalProperties: false,
            required: ['id', 'type', 'start', 'end', 'title'],
            properties: {
              id: { type: 'string', minLength: 1 },
              type: { const: 'cta' },
              start: time,
              end: time,
              title: { type: 'string', minLength: 1, maxLength: 90 },
              text: { type: 'string', maxLength: 160 },
              site: { type: 'string', maxLength: 80 },
              phone: { type: 'string', maxLength: 40 },
            },
          },
        ],
        discriminator: { propertyName: 'type' },
        required: ['type'],
        properties: { type: { type: 'string' } },
      },
    },
    captions: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['start', 'end', 'text', 'words'],
        properties: {
          start: time,
          end: time,
          text: { type: 'string', minLength: 1 },
          words: {
            type: 'array',
            items: {
              type: 'object',
              additionalProperties: false,
              required: ['start', 'end', 'text'],
              properties: { start: time, end: time, text: { type: 'string', minLength: 1 } },
            },
          },
        },
      },
    },
  },
};

export const hintsSchema = {
  $id: 'mini-video-engine/hints-v1',
  type: 'object',
  additionalProperties: false,
  properties: {
    title: { type: 'string', minLength: 1, maxLength: 90 },
    subtitle: { type: 'string', maxLength: 140 },
    broll: { anyOf: [{ type: 'string', minLength: 1 }, { type: 'array', minItems: 1, items: { type: 'string', minLength: 1 } }] },
    brollLabel: { type: 'string', maxLength: 90 },
    accent: color,
    background: color,
    cta: { type: 'string', maxLength: 90 },
    ctaText: { type: 'string', maxLength: 160 },
  },
};

export const themeSchema = {
  $id: 'mini-video-engine/theme-v1',
  type: 'object',
  additionalProperties: false,
  required: ['name', 'brand', 'colors', 'safeZone', 'audio', 'cta'],
  properties: {
    name: { type: 'string', minLength: 1 },
    brand: planSchema.properties.brand,
    colors: { type: 'object', additionalProperties: false, required: ['background', 'accent', 'text'], properties: { background: color, accent: color, text: color } },
    safeZone: {
      type: 'object',
      additionalProperties: false,
      required: ['landscape', 'vertical'],
      properties: { landscape: planSchema.properties.style.properties.safeZone, vertical: planSchema.properties.style.properties.safeZone },
    },
    audio: { type: 'object', additionalProperties: false, required: ['gainDb', 'thresholdDb', 'ratio', 'attackMs', 'releaseMs'], properties: planSchema.properties.audio.properties },
    cta: { type: 'object', additionalProperties: false, required: ['title', 'text'], properties: { title: { type: 'string', maxLength: 90 }, text: { type: 'string', maxLength: 160 } } },
  },
};

const ajv = new Ajv({ allErrors: true, discriminator: true, strict: true, allowUnionTypes: true });
const validatePlanFn = ajv.compile(planSchema);
const validateHintsFn = ajv.compile(hintsSchema);
const validateThemeFn = ajv.compile(themeSchema);

/** «/scenes/1/title» -> «scenes[1].title» (+ человеческое название сцены). */
function where(instancePath, plan) {
  if (!instancePath) return 'весь файл плана';
  const parts = instancePath.split('/').slice(1);
  let pretty = '';
  for (const p of parts) pretty += /^\d+$/.test(p) ? `[${p}]` : pretty ? `.${p}` : p;
  const m = instancePath.match(/^\/scenes\/(\d+)/);
  if (m && plan?.scenes?.[Number(m[1])]) {
    const sc = plan.scenes[Number(m[1])];
    return `${pretty} (сцена №${Number(m[1]) + 1}${sc.type ? `, тип «${sc.type}»` : ''})`;
  }
  return pretty;
}

function humanAjv(e, plan) {
  const at = where(e.instancePath, plan);
  const p = e.params || {};
  switch (e.keyword) {
    case 'required':
      return `Поле «${at}»: не хватает обязательного значения «${p.missingProperty}».`;
    case 'additionalProperties':
      return `Поле «${at}»: лишнее значение «${p.additionalProperty}». Возможно, опечатка в названии.`;
    case 'type':
      return `Поле «${at}»: ожидается ${{ string: 'текст', number: 'число', integer: 'целое число', array: 'список', object: 'блок {…}', boolean: 'да/нет (true/false)' }[p.type] || p.type}.`;
    case 'enum':
      return `Поле «${at}»: допустимы только значения ${p.allowedValues.map((v) => `«${v}»`).join(', ')}.`;
    case 'const':
      return `Поле «${at}»: должно быть ровно «${p.allowedValue}».`;
    case 'minimum':
    case 'exclusiveMinimum':
      return `Поле «${at}»: число слишком маленькое (минимум ${p.limit}).`;
    case 'maximum':
      return `Поле «${at}»: число слишком большое (максимум ${p.limit}).`;
    case 'minLength':
      return `Поле «${at}»: текст не может быть пустым.`;
    case 'maxLength':
      return `Поле «${at}»: текст слишком длинный (максимум ${p.limit} знаков). Сократите.`;
    case 'minItems':
      return `Поле «${at}»: нужно не меньше ${p.limit} элементов (сцен должно быть минимум ${p.limit}).`;
    case 'pattern':
      return `Поле «${at}»: недопустимые символы.`;
    case 'discriminator':
      if (p.error === 'tag') return `Поле «${at}»: у сцены нет поля «type» (нужно одно из: ${SCENE_TYPES.join(', ')}).`;
      return `Поле «${at}»: неизвестный тип сцены «${p.tagValue}». Допустимо: ${SCENE_TYPES.join(', ')}.`;
    case 'oneOf':
      return null; // подробности уже в других ошибках
    default:
      return `Поле «${at}»: ${e.message}.`;
  }
}

/** Смысловые правила, которые схема выразить не может. Возвращает список текстов. */
function semanticProblems(plan, { checkFiles = true } = {}) {
  const out = [];
  const eps = 0.02;
  const dur = plan.source.duration;
  const scenes = plan.scenes;

  if (checkFiles) {
    const v = path.resolve(ROOT, plan.source.video);
    if (!fs.existsSync(v)) out.push(`Исходное видео не найдено: «${plan.source.video}». Проверьте, что файл лежит в папке input/.`);
  }

  const ids = new Set();
  scenes.forEach((s, i) => {
    const n = `Сцена №${i + 1} («${s.id}»)`;
    if (ids.has(s.id)) out.push(`${n}: повторяется id «${s.id}». У каждой сцены должен быть свой id.`);
    ids.add(s.id);
    if (!(s.end > s.start)) out.push(`${n}: конец (${s.end} с) должен быть позже начала (${s.start} с).`);
    else if (s.end - s.start < 0.5) out.push(`${n}: слишком короткая (${(s.end - s.start).toFixed(2)} с). Минимум 0.5 с.`);
    if (i === 0 && Math.abs(s.start) > eps) out.push(`${n}: первая сцена должна начинаться с 0 с, а начинается с ${s.start} с.`);
    if (i > 0) {
      const gap = s.start - scenes[i - 1].end;
      if (gap > eps) out.push(`Между сценами №${i} и №${i + 1} дыра ${gap.toFixed(2)} с: видео в этот момент будет пустым. Сделайте start следующей сцены равным end предыдущей.`);
      if (gap < -eps) out.push(`Сцены №${i} и №${i + 1} накладываются на ${(-gap).toFixed(2)} с. Сделайте start следующей сцены равным end предыдущей.`);
    }
    if (s.type === 'broll' && checkFiles) {
      for (const img of s.images || []) {
        if (!fs.existsSync(path.resolve(ROOT, img))) out.push(`${n}: картинка «${img}» не найдена. Положите файл в assets/broll/ или уберите её из списка «images» (без картинок будет градиент).`);
      }
    }
    if (s.type === 'speaker' && plan.source.hasVideo === false) {
      out.push(`${n}: сцена «speaker» невозможна, потому что исходник — только звук (нет видео со спикером). Используйте «broll» (фото) или «title».`);
    }
  });
  const last = scenes[scenes.length - 1];
  if (last && Math.abs(last.end - dur) > 0.1) {
    out.push(`Последняя сцена заканчивается на ${last.end} с, а видео длится ${dur} с. Сцены должны покрывать видео целиком (иначе звук и картинка разойдутся).`);
  }
  const need = plan.source.hasVideo === false ? ['title', 'broll'] : ['speaker', 'title', 'broll'];
  for (const t of need) {
    if (!scenes.some((s) => s.type === t)) {
      out.push(`Нет ни одной сцены типа «${t}». Обязательны: ${need.join(', ')} (speaker — спикер + субтитры, title — крупный заголовок, broll — картинки).`);
    }
  }
  const ctaIdx = scenes.findIndex((s) => s.type === 'cta');
  if (ctaIdx >= 0 && ctaIdx !== scenes.length - 1) out.push('Сцена «cta» (призыв и контакты) должна быть последней.');
  if (checkFiles && plan.audio?.music && !fs.existsSync(path.resolve(ROOT, plan.audio.music))) {
    out.push(`Музыка «${plan.audio.music}» не найдена. Положите трек в assets/music/ или уберите поле audio.music.`);
  }

  plan.captions.forEach((c, i) => {
    const n = `Субтитр №${i + 1} («${c.text.slice(0, 30)}»)`;
    if (c.end <= c.start) out.push(`${n}: конец раньше начала.`);
    if (c.end > dur + 0.5) out.push(`${n}: выходит за длину видео (${c.end} с > ${dur} с).`);
    if (i > 0 && c.start < plan.captions[i - 1].end - eps) out.push(`${n}: накладывается на предыдущий субтитр.`);
    c.words.forEach((w, j) => {
      if (w.end < w.start) out.push(`${n}, слово №${j + 1}: конец раньше начала.`);
    });
  });

  const { width, height } = plan.output;
  if (plan.source.hasVideo !== false && !(plan.source.width && plan.source.height && plan.source.fps)) {
    out.push('В блоке «source» не хватает width, height и fps (они обязательны, когда в исходнике есть видео).');
  }
  if (width % 2 || height % 2) out.push(`Размер ${width}×${height}: ширина и высота должны быть чётными (требование H.264).`);
  return out;
}

function fail(problems) {
  const shown = problems.slice(0, 12);
  const more = problems.length > shown.length ? `\n  …и ещё ${problems.length - shown.length}.` : '';
  const n = problems.length;
  const word = n % 10 === 1 && n % 100 !== 11 ? 'проблема' : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20) ? 'проблемы' : 'проблем';
  throw new EngineError('PLAN_INVALID', `План сцен не прошёл проверку (${n} ${word})`, {
    why: 'Рендер не запускали: он потратил бы время и выдал бы сломанный ролик.',
    fix: 'Исправьте пункты выше в файле плана (brief/*.plan.json) и повторите. Проверить без рендера: npm run validate-plan -- <файл>.',
    details: '\n' + shown.map((p, i) => `  ${i + 1}. ${p}`).join('\n') + more,
  });
}

/** Полная проверка плана. Бросает EngineError с понятным списком проблем. */
export function validatePlan(plan, opts = {}) {
  if (!validatePlanFn(plan)) {
    const problems = [...new Set(validatePlanFn.errors.map((e) => humanAjv(e, plan)).filter(Boolean))];
    fail(problems.length ? problems : ['Структура плана не соответствует схеме.']);
  }
  const sem = semanticProblems(plan, opts);
  if (sem.length) fail(sem);
  return true;
}

export function validatePlanFile(file, opts = {}) {
  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch {
    throw new EngineError('PLAN_NOT_FOUND', `Файл плана не найден: ${file}`, {
      why: 'Указан неверный путь или план ещё не создан.',
      fix: 'Планы лежат в brief/ и называются <имя-видео>.plan.json. Создать план: npm run run -- <видео> --plan-only',
    });
  }
  let plan;
  try {
    plan = JSON.parse(raw);
  } catch (e) {
    throw new EngineError('PLAN_BAD_JSON', 'Файл плана — не корректный JSON', {
      why: `Где-то нарушен синтаксис: ${String(e.message).replace(/\s+/g, ' ')}`,
      fix: 'Частые причины: лишняя или недостающая запятая, кавычки «» вместо "", комментарии. Проверьте файл в любом JSON-валидаторе.',
    });
  }
  validatePlan(plan, opts);
  return plan;
}

export function validateHints(hints, file = 'hints') {
  if (!validateHintsFn(hints)) {
    const problems = validateHintsFn.errors.map((e) => humanAjv(e, hints)).filter(Boolean);
    throw new EngineError('HINTS_INVALID', `Файл подсказок ${file} заполнен неверно`, {
      why: 'Он необязателен, но если есть — должен подчиняться правилам.',
      fix: 'Допустимые поля: title, subtitle, broll, brollLabel, accent, background.',
      details: '\n' + problems.map((p, i) => `  ${i + 1}. ${p}`).join('\n'),
    });
  }
  return hints;
}

export function validateTheme(theme, file = 'theme') {
  if (!validateThemeFn(theme)) {
    const problems = validateThemeFn.errors.map((e) => humanAjv(e, theme)).filter(Boolean);
    throw new EngineError('THEME_INVALID', `Файл темы ${file} заполнен неверно`, {
      why: 'Тема задаёт цвета, шрифты безопасных зон и параметры звука — без неё рендер невозможен.',
      fix: 'Сравните с theme/mebel-inside.json: нужны блоки name, brand, colors, safeZone (landscape и vertical), audio, cta.',
      details: '\n' + problems.map((p, i) => `  ${i + 1}. ${p}`).join('\n'),
    });
  }
  return theme;
}
