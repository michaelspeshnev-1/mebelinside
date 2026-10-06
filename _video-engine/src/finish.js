// Шаг 8: FFmpeg-финиш. Картинка от Remotion + оригинальный звук (+ музыка с sidechain) -> итоговый MP4.
import fs from 'node:fs';
import path from 'node:path';
import { run } from './exec.js';
import { EngineError } from './errors.js';
import { DIRS, ROOT, assertNotSource } from './paths.js';

const dbToLin = (db) => Math.pow(10, db / 20);

/** Граф звука: голос нажимает на музыку «как на педаль» (sidechaincompress), затем смешивание и выравнивание громкости. */
export function audioGraph(plan, { stemOnly = false } = {}) {
  const a = plan.audio;
  const D = plan.source.duration;
  const thr = Math.min(1, Math.max(0.000976563, dbToLin(a.thresholdDb))); // sidechaincompress ждёт линейное значение
  const lines = [
    '[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[vsc][vmix]',
    `[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=${a.gainDb}dB,afade=t=in:d=0.8[m]`,
    `[m][vsc]sidechaincompress=threshold=${thr.toFixed(6)}:ratio=${a.ratio}:attack=${a.attackMs}:release=${a.releaseMs}[mduck]`,
  ];
  if (stemOnly) {
    lines.push('[vmix]anullsink'); // голос нужен только как «педаль»; сам в дорожку не попадает
    return { graph: lines.join(';'), map: '[mduck]' };
  }
  lines.push('[vmix][mduck]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mix]');
  lines.push(`[mix]afade=t=out:st=${Math.max(0, D - 1.2).toFixed(2)}:d=1.2,loudnorm=I=-16:TP=-1.5:LRA=11[aout]`);
  return { graph: lines.join(';'), map: '[aout]' };
}

export async function finish(plan, visualMp4, { log = console.log } = {}) {
  const source = path.resolve(ROOT, plan.source.video);
  const music = plan.audio?.music ? path.resolve(ROOT, plan.audio.music) : null;
  const out = assertNotSource(path.join(DIRS.final, `${plan.name}.mp4`));
  const tmp = out.replace(/\.mp4$/, '.partial.mp4');
  fs.mkdirSync(DIRS.final, { recursive: true });

  const args = ['-y', '-v', 'error', '-i', visualMp4, '-i', source];
  if (music) args.push('-stream_loop', '-1', '-i', music);
  args.push('-map', '0:v:0');
  if (music) {
    const { graph, map } = audioGraph(plan);
    args.push('-filter_complex', graph, '-map', map);
    log(`  музыка: ${path.relative(ROOT, music)} (sidechain: ${plan.audio.gainDb} дБ, порог ${plan.audio.thresholdDb} дБ, ${plan.audio.ratio}:1, атака ${plan.audio.attackMs} мс, возврат ${plan.audio.releaseMs} мс)`);
  } else {
    args.push('-map', '1:a:0', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11'); // ровная громкость как на видеоплатформах
  }
  args.push(
    // Remotion пишет «полный» цветовой диапазон (yuvj420p), который часть плееров и площадок показывает с
    // искажёнными цветами. Переводим в обычный вещательный yuv420p (limited range, BT.709).
    '-vf', 'scale=in_range=pc:out_range=tv:in_color_matrix=bt470bg:out_color_matrix=bt709,format=yuv420p',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-profile:v', 'high',
    '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
    '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-ac', '2',
    '-t', String(plan.source.duration), '-shortest',
    '-movflags', '+faststart', // ролик можно смотреть, не дожидаясь полной загрузки
    tmp,
  );
  const res = await run('ffmpeg', args);
  if (res.code !== 0) {
    fs.rmSync(tmp, { force: true });
    throw new EngineError('FINISH_FAILED', 'FFmpeg не смог собрать итоговый MP4', {
      why: music ? 'Не получилось соединить картинку, голос и музыку (возможно, трек повреждён или это не аудиофайл).' : 'Не получилось соединить картинку и звук.',
      fix: 'Проверьте, что исходное видео и трек музыки на месте и открываются. Затем npm run doctor.',
      details: res.stderr.trim().split('\n')[0],
    });
  }
  fs.renameSync(tmp, out);
  log(`  итоговый файл: ${path.relative(ROOT, out)} (${(fs.statSync(out).size / 1e6).toFixed(1)} МБ)`);
  return out;
}

/**
 * Проверка «музыка не перекрывает голос»: в окнах речи сравниваем громкость голоса и ПРИГЛУШЁННОЙ музыки
 * (та же цепочка, что в финале, но отдельной дорожкой). Возвращает запас в дБ.
 */
export async function measureDuck(plan, voiceWav, windows) {
  if (!plan.audio?.music || !windows.length) return null;
  const music = path.resolve(ROOT, plan.audio.music);
  const stem = path.join(DIRS.renders, `.${plan.name}.music-stem.wav`);
  const { graph, map } = audioGraph(plan, { stemOnly: true });
  const r = await run('ffmpeg', ['-y', '-v', 'error', '-i', voiceWav, '-i', voiceWav, '-stream_loop', '-1', '-i', music, '-filter_complex', graph, '-map', map, '-t', String(plan.source.duration), '-ar', '48000', stem]);
  if (r.code !== 0) return null;
  const sel = windows.slice(0, 60).map(([a, b]) => `between(t,${a.toFixed(2)},${b.toFixed(2)})`).join('+');
  const mean = async (file) => {
    const v = await run('ffmpeg', ['-v', 'info', '-i', file, '-af', `aselect='${sel}',volumedetect`, '-f', 'null', '-']);
    const m = v.stderr.match(/mean_volume: (-?[\d.]+) dB/);
    return m ? Number(m[1]) : null;
  };
  const voice = await mean(voiceWav);
  const mus = await mean(stem);
  fs.rmSync(stem, { force: true });
  if (voice === null || mus === null) return null;
  return { voiceDb: voice, musicDb: mus, marginDb: Math.round((voice - mus) * 10) / 10 };
}
