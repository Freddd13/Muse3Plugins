const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function read(file,scope={}){vm.createContext(scope);vm.runInContext(fs.readFileSync(path.join(__dirname,'..',file),'utf8').replace(/^\.(pragma|import).*$/gm,''),scope);return scope;}
const h=read('Harmony.js'),t=read('Timeline.js',{Harmony:h}),p=read('Preferences.js');
const corpus=JSON.parse(fs.readFileSync(path.join(__dirname,'theory-corpus.json'),'utf8'));
let checked=0;
for(const row of corpus.cases){
 const notes=row.pitches.map((pitch,i)=>({tick:0,attackTick:0,end:960,track:0,index:i,pitch,tpc:row.tpc[i]}));
 const config=p.defaults();config.pedalMode=1;config.keyMode=row.minor?1:0;if(row.degreeMode!==undefined)config.degreeMode=row.degreeMode;
 const frame={tick:0,keySignature:row.key,notes,scoreEnd:960,parts:[{startTrack:0,endTrack:4}]};
 let result;
 if(row.specified)result=t.describe({root:row.root,definition:row.definition},notes,0,t.tonicAt(frame,config),!!row.minor,config.degreeMode,row.key<0,t.tonicNameAt(frame,config));
 else {
  result=t.build([frame],config,0,[])[0];
  const instant=t.describe(h.detect(row.pitches,notes),notes,0,t.tonicAt(frame,config),!!row.minor,config.degreeMode,row.key<0,t.tonicNameAt(frame,config));
  assert.equal(instant.chord,row.chord,row.name+'即时名称');assert.equal(instant.degree,row.degree,row.name+'即时级数');
 }
 assert(result,row.name);assert.equal(result.chord,row.chord,row.name);assert.equal(result.degree,row.degree,row.name);
 assert.equal(result.root,row.root,row.name);assert.equal(result.definition,row.definition,row.name);++checked;
}
// Older readers can omit pitch spelling; their pitch-only calls remain available.
assert.equal(h.detect([47,51,54,57]).root,11);
assert.equal(h.roman(0,false,3,0,1),'♭III');
assert.equal(h.roman(0,false,3,0,1,undefined,undefined,'D♯','C'),'♯II');
console.log('Hand-checked theory corpus passed: '+checked+' cases, instant and region results');
