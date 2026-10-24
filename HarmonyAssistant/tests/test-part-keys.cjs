const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function load(name,scope={}){vm.createContext(scope);vm.runInContext(fs.readFileSync(path.join(__dirname,'..',name),'utf8').replace(/^\.(pragma|import).*$/gm,''),scope);return scope;}
const H=load('Harmony.js'),T=load('Timeline.js',{Harmony:H}),P=load('Preferences.js');
const notes=track=>[48,52,55].map((pitch,index)=>({pitch,tpc:[14,18,15][index],tick:0,attackTick:0,end:1920,track,index}));
const parts=[{startTrack:0,endTrack:4,keySignature:0},{startTrack:4,endTrack:8,keySignature:1}];
const frame={tick:0,keySignature:0,scoreEnd:1920,parts,notes:notes(0).concat(notes(4)),pedalWindows:[]};
const config=P.defaults();config.pedal=false;config.window=0;
const regions=T.build([frame],config,0,[]);
assert.deepEqual(regions.map(r=>[r.part,r.chord,r.degree,r.tonicSpelling]),[[0,'C','I','C'],[4,'C','IV','G']]);
config.manualKey=true;config.keyTonic=H.rootNames.indexOf('F');
assert.deepEqual(T.build([frame],config,0,[]).map(r=>r.degree),['V','V']);
const saved=T.validEdits([{start:0,end:1920,part:0,root:1,definition:0,tonic:11,rootSpelling:'C♯',tonicSpelling:'C♭',notes:[]}])[0];
assert.equal(saved.rootSpelling,'C♯');assert.equal(saved.tonicSpelling,'C♭');
const arpeggioNotes=[48,52,55].map((pitch,index)=>({pitch,tpc:[14,18,15][index],tick:index*240,attackTick:index*240,end:index<2?(index+1)*240:960,track:0,index:0}));
const arpeggioFrames=[0,240,480].map((tick,index)=>({tick,keySignature:0,scoreEnd:960,parts:[{startTrack:0,endTrack:4,keySignature:0}],notes:arpeggioNotes.slice(0,index+1),pedalWindows:[]}));
config.manualKey=false;config.window=2;
const aggregate=T.atTick(T.build(arpeggioFrames,config,0,[]),480,0);
assert(aggregate && aggregate.root===0 && aggregate.definition===0,'one-beat arpeggio window keeps the C major interpretation');
console.log('Part keys: independent signatures and explicit common key passed');
