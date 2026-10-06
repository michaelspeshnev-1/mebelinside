// Запуск внешних программ с понятными ошибками.
import { spawn } from 'node:child_process';
import { toolMissing } from './errors.js';

/**
 * Запускает программу. Не бросает ошибку при ненулевом коде выхода —
 * вызывающий сам решает, что это значит. Бросает только если программы нет.
 */
export function run(cmd, args = [], { cwd, env, timeoutMs = 0, onStderr } = {}) {
  return new Promise((resolve, reject) => {
    let child;
    try {
      child = spawn(cmd, args, { cwd, env: { ...process.env, ...env }, stdio: ['ignore', 'pipe', 'pipe'] });
    } catch (e) {
      return reject(e);
    }
    let stdout = '';
    let stderr = '';
    let timedOut = false;
    const timer = timeoutMs
      ? setTimeout(() => {
          timedOut = true;
          child.kill('SIGKILL');
        }, timeoutMs)
      : null;
    child.stdout.on('data', (d) => (stdout += d));
    child.stderr.on('data', (d) => {
      stderr += d;
      if (onStderr) onStderr(String(d));
    });
    child.on('error', (e) => {
      if (timer) clearTimeout(timer);
      if (e.code === 'ENOENT') reject(toolMissing(cmd.split('/').pop()));
      else reject(e);
    });
    child.on('close', (code) => {
      if (timer) clearTimeout(timer);
      resolve({ code: timedOut ? -1 : code, stdout, stderr, timedOut });
    });
  });
}
