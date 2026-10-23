const fs=require("fs"),vm=require("vm"),assert=require("assert");
const ctx={};vm.createContext(ctx);vm.runInContext(fs.readFileSync("PerformanceExpression/Alignment.js","utf8"),ctx);
const notes=[60,62,64,65,67,69,71,72].map((pitch,i)=>({id:"s"+i,logicalId:"s"+i,pitch,tick:i*480,track:0,index:0,onSeconds:i*.5,velocity:80,velocityType:0,velocityRaw:0,velocityBase:80,bpm:120}));
const performance=notes.map((n,i)=>({id:"m"+i,pitch:n.pitch,seconds:i*.52,velocity:60+i*4}));
let reports=[];
function run(name,p,extra={},truth=null){
 const r=ctx.align(Object.assign({notes,performance:p,mode:"score"},extra));
 const correct=r.matches.filter(m=>m.midiId==="m"+m.scoreId.substr(1)).length;
 const high=r.matches.filter(m=>m.confidence>=.8&&!m.confirmed);
 const wrongHigh=high.filter(m=>m.midiId!=="m"+m.scoreId.substr(1)).length;
 assert.strictEqual(wrongHigh,0,name+" high-confidence wrong match");
 if(truth!==null)assert.strictEqual(correct,truth,name);
 reports.push({name,matches:r.matches.length,correct,coverage:correct/notes.length,pending:r.pending,wrongHigh});return r;
}
run("exact",performance,{},8);
run("missed-middle",performance.filter(n=>n.id!=="m3"),{},7);
run("extra-middle",performance.concat([{id:"extra",pitch:58,seconds:1.81,velocity:70}]),{},8);
let wrong=performance.map(n=>Object.assign({},n));wrong[3].pitch=66;let r=run("wrong-note",wrong,{},8);assert(r.matches.find(m=>m.scoreId==="s3").confidence<.8);
run("tap-any-pitch",performance.map(n=>Object.assign({},n,{pitch:40})),{mode:"tap"},8);
run("tap-missed-recovery",performance.filter(n=>n.id!=="m3").map(n=>Object.assign({},n,{pitch:40})),{mode:"tap",anchors:[{scoreId:"s4",midiId:"m4"}]},7);
run("manual-confirm",wrong,{links:[{scoreId:"s3",midiId:"m3"}]},8);
const prefix=Array.from({length:500},(_,i)=>({id:"prefix"+i,pitch:40+i%4,seconds:i*.5,velocity:50}));
const passage=performance.map(n=>Object.assign({},n,{seconds:n.seconds+260}));
let found=run("whole-midi-selected-passage",prefix.concat(passage).concat([{id:"tail",pitch:33,seconds:270,velocity:50}]),{},8);
assert(found.passage.from>=260&&found.passage.until<270);
r=run("manual-disconnect",performance,{links:[{scoreId:"s3",midiId:"m3",disabled:true}]},7);assert(r.missing.some(n=>n.id==="s3"));assert(r.extra.some(n=>n.id==="m3"));
assert.throws(()=>ctx.align({notes,performance,anchors:[{scoreId:"s2",midiId:"m4"},{scoreId:"s4",midiId:"m2"}]}));
let poly=notes.concat([Object.assign({},notes[2],{id:"s2b",logicalId:"s2b",track:4}),Object.assign({},notes[3],{id:"tie",logicalId:"s2",tieBack:true})]);
r=ctx.align({notes:poly,performance:performance.concat([{id:"m2b",pitch:64,seconds:1.043,velocity:78}])});assert(r.matches.some(m=>m.scoreId==="s2b"));assert(!r.matches.some(m=>m.scoreId==="tie"));
let protectedResult=ctx.align({notes:notes.map(n=>Object.assign({},n,{protected:n.id==="s3"})),performance});
let c=ctx.candidates({result:protectedResult,notes,revision:"1",scope:{start:0,end:3840},config:{strength:50,velocity:true,rubato:true,keepDuration:true}});
assert.strictEqual(c.velocity.length,7);assert(c.kept.some(n=>n.id==="s3"));assert.strictEqual(c.tempos.length,0); // Uniform time scaling vanishes when the original duration is retained.
c=ctx.candidates({result:protectedResult,notes,scope:{start:0,end:3840},config:{velocity:true,keepManual:false}});
assert.strictEqual(c.velocity.length,8);assert(c.velocity.find(n=>n.id==='s3').unlock);
c=ctx.candidates({result:protectedResult,config:{strength:0,velocity:true}});assert(c.velocity.every(n=>n.target===80));
const repeated=ctx.align({notes,performance:performance.concat(performance.map(n=>Object.assign({},n,{id:"second"+n.id,seconds:n.seconds+5}))),repeats:[{tick:0,end:3840,utick:0},{tick:0,end:3840,utick:3840}],occurrence:0});assert.strictEqual(repeated.matches.length,16);assert(repeated.matches.some(m=>m.scoreId==="s0@2"));
const cached=ctx.align({notes,performance,cacheKey:"stable"});const reused=ctx.align({notes,performance,cacheKey:"stable",previousKey:cached.cacheKey,segments:cached.segments,links:[{scoreId:"s3",midiId:"m3"}]});assert.strictEqual(reused.matches.length,8);assert.strictEqual(reused.segments[Object.keys(cached.segments)[0]],cached.segments[Object.keys(cached.segments)[0]]);
fs.mkdirSync("P1/out/expression",{recursive:true});fs.writeFileSync("P1/out/expression/alignment.json",JSON.stringify(reports,null,2));
console.log("Alignment truth fixtures, corrections, polyphony, tie and protected candidates passed.");

const expressive=performance.map((n,i)=>Object.assign({},n,{seconds:[0,.48,1.01,1.55,2.1,2.69,3.27,3.95][i]}));
let er=ctx.align({notes,performance:expressive});er.matches.forEach(m=>m.confirmed=true);
let rub=ctx.candidates({result:er,notes,scope:{start:0,end:3840},config:{velocity:false,rubato:true,keepDuration:true,strength:50}});
function writtenSeconds(points,end){let at=0,bpm=120,seconds=0;for(const p of points.slice().sort((a,b)=>a.tick-b.tick)){if(p.tick>end)break;seconds+=(p.tick-at)/480*60/bpm;at=p.tick;bpm=p.bpm;}return seconds+(end-at)/480*60/bpm;}
assert(Math.abs(writtenSeconds(rub.tempos,3840)-4)<1e-8);
let relNotes=notes.map(n=>Object.assign({},n,{onSeconds:n.onSeconds*2,scoreSeconds:n.onSeconds}));let rel=ctx.align({notes:relNotes,performance:expressive});rel.matches.forEach(m=>m.confirmed=true);let rc=ctx.candidates({result:rel,scope:{start:0,end:3840},config:{rubato:true,keepDuration:true}});assert.deepStrictEqual(JSON.parse(JSON.stringify(rc.tempos)),JSON.parse(JSON.stringify(rub.tempos)));
const eight=notes.map((n,i)=>Object.assign({},n,{tick:i*240}));assert.strictEqual(ctx.align({notes:eight,performance}).matches.length,8);
const triplet=notes.map((n,i)=>Object.assign({},n,{tick:i*160}));assert.strictEqual(ctx.align({notes:triplet,performance}).matches.length,8);
console.log("Written rubato duration, independent transport clock, compound subdivisions passed.");
