const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function load(name,scope={}){vm.createContext(scope);vm.runInContext(fs.readFileSync(path.join(__dirname,'..',name),'utf8').replace(/^\.(pragma|import).*$/gm,''),scope);return scope;}
const H=load('Harmony.js'),T=load('Timeline.js',{Harmony:H}),P=load('Preferences.js'),config=P.defaults();config.window=0;config.pedalMode=1;
const notes=(pitches,tick=0)=>pitches.map((pitch,index)=>({pitch,tpc:14,index,track:0,tick,attackTick:tick,end:tick+480}));
const frame=(tick,notes)=>({tick,notes,keySignature:0,scoreEnd:1920,parts:[{startTrack:0,endTrack:4}]});
const region=T.build([frame(0,notes([60,61,62])),frame(480,[])],config,0,[])[0];
assert(region,'unresolved polyphony retains a visible editing point');assert.equal(region.root,-1);assert.equal(region.chord,'?');assert.equal(region.start,0);assert.equal(region.end,480);
for(const pitches of [[],[60],[60,66]])assert.equal(T.build([frame(0,notes(pitches)),frame(480,[])],config,0,[]).length,0,'rests and unresolved single/double notes remain uncluttered');
const changed=T.build([frame(0,notes([60,61,62])),frame(480,notes([65,66,67],480)),frame(960,[])],config,0,[]);assert.equal(changed.length,2);assert.equal(changed[1].start,480);
console.log('Unresolved harmony: editing points, empty positions and distinct note groups passed');
