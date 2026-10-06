// Разбор опций командной строки (общий для run, demo и watch).
import { EngineError } from './errors.js';

const WITH_VALUE = new Set(['name', 'format', 'size', 'fps', 'language', 'engine', 'model', 'plan', 'theme', 'music', 'only', 'interval']);

export function parseArgs(argv, usage = '') {
  const o = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      if (WITH_VALUE.has(k)) {
        if (argv[i + 1] === undefined) throw new EngineError('BAD_ARGS', `У опции --${k} нет значения`, { why: 'После неё нужно указать значение.', fix: usage || 'Запустите: npm run help' });
        o[k] = argv[++i];
      } else o[k] = true;
    } else o._.push(a);
  }
  return o;
}
