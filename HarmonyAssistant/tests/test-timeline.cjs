const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function read(name,context={}) {vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'..',name),'utf8').replace(/^\.(pragma|import).*$/gm,''),context);return context;}
const h=read('Harmony.js'),t=read('Timeline.js',{Harmony:h}),p=read('Preferences.js'),a=read('Analysis.js');
function notes(pitches,start,end,track=4){return pitches.map((pitch,index)=>({tick:start,attackTick:start,end,track,index,pitch,tpc:({0:14,2:16,4:18,5:13,7:15,9:17,11:19})[pitch%12]||14}));}
const c=notes([36,52,55],0,3840),melody=notes([74],480,600,0);
function frame(tick,ns,pedal=true){return {tick,bar:Math.floor(tick/1920)+1,beat:tick/480+1,notes:ns,keySignature:0,scoreEnd:4320,parts:[{startTrack:0,endTrack:8}],pedalWindows:pedal?[{start:0,end:3840,firstTrack:0,endTrack:8}]:[]};}
const frames=[frame(0,c),frame(480,c.concat(melody)),frame(600,c.concat(melody)),frame(1920,c),frame(3840,[],false),frame(4320,[],false)];
let config=p.defaults(),regions=t.build(frames,config,0,[]);
assert.equal(regions.length,1,'one region for one pedal across bars');assert.equal(regions[0].root,0);assert.equal(regions[0].definition,0);assert.equal(regions[0].end,3840);assert.equal(regions[0].degree,'I');
const inverted=notes([40,48,55],0,960);
regions=t.build([frame(0,inverted,false),frame(960,[],false)],config,0,[]);
assert.equal(regions[0].chord,'C/E');assert.equal(regions[0].degree,'I');
config.pedalMode=1;
const old=notes([36,52,55],0,480),g=notes([43,59,62],480,960),sustained=notes([76],0,960,0);
regions=t.build([frame(0,old.concat(sustained)),frame(480,old.concat(g,sustained)),frame(960,[],false)],config,0,[]);
assert.equal(regions[0].root,0);assert.equal(regions[1].root,7,'new accompaniment dominates expired pedal bass');
assert.equal(t.atTick(regions,480,0).root,7);assert.equal(t.atTick(regions,960,0),null);
const heldOld=notes([36,52,55],0,960);
let sustainedRegions=t.build([frame(0,heldOld),frame(480,heldOld.concat(g,sustained)),frame(960,[],false)],config,0,[]);
assert.equal(sustainedRegions[1].root,7,'fresh accompaniment can change under held old notes');
const extensions=notes([59,62,69],480,960,0);
const extended=t.build([frame(0,heldOld,false),frame(480,heldOld.concat(extensions),false),frame(960,[],false)],config,0,[]);
assert.equal(extended[1].root,0,'upper extensions retain the held bass harmony');
assert.equal(extended[1].definition,23,'upper extensions form Cmaj13 rather than E7sus4/C');
let manual=JSON.parse(JSON.stringify(regions[0]));manual.start=240;manual.end=720;manual.root=9;manual.definition=1;manual.chord='Am';manual.degree='vi';
let edits=t.validEdits([manual]);let overridden=t.overlay(regions,edits);
assert.equal(t.atTick(overridden,300,0).source,'manual');assert.equal(t.atTick(overridden,720,0).root,7);
assert.equal(t.atTick(overridden,239,0).root,0);
manual.suppressed=true;assert.equal(t.atTick(t.overlay(regions,[manual]),480,0),null);
const restored=t.restore(edits,360,480,0);assert.equal(restored.length,2);assert.equal(restored[0].end,360);assert.equal(restored[1].start,480);
assert.throws(()=>t.validEdits([{...manual,end:manual.start}]));
const other=regions.map(r=>({...r,part:8}));overridden=t.overlay(regions.concat(other).sort((a,b)=>a.start-b.start||a.part-b.part),edits);
assert.equal(t.atTick(overridden,300,8).source,'auto','other part unaffected');
const doc=a.document([{tick:0,bar:1,beat:1,root:0,definition:0,notes:c,chord:'C',degree:'I'}],'a'.repeat(64),config,regions,edits);
assert.equal(a.validate(JSON.parse(JSON.stringify(doc))).overrides.length,1);doc.schema=1;assert.equal(a.validate(doc).overrides.length,0);
const long=[];for(let i=0;i<10000;i++)long.push(frame(i*480,notes(i%2?[43,59,62]:[36,52,55],i*480,(i+1)*480),false));
long.forEach(f=>f.scoreEnd=4800000);
const begin=performance.now();const result=t.build(long,config,0,[]);assert.equal(result.length,10000);
console.log('Timeline checks passed; 10000 frames '+(performance.now()-begin).toFixed(1)+' ms');
