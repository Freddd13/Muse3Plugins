const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function read(file,context={}) {vm.createContext(context);vm.runInContext(fs.readFileSync(path.resolve(__dirname,file),'utf8').replace(/^\.(pragma|import).*$/gm,''),context);return context;}
const h=read('../../HarmonyAssistant/Harmony.js'),t=read('../../HarmonyAssistant/Timeline.js',{Harmony:h}),r=read('../Rules.js',{Harmony:h,Timeline:t});
let passed=0;
function test(name,body){body();passed++;console.log('PASS '+name);}
function note(pitch,tick=0,end=960,track=0,tpc){return {id:`${tick}:${track}:${pitch}`,pitch,tick,attackTick:tick,end,logicalEnd:end,track,index:0,tpc:tpc===undefined?({0:14,1:21,2:16,3:11,4:18,5:13,6:20,7:15,8:10,9:17,10:12,11:19})[pitch%12]:tpc,measure:1,beat:1+tick/480,onSeconds:tick/960,endSeconds:end/960};}
function data(notes,pedals=[]){return {notes,pedals,hands:[],harmonies:[],meters:[{tick:0,end:7680,measure:1,denominator:4}],scope:{start:0,end:7680,firstTrack:0,endTrack:8}};}
function check(notes,config=r.defaults(),pedals=[]){return r.run(data(notes,pedals),config).issues;}
function codes(issues){return issues.map(i=>i.code);}
test('read-only same-pitch voices retained',()=>{let d=data([note(60,0,480,0),note(60,0,480,4)]),before=JSON.stringify(d),state=r.run(d,r.defaults());assert.equal(state.roles.length,2);assert.equal(JSON.stringify(d),before);});
test('spelled pure fifth to diminished fifth is not parallel',()=>{let ns=[note(60,0,480,4),note(67,0,480,0),note(62,480,960,4),note(68,480,960,0,10)];assert(!codes(check(ns)).includes('parallel-5'));});
test('parallel fifth in either track order',()=>{let ns=[note(60,0,480,4),note(67,0,480,0),note(62,480,960,4),note(69,480,960,0)];assert(codes(check(ns)).includes('parallel-5'));});
test('contrary motion does not create parallels',()=>{let ns=[note(60,0,480,4),note(67,0,480,0),note(58,480,960,4),note(69,480,960,0)];assert(!codes(check(ns)).some(c=>/^parallel/.test(c)));});
test('polyphonic automatic voice is uncertain',()=>{let state=r.run(data([note(60),note(64),note(67)]),r.defaults());assert(state.roles[0].uncertain);assert(!state.roles[0].independent);});
test('doubled voice explicitly disabled',()=>{let c=r.defaults();c.roles={'4':{independent:false}};let ns=[note(60,0,480,4),note(72,0,480,0),note(62,480,960,4),note(74,480,960,0)];assert(!codes(check(ns,c)).includes('parallel-8'));});
test('passing nonchord tone not called a color error',()=>{let c=r.defaults();c.chords=[{start:0,end:2000,root:0,definition:0,source:'局部指定'}];assert(!codes(check([note(64,0,480),note(66,480,960),note(67,960,1440)],c)).includes('chord-color'));});
test('suspension resolves by step',()=>{let c=r.defaults();c.chords=[{start:480,end:2000,root:0,definition:0,source:'局部指定'}];assert(!codes(check([note(71,0,960),note(72,960,1440)],c)).includes('chord-color'));});
test('extended chord tensions do not become automatic errors',()=>{let c=r.defaults();c.chords=[{start:0,end:2000,root:0,definition:22,source:'局部指定'}];assert(!codes(check([note(60),note(64),note(70),note(74),note(81)],c)).includes('chord-color'));});
test('user chord sustained semitone conflict requires review',()=>{let c=r.defaults();c.chords=[{start:0,end:2000,root:0,definition:0,source:'局部指定'}];assert(codes(check([note(61,0,1440)],c)).includes('chord-color'));});
test('ambiguity suppresses definite chord warnings',()=>{let c=r.defaults();let s=r.create(data([note(61)]),c,[{start:0,end:2000,part:0,root:0,definition:0,source:'导入',alternatives:[{root:1}]}]);while(!r.step(s,20)){}assert(!codes(s.issues).includes('chord-color'));});
test('white endpoints allow major tenth',()=>{assert(!codes(check([note(60),note(76)])).includes('span-right'));assert(codes(check([note(61),note(77)])).includes('span-right'));});
test('major ninth is comfortable',()=>{assert(!codes(check([note(60),note(74)])).includes('comfort-right'));});
test('equal span different transition context',()=>{let stationary=[note(60,0,120),note(74,0,120),note(60,120,240),note(74,120,240)];let moving=[note(60,0,120),note(74,0,120),note(84,120,240),note(98,120,240)];assert(!codes(check(stationary)).includes('transition-right'));assert(codes(check(moving)).includes('transition-right'));});
test('pedal release changes span explanation',()=>{let ns=[note(60),note(79)],plain=check(ns),under=check(ns,r.defaults(),[{tick:0,end:1500,firstTrack:0,endTrack:8}]);assert.equal(plain.find(i=>i.code==='span-right').severity,'需核查');assert.equal(under.find(i=>i.code==='span-right').severity,'注意');});
test('six different keys produce burden but unison does not',()=>{assert(codes(check([60,62,64,65,67,69].map(p=>note(p)))).includes('keys-right'));assert(!codes(check(Array.from({length:6},()=>note(60)))).includes('keys-right'));});
test('tie across bar appears once logically',()=>{let n=note(60,0,3840);let continuation={...n,tick:1920,tieBack:true,id:'1920:0:0'};let s=r.run(data([n,continuation]),r.defaults());assert.equal(s.byTick[0].length,1);});
test('unpaired native hand ranges need correction',()=>{let d=data([note(60),note(79)]);d.hands=[{tick:0,track:0,index:-1,left:true,bracket:false}];let s=r.run(d,r.defaults());assert(codes(s.issues).includes('span-left'));});
test('ignored issue remains absent',()=>{let ns=[note(60),note(79)],c=r.defaults(),first=check(ns,c);c.ignored=[first.find(i=>i.code==='span-right').id];assert(!codes(check(ns,c)).includes('span-right'));});
test('one pedal keeps one stable chord across bar',()=>{let ns=[note(36,0,480,4),note(52,0,480,4),note(55,0,480,4),note(74,1920,2400,0)];let s=r.run(data(ns,[{tick:0,end:3840,firstTrack:0,endTrack:8}]),r.defaults());assert.equal(s.regions.length,1);assert.equal(s.regions[0].root,0);});
test('automatic octave doubling not claimed independent',()=>{let ns=[note(60,0,480,4),note(72,0,480,0),note(62,480,960,4),note(74,480,960,0)];assert(!codes(check(ns)).includes('parallel-8'));});
test('worker bundle uses the exact shared modules',()=>{const source=r.workerBundle({harmony:fs.readFileSync(path.resolve(__dirname,'../../HarmonyAssistant/Harmony.js'),'utf8'),timeline:fs.readFileSync(path.resolve(__dirname,'../../HarmonyAssistant/Timeline.js'),'utf8'),rules:fs.readFileSync(path.resolve(__dirname,'../Rules.js'),'utf8')});let output=vm.runInNewContext(source,{input:{data:data([note(60),note(79)]),config:r.defaults(),imported:[]}});assert(codes(output.issues).includes('span-right'));});
test('conflicting hand symbols remain uncertain, not an impossible span',()=>{let d=data([note(60),note(79)]);d.hands=[{tick:0,track:0,index:-1,left:true},{tick:0,track:0,index:-1,left:false}];let c=codes(r.run(d,r.defaults()).issues);assert(c.includes('hand-uncertain'));assert(!c.includes('span-left')&&!c.includes('span-right'));});
test('unpaired bracket applies to its onset and not later notes',()=>{let d=data([note(60,0,480),note(79,0,480),note(60,480,960),note(79,480,960)]);d.hands=[{tick:0,track:0,index:-1,left:true,bracket:true}];let issues=r.run(d,r.defaults()).issues;assert(issues.some(i=>i.code==='span-left'&&i.tick===0));assert(issues.some(i=>i.code==='span-right'&&i.tick===480));assert(!codes(issues).includes('hand-uncertain'));});
test('glyph and drawn bracket carry the same hand range',()=>{let d=data([note(60,0,480),note(79,480,960),note(64,960,1440)]);d.hands=[{tick:0,track:0,index:-1,left:true,end:false,bracket:false},{tick:960,track:0,index:-1,left:true,end:true,bracket:false}];let state=r.run(d,r.defaults());assert.equal(r.handFor(state,d.notes[1],480).hand,'left');d.hands.forEach(m=>m.bracket=true);state=r.run(d,r.defaults());assert.equal(r.handFor(state,d.notes[1],480).hand,'left');});
test('single note mark does not assign its whole chord',()=>{let d=data([{...note(60),index:0},{...note(79),index:1}]);d.hands=[{tick:0,track:0,index:0,left:true,bracket:true}];let state=r.run(d,r.defaults());assert.equal(r.handFor(state,d.notes[0],0).hand,'left');assert.equal(r.handFor(state,d.notes[1],0).hand,'right');});
test('Jazz defaults and explicit parallel rule override',()=>{let ns=[note(60,0,480,4),note(67,0,480,0),note(62,480,960,4),note(69,480,960,0)],c=r.defaults();c.style=2;assert(!codes(check(ns,c)).includes('parallel-5'));c.ruleOverrides.parallel=true;assert(codes(check(ns,c)).includes('parallel-5'));});
test('logical tie uses the origin index even when chord ordering changes',()=>{let n=note(60,0,3840);n.attackIndex=1;n.index=1;let continuation={...n,tick:1920,index:0,tieBack:true,id:'1920:0:0'};let s=r.run(data([n,continuation]),r.defaults());assert.equal(s.byTick[0].length,1);});
test('leading-tone guidance requires an explicitly confirmed tonic',()=>{let ns=[note(71,0,480),note(67,480,960)],c=r.defaults();assert(!codes(check(ns,c)).includes('resolution'));c.tonic=0;assert(codes(check(ns,c)).includes('resolution'));});
test('hand correction alone does not turn doubling into counterpoint',()=>{let ns=[note(60,0,480,4),note(72,0,480,0),note(62,480,960,4),note(74,480,960,0)],c=r.defaults();c.roles={'4':{hand:'left'}};assert(!codes(check(ns,c)).includes('parallel-8'));});
test('pedal catches an already held note when it goes down',()=>{let ns=[note(36,0,240,4),note(37,480,1200,4)];assert(!codes(check(ns)).includes('low-cluster'));const issues=check(ns,r.defaults(),[{tick:120,end:1500,firstTrack:0,endTrack:8}]);assert(codes(issues).includes('low-cluster'));});
test('pedal residue does not become an extra held finger',()=>{let ns=[note(36,0,240,4),note(72,480,960,4)];const issues=check(ns,r.defaults(),[{tick:120,end:1500,firstTrack:0,endTrack:8}]);assert(!issues.some(i=>i.tick===480&&i.code==='span-left'));});
test('standalone hand end identifies its attached note only',()=>{let d=data([note(60,0,480),note(79,480,960)]);d.hands=[{tick:0,track:0,index:-1,left:true,end:true}];let state=r.run(d,r.defaults());assert.equal(r.handFor(state,d.notes[0],0).hand,'left');assert.equal(r.handFor(state,d.notes[1],480).hand,'right');});
test('range indexing is independent of input ordering',()=>{let d=data([note(60,0,480),note(79,480,960),note(64,960,1440)]);d.hands=[{tick:960,track:0,index:-1,left:true,end:true},{tick:0,track:0,index:-1,left:true,end:false}];let state=r.run(d,r.defaults());assert.equal(r.handFor(state,d.notes[1],480).hand,'left');});
test('each piano is checked separately and its upper staff suggests right hand',()=>{let calls=[];const native=read('../Rules.js',{Harmony:h,Timeline:t,PianoHands:{analyse:(notes,pedals,options)=>{calls.push({notes,options});return {sides:[],possible:true};}}});let d=data([{...note(72,0,480,0),partId:0,piano:true},{...note(72,0,480,8),partId:8,piano:true},{...note(40,0,480,16),partId:16,piano:false}]);d.scope.endTrack=24;let state=native.run(d,native.defaults());assert(calls.some(c=>c.options.part===0));assert(calls.some(c=>c.options.part===8));assert(!calls.some(c=>c.options.part===16));assert(calls.every(c=>c.notes.every(n=>n.partId===c.options.part)));assert.equal(state.roles.find(role=>role.track===8).hand,'right');});
test('overlap is detected with bass in either track order',()=>{for(const [low,high] of [[0,4],[4,0]]){let ns=[note(60,0,480,low),note(67,0,480,high),note(68,480,960,low),note(72,480,960,high)];assert(codes(check(ns)).includes('overlap'));}});
test('broken chord is suggested separately from an independent line',()=>{let ns=[48,52,55,60,55,52,48,52].map((pitch,i)=>note(pitch,i*240,(i+1)*240,4)),c=r.defaults(),state=r.run(data(ns),c);assert(state.roles[0].uncertain);assert(!state.roles[0].independent);c.roles={'4':{independent:true}};state=r.run(data(ns),c);assert(state.roles[0].independent);assert(!state.roles[0].uncertain);});
test('opposite perfect fifths are a separate strict-style hint',()=>{let ns=[note(60,0,480,4),note(67,0,480,0),note(50,480,960,4),note(69,480,960,0)],c=r.defaults();assert(!codes(check(ns,c)).includes('opposite-perfect-5'));c.style=1;assert(codes(check(ns,c)).includes('opposite-perfect-5'));});
function harmonicFrame(notes,candidates){let state=r.create(data(notes),r.defaults());state.regions=[{start:0,end:1920,part:0,root:0,definition:0,source:'auto',alternatives:candidates||[]}];r.harmonic(state,{tick:0,notes});return state.issues;}
test('automatic harmony reports the two sustained rubbing tones',()=>{const issues=harmonicFrame([note(60),note(64),note(67),note(73)]);const found=issues.find(i=>i.code==='auto-chord-color');assert(found);assert(found.notes.some(n=>n.pitch===60));assert(found.notes.some(n=>n.pitch===73));assert(found.basis.includes('C'));});
test('a shared clash can be reviewed across complete alternatives',()=>{const issues=harmonicFrame([note(60),note(64),note(67),note(73)],[{root:9,definition:1}]);assert(codes(issues).includes('auto-chord-color'));});
test('a tone supported by another interpretation has no common clash',()=>{const issues=harmonicFrame([note(60),note(64),note(67),note(73)],[{root:1,definition:0}]);assert(!codes(issues).includes('auto-chord-color'));});
test('short automatic dissonance is left to its musical context',()=>{assert(!codes(harmonicFrame([note(60),note(64),note(67),note(73,0,120)])).includes('auto-chord-color'));});
test('automatic harmony needs an audible chord tone for the finding',()=>{assert(!codes(harmonicFrame([note(73)])).includes('auto-chord-color'));});
test('low interval chart uses the actual distance and lower-note boundary',()=>{
 for(const [distance,limit] of Object.entries(r.lowIntervalLimits)){
  assert(!codes(check([note(limit),note(limit+Number(distance))])).includes('low-cluster'),`at ${distance}`);
  assert(codes(check([note(limit-1),note(limit-1+Number(distance))])).includes('low-cluster'),`below ${distance}`);
 }
});
test('low octave and unison have no low interval limit',()=>{assert(!codes(check([note(24),note(36)])).includes('low-cluster'));assert(!codes(check([note(24,0,960,0),note(24,0,960,4)])).includes('low-cluster'));});
test('compound intervals keep their own chart boundary',()=>{assert(!codes(check([note(40),note(54)])).includes('low-cluster'));assert(codes(check([note(38),note(52)])).includes('low-cluster'));});
test('each piano has its own low voicing',()=>{assert(!codes(check([{...note(28),partId:0},{...note(29),partId:8}])).includes('low-cluster'));});
test('personal low interval references can be changed',()=>{let c=r.defaults();c.lowIntervalLimits['2']=40;assert(!codes(check([note(42),note(44)],c)).includes('low-cluster'));});
test('certain attacks are checked while another hand remains uncertain',()=>{
 const native=read('../Rules.js',{Harmony:h,Timeline:t,PianoHands:{analyse:()=>({sides:[],possible:false,uncertain:true})}});
 let c=native.defaults();c.roles={'0':{hand:'right'}};let s=native.run(data([note(60),note(84),note(40,0,960,4)]),c);
 assert(s.issues.some(i=>i.code==='span-right'));
});

