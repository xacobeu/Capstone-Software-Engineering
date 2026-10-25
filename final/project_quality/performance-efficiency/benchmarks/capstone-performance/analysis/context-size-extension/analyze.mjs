// Derive extension tables/comparisons from a completed full run; never edit raw input.
import fs from 'node:fs';
import path from 'node:path';
import {quantile,rng,SEED,stats} from '../../src/common.mjs';
const [input,output]=process.argv.slice(2);
if(!input||!output)throw Error('usage: node analyze.mjs FULL_RUN NEW_ANALYSIS_DIR');
fs.mkdirSync(output,{recursive:false});
const summaries=JSON.parse(fs.readFileSync(path.join(input,'summary.json'),'utf8'));
const rows=fs.readFileSync(path.join(input,'raw.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
const measured=rows.filter(r=>r.stage==='measured');
if(measured.length!==150||measured.some(r=>r.status!=='ok'))throw Error('incomplete/failed full data; explicitly revise analysis before use');
const ids=summaries.map(s=>s.scenario),blocks=[...new Set(measured.map(r=>r.block))].sort((a,b)=>a-b);
const values=blocks.map(b=>ids.map(id=>{const r=measured.filter(r=>r.block===b&&r.scenario===id);if(r.length!==1)throw Error('not complete blocks');return r[0].contextMs;}));
const pairs=[[0,1],[1,2],[2,3],[3,4],[0,4]];
const random=rng(SEED),boots=pairs.map(()=>({difference:[],ratio:[]}));
for(let b=0;b<2000;b++){
 const sampled=values.map(()=>values[Math.floor(random()*values.length)]);
 const medians=ids.map((_,i)=>quantile(sampled.map(v=>v[i]),.5));
 pairs.forEach(([a,c],i)=>{boots[i].difference.push(medians[c]-medians[a]);boots[i].ratio.push(medians[c]/medians[a]);});
}
const comparisons=pairs.map(([a,b],i)=>{const from=summaries[a],to=summaries[b],x=from.contextMs.median,y=to.contextMs.median;return {from:from.bytes,to:to.bytes,differenceMs:y-x,percent:100*(y/x-1),differenceCI95:[quantile(boots[i].difference,.025),quantile(boots[i].difference,.975)],ratio:y/x,ratioCI95:[quantile(boots[i].ratio,.025),quantile(boots[i].ratio,.975)]};});
const numeric=summaries.map(s=>({scenario:s.scenario,count:s.count,bytes:s.bytes,KiB:s.bytes/1024,MiB:s.bytes/1048576,...s.contextMs,startupMedianMs:s.spawnToReadyMs.median,RSSMedianMiB:s.peakRSSMiB.median}));
fs.writeFileSync(path.join(output,'table.json'),JSON.stringify(numeric,null,2));
fs.writeFileSync(path.join(output,'comparisons.json'),JSON.stringify(comparisons,null,2));
const cols=['bytes','KiB','MiB','count','n','median','p90','iqr','mad','min','max','mean','sd','ciLow','ciHigh','startupMedianMs','RSSMedianMiB'];
fs.writeFileSync(path.join(output,'table.csv'),[cols.join(','),...numeric.map(r=>cols.map(c=>c==='ciLow'?r.medianCI95[0]:c==='ciHigh'?r.medianCI95[1]:r[c]).join(','))].join('\n')+'\n');
const f=x=>x.toFixed(3);
const md=['| Input | Files | n | Median ms | p90 ms | IQR ms | Median 95% CI ms | Startup median ms | RSS median MiB |','|---|---:|---:|---:|---:|---:|---|---:|---:|',...numeric.map(r=>`| ${r.KiB<1024?r.KiB+' KiB':r.MiB+' MiB'} | ${r.count} | ${r.n} | ${f(r.median)} | ${f(r.p90)} | ${f(r.iqr)} | ${r.medianCI95.map(f).join('–')} | ${f(r.startupMedianMs)} | ${f(r.RSSMedianMiB)} |`),'','| Comparison (KiB) | Difference ms | Change % | Difference 95% CI ms | Median ratio 95% CI |','|---|---:|---:|---|---|',...comparisons.map(c=>`| ${c.from/1024} → ${c.to/1024} | ${f(c.differenceMs)} | ${f(c.percent)} | ${c.differenceCI95.map(f).join('–')} | ${c.ratioCI95.map(f).join('–')} |`)];
fs.writeFileSync(path.join(output,'tables.md'),md.join('\n')+'\n');
fs.writeFileSync(path.join(output,'analysis-manifest.json'),JSON.stringify({input:path.resolve(input),seed:SEED,resamples:2000,method:'joint complete-block bootstrap; difference and ratio of medians',monotonicMedians:numeric.every((r,i)=>!i||r.median>=numeric[i-1].median),AAcontext:Object.fromEntries(ids.map(id=>[id,{even:stats(measured.filter(r=>r.scenario===id&&r.block%2===0).map(r=>r.contextMs)),odd:stats(measured.filter(r=>r.scenario===id&&r.block%2).map(r=>r.contextMs))}]))},null,2));
console.log(md.join('\n'));
