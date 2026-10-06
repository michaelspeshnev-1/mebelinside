// Выбирает установщик под вашу систему: Windows -> setup.ps1, иначе setup.sh
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const d = path.dirname(fileURLToPath(import.meta.url));
const r = process.platform === 'win32'
  ? spawnSync('powershell', ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', path.join(d, 'setup.ps1')], { stdio: 'inherit' })
  : spawnSync('bash', [path.join(d, 'setup.sh'), ...process.argv.slice(2)], { stdio: 'inherit' });
process.exit(r.status ?? 1);
