// Финальная приёмка в три независимых контура: СМЫСЛ, КАРТИНКА, ТЕХНИКА.
// Автоматически проверяется всё, что можно проверить машиной; остальное честно помечено «посмотрите глазами» (👁).
import fs from 'node:fs';
import path from 'node:path';
import { DIRS, ROOT } from './paths.js';

const PRICE_RE = /₽|руб|\bцен[аыуе]\b|стоимост|тыс\.?\s*р|\$|€|\bprice\b|\bcost\b/i;

export function accept({ plan, transcript, verifyRep, duck }) {
  const L = { meaning: [], picture: [], tech: [] };
  const ok = (c, name, detail = '') => L[c].push({ s: 'ok', name, detail });
  const bad = (c, name, detail = '') => L[c].push({ s: 'fail', name, detail });
  const eye = (c, name, detail = '') => L[c].push({ s: 'eye', name, detail });
  const D = plan.source.duration;

  // ---- СМЫСЛ
  const words = plan.captions.flatMap((c) => c.words.map((w) => w.text));
  if (transcript) {
    const tw = transcript.segments.flatMap((s) => (s.words?.length ? s.words.map((w) => w.word) : s.text.split(/\s+/))).filter(Boolean);
    words.length === tw.length ? ok('meaning', 'Субтитры содержат все слова расшифровки', `${words.length} слов`) : bad('meaning', 'Субтитры потеряли слова расшифровки', `в субтитрах ${words.length}, в расшифровке ${tw.length}`);
    const first = transcript.segments[0]?.start;
    first !== undefined && first <= 3 ? ok('meaning', 'Хук: речь начинается в первые 3 секунды', `${first.toFixed(1)} с`) : bad('meaning', 'Хук: речь начинается слишком поздно', `${first?.toFixed?.(1)} с — зритель уйдёт; обрежьте начало`);
    if (transcript.engine === 'pocketsphinx') eye('meaning', 'ТЕКСТ СУБТИТРОВ — проверьте глазами', 'расшифровка запасным движком pocketsphinx: слова могут быть неверными. Лучше подключить Whisper (README).');
    else eye('meaning', 'Прочитайте субтитры целиком', 'Whisper ошибается на именах, названиях материалов и фурнитуры.');
  } else eye('meaning', 'Расшифровки нет (использован готовый план) — проверка текста невозможна');
  const title = plan.scenes.find((s) => s.type === 'title');
  title && title.title.trim().length >= 3 ? ok('meaning', 'Есть смысловой заголовок', `«${title.title}»`) : bad('meaning', 'Нет заголовка');
  const cta = plan.scenes.find((s) => s.type === 'cta');
  cta && (cta.site || cta.phone) ? ok('meaning', 'Есть призыв к действию с контактами', [cta.site, cta.phone].filter(Boolean).join(', ')) : eye('meaning', 'Нет финального призыва (CTA)', D < 15 ? 'ролик короче 15 с — CTA не добавляется' : 'в теме не заданы сайт и телефон');
  const onScreen = [...plan.scenes.flatMap((s) => [s.title, s.subtitle, s.text, s.label].filter(Boolean)), ...plan.captions.map((c) => c.text)].join(' | ');
  const price = onScreen.match(PRICE_RE);
  price ? bad('meaning', 'На экране есть упоминание цены/стоимости', `«${price[0]}» — по правилам канала цены не показываем`) : ok('meaning', 'На экране нет цен');

  // ---- КАРТИНКА
  const sz = plan.style.safeZone;
  sz ? ok('picture', 'Субтитры и плашка внутри безопасной зоны', `сверху ${sz.top}%, снизу ${sz.bottom}%, по бокам ${sz.side}%`) : eye('picture', 'Безопасная зона не задана в теме');
  const short = plan.scenes.filter((s) => s.end - s.start < 1.5);
  short.length ? bad('picture', 'Есть слишком короткие сцены (мелькание)', short.map((s) => `${s.id} ${(s.end - s.start).toFixed(1)} с`).join(', ')) : ok('picture', 'Нет сцен короче 1.5 с', `${plan.scenes.length} сцен: ${plan.scenes.map((s) => s.type).join(' → ')}`);
  const imgs = plan.scenes.filter((s) => s.type === 'broll').flatMap((s) => s.images || []);
  imgs.length ? ok('picture', 'B-roll: использованы ваши фото', `${imgs.length} шт.`) : eye('picture', 'B-roll — градиент вместо фото', 'положите снимки работ в assets/broll/');
  verifyRep?.checks?.find((c) => c.name.startsWith('сцены визуально'))?.ok ? ok('picture', 'Кадры разных сцен различаются, кадры не чёрные') : bad('picture', 'Кадры сцен не прошли проверку на различимость');
  eye('picture', `Посмотрите previews/${plan.name}-preview.mp4 и кадры сцен`, 'машина не оценит красоту: ровные ли переходы, не перекрывает ли текст важное');

  // ---- ТЕХНИКА
  for (const c of verifyRep?.checks || []) (c.ok ? ok : bad)('tech', c.name, c.detail);
  if (plan.audio?.music) {
    if (!duck) bad('tech', 'Не удалось измерить, перекрывает ли музыка голос');
    else duck.marginDb >= 6 ? ok('tech', 'Музыка не перекрывает голос (sidechain работает)', `в речи голос громче приглушённой музыки на ${duck.marginDb} дБ`) : bad('tech', 'Музыка слишком громкая под речью', `голос громче музыки всего на ${duck.marginDb} дБ (нужно ≥ 6)`);
  }

  const failed = Object.values(L).flat().filter((x) => x.s === 'fail');
  return { contours: L, ok: failed.length === 0, failed, manual: Object.values(L).flat().filter((x) => x.s === 'eye') };
}

export function reportMarkdown(plan, acc, meta = {}) {
  const icon = { ok: '✔', fail: '✖', eye: '👁' };
  const titles = { meaning: 'Смысл', picture: 'Картинка', tech: 'Техника' };
  const out = [`# Приёмка ролика «${plan.name}»`, '', `Итог: **${acc.ok ? 'автоматические проверки пройдены' : 'ЕСТЬ ПРОВАЛЕННЫЕ ПРОВЕРКИ — не публиковать'}**` + (acc.manual.length ? `; ещё ${acc.manual.length} пункт(а) нужно посмотреть человеку (👁).` : '.'), ''];
  if (meta.engine) out.push(`Распознавание речи: ${meta.engine}`, '');
  for (const k of ['meaning', 'picture', 'tech']) {
    out.push(`## ${titles[k]}`, '');
    for (const c of acc.contours[k]) out.push(`- ${icon[c.s]} ${c.name}${c.detail ? ` — ${c.detail}` : ''}`);
    out.push('');
  }
  out.push('Принцип: человек решает → агент режиссирует → движок исполняет. Значок 👁 — это решение человека.');
  return out.join('\n') + '\n';
}

export function writeReport(plan, acc, meta) {
  const file = path.join(DIRS.final, `${plan.name}.report.md`);
  fs.writeFileSync(file, reportMarkdown(plan, acc, meta));
  return path.relative(ROOT, file);
}
