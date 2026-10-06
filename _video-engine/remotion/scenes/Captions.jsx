import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { FONT, unit } from '../theme.js';

/** Субтитры: короткие строки, текущее слово подсвечено. t0 - кадр, с которого начинается Sequence. */
export const Captions = ({ captions, t0, accent, safeZone, textColor = '#fff' }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = (t0 + frame) / fps;
  const u = unit(width, height);
  const vertical = height > width;

  // Показываем строку, пока она звучит, и ещё чуть-чуть после (не мигает между словами).
  const idx = captions.findIndex((c, i) => {
    const next = captions[i + 1];
    const hold = Math.min(c.end + 0.25, next ? next.start : Infinity);
    return t >= c.start - 0.03 && t < hold;
  });
  if (idx < 0) return null;
  const cap = captions[idx];

  const appear = spring({ frame: Math.round((t - cap.start) * fps), fps, config: { damping: 18, stiffness: 220 }, durationInFrames: 10 });
  const scale = interpolate(appear, [0, 1], [0.94, 1], { extrapolateLeft: 'clamp' });
  const opacity = interpolate(appear, [0, 1], [0, 1], { extrapolateLeft: 'clamp' });

  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: `${safeZone ? safeZone.bottom : vertical ? 17 : 8}%`, display: 'flex', justifyContent: 'center', padding: `0 ${safeZone ? safeZone.side : 6}%` }}>
      <div
        style={{
          fontFamily: FONT,
          fontWeight: 800,
          fontSize: (vertical ? 5.2 : 5.6) * u,
          lineHeight: 1.18,
          textAlign: 'center',
          color: textColor,
          background: 'rgba(8,12,24,0.62)',
          padding: `${1.6 * u}px ${3 * u}px`,
          borderRadius: 2.2 * u,
          maxWidth: '90%',
          transform: `scale(${scale})`,
          opacity,
          textShadow: '0 2px 6px rgba(0,0,0,0.45)',
        }}
      >
        {cap.words.map((w, i) => {
          const active = t >= w.start - 0.02 && t < w.end + 0.02;
          return (
            <span key={i} style={{ color: active ? accent : textColor, display: 'inline-block', transform: active ? 'scale(1.07)' : 'none', marginRight: i < cap.words.length - 1 ? '0.28em' : 0 }}>
              {w.text}
            </span>
          );
        })}
      </div>
    </div>
  );
};
