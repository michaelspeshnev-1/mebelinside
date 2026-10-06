// Шаг 1: проверка параметров входного видео через ffprobe.
import { run } from './exec.js';
import { EngineError } from './errors.js';

function parseRate(r) {
  if (!r || r === '0/0') return 0;
  const [a, b] = r.split('/').map(Number);
  return b ? a / b : a;
}

export async function probe(file) {
  const res = await run('ffprobe', ['-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', file]);
  if (res.code !== 0) {
    const err = res.stderr.trim();
    if (/Invalid data found|moov atom not found|could not find codec/i.test(err)) {
      throw new EngineError('BAD_MEDIA', 'Файл не читается как видео или звук', {
        why: 'Он повреждён, не дозагружен или это вовсе не видеофайл.',
        fix: 'Откройте его в обычном плеере. Если не играет — скачайте или экспортируйте заново. Подойдут MP4, MOV, MKV, WebM, M4A, MP3, WAV.',
        details: err.split('\n')[0],
      });
    }
    throw new EngineError('PROBE_FAILED', 'ffprobe не смог проверить файл', {
      why: 'Программа проверки вернула ошибку.',
      fix: 'Убедитесь, что файл существует и открывается. Затем запустите npm run doctor.',
      details: err.split('\n')[0],
    });
  }
  const j = JSON.parse(res.stdout);
  const v = (j.streams || []).find((s) => s.codec_type === 'video' && s.disposition?.attached_pic !== 1);
  const a = (j.streams || []).find((s) => s.codec_type === 'audio');

  let video = null;
  if (v) {
    let w = v.width;
    let h = v.height;
    const rot = Math.abs(Number(v.tags?.rotate ?? v.side_data_list?.find((x) => 'rotation' in x)?.rotation ?? 0)) % 360;
    if (rot === 90 || rot === 270) [w, h] = [h, w];
    video = {
      codec: v.codec_name,
      width: w,
      height: h,
      fps: Math.round(parseRate(v.avg_frame_rate || v.r_frame_rate) * 1000) / 1000,
      pixFmt: v.pix_fmt,
      rotation: rot,
      nbFrames: v.nb_frames ? Number(v.nb_frames) : null,
    };
  }
  const audio = a
    ? { codec: a.codec_name, sampleRate: Number(a.sample_rate), channels: a.channels }
    : null;

  return {
    file,
    duration: Number(j.format?.duration ?? v?.duration ?? 0),
    sizeBytes: Number(j.format?.size ?? 0),
    container: j.format?.format_name,
    video,
    audio,
  };
}

/** Проверка: годится ли файл для нашего конвейера. Бросает EngineError. */
export function checkInput(info) {
  // Только звук допустим: движок соберёт ролик из ваших фото (режим «голос + фото», без лица в кадре).
  if (!info.video && !info.audio) {
    throw new EngineError('NO_MEDIA_STREAMS', 'В файле нет ни видео, ни звука', {
      why: 'Внутри нечего монтировать.',
      fix: 'Выберите видео (MP4, MOV, MKV, WebM) или запись голоса (M4A, MP3, WAV).',
    });
  }
  if (!info.audio) {
    throw new EngineError('NO_AUDIO_STREAM', 'В видео нет звука', {
      why: 'Субтитры строятся по речи, а речи в файле нет.',
      fix: 'Возьмите видео с записанным голосом. Если звук был, но пропал при экспорте — экспортируйте заново с аудиодорожкой.',
    });
  }
  if (!(info.duration > 1)) {
    throw new EngineError('TOO_SHORT', 'Видео короче одной секунды', {
      why: 'Для трёх сцен нужен хотя бы небольшой ролик.',
      fix: 'Возьмите видео от 6 секунд и длиннее.',
      details: `duration=${info.duration}`,
    });
  }
  const warnings = [];
  if (info.duration < 6) warnings.push('Видео короче 6 секунд: сцены получатся очень короткими.');
  if (info.duration > 900) warnings.push('Видео длиннее 15 минут: рендер на слабом компьютере займёт очень много времени.');
  return warnings;
}
