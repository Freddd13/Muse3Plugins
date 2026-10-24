const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function load(name,scope={}){vm.createContext(scope);vm.runInContext(fs.readFileSync(path.join(__dirname,'..',name),'utf8').replace(/^\.(pragma|import).*$/gm,''),scope);return scope;}
const H=load('Harmony.js'),T=load('Timeline.js',{Harmony:H}),A=load('Analysis.js');
const region={start:0,end:1920,part:0,root:0,definition:0,bass:0,tonic:0,rootSpelling:'C',tonicSpelling:'C',chord:'C',degree:'I',notes:[]};
const chosen={...region,start:480,end:960,root:1,rootSpelling:'D♭',definition:3,bass:5,bassName:'F',chord:'D♭maj7/F',degree:'♭IImaj⁶₅'};
const hidden={...region,start:960,end:1440,root:-1,definition:-1,suppressed:true};
const original=JSON.stringify({region,chosen,hidden});
let edits=T.importEdits([region],[chosen,hidden]);assert.equal(edits.length,4);
assert.equal(T.atTick(edits,600,0).source,'manual');assert.equal(T.atTick(edits,600,0).chord,chosen.chord);assert(T.atTick(edits,1100,0).suppressed);
assert.equal(T.atTick(edits,1600,0).source,'imported');assert.equal(JSON.stringify({region,chosen,hidden}),original);
for(let iteration=0;iteration<5;++iteration){
 const visible=T.overlay([],edits),document=A.document([],'a'.repeat(64),{},visible,edits,[]),decoded=A.validate(JSON.parse(JSON.stringify(document)));
 edits=T.importEdits(decoded.regions,decoded.overrides);assert.equal(edits.length,4,'repeat export/import keeps a single copy of each range');
 assert(T.atTick(edits,1100,0).suppressed);assert.equal(T.atTick(edits,600,0).rootSpelling,'D♭');
}
assert.equal(T.overlay([],edits).length,3);assert.equal(edits.filter(r=>r.source!=='imported').length,2);
const tonalDocument=A.validate(A.document([],'b'.repeat(64),{schema:1,keyMode:1,manualKey:false,keyTonic:0}));
assert.equal(tonalDocument.configuration.keyMode,1,'legacy files retain their tonal interpretation');
const current={keyMode:0,keyTonic:0,manualKey:false,degreeMode:1,colors:{'1':'#112233'}};
const interpreted=A.interpretationConfig({...tonalDocument.configuration,colors:{'1':'#ffffff'}},current);
assert.equal(interpreted.keyMode,1);assert.equal(current.keyMode,0);assert.equal(interpreted.colors['1'],'#112233');
assert.throws(()=>A.interpretationConfig({manualKey:true},current));
console.log('Analysis round trip: imported ranges, manual priority, hidden ranges and repeated import passed');
