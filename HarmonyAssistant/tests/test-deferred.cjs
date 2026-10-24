const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function source(file){return fs.readFileSync(path.join(__dirname,'..',file),'utf8');}
function load(file,scope={}){vm.createContext(scope);vm.runInContext(source(file).replace(/^\.(pragma|import).*$/gm,''),scope);return scope;}
const H=load('Harmony.js'),T=load('Timeline.js',{Harmony:H}),P=load('Preferences.js'),cases=JSON.parse(fs.readFileSync(path.join(__dirname,'theory-corpus.json'),'utf8')).cases;
let checked=0;
for(const row of cases){
 const notes=row.pitches.map((pitch,index)=>({pitch,tpc:row.tpc[index],tick:0,attackTick:0,end:960,index,track:0}));
 const config=P.defaults();config.pedalMode=1;config.keyMode=row.minor?1:0;if(row.degreeMode!==undefined)config.degreeMode=row.degreeMode;
 const frame={tick:0,notes,parts:[{startTrack:0,endTrack:4}],scoreEnd:960,keySignature:row.key,deferredDescription:true};
 const direct=T.describe(H.detect(row.pitches,notes),notes,0,T.tonicAt(frame,config),!!row.minor,config.degreeMode,row.key<0,T.tonicNameAt(frame,config));
 for(const packed of [false,true]){
  const program=T.workerBundle({harmony:source('Harmony.js'),timeline:source('Timeline.js'),packed});
  let result=vm.runInNewContext(program,{input:{frames:JSON.parse(JSON.stringify([frame])),config,part:0}});
  if(packed)result=JSON.parse(result.payload);
  for(const field of ['root','definition','chord','degree','rootSpelling','tonicSpelling','chromatic'])assert.equal(result.descriptions[0][field],direct[field],row.name+' '+field);
  assert.equal(result.descriptions[0].tick,0);assert(result.regions.length);
 }
 const fallback=JSON.parse(JSON.stringify(frame));T.build([fallback],config,0,[]);
 assert.equal(fallback.chord,direct.chord);assert.equal(fallback.degree,direct.degree);assert(!Object.hasOwn(fallback,'deferredDescription'));
 ++checked;
}
console.log('Deferred frame descriptions passed: '+checked+' cases, worker values, packed data and incremental fallback');
