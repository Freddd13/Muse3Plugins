const fs=require('fs'),vm=require('vm'),assert=require('assert');
const modulePath=process.argv[2]||'PerformanceExpression/Alignment.js',rules={};vm.createContext(rules);vm.runInContext(fs.readFileSync(modulePath,'utf8'),rules);
const notes=[{id:'a',tick:0,track:0,index:0,pitch:60,writtenPitch:60,writtenTpc:14,velocity:80,velocityType:0,velocityRaw:0,velocityBase:80,protected:false},{id:'b',tick:480,track:4,index:0,pitch:48,writtenPitch:48,writtenTpc:14,velocity:48,velocityType:0,velocityRaw:0,velocityBase:48,protected:false}];
const matches=notes.map((n,i)=>({id:n.id,scoreId:n.id,tick:n.tick,original:n,velocity:i?84:108,seconds:i*.6,confidence:1,confirmed:true}));
const source={result:{matches},notes,scope:{start:0,end:960,firstTrack:0,endTrack:8},revision:'1'},before=JSON.stringify(source);
function candidate(config){return rules.candidates({...source,config:{velocity:true,keepManual:false,...config}})}
let output=candidate({velocityStrength:100,velocityWriteMode:'fixed'});
assert.deepStrictEqual(Array.from(output.velocity,v=>v.target),[108,84]);assert(output.velocity.every(v=>v.writeMode==='fixed'));assert.deepStrictEqual(Array.from(output.velocity,v=>v.originalVelocity),[80,48]);
output=candidate({velocityStrength:50,velocityWriteMode:'fixed'});assert.deepStrictEqual(Array.from(output.velocity,v=>v.target),[94,66]);
output=candidate({strength:50});assert.deepStrictEqual(Array.from(output.velocity,v=>v.target),[94,66]);assert(output.velocity.every(v=>v.writeMode==='preserve'));
output=candidate({velocityStrength:100,velocityWriteMode:'follow'});assert(output.velocity.every(v=>v.writeMode==='follow'));
assert.strictEqual(JSON.stringify(source),before);
notes[0].velocityBase=0;output=candidate({velocityStrength:100,velocityWriteMode:'follow'});assert.strictEqual(output.velocity.length,1);assert(output.kept.some(v=>v.id==='a'));
output=candidate({velocityStrength:100,velocityWriteMode:'fixed'});assert.strictEqual(output.velocity[0].target,108);
console.log('Velocity: 100%, 50%, legacy settings, per-staff bases, fixed/follow and zero reference passed.');

const settings={};vm.createContext(settings);vm.runInContext(fs.readFileSync('PerformanceExpression/ExpressionSettings.js','utf8'),settings);
assert.strictEqual(settings.defaults().velocityStrength,100);assert.strictEqual(settings.defaults().velocityWriteMode,'fixed');
let legacy=settings.restored({strength:35,keepManual:true});assert.strictEqual(legacy.velocityStrength,35);assert.strictEqual(legacy.rubatoStrength,35);assert.strictEqual(legacy.velocityWriteMode,'preserve');assert(legacy.velocity);
let saved={velocityStrength:75,velocityWriteMode:'follow',rubatoStrength:30,unlocked:['a']};let restored=settings.restored(saved);assert.strictEqual(restored.velocityStrength,75);assert.strictEqual(restored.rubatoStrength,30);assert.strictEqual(restored.velocityWriteMode,'follow');restored.unlocked.push('b');assert.deepStrictEqual(saved.unlocked,['a']);
assert(settings.restored().velocity);assert.strictEqual(settings.restored().velocityStrength,50);console.log('Fresh and saved expression settings preserve their own ratio and save mode.');
