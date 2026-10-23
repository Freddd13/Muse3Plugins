const fs = require('fs'), vm = require('vm'), assert = require('assert'), path = require('path');
const rules = vm.createContext({});
vm.runInContext(fs.readFileSync(path.join(__dirname, '../ExpressionRows.js'), 'utf8'), rules);
const a = {id:'score-internal-a', tick:0, track:0, index:0, measure:7, beat:1.5, pitch:63, writtenPitch:63, writtenTpc:23, velocity:80};
const b = {...a, id:'score-internal-b', track:4, velocity:48};
const matches = [a,b].map((note,i) => ({original:note, pitch:note.pitch, seconds:.3+i/100, velocity:105, confidence:i ? .6 : .95, confirmed:false}));
const result = {matches, missing:[{...a,id:'missing',beat:3}], extra:[{id:'midi-internal',pitch:60,seconds:4.1}]};
const candidate = {velocityById:{[a.id]:{target:105}}, kept:[]};
let count=0;
function test(name, run) { run(); count++; console.log('PASS '+name); }
test('same-pitch voices retain their own note and old velocity',()=>{
 const rows=rules.build(result,{},candidate,0);
 assert.equal(rows.length,2);assert.equal(rows[0].original,80);assert.equal(rows[1].original,48);
 assert.equal(rows[0].proposed,105);assert.equal(rows[1].proposed,null);
 assert.equal(rows[0].pitch,'D♯4');assert(rows[0].place.includes('第 7 小节'));assert(rows[0].place.includes('第 1.5 拍'));
});
test('pending filter keeps uncertain pairs until checked',()=>{
 assert.equal(rules.build(result,{},candidate,1).length,1);
 const fixed={matches:[{...matches[1],confirmed:true}]};assert.equal(rules.build(fixed,{},candidate,1).length,0);
});
test('uncertain matches explain what needs attention',()=>{
 const explanation='附近弹了几次同音，请选择这个谱音对应的那一次。';
 const r={matches:[{...matches[1],uncertainty:explanation}]};
 assert.equal(rules.build(r,{},candidate,1)[0].detail,explanation);
});
test('adopting part of a chord removes only that physical note',()=>{
 const progress={velocity:{'0:0::0':true}};
 assert.equal(rules.build(result,progress,candidate,0)[0].note.id,b.id);
 assert.equal(rules.build(result,progress,candidate,4)[0].note.id,a.id);
});
test('missing and extra notes expose musical positions',()=>{
 const missing=rules.build(result,{},candidate,2)[0],extra=rules.build(result,{},candidate,3)[0];
 assert.equal(missing.kind,'missing');assert(missing.place.includes('第 3 拍'));
 assert.equal(extra.kind,'extra');assert.equal(extra.place,'4.100 秒');assert.equal(extra.pitch,'C4');
 for(const row of [missing,extra])assert(![row.pitch,row.place,row.detail].join(' ').includes('internal'));
});
test('protected results explain the retained value',()=>{
 const c={velocityById:{},kept:[{id:a.id,reason:'保留手动调整'}]};
 const row=rules.build(result,{},c,0)[0];assert.equal(row.proposed,null);assert.equal(row.detail,'保留手动调整');
});
test('enharmonic spelling keeps the written octave',()=>{
 assert.equal(rules.pitchName(60,26),'B♯3');assert.equal(rules.pitchName(59,7),'C♭4');
});
console.log(count+' result-list checks passed');
