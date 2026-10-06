import React from 'react';
import { AbsoluteFill, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { FONT, unit } from '../theme.js';
import { useFade } from './useFade.js';

// Сцена 2: крупный смысловой заголовок на затемнённом размытом видео (речь при этом продолжается).
export const TitleScene = ({ scene, plan, videoFile, fadeFrames, sceneFrames, t0 }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const u = unit(width, height);
  const opacity = useFade(fadeFrames);
  const accent = plan.style.accent;

  const blur = interpolate(frame, [0, 14], [0, 16], { extrapolateRight: 'clamp' });
  const dim = interpolate(frame, [0, 14], [1, 0.42], { extrapolateRight: 'clamp' });

  const text = scene.title;
  const words = text.split(/\s+/);
  // Размер подбираем по длине заголовка, чтобы он всегда помещался и оставался КРУПНЫМ.
  const len = text.length;
  const base = height > width ? 11.5 : 9.2;
  const size = base * u * (len <= 18 ? 1 : len <= 34 ? 0.98 : len <= 55 ? 0.78 : 0.6);

  const barW = spring({ frame: frame - 6, fps, config: { damping: 20, stiffness: 120 } });
  const subIn = interpolate(frame, [18 + words.length * 4, 30 + words.length * 4], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const outFade = interpolate(frame, [sceneFrames - 6, sceneFrames], [1, 0.0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const useVideo = scene.backdrop !== 'gradient';
  return (
    <AbsoluteFill style={{ opacity }}>
      {useVideo ? (
        <AbsoluteFill style={{ filter: `blur(${blur}px) brightness(${dim})`, transform: 'scale(1.08)' }}>
          <OffthreadVideo
            src={staticFile(videoFile)}
            muted
            trimBefore={t0}
            style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: `${(scene.focusX ?? 0.5) * 100}% 50%` }}
          />
        </AbsoluteFill>
      ) : (
        <AbsoluteFill style={{ background: `radial-gradient(circle at 30% 20%, ${accent}33, ${plan.style.background} 70%)` }} />
      )}
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', padding: `${plan.style.safeZone?.top ?? 6}% ${(plan.style.safeZone?.side ?? 6) + 2}% ${plan.style.safeZone?.bottom ?? 9}%`, opacity: outFade }}>
        <div style={{ fontFamily: FONT, textAlign: 'center', maxWidth: '100%' }}>
          <div style={{ fontWeight: 900, fontSize: size, lineHeight: 1.08, color: plan.style.text || '#fff', textShadow: '0 4px 24px rgba(0,0,0,0.5)', letterSpacing: '-0.01em' }}>
            {words.map((w, i) => {
              const p = spring({ frame: frame - (4 + i * 4), fps, config: { damping: 16, stiffness: 160 } });
              return (
                <span key={i} style={{ display: 'inline-block', marginRight: '0.26em', opacity: p, transform: `translateY(${interpolate(p, [0, 1], [28, 0])}px)` }}>
                  {w}
                </span>
              );
            })}
          </div>
          <div style={{ margin: `${2.4 * u}px auto 0`, height: 1.1 * u, width: `${34 * barW}%`, background: accent, borderRadius: u }} />
          {scene.subtitle ? (
            <div style={{ marginTop: 2.6 * u, fontWeight: 600, fontSize: size * 0.34, color: 'rgba(255,255,255,0.88)', opacity: subIn }}>{scene.subtitle}</div>
          ) : null}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
