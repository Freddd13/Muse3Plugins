// Independent playback integration checks for expression tempo transfer.
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const rules=vm.createContext({});vm.runInContext(fs.readFileSync('PerformanceExpression/Alignment.js','utf8'),rules);
function bpmAt(events,tick){let bpm=120;for(const p of events.slice().sort((a,b)=>a.tick-b.tick))if(p.tick<=tick&&p.fixed!==false)bpm=p.bpm;return bpm;}
function secondsAt(events,tick){const points=events.filter(p=>p.tick<=tick).slice().sort((a,b)=>a.tick-b.tick);let at=0,bpm=120,time=0;for(const p of points){time+=(p.tick-at)/480*60/bpm+(p.pause||0);at=p.tick;if(p.fixed!==false)bpm=p.bpm;}return time+(tick-at)/480*60/bpm;}
function playedClock(base,tempos){const map=new Map(base.map(p=>[p.tick,{...p}]));for(const p of tempos)map.set(p.tick,{...map.get(p.tick),tick:p.tick,bpm:p.bpm,fixed:true});return [...map.values()].sort((a,b)=>a.tick-b.tick);}
function fixture(marker=1920){
 const base=[{tick:0,bpm:120},{tick:marker,bpm:80}];const pitches=[60,62,64,65,67,69,71,72],factors=[.8,1.2,.9,1.15,.85,1.25,1.1];let time=0;
 const notes=pitches.map((pitch,i)=>({id:'s'+i,logicalId:'s'+i,pitch,tick:i*480,track:0,index:0,measure:Math.floor(i/4)+1,beat:i%4+1,scoreSeconds:secondsAt(base,i*480),onSeconds:secondsAt(base,i*480),bpm:bpmAt(base,i*480),tempoProtected:i===0||i*480===marker,velocity:80,velocityType:0,velocityRaw:0,velocityBase:80}));
 const matches=notes.map((n,i)=>{if(i)time+=(n.scoreSeconds-notes[i-1].scoreSeconds)*factors[i-1];return {scoreId:n.id,midiId:'m'+i,tick:n.tick,track:0,index:0,pitch:n.pitch,seconds:time,velocity:96,confirmed:true,confidence:1,original:n};});
 const points=base.map(p=>({...p,seconds:secondsAt(base,p.tick)}));
 const tempoContext={start:0,end:3840,startSeconds:0,endSeconds:secondsAt(base,3840),points,protectedTicks:[0,marker],protectedRanges:[],restoreTicks:marker>0?[{tick:Math.floor((marker-1)/480)*480,bpm:bpmAt(base,marker-1)}]:[]};
 return {notes,result:{matches},base,tempoContext,scope:{start:0,end:3840,firstTrack:0,endTrack:4}};
}
for(const marker of [1920,1680]){
 const f=fixture(marker),candidate=rules.candidates({...f,config:{rubato:true,velocity:true,rubatoStrength:80,keepDuration:true}}),clock=playedClock(f.base,candidate.tempos);
 const duration=secondsAt(clock,3840)-secondsAt(clock,0),original=secondsAt(f.base,3840)-secondsAt(f.base,0);
 assert(Math.abs(duration-original)<1e-6,`marker at ${marker}: original ${original}s, written ${duration}s`);
 assert.equal(bpmAt(clock,marker),80);assert(candidate.tempos.every(p=>p.tick!==marker&&p.tick!==0));
 assert(candidate.tempos.some(p=>Math.abs(p.bpm-p.oldBpm)>.001));
 console.log('PASS protected marker at',marker,'duration',duration);
}
function contextFor(f){return {...f.tempoContext,scoreEnd:3840,endWritable:false,writableTicks:Array.from({length:9},(_,i)=>i*480)};}
for(const strength of [0,50,100]){
 const f=fixture(),candidate=rules.candidates({...f,tempoContext:contextFor(f),config:{velocity:true,rubato:true,rubatoStrength:strength,keepDuration:false}}),clock=playedClock(f.base,candidate.tempos);
 const m=f.result.matches,performed=m[7].seconds+(m[7].seconds-m[6].seconds),original=secondsAt(f.base,3840),expected=original*(1-strength/100)+performed*strength/100;
 assert(Math.abs(secondsAt(clock,3840)-expected)<1e-6);assert.equal(candidate.velocity.length,8);
 console.log('PASS performed duration at',strength,'percent');
}
for(const keep of [true,false]){
 const f=fixture(),candidate=rules.candidates({...f,tempoContext:contextFor(f),tempoRanges:[{start:480,end:960},{start:2400,end:2880}],config:{rubato:true,rubatoStrength:100,keepDuration:keep}}),clock=playedClock(f.base,candidate.tempos);
 for(const tick of [0,960,1920,2880,3360])assert(Math.abs(bpmAt(clock,tick)-bpmAt(f.base,tick))<1e-6,'tempo outside selected notes at '+tick);
 for(const [a,b] of [[1,2],[5,6]]){const expected=keep?f.notes[b].scoreSeconds-f.notes[a].scoreSeconds:f.result.matches[b].seconds-f.result.matches[a].seconds;assert(Math.abs(secondsAt(clock,b*480)-secondsAt(clock,a*480)-expected)<1e-6);}
 assert.equal(candidate.tempoScoped,true);if(keep)assert.equal(candidate.tempos.length,0);
 console.log('PASS two disjoint selected notes, keep duration',keep);
}
{
 const f=fixture(),candidate=rules.candidates({...f,tempoContext:contextFor(f),config:{rubato:true,velocity:true,rubatoStrength:80,keepDuration:true}}),clock=playedClock(f.base,candidate.tempos),applied={};
 candidate.tempoNodes.forEach(tick=>applied[tick]={bpm:bpmAt(clock,tick)});
 const nextContext={...contextFor(f),points:clock.map(p=>({...p,owned:candidate.tempos.some(v=>v.tick===p.tick)}))};
 const again=rules.candidates({...f,tempoContext:nextContext,appliedTempos:applied,config:{rubato:true,keepDuration:true}});assert.equal(again.tempos.length,0);
 console.log('PASS adopted tempo points stay applied');
}
{
 const f=fixture();f.result.matches[4].seconds=f.result.matches[3].seconds-.01;
 const c=rules.candidates({...f,config:{rubato:true,velocity:true}});assert.equal(c.velocity.length,8);assert.equal(c.tempos.length,0);assert(c.kept.some(p=>p.reason.includes('交叉')));
 console.log('PASS crossing performance times retain velocity use');
}
{
 const f=fixture(),pause=.6;f.base.splice(1,0,{tick:1440,bpm:120,pause,fixed:false});
 f.notes.forEach(n=>{n.scoreSeconds=secondsAt(f.base,n.tick);n.onSeconds=n.scoreSeconds;});
 f.result.matches.forEach(m=>{if(m.tick>=1440)m.seconds+=pause;});
 const context={...contextFor(f),points:f.base,restoreTicks:[{tick:960,bpm:120},{tick:1440,bpm:120}],protectedRanges:[{start:1920,end:2880,reason:'原有渐慢'}]};
 const c=rules.candidates({...f,tempoContext:context,config:{rubato:true,keepDuration:true}}),clock=playedClock(f.base,c.tempos);
 assert(Math.abs(secondsAt(clock,3840)-secondsAt(f.base,3840))<1e-6);
 assert(!c.tempos.some(p=>p.tick>=1920&&p.tick<2880));assert.equal(clock.find(p=>p.tick===1440).pause,pause);
 console.log('PASS pause and existing tempo curve retain written timing');
}
{
 const f=fixture(),context={...contextFor(f),protectedRanges:[{start:0,end:3840}]};
 const c=rules.candidates({...f,tempoContext:context,config:{rubato:true,keepDuration:true}});assert.equal(c.tempos.length,0);assert(c.kept.length>0);
 console.log('PASS fully protected passage retains original speed');
}
{
 const f=fixture(),context=contextFor(f),settings={rubato:true,keepDuration:true,previewTempo:{480:140}};
 const c=rules.candidates({...f,tempoContext:context,tempoRanges:[f.scope],config:settings}),clock=playedClock(f.base,c.tempos);
 assert.equal(bpmAt(clock,480),140);assert(Math.abs(secondsAt(clock,3840)-secondsAt(f.base,3840))<1e-6);
 console.log('PASS manually adjusted preview preserves duration and restoration');
}
module.exports={fixture,playedClock,secondsAt,bpmAt,rules};
