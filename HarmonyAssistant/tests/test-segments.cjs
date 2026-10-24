const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
function load(file,scope={}){vm.createContext(scope);vm.runInContext(fs.readFileSync(path.join(__dirname,'..',file),'utf8').replace(/^\.(pragma|import).*$/gm,''),scope);return scope;}
const H=load('Harmony.js'),T=load('Timeline.js',{Harmony:H}),P=load('Preferences.js'),data=JSON.parse(fs.readFileSync(path.join(__dirname,'segment-corpus.json'),'utf8'));
let checked=0;
for(const row of data.cases){
 const ticks=[0,row.end,...row.notes.flatMap(n=>[n.tick,n.end]),...row.pedals.flatMap(p=>[p.start,p.end])].filter(t=>t>=0&&t<=row.end).sort((a,b)=>a-b).filter((t,i,a)=>!i||t!==a[i-1]);
 const frames=ticks.map(tick=>{
  const pedal=row.pedals.filter(p=>p.start<=tick&&tick<p.end),byPitch={};
  for(const n of [...row.notes].sort((a,b)=>a.tick-b.tick))if(n.tick<=tick && (n.end>tick || pedal.some(p=>n.end>p.start)))byPitch[n.pitch]=n;
  return {tick,notes:Object.values(byPitch),parts:[{startTrack:0,endTrack:8}],pedalWindows:pedal,scoreEnd:row.end,keySignature:row.key,bar:1,beat:tick/240+1};
 });
 const config=P.defaults();config.pedalMode=1;
 const result=T.build(frames,config,0,[]).map(r=>({start:r.start,end:r.end,chord:r.chord,root:r.root,definition:r.definition,degree:r.degree}));
 try{assert.deepEqual(result,row.expected,row.name);}catch(e){console.log(row.name,JSON.stringify(result));throw e;}
 const state=T.createBuilder(frames,config,0);let steps=0;while(!T.step(state,1))assert(++steps<10000);
 assert.deepEqual(state.regions.map(r=>({start:r.start,end:r.end,chord:r.chord,root:r.root,definition:r.definition,degree:r.degree})),row.expected,row.name+'分批');
 ++checked;
}
console.log('Continuous harmony corpus passed: '+checked+' cases and incremental calculation');
