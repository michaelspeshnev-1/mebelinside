// Шаг 2: извлечение звука (WAV 16 кГц, моно) для распознавания речи.
import fs from 'node:fs';
import { run } from './exec.js';
import { EngineError } from './errors.js';
import { assertNotSource } from './paths.js';

export async function extractAudio(inputFile, outWav) {
  assertNotSource(outWav);
  const tmp = outWav.replace(/\.wav$/, '.partial.wav');
  const res = await run('ffmpeg', ['-y', '-v', 'error', '-i', inputFile, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', tmp]);
  if (res.code !== 0) {
    fs.rmSync(tmp, { force: true });
    throw new EngineError('AUDIO_EXTRACT_FAILED', 'Не удалось вытащить звук из видео', {
      why: 'FFmpeg остановился с ошибкой при чтении аудиодорожки.',
      fix: 'Проверьте, что файл проигрывается со звуком. Затем запустите npm run doctor.',
      details: res.stderr.trim().split('\n')[0],
    });
  }
  fs.renameSync(tmp, outWav);
  const size = fs.statSync(outWav).size;
  if (size < 4000) {
    throw new EngineError('AUDIO_EMPTY', 'Извлечённый звук пустой', {
      why: 'Аудиодорожка есть, но в ней нет данных.',
      fix: 'Проверьте исходное видео в плеере: должен быть слышен голос.',
      details: `bytes=${size}`,
    });
  }
  return outWav;
}
