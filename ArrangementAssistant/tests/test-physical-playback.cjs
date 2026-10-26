const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function load(file,context={}){vm.createContext(context);vm.runInContext(fs.readFileSync(path.resolve(__dirname,file),'utf8').replace(/^\.(pragma|import).*$/gm,''),context);return context;}
const Harmony=load('../../HarmonyAssistant/Harmony.js'),Timeline=load('../../HarmonyAssistant/Timeline.js',{Harmony}),Playback=load('../Playback.js');
let passed=0,failed=0;
function test(name,body){try{body();passed++;console.log('PASS '+name);}catch(error){failed++;console.error('FAIL '+name+'\n'+error.stack);}}
function note(pitch,tick=0,end=960,track=4,index=pitch){return {id:`${tick}:${track}:${index}`,logicalId:`${tick}:${track}:${index}`,tick,attackTick:tick,logicalEnd:end,end,track,index,pitch,writtenPitch:pitch,tpc:14,partId:0,piano:true,play:true,onSeconds:tick/960,endSeconds:end/960};}
function on(n,utick=n.tick,extra={}){return {...n,utick,seconds:utick/960,kind:'on',channel:0,partId:0,velocity:80,discard:0,...extra};}
function off(n,utick,extra={}){return {...on(n,utick,extra),kind:'off',velocity:0};}
function pedal(utick,value,channel=0){return {kind:'pedal',utick,seconds:utick/960,partId:0,channel,value};}
function run(notes,events,options={}){
    const calls=[],PianoHands={playbackFieldsVersion:options.apiVersion===undefined?1:options.apiVersion,analyse:(notes,pedals,options)=>{calls.push(JSON.parse(JSON.stringify({notes,pedals,options})));return {sides:[],possible:true};}};
    const Rules=load('../Rules.js',{Harmony,Timeline,Playback,PianoHands}),config=Rules.defaults();config.harmony=false;config.counterpoint=false;config.roles={'4':{hand:'left'},'0':{hand:'right'}};
    if(options.configure)options.configure(config);
    const scope=options.scope||{start:0,end:1920,firstTrack:0,endTrack:8},meters=[{tick:0,end:1920,measure:1,denominator:4}];
    const data={scope,meters,notes,rests:[],pedals:[],hands:[],keys:[],harmonies:[]};
    if(events)data.playback={scope,meters,notes,events,ranges:options.ranges||[{start:0,end:1920,scoreStart:0,scoreEnd:1920,startSeconds:0,endSeconds:2,offset:0,occurrence:1}],endTick:options.endTick||1920,endSeconds:(options.endTick||1920)/960};
    const before=JSON.stringify(data),state=Rules.run(data,config);assert.equal(JSON.stringify(data),before,'analysis preserves input');return {calls,state,Rules};
}
test('written fallback excludes a note whose playback is disabled',()=>{
    const a=note(36),b=note(72);a.play=false;const {calls}=run([a,b]);assert(calls.length);assert(calls.every(c=>c.notes.every(n=>n.id!==a.id)));
});
test('an early manual release frees the old key before the next group',()=>{
    const a=note(36),b=note(72,480,960,4,1);const {calls}=run([a,b],[on(a),off(a,120),on(b),off(b,960)]);
    const next=calls.find(c=>c.options.tick===480);assert(next);assert.deepEqual(next.notes.map(n=>n.pitch),[72]);
});
test('a manually extended key still occupies the hand past its written end',()=>{
    const a=note(36,0,240),b=note(72,480,960,4,1);const {calls}=run([a,b],[on(a),on(b),off(b,960),off(a,1440)]);
    const next=calls.find(c=>c.options.tick===480);assert(next);assert.deepEqual(next.notes.map(n=>n.pitch).sort((a,b)=>a-b),[36,72]);assert.equal(next.notes.find(n=>n.pitch===36).physicalEnd,1440);
});
test('pedal residue sounds without occupying a finger',()=>{
    const a=note(36),b=note(72,480,960,4,1);const {calls}=run([a,b],[on(a),pedal(10,127),off(a,120),on(b),off(b,960),pedal(1440,0)]);
    const next=calls.find(c=>c.options.tick===480);assert(next);assert.deepEqual(next.notes.map(n=>n.pitch),[72]);
});
test('lifting the pedal leaves a still-held key in the hand',()=>{
    const a=note(36),b=note(72,480,960,4,1);const {calls}=run([a,b],[on(a),pedal(10,127),pedal(240,0),on(b),off(a,800),off(b,960)]);
    const next=calls.find(c=>c.options.tick===480);assert(next);assert.equal(next.notes.length,2);
});
test('muted MIDI sources do not appear as played keys',()=>{
    const a=note(36),b=note(72);const {calls}=run([a,b],[on(a,0,{muted:true}),on(b),off(a,800),off(b,960)]);assert(calls.every(c=>c.notes.every(n=>n.pitch!==36)));
});
test('doubling keeps both written references on one physical interval',()=>{
    const a=note(60,0,960,0),b=note(60,0,480,4);const {calls}=run([a,b],[on(a),on(b,0,{discard:2}),off(b,480,{discard:1}),off(a,960)]);
    const first=calls.find(c=>c.options.tick===0);assert(first);assert.equal(first.notes.length,2);assert(first.notes.every(n=>n.physicalEnd===960));
});
test('early and late attacks use real time while keeping written identity',()=>{
    const a=note(60,0,960),b=note(67,480,960,4,1);const {calls}=run([a,b],[on(a,120),on(b,720),off(a,1000),off(b,1100)]);
    const first=calls.find(c=>c.options.tick===120);assert(first);assert.equal(first.options.seconds,.125);assert.equal(first.notes[0].tick,0);assert.equal(first.notes[0].attackTick,0);assert.equal(first.notes[0].physicalStart,120);
    const next=calls.find(c=>c.options.tick===720);assert(next);assert.equal(next.options.seconds,.75);assert.equal(next.notes.find(n=>n.pitch===67).tick,480);
});
test('repeated appearances have separate physical identities',()=>{
    const a=note(60),ranges=[{start:0,end:1920,scoreStart:0,scoreEnd:1920,startSeconds:0,endSeconds:2,offset:0,occurrence:1},{start:1920,end:3840,scoreStart:0,scoreEnd:1920,startSeconds:2,endSeconds:4,offset:1920,occurrence:2}];
    const {calls}=run([a],[on(a),off(a,960),on(a,1920,{occurrence:2,offset:1920}),off(a,2880,{occurrence:2,offset:1920})],{ranges,endTick:3840});
    const first=calls.find(c=>c.options.tick===0),second=calls.find(c=>c.options.tick===1920);assert(first&&second);assert.equal(first.notes[0].id,second.notes[0].id);assert.notEqual(first.notes[0].analysisId,second.notes[0].analysisId);
});
test('played pedals carry their channel and exact boundaries',()=>{
    const a=note(36),b=note(72,480,960,4,1);const {calls}=run([a,b],[on(a),pedal(10,127),on(b),off(a,800),off(b,960),pedal(1440,0)]);
    const next=calls.find(c=>c.options.tick===480);assert(next);assert(next.pedals.some(p=>p.channelKey==='0:0'&&p.tick===10&&p.end===1440&&p.supported));
});
test('continuous pedal values keep their cautious release setting',()=>{
    const a=note(36),b=note(72,480,960,4,1);const {calls}=run([a,b],[on(a),pedal(10,127),pedal(240,80),on(b),off(a,800),off(b,960),pedal(1440,0)]);
    const next=calls.find(c=>c.options.tick===480);assert(next);assert(next.pedals.length);assert(next.pedals.every(p=>p.supported===false));
});
test('lookahead follows the actual next group and released old notes',()=>{
    const a=note(36),b=note(72,480,960,4,1),d=note(76,960,1440,4,2);const {calls}=run([a,b,d],[on(a),off(a,120),on(b,600),off(b,850),on(d,1100),off(d,1500)]);
    const first=calls.find(c=>c.options.tick===0);assert(first);assert(first.options.lookahead.length>=2);assert.equal(first.options.lookahead[0].tick,600);assert.equal(first.options.lookahead[0].seconds,.625);assert.deepEqual(first.options.lookahead[0].notes.map(n=>n.pitch),[72]);
});
test('selection starts with the keys already held before its boundary',()=>{
    const a=note(36),b=note(72,480,960,4,1),scope={start:480,end:960,firstTrack:0,endTrack:8},ranges=[{start:480,end:960,scoreStart:480,scoreEnd:960,startSeconds:.5,endSeconds:1,offset:0,occurrence:1}];
    const {calls}=run([a,b],[on(a),on(b,600),off(a,800),off(b,960)],{scope,ranges});
    const start=calls.find(c=>c.options.tick===480);assert(start);assert.deepEqual(start.notes.map(n=>n.pitch),[36]);assert.equal(start.options.lookahead[0].tick,600);
});
test('another piano does not consume this piano’s two lookahead groups',()=>{
    const a=note(36),next=note(60,480,800,4,1),later=note(64,960,1440,4,2);
    const other=[0,120,240].map((tick,index)=>({...note(72+index,tick,tick+120,12,index),partId:8}));
    const events=[on(a),...other.flatMap(n=>[on(n,n.tick,{partId:8,channel:1}),off(n,n.end,{partId:8,channel:1})]),on(next),off(next,800),on(later),off(a,1200),off(later,1500)].sort((a,b)=>a.utick-b.utick);
    const {calls}=run([a,next,later,...other],events,{scope:{start:0,end:1920,firstTrack:0,endTrack:16},configure:c=>{c.roles['12']={hand:'left'};}});
    const first=calls.find(c=>c.options.part===0&&c.options.tick===0);assert(first);assert.deepEqual(first.options.lookahead.map(f=>f.tick),[480,960]);
});
test('older hosts use the actual-key fallback for played material',()=>{
    const a=note(36),b=note(72,480,960,4,1);
    const shortened=run([a,b],[on(a),off(a,120),on(b),off(b,960)],{apiVersion:0});assert.equal(shortened.calls.length,0);assert(!shortened.state.issues.some(i=>i.code==='span-left'&&i.tick===480));
    const held=run([a,b],[on(a),on(b),off(a,1200),off(b,960)].sort((a,b)=>a.utick-b.utick),{apiVersion:0});assert.equal(held.calls.length,0);assert(held.state.issues.some(i=>i.code==='span-left'&&i.tick===480));
});
console.log(`${passed} physical-playback checks passed; ${failed} failed`);if(failed)process.exitCode=1;
