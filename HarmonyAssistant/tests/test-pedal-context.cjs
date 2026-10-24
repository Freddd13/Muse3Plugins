const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function load(name,scope={}){vm.createContext(scope);vm.runInContext(fs.readFileSync(path.join(__dirname,'..',name),'utf8').replace(/^\.(pragma|import).*$/gm,''),scope);return scope;}
const H=load('Harmony.js'),T=load('Timeline.js',{Harmony:H}),P=load('Preferences.js');
const tpcs=[14,21,16,23,18,13,20,15,22,17,24,19];
function group(pitches,tick,end,track=4){return pitches.map((pitch,index)=>({pitch,tpc:tpcs[pitch%12],tick,attackTick:tick,end,track,index}));}
function frame(tick,notes,pedal=[],key=0){return {tick,notes,keySignature:key,scoreEnd:1920,parts:[{startTrack:0,endTrack:8}],pedalWindows:pedal};}
const pedal=[{start:0,end:1920,firstTrack:0,endTrack:8}],C=group([36,52,55],0,480),G=group([43,59,62],480,1920);
const config=P.defaults();config.pedalMode=0;
const imported=[{...frame(0,C,pedal),imported:true,root:0,definition:0,chord:'C',degree:'I'},
 {...frame(480,G,pedal),imported:true,root:7,definition:0,chord:'G',degree:'V'}];
let result=T.build(imported,config,0,[]);
assert.equal(result.length,2,'explicit analysis keeps both harmonies within one pedal');
assert.deepEqual(result.map(r=>[r.start,r.end,r.chord,r.degree]),[[0,480,'C','I'],[480,1920,'G','V']]);
const held=group([36,52,55],0,1920);
result=T.build([frame(0,held,pedal),frame(960,held,pedal,1)],config,0,[]);
assert.deepEqual(result.map(r=>[r.start,r.end,r.chord,r.degree]),[[0,960,'C','I'],[960,1920,'C','IV']],'key change updates degree while keeping the chord');
result=T.build([frame(0,held,pedal),frame(960,held,pedal)],config,0,[]);assert.equal(result.length,1,'unchanged sustained chord remains a single region');
const arpeggio=[frame(0,group([36],0,240),pedal),frame(240,group([36],0,240).concat(group([52],240,480)),pedal),
 frame(480,group([36],0,240).concat(group([52],240,480),group([55],480,720)),pedal)];
result=T.build(arpeggio,config,0,[]);assert.equal(result.length,1);assert.equal(result[0].chord,'C');assert.equal(result[0].start,0);
result=T.build([frame(0,held,pedal),imported[1]],config,0,[]);assert.equal(result[1].source,'imported');assert.equal(result[1].start,480);
const manual={...imported[1],part:0,start:480,end:960,suppressed:false};
result=T.build([frame(0,held,pedal)],config,0,[manual]);assert.equal(T.atTick(result,600,0).source,'manual');assert.equal(T.atTick(result,600,0).chord,'G');assert.equal(T.atTick(result,1000,0).chord,'C');
console.log('Pedal context: imported boundaries, key change, arpeggio, sustain and manual priority passed');
