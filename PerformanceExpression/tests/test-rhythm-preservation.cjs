const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function read(name,context={}){vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'..',name),'utf8'),context);return context;}
const rhythm=read('Rhythm.js',{Alignment:read('Alignment.js')});
function note(pitch,tick,duration,extra={}) {return {id:`${tick}:0:0`,pitch,writtenPitch:pitch,tpc1:14,tpc2:14,track:0,tick,attackTick:tick,end:tick+duration,logicalEnd:tick+duration,duration,velocity:80,...extra};}
function build(notes){return rhythm.build({data:{notes,scope:{start:0,end:1920,firstTrack:0,endTrack:1},meters:[{tick:0,end:1920}]},performance:[],settings:{track:0,quantum:120}});}
const cases=[
 ['打开草稿保留两音之间的休止',()=>{
   const draft=build([note(60,0,240),note(62,480,240)]);assert.equal(draft.errors.length,0);
   assert.equal(draft.rows[0].effectiveDuration,240);assert.equal(draft.rows[1].effectiveDuration,240);
   const rests=draft.voices[0].events.filter(e=>!e.pitches.length);assert(rests.some(e=>e.quarterTime.numerator/e.quarterTime.denominator===.5));
 }],
 ['最后一个延音使用完整时值',()=>{
   const draft=build([note(60,0,480,{logicalEnd:1920}),note(60,480,480,{tieBack:true,logicalEnd:1920})]);
   assert.equal(draft.errors.length,0);assert.equal(draft.rows.length,1);assert.equal(draft.rows[0].effectiveDuration,1920);
 }],
 ['修改力度继续保留原休止',()=>{
   const notes=[note(60,480,240),note(62,1440,240)];let draft=build(notes);draft.rows[0].velocity=100;draft.rows[0].velocityEdited=true;
   draft=rhythm.build({data:{notes,scope:{start:0,end:1920,firstTrack:0,endTrack:1},meters:[{tick:0,end:1920}]},rows:draft.rows,performance:[],settings:{track:0,quantum:120}});
   assert.equal(draft.errors.length,0);assert.equal(draft.rows[0].effectiveDuration,240);assert.equal(draft.rows[1].effectiveDuration,240);
   assert.equal(draft.voices[0].events[0].pitches.length,0);
   const sounding=draft.voices[0].events.filter(e=>e.pitches.length);
   assert.equal(sounding[0].pitches[0].velocity,100);assert(!Object.hasOwn(sounding[1].pitches[0],'velocity'));
 }],
 ['原谱三连音保留拍位和分组',()=>{
   const tuplet={ratio:'3/2',start:0,duration:480};
   const draft=build([note(60,0,160,{tuplet}),note(62,160,160,{tuplet}),note(64,320,160,{tuplet})]);
   assert.equal(draft.errors.length,0);assert.deepEqual(Array.from(draft.rows.map(n=>n.start)),[0,160,320]);
   assert.equal(draft.voices[0].tuplets.length,1);assert.equal(draft.voices[0].tuplets[0].actual,3);
 }],
 ['较短原音保留原长',()=>{
   const draft=build([note(60,0,60),note(62,240,60)]);assert.equal(draft.errors.length,0);
   assert.equal(draft.rows[0].effectiveDuration,60);assert.equal(draft.rows[1].effectiveDuration,60);
 }],
 ['同声部的长音继续保持，后来的音正常进入',()=>{
   const draft=build([note(60,0,480,{logicalEnd:960}),note(60,480,480,{tieBack:true,logicalEnd:960}),note(64,480,240)]);
   assert.equal(draft.errors.length,0);
   const sounding=draft.voices[0].events.filter(e=>e.pitches.length);
   const middle=sounding.find(e=>e.quarterTime.numerator/e.quarterTime.denominator===1);
   assert.deepEqual(Array.from(middle.pitches.map(p=>p.pitch)),[60,64]);
   assert(middle.pitches.find(p=>p.pitch===60).tieNext);assert(!middle.pitches.find(p=>p.pitch===64).tieNext);
   const last=sounding.find(e=>e.quarterTime.numerator/e.quarterTime.denominator===1.5);
   assert.deepEqual(Array.from(last.pitches.map(p=>p.pitch)),[60]);
 }],
 ['同一和弦里，各音保留自己的延长',()=>{
   const draft=build([note(60,0,240,{id:'0:0:0',logicalEnd:960}),note(64,0,240,{id:'0:0:1'}),note(60,240,720,{tieBack:true,logicalEnd:960})]);
   assert.equal(draft.errors.length,0);const events=draft.voices[0].events;
   assert.equal(events[0].pitches.length,2);assert(events[0].pitches[0].tieNext);assert(!events[0].pitches[1].tieNext);
   assert.deepEqual(Array.from(events[1].pitches.map(p=>p.pitch)),[60]);
 }]
];
let failures=0;for(const [name,run] of cases){try{run();console.log('PASS '+name);}catch(error){++failures;console.error('FAIL '+name+'\n'+error.message);}}
console.log(`${cases.length-failures} passed, ${failures} failed`);process.exitCode=failures?1:0;
