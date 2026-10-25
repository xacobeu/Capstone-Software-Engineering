// Opt-in Protocol v2 input-size extension; no change to default definitions.
import fs from 'node:fs';
import path from 'node:path';
import { cases } from './common.mjs';
export const EXTENSION_ID = 'v2-context-size-extension';
export const sizeCases = [65536,262144,1048576,4194304,16777216].map(bytes=>({id:`size-ext-${String(bytes).padStart(8,'0')}`,count:4,bytes}));
export const selectCases = args => args.includes('--context-size-extension') ? sizeCases : cases;
export function extensionOutput(base, stage) {
 if(!['probe','pilot','full'].includes(stage))throw Error('invalid extension stage');
 fs.mkdirSync(base,{recursive:true});
 return fs.mkdtempSync(path.join(base,`${stage}-${new Date().toISOString().replaceAll(':','-')}-`));
}
// Additional parent-side acceptance checks, all outside the refresh timer.
// The unchanged preload verifies disk hashes, complete trimmed payloads and isolation.
export function validateBoundary(events,pid,manifest,receipt) {
 if(events.length!==2||events[0].event!=='local-ready'||events[1].event!=='validated')throw Error('invalid readiness/validation sequence');
 const [r,v]=events;
 if(r.pid!==pid||v.pid!==pid)throw Error('incorrect CLI PID');
 if(!r.initialized||!r.chatInitialized||!Number.isFinite(receipt))throw Error('unverified readiness');
 if(r.networkAttempts.length||r.modelCalls.length||r.subprocesses.some(p=>!p.allowed))throw Error('external attempt');
 const paths=r.loadedPaths;
 if(new Set(paths).size!==4||paths.length!==4||JSON.stringify([...paths].sort())!==JSON.stringify(manifest.files.map(f=>f.path).sort()))throw Error('loaded-path mismatch');
 if(v.actualCount!==4||v.actualBytes!==manifest.bytes)throw Error('fixture totals mismatch');
 const f=r.refresh;
 if(![r.initStart,f.startMs,f.endMs,r.readyMs,f.elapsedMs,r.peakRSSMiB].every(Number.isFinite)||!(r.initStart<=f.startMs&&f.startMs<=f.endMs&&f.endMs<=r.readyMs)||Math.abs(f.endMs-f.startMs-f.elapsedMs)>1e-6||r.peakRSSMiB<=0)throw Error('invalid measurement ordering/value');
 return true;
}