test('chosen melodic lines participate in counterpoint inside chords',()=>{
 let c=r.defaults();c.roles={'0':{role:'melody',line:'top'},'4':{role:'bass',line:'bottom'}};
 let ns=[note(64,0,480,0),note(67,0,480,0),note(60,0,480,4),note(62,0,480,4),note(66,480,960,0),note(69,480,960,0),note(62,480,960,4),note(64,480,960,4)];
 const state=r.run(data(ns),c);
 assert(state.roles.every(role=>role.independent),'the chosen lines must be checked');
 assert(codes(state.issues).includes('parallel-5'));
 c.roles['4'].independent=false;
 assert(!codes(check(ns,c)).includes('parallel-5'),'an explicit doubling choice remains in force');
});
test('one low physical interval has one explanation across doubled voices',()=>{
 const ns=[note(36,0,960,0),note(37,0,960,0),note(36,0,960,4),note(37,0,960,4)];
 const issue=check(ns).find(i=>i.code==='low-cluster');assert(issue);
 assert.equal((issue.basis.match(/小二度/g)||[]).length,1);
 assert.equal(issue.notes.length,4,'all score notes remain available for highlighting');
});

test('enharmonic augmented sevenths are not written octaves',()=>{
 const c=r.defaults();c.roles={'0':{role:'melody'},'4':{role:'bass'}};
 const ns=[note(60,0,480,4),note(72,0,480,0,26),note(62,480,960,4),note(74,480,960,0,28)];
 assert.equal(r.perfect(ns[0],ns[1]),0);assert(!codes(check(ns,c)).includes('parallel-8'));
});
console.log(`${passed} rule tests passed`);
