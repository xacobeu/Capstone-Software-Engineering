import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
export const SHA = '85aca163f6c73ac6ce380b5447359146b8adcae4';
export const VERSION = 1;
export const SEED = 250102023;
export const sourceFiles = ['context/memoryContextManager.ts', 'utils/memoryDiscovery.ts', 'utils/memoryImportProcessor.ts', 'utils/paths.ts', 'utils/debugLogger.ts', 'utils/events.ts', 'utils/errors.ts', 'utils/googleErrors.ts', 'tools/memoryTool.ts'];
export const hash = (x) => createHash('sha256').update(x).digest('hex');
export function rng(seed = SEED) { let x = seed >>> 0; return () => { x = (Math.imul(x, 1664525) + 1013904223) >>> 0; return x / 4294967296; }; }
export function shuffle(items, random) { const a = [...items]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
export const cases = [{ id: 'zero', count: 0, bytes: 0 }, ...[1, 4, 16, 32].map(count => ({ id: `count-${count}`, count, bytes: 65536 })), ...[4096, 16384, 65536, 262144].map(bytes => ({ id: `bytes-${bytes}`, count: 4, bytes }))];
export function fixture(base, scenario) {
  const root = join(base, scenario.id); mkdirSync(join(root, '.git'), { recursive: true });
  const dirs = [root]; for (let i = 1; i <= 32; i++) { dirs.push(join(dirs.at(-1), `d${String(i).padStart(2, '0')}`)); mkdirSync(dirs.at(-1)); }
  const files = []; const random = rng(SEED); let remainder = scenario.bytes;
  for (let i = 0; i < scenario.count; i++) {
    const bytes = Math.floor(scenario.bytes / scenario.count) + (i < scenario.bytes % scenario.count ? 1 : 0);
    const token = `fixture-${scenario.id}-${i}-${Math.floor(random()*1e9)}\n`;
    const content = (token + 'abcdefghijklmnopqrstuvwxyz0123456789\n'.repeat(Math.ceil(bytes / 37))).slice(0, bytes);
    const path = join(dirs[i], 'GEMINI.md'); writeFileSync(path, content); files.push({ path, bytes, sha256: hash(content) }); remainder -= bytes;
  }
  if (remainder !== 0) throw Error('fixture byte allocation');
  return { ...scenario, root, workspace: dirs.at(-1), depth: 32, files, seed: SEED, importFormat: 'tree', markers: ['.git'], trusted: true };
}
export function verifyLoaded(paths, manifest, content) {
  const expected = manifest.files.map(f => f.path).sort(); const actual = [...paths].sort();
  if (JSON.stringify(actual) !== JSON.stringify(expected)) throw Error('loaded-path mismatch');
  let bytes = 0;
  for (const f of manifest.files) { const b = readFileSync(f.path); if (b.length !== f.bytes || hash(b) !== f.sha256) throw Error('fixture checksum/size mismatch'); if (!content.includes(b.toString().trim())) throw Error('loaded-content mismatch'); bytes += b.length; }
  if (bytes !== manifest.bytes || paths.size !== manifest.count) throw Error('manifest totals mismatch');
  return { actualCount: actual.length, actualBytes: bytes };
}
export function rssMiB(kib) { if (!Number.isFinite(kib) || kib < 0) throw Error('invalid KiB'); return kib / 1024; }
export function quantile(a, p) { if (!a.length) return null; const s=[...a].sort((x,y)=>x-y); const k=(s.length-1)*p; const lo=Math.floor(k); return s[lo]+(s[Math.ceil(k)]-s[lo])*(k-lo); }
export function stats(a) {
  if (!a.length) return { n: 0 };
  const random=rng(SEED); const boot=[]; for(let b=0;b<2000;b++) boot.push(quantile(a.map(()=>a[Math.floor(random()*a.length)]),.5));
  const median=quantile(a,.5); const mean=a.reduce((x,y)=>x+y,0)/a.length;
  return { n:a.length,median,p90:quantile(a,.9),iqr:quantile(a,.75)-quantile(a,.25),mad:quantile(a.map(x=>Math.abs(x-median)),.5),min:Math.min(...a),max:Math.max(...a),mean,sd:a.length>1?Math.sqrt(a.reduce((s,x)=>s+(x-mean)**2,0)/(a.length-1)):null,medianCI95:[quantile(boot,.025),quantile(boot,.975)] };
}
