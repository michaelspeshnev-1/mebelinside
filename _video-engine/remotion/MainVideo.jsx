import React from 'react';
import { AbsoluteFill, Sequence, useVideoConfig } from 'remotion';
import { SpeakerScene } from './scenes/SpeakerScene.jsx';
import { TitleScene } from './scenes/TitleScene.jsx';
import { BrollScene } from './scenes/BrollScene.jsx';
import { CtaScene } from './scenes/CtaScene.jsx';

const FADE = 8; // кадров плавного появления сцены поверх предыдущей

export const MainVideo = ({ plan, videoFile, images, logoFile }) => {
  const { fps, durationInFrames } = useVideoConfig();

  // Границы сцен в кадрах: считаем накопительно, чтобы не было щелей из-за округления.
  const bounds = plan.scenes.map((s, i) => ({
    from: i === 0 ? 0 : Math.round(s.start * fps),
    to: i === plan.scenes.length - 1 ? durationInFrames : Math.round(s.end * fps),
  }));

  return (
    <AbsoluteFill style={{ backgroundColor: plan.style.background }}>
      {plan.scenes.map((scene, i) => {
        const { from, to } = bounds[i];
        const lead = i === 0 ? 0 : Math.min(FADE, from); // сцена начинается чуть раньше и «проявляется»
        const common = {
          scene,
          plan,
          videoFile,
          fadeFrames: lead,
          sceneFrames: to - from + lead,
          t0: from - lead, // кадр композиции, с которого начинается эта Sequence
          logoFile,
        };
        return (
          <Sequence key={scene.id} from={from - lead} durationInFrames={to - from + lead} name={`${scene.type}: ${scene.id}`}>
            {scene.type === 'speaker' && <SpeakerScene {...common} />}
            {scene.type === 'title' && <TitleScene {...common} />}
            {scene.type === 'broll' && <BrollScene {...common} imageFiles={images?.[scene.id] || []} />}
            {scene.type === 'cta' && <CtaScene {...common} />}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
