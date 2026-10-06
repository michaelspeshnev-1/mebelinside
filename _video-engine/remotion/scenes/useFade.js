import { interpolate, useCurrentFrame } from 'remotion';

/** Прозрачность сцены: плавное появление в первые fadeFrames кадров. */
export const useFade = (fadeFrames) => {
  const frame = useCurrentFrame();
  return fadeFrames > 0 ? interpolate(frame, [0, fadeFrames], [0, 1], { extrapolateRight: 'clamp' }) : 1;
};
