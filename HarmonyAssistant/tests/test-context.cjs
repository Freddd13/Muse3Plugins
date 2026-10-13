const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function read(name,context={}) {vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'..',name),'utf8').replace(/^\.(pragma|import).*$/gm,''),context);return context;}
const h=read('Harmony.js'),t=read('Timeline.js',{Harmony:h}),p=read('Preferences.js');
const tpc={0:14,2:16,4:18,5:13,7:15,9:17,10:12,11:19};
function notes(pitches,tick=0,end=1920) {return pitches.map((pitch,index)=>({pitch,tpc:tpc[pitch%12],tick,attackTick:tick,end,track:0,index}));}
function frame(tick,notes,pedal=[]) {return {tick,notes,scoreEnd:1920,keySignature:0,parts:[{startTrack:0,endTrack:8}],pedalWindows:pedal};}
let config=p.defaults();config.pedalMode=1;
for(const [pitches,chord,inversion] of [[[40,48,55],'C/E','第一转位'],[[43,48,52],'C/G','第二转位'],[[46,48,52,55],'C7/B♭','第三转位']]) {
 const result=t.build([frame(0,notes(pitches)),frame(1920,[])],config,0,[])[0];assert.equal(result.chord,chord);assert.equal(result.inversion,inversion);
}
const emptyBass=t.describe({root:0,definition:3},[],0,0,false,1);assert.equal(emptyBass.inversion,'低音未确定');
const spelled=t.describe({root:3,rootSpelling:'E♭',definition:0},notes([55,58]),0,0,false,1,false);assert.equal(spelled.chord,'E♭/G');
const imported={...frame(0,notes([60,64,67])),root:0,definition:0,chord:'C (my voicing)',degree:'I custom',imported:true};
const noChord={...imported,notes:[],root:-1,definition:-1,chord:'N.C.',degree:''};const noChordRegion=t.build([noChord,frame(1920,[])],config,0,[])[0];assert.equal(noChordRegion.chord,'N.C.');assert.equal(noChordRegion.inversion,'未指定和弦');
const importedRest={...imported,notes:[]};assert.equal(t.build([importedRest,frame(1920,[])],config,0,[])[0].chord,'C (my voicing)','explicit imported chord is retained at a rest');
const kept=t.build([imported,frame(1920,[])],config,0,[])[0];assert.equal(kept.chord,'C (my voicing)');assert.equal(kept.degree,'I custom');
const residue=notes([36,52,55],0,100).concat(notes([37],480,960));
assert.equal(h.detectWeighted(residue,{0:.12,4:.12,7:.12,1:1},null,0,false,480,{bass:residue[3]}).root,-1,'one fresh tone is not renamed from de-emphasized pedal residue');
assert.equal(h.roman(9,true,0,0,0),'III');assert.equal(h.roman(9,true,0,0,1),'♭III');assert.equal(h.roman(9,true,5,0,0),'VI');assert.equal(h.roman(9,true,7,0,0),'VII');assert.equal(h.roman(9,true,8,5,0),'♯vii°');
assert.equal(p.clean({...p.defaults(),degreeMode:0}).degreeMode,0);assert.equal(p.clean({...p.defaults(),degreeMode:1}).degreeMode,1);
const chord=notes([36,52,55]),pedal=[{start:0,end:1920,firstTrack:0,endTrack:8}];
const tied=t.build([frame(0,chord,pedal),frame(960,chord,pedal),frame(1920,[])],config,0,[]);assert.equal(tied.length,1,'no new attack, no new chord at an artificial boundary');
const old=notes([36,52,55]),fresh=notes([43,59,62],480,1920),melody=notes([76]);
const changed=t.build([frame(0,old.concat(melody),pedal),frame(480,old.concat(fresh,melody),pedal),frame(1920,[])],config,0,[]);assert.equal(changed[1].root,7);assert.equal(changed[1].harmonicBass,7);assert.equal(changed[1].bass,0,'actual held bass remains separately visible');
const ambiguous=h.detectWeighted(notes([48,52,55,57]),{0:1,4:1,7:1,9:1},null,0,false,0);assert(ambiguous.alternatives.some(a=>a.root===9 && a.definition===4),'C6 / Am7 ambiguity remains available');
const base=notes([36,52,55],0,1920).map(n=>({...n,track:4}));
const a=notes([69],0,120),b=notes([71],120,240),c=notes([72],240,480);
const passing=t.build([frame(0,base.concat(a)),frame(120,base.concat(b)),frame(240,base.concat(c)),frame(480,base),frame(1920,[])],config,0,[]);
assert.equal(t.atTick(passing,120,0).root,0);assert.equal(t.atTick(passing,120,0).definition,0,'short stepwise B is a passing tone, not a new Cmaj7 region');
config.pedalMode=0;const single=t.build([frame(0,chord,pedal),frame(480,chord.concat(fresh,melody),pedal),frame(1920,[])],config,0,[]);assert.equal(single.length,1,'single-chord pedal mode remains one region');
const bundle=t.workerBundle({harmony:fs.readFileSync(path.join(__dirname,'..','Harmony.js'),'utf8'),timeline:fs.readFileSync(path.join(__dirname,'..','Timeline.js'),'utf8')});
const worker=vm.runInNewContext(bundle,{input:{frames:[frame(0,notes([40,48,55])),frame(1920,[])],config,part:0}});assert.equal(worker.regions[0].chord,'C/E');assert.equal(worker.regions[0].inversion,'第一转位');
console.log('Chord context, spelling, inversions and both minor degree modes passed');
