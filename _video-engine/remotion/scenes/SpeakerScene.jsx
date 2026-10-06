import React from 'react';
import { AbsoluteFill, OffthreadVideo, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { Captions } from './Captions.jsx';
import { Brand } from './Brand.jsx';
import { useFade } from './useFade.js';

// Сцена 1: видео со спикером + субтитры. Звук берёт FFmpeg из оригинала, поэтому видео здесь без звука.
export const SpeakerScene = ({ scene, plan, videoFile, fadeFrames, sceneFrames, t0, logoFile }) => {
  const frame = useCurrentFrame();
  const opacity = useFade(fadeFrames);
  const zoom = interpolate(frame, [0, sceneFrames], [1.0, 1.06], { extrapolateRight: 'clamp' }); // еле заметный «наезд»
  const fx = (scene.focusX ?? 0.5) * 100;
  const fy = (scene.focusY ?? 0.5) * 100;

  return (
    <AbsoluteFill style={{ opacity }}>
      <AbsoluteFill style={{ transform: `scale(${zoom})`, transformOrigin: `${fx}% ${fy}%` }}>
        <OffthreadVideo
          src={staticFile(videoFile)}
          muted
          trimBefore={t0}
          style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: `${fx}% ${fy}%` }}
        />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: 'linear-gradient(to top, rgba(5,8,18,0.55) 0%, rgba(5,8,18,0) 38%)' }} />
      <Brand plan={plan} logoFile={logoFile} />
      {scene.subtitles !== false && <Captions captions={plan.captions} t0={t0} accent={plan.style.accent} safeZone={plan.style.safeZone} textColor={plan.style.text} />}
    </AbsoluteFill>
  );
};
