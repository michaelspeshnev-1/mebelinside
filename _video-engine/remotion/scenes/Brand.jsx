import React from 'react';
import { Img, staticFile, useVideoConfig } from 'remotion';
import { FONT, unit } from '../theme.js';

/** Фирменная плашка в углу (в пределах безопасной зоны): логотип, если он есть в assets/, иначе название. */
export const Brand = ({ plan, logoFile }) => {
  const { width, height } = useVideoConfig();
  const u = unit(width, height);
  const sz = plan.style.safeZone || { top: 6, bottom: 9, side: 6 };
  const name = plan.brand?.name;
  if (!logoFile && !name) return null;
  return (
    <div style={{ position: 'absolute', top: `${sz.top}%`, left: `${sz.side}%`, display: 'flex', alignItems: 'center', gap: u, padding: `${0.8 * u}px ${1.8 * u}px`, borderRadius: u * 1.1, background: 'rgba(12,14,18,0.55)', fontFamily: FONT, fontWeight: 800, fontSize: 2.5 * u, letterSpacing: '0.06em', textTransform: 'uppercase', color: plan.style.text || '#fff' }}>
      {logoFile ? <Img src={staticFile(logoFile)} style={{ height: 4 * u, width: 'auto' }} /> : <span style={{ display: 'inline-block', width: 1.1 * u, height: 1.1 * u, borderRadius: '50%', background: plan.style.accent }} />}
      {!logoFile && <span>{name}</span>}
    </div>
  );
};
