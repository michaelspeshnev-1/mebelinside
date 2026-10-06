#!/usr/bin/env node
// Командная строка движка: run / demo / validate-plan.
import fs from 'node:fs';
import path from 'node:path';
import { validatePlanFile } from './schema.js';
import { runPipeline } from './pipeline.js';
import { parseArgs } from './args.js';
import { makeTestAssets, TEST_VIDEO, TEST_MUSIC } from './make-test-assets.js';
import { ROOT } from './paths.js';
import { EngineError, explain } from './errors.js';

const log = console.log;
const HELP = `Использование:
  npm run run -- <видео|голос> [опции] полный цикл: видео -> final/<имя>.mp4
  npm run demo                      тестовое видео -> final/demo.mp4 + проверка
  npm run validate-plan -- <план>   проверить JSON-план без рендера
  npm run doctor                    диагностика окружения
  npm run watch                     автозапуск: следит за input/ и делает ролики сам
Опции run: --name <имя>  --format landscape|vertical|square  --size 1280x720  --fps 30
           --theme mebel-inside  --music assets/music/трек.mp3|auto|none
           --language auto|en|ru  --engine auto|whisper|sphinx  --model small
           --face (искать лицо для кадрирования, нужен OpenCV)
           --finish-only (не рисовать заново, только склейка со звуком)  --plan-only (остановиться после плана)  --plan <файл> (взять свой план)  --no-preview`;

async function main() {
  const [cmd, ...rest] = process.argv.slice(2);
  const o = parseArgs(rest, HELP);
  if (!cmd || cmd === 'help' || o.help) return log(HELP);
  if (cmd === 'run') {
    if (!o._[0]) throw new EngineError('NO_INPUT', 'Не указано видео', { why: 'Команде run нужен файл.', fix: 'Пример: npm run run -- input/мой-ролик.mp4' });
    return runPipeline(o._[0], o);
  }
  if (cmd === 'demo') {
    await makeTestAssets({ log });
    // Демо показывает всё сразу: вертикальный кадр для рилсов, тему, CTA, фото-слайдшоу и музыку с sidechain
    return runPipeline(TEST_VIDEO, { format: 'vertical', size: '720x1280', music: path.relative(ROOT, TEST_MUSIC), ...o, name: 'demo' });
  }
  if (cmd === 'validate-plan') {
    if (!o._[0]) throw new EngineError('NO_INPUT', 'Не указан файл плана', { why: 'Нужен путь к *.plan.json.', fix: 'Пример: npm run validate-plan -- brief/demo.plan.json' });
    const p = validatePlanFile(path.resolve(ROOT, o._[0]));
    return log(`✔ План «${p.name}» корректен: ${p.scenes.length} сцен, ${p.captions.length} субтитров, ${p.source.duration} с.`);
  }
  throw new EngineError('BAD_COMMAND', `Неизвестная команда «${cmd}»`, { why: 'Такой команды нет.', fix: HELP });
}

main().catch((e) => {
  console.error('\n' + explain(e));
  process.exit(1);
});
