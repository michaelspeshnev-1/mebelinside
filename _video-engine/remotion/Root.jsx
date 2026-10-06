import React from 'react';
import { Composition } from 'remotion';
import { MainVideo } from './MainVideo.jsx';

export const COMPOSITION_ID = 'Main';

// Размер, частота кадров и длина берутся из JSON-плана (inputProps) - композиция сама под него подстраивается.
export const Root = () => (
  <Composition
    id={COMPOSITION_ID}
    component={MainVideo}
    width={1280}
    height={720}
    fps={30}
    durationInFrames={90}
    defaultProps={{ plan: null, videoFile: null, images: {}, logoFile: null }}
    calculateMetadata={({ props }) => {
      if (!props.plan) throw new Error('В композицию не передан plan (JSON-план сцен).');
      const { output, source } = props.plan;
      return {
        width: output.width,
        height: output.height,
        fps: output.fps,
        durationInFrames: Math.max(1, Math.round(source.duration * output.fps)),
      };
    }}
  />
);
