import React from 'react';
import { AbsoluteFill, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { FONT, unit } from '../theme.js';
import { useFade } from './useFade.js';

// Финальная сцена: призыв и контакты (без цен). Видео продолжается под размытием, пока идёт речь.
export const CtaScene = ({ scene, plan, videoFile, fadeFrames, t0 }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const u = unit(width, height);
  const opacity = useFade(fadeFrames);
  const a = plan.style.accent;
  const sz = plan.style.safeZone || { top: 6, bottom: 9, side: 6 };
  const vertical = height > width;

  const blur = interpolate(frame, [0, 12], [0, 18], { extrapolateRight: 'clamp' });
  const dim = interpolate(frame, [0, 12], [1, 0.38], { extrapolateRight: 'clamp' });
  const pop = (d) => spring({ frame: frame - d, fps, config: { damping: 16, stiffness: 150 } });
  const p1 = pop(4), p2 = pop(12), p3 = pop(20);
  const useVideo = Boolean(videoFile) && plan.source.hasVideo !== false;

  return (
    <AbsoluteFill style={{ opacity }}>
      {useVideo ? (
        <AbsoluteFill style={{ filter: `blur(${blur}px) brightness(${dim})`, transform: 'scale(1.08)' }}>
          <OffthreadVideo src={staticFile(videoFile)} muted trimBefore={t0} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </AbsoluteFill>
      ) : (
        <AbsoluteFill style={{ background: `radial-gradient(circle at 70% 25%, ${a}40, ${plan.style.background} 68%)` }} />
      )}
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: `${sz.top}% ${sz.side}% ${sz.bottom}%`, fontFamily: FONT, textAlign: 'center', color: plan.style.text || '#fff' }}>
        <div style={{ opacity: p1, transform: `translateY(${interpolate(p1, [0, 1], [24, 0])}px)`, fontWeight: 900, fontSize: (vertical ? 8.4 : 7.2) * u, lineHeight: 1.1, textShadow: '0 4px 24px rgba(0,0,0,.5)' }}>{scene.title}</div>
        <div style={{ margin: `${2.2 * u}px 0`, height: u, width: `${30 * p1}%`, background: a, borderRadius: u }} />
        {scene.text ? <div style={{ opacity: p2, fontWeight: 600, fontSize: (vertical ? 3.7 : 3.1) * u, lineHeight: 1.3, maxWidth: '86%', color: 'rgba(255,255,255,.9)' }}>{scene.text}</div> : null}
        <div style={{ opacity: p3, marginTop: 3.2 * u, display: 'flex', flexDirection: 'column', gap: 1.2 * u, alignItems: 'center' }}>
          {scene.site ? <div style={{ fontWeight: 800, fontSize: (vertical ? 5 : 4.2) * u, color: a, letterSpacing: '0.02em' }}>{scene.site}</div> : null}
          {scene.phone ? <div style={{ fontWeight: 700, fontSize: (vertical ? 4.2 : 3.6) * u }}>{scene.phone}</div> : null}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
