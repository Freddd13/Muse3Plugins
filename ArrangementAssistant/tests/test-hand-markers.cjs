const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function load(file,context={}){vm.createContext(context);vm.runInContext(fs.readFileSync(path.resolve(__dirname,file),'utf8').replace(/^\.(pragma|import).*$/gm,''),context);return context;}
const Harmony=load('../../HarmonyAssistant/Harmony.js'),Timeline=load('../../HarmonyAssistant/Timeline.js',{Harmony});
const Rules=load('../Rules.js',{Harmony,Timeline});
function note(track=0,index=0,graceIndex){const n={id:`0:${track}:${graceIndex===undefined?'':`g${graceIndex}:`}${index}`,tick:0,attackTick:0,index,attackIndex:index,track,pitch:60,tpc:14,logicalEnd:960,end:960,onSeconds:0,endSeconds:1,partId:0,piano:true};if(graceIndex!==undefined){n.grace=true;n.graceIndex=graceIndex;}return n;}
function check(n,marks,extras=[]){const data={scope:{start:0,end:1920,firstTrack:0,endTrack:8},notes:[n,...extras],hands:marks,pedals:[],harmonies:[],keys:[],rests:[],meters:[{tick:0,end:1920,measure:1,denominator:4}]},state=Rules.run(data,Rules.defaults());return Rules.handFor(state,n,n.attackTick);}
let passed=0,failed=0;function test(name,body){try{body();++passed;console.log('PASS '+name);}catch(error){++failed;console.error('FAIL '+name+'\n'+error.message);}}
test('a grace-note hand mark leaves the main note’s hand unchanged',()=>{const n=note();assert.equal(check(n,[{tick:0,track:0,index:0,left:true,bracket:true,grace:true,graceIndex:0}]).hand,'right');});
test('grace and main-note marks at the same tick remain separate',()=>{const n=note();const hand=check(n,[{tick:0,track:0,index:0,left:true,bracket:true,grace:true,graceIndex:0},{tick:0,track:0,index:0,left:false,bracket:true}]);assert.equal(hand.hand,'right');assert.equal(hand.source,'分手符号');});
test('grace-only marks leave normal-note range analysis unchanged',()=>{const n=note();const marks=[{tick:0,track:0,index:0,left:true,bracket:true,grace:true,graceIndex:0}];assert.deepEqual(check(n,marks),check(n,[]));});
test('another grace chord at the same tick keeps its own hand',()=>{const n=note(0,0,1);assert.equal(check(n,[{tick:0,track:0,index:0,left:true,bracket:true,grace:true,graceIndex:0}],[note()]).hand,'right');});
test('a mark on another normal chord note leaves this note unchanged',()=>{const n=note(4,1);assert.equal(check(n,[{tick:0,track:4,index:0,left:false,bracket:true}]).hand,'left');});
test('the lower staff keeps its left-hand suggestion beside a right-hand grace note',()=>{const n=note(4);assert.equal(check(n,[{tick:0,track:4,index:0,left:false,end:true,bracket:true,grace:true,graceIndex:0}]).hand,'left');});
test('a normal note mark still applies to its exact chord note',()=>{const n=note(4);assert.equal(check(n,[{tick:0,track:4,index:0,left:false,bracket:true}]).hand,'right');});
test('a chord mark still applies to each normal chord note',()=>{const n=note(4,1);assert.equal(check(n,[{tick:0,track:4,index:-1,left:false,bracket:true}]).hand,'right');});
test('a grace-only start does not assign the main chord a new hand',()=>{const n=note();assert.equal(check(n,[{tick:0,track:0,index:0,left:true,grace:true,graceIndex:0},{tick:960,track:0,index:-1,left:true,end:true}]).hand,'right');});
console.log(`${passed} hand-marker checks passed; ${failed} failed`);if(failed)process.exitCode=1;
