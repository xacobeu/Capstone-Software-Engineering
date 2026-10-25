// Protocol v2: benchmark-only in-memory observation of an unchanged built CLI.
import fs from 'node:fs';
import net from 'node:net';
import tls from 'node:tls';
import http from 'node:http';
import https from 'node:https';
import http2 from 'node:http2';
import dns from 'node:dns';
import dgram from 'node:dgram';
import cp from 'node:child_process';
import { registerHooks, syncBuiltinESMExports } from 'node:module';
import { performance } from 'node:perf_hooks';
import { fileURLToPath } from 'node:url';
import { verifyLoaded, rssMiB } from './common.mjs';
const manifest=JSON.parse(fs.readFileSync(process.env.CAPSTONE_MANIFEST,'utf8'))[Number(process.env.CAPSTONE_INDEX)];
const mode=process.env.CAPSTONE_OBSERVER??'minimal';
const state={networkAttempts:[],subprocesses:[],modelCalls:[],refreshes:[],patched:[]};
const emit=x=>fs.writeSync(3,JSON.stringify(x)+'\n');
const deny=name=>(...args)=>{state.networkAttempts.push({name,stack:new Error('blocked').stack});throw Error(`CAPSTONE_NETWORK_DENIED ${name}`);};
net.Socket.prototype.connect=deny('net.Socket.connect');tls.connect=deny('tls.connect');
for(const m of [http,https])for(const k of ['request','get'])m[k]=deny(k);
http2.connect=deny('http2.connect');
for(const k of ['lookup','resolve','resolve4','resolve6','reverse']){dns[k]=deny(`dns.${k}`);dns.promises[k]=deny(`dns.promises.${k}`);}
dgram.Socket.prototype.send=deny('dgram.send');dgram.Socket.prototype.connect=deny('dgram.connect');const originalFetch=globalThis.fetch;globalThis.fetch=(input,...args)=>{if(typeof input==='string'&&input.startsWith('data:application/octet-stream;base64,'))return originalFetch(input,...args);let target='unknown';try{const u=new URL(typeof input==='string'?input:input.url);target=u.origin+u.pathname;}catch{}return deny('fetch '+target)(input,...args);};
for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork']){
 const original=cp[k];cp[k]=function(...args){
  const command=String(args[0]);const argv=Array.isArray(args[1])?args[1]:[];
  // Read-only Git queries may run during workspace detection; forbid shell commands.
  const allowed=(['exec','execFile','spawn'].includes(k)&&command==='system_profiler -xml -detailLevel full SPDisplaysDataType')||['spawn','spawnSync','execFile','execFileSync'].includes(k)&&/^(\/usr\/bin\/)?git$/.test(command)&&['rev-parse','status','ls-files','check-ignore','config','log'].includes(argv[0])&&(!argv.includes('--global'))&&(!argv.includes('--system'))&&(!argv.includes('--add'));
  state.subprocesses.push({method:k,command,args:argv,allowed});if(!allowed)throw Error(`CAPSTONE_SUBPROCESS_DENIED ${command}`);return original.apply(this,args);
 };
}
syncBuiltinESMExports();
// Store a non-enumerable observation object; only appended wrappers reference it.
Object.defineProperty(globalThis,'__capstone',{value:{
 async refresh(manager,original,args){
  const before={rssMiB:process.memoryUsage().rss/1048576,peakRSSMiB:rssMiB(process.resourceUsage().maxRSS)};
  const start=performance.now();if(mode==='extra'){process.memoryUsage();process.resourceUsage();}
  const value=await original.apply(manager,args);if(mode==='extra'){process.memoryUsage();process.resourceUsage();}
  const end=performance.now();state.refreshes.push({startMs:start,endMs:end,elapsedMs:end-start,peakRSSMiB:rssMiB(process.resourceUsage().maxRSS),baseline:before});return value;
 },
 model(name){state.modelCalls.push(name);throw Error(`CAPSTONE_MODEL_CALL_DENIED ${name}`);},
 async ready(config,original,args){
  const initStart=performance.now();const value=await original.apply(config,args);const readyMs=performance.now();
  const peakRSSMiB=rssMiB(process.resourceUsage().maxRSS);const memory=process.memoryUsage();
  if(!config.isInitialized()||!config.getGeminiClient().isInitialized())throw Error('Config/chat not initialized');
  if(state.refreshes.length!==1)throw Error('Expected one integrated refresh');
  if(state.networkAttempts.length||state.modelCalls.length||state.subprocesses.some(p=>!p.allowed))throw Error('Unexpected external operation attempted');
  const manager=config.getMemoryContextManager();
  const phases=performance.getEntriesByType('measure').map(x=>({name:x.name,startMs:x.startTime,durationMs:x.duration}));
  emit({event:'local-ready',pid:process.pid,ppid:process.ppid,readyMs,initStart,peakRSSMiB,heapUsedMiB:memory.heapUsed/1048576,externalMiB:memory.external/1048576,arrayBuffersMiB:memory.arrayBuffers/1048576,refresh:state.refreshes[0],phases,networkAttempts:state.networkAttempts,modelCalls:state.modelCalls,subprocesses:state.subprocesses,patched:state.patched,initialized:true,chatInitialized:true,loadedPaths:[...manager.getLoadedPaths()]});
  // Assertions occur after milestone/peak capture; they can invalidate a sample.
  const validation=verifyLoaded(manager.getLoadedPaths(),manifest,manager.getEnvironmentMemory());
  if(!config.isTrustedFolder())throw Error('Workspace not trusted');
  if(config.getExtensions().length)throw Error('Unexpected extensions');if(config.getTelemetryEnabled()||config.getUsageStatisticsEnabled()||config.getIdeMode()||Object.keys(config.getMcpServers()??{}).length)throw Error('Isolation settings not applied');
  emit({event:'validated',pid:process.pid,...validation});process.exit(0);return value;
 }
}});
registerHooks({load(url,context,next){
 const result=next(url,context);if(!url.startsWith('file:'))return result;
 const file=fileURLToPath(url);let suffix='';
 if(file.endsWith('/packages/core/dist/src/context/memoryContextManager.js'))suffix=`\n{ const original=MemoryContextManager.prototype.refresh;MemoryContextManager.prototype.refresh=function(...args){return globalThis.__capstone.refresh(this,original,args);}; }`;
 if(file.endsWith('/packages/core/dist/src/config/config.js'))suffix=`\n{ const original=Config.prototype.initialize;Config.prototype.initialize=function(...args){return globalThis.__capstone.ready(this,original,args);}; }`;
 if(file.endsWith('/packages/core/dist/src/core/fakeContentGenerator.js'))suffix=`\nfor(const name of ['generateContent','generateContentStream','countTokens','embedContent']){FakeContentGenerator.prototype[name]=function(){return globalThis.__capstone.model(name);};}`;
 if(!suffix)return result;state.patched.push(file);return {...result,source:String(result.source)+suffix};
}});
process.on('uncaughtExceptionMonitor',error=>{try{emit({event:'failure',error:error.stack,...state});}catch{}});
process.on('exit',code=>{if(code!==0){try{emit({event:'exit-failure',code,...state});}catch{}}});
