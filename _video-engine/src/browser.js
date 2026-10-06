// Поиск браузера для Remotion. Порядок: переменная окружения -> уже скачанный Remotion -> Playwright -> системный Chrome.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { ROOT } from './paths.js';

function firstExisting(list) {
  return list.find((p) => p && fs.existsSync(p) && fs.statSync(p).isFile()) || null;
}

function globDirs(base, prefix) {
  try {
    return fs.readdirSync(base).filter((d) => d.startsWith(prefix)).sort().reverse().map((d) => path.join(base, d));
  } catch {
    return [];
  }
}

export function findBrowser() {
  const env = process.env.REMOTION_BROWSER || process.env.BROWSER_EXECUTABLE;
  if (env) {
    return fs.existsSync(env) ? { path: env, source: 'переменная окружения REMOTION_BROWSER' } : null;
  }
  // Браузер, который Remotion скачал сам
  const own = globDirs(path.join(ROOT, 'node_modules', '.remotion'), 'chrome-headless-shell')
    .flatMap((d) => [path.join(d, 'headless_shell'), path.join(d, 'chrome-headless-shell'), ...globDirs(d, 'chrome-headless-shell').map((x) => path.join(x, 'chrome-headless-shell'))]);
  const a = firstExisting(own);
  if (a) return { path: a, source: 'скачан Remotion' };

  // Playwright (может быть установлен заранее)
  const pwBases = [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(os.homedir(), '.cache', 'ms-playwright'), '/opt/pw-browsers'].filter(Boolean);
  for (const base of pwBases) {
    const shells = globDirs(base, 'chromium_headless_shell').map((d) => path.join(d, 'chrome-linux', 'headless_shell'));
    const p = firstExisting(shells);
    if (p) return { path: p, source: 'Playwright headless shell' };
  }
  const system = [
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  ];
  const s = firstExisting(system);
  if (s) return { path: s, source: 'Chrome/Chromium в системе' };
  return null;
}
