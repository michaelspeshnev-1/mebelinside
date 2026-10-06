import React from 'react';
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { FONT, unit } from '../theme.js';
import { Captions } from './Captions.jsx';
import { Brand } from './Brand.jsx';
import { useFade } from './useFade.js';

const XFADE = 10; // кадров перекрёстного перехода между фото

// B-roll: одно или несколько фото, медленное движение камеры (Ken Burns), плавная смена.
// Нет фото - анимированный градиент в цветах темы.
export const BrollScene = ({ scene, plan, imageFiles, fadeFrames, sceneFrames, t0, logoFile }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const u = unit(width, height);
  const opacity = useFade(fadeFrames);
  const n = imageFiles.length;
  const slot = n ? sceneFrames / n : sceneFrames;

  return (
    <AbsoluteFill style={{ opacity, backgroundColor: plan.style.background }}>
      {n ? (
        imageFiles.map((file, i) => {
          const start = i * slot - (i > 0 ? XFADE : 0);
          const end = (i + 1) * slot;
          if (frame < start || frame > end + XFADE) return null;
          const local = interpolate(frame, [start, end], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
          const fadeIn = i === 0 ? 1 : interpolate(frame, [start, start + XFADE], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
          const scale = 1.04 + 0.1 * local;
          const dir = i % 2 === 0 ? -1 : 1;
          return (
            <AbsoluteFill key={file} style={{ opacity: fadeIn, transform: `translateX(${dir * (local - 0.5) * 3}%) scale(${scale})` }}>
              <Img src={staticFile(file)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            </AbsoluteFill>
          );
        })
      ) : (
        <AbsoluteFill style={{ background: `linear-gradient(${120 + 60 * (frame / Math.max(sceneFrames, 1))}deg, ${plan.style.background}, ${plan.style.accent}66 55%, ${plan.style.background})` }} />
      )}
      <AbsoluteFill style={{ background: 'linear-gradient(to top, rgba(5,8,18,0.6) 0%, rgba(5,8,18,0) 40%), radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.35) 100%)' }} />
      <Brand plan={plan} logoFile={logoFile} />
      {scene.label ? (
        <div style={{ position: 'absolute', top: `${(plan.style.safeZone?.top ?? 6) + 7}%`, left: `${plan.style.safeZone?.side ?? 6}%`, fontFamily: FONT, fontWeight: 800, fontSize: 3.2 * u, color: '#101216', background: plan.style.accent, padding: `${0.9 * u}px ${2 * u}px`, borderRadius: 1.2 * u }}>
          {scene.label}
        </div>
      ) : null}
      {scene.subtitles !== false && <Captions captions={plan.captions} t0={t0} accent={plan.style.accent} safeZone={plan.style.safeZone} textColor={plan.style.text} />}
    </AbsoluteFill>
  );
};
