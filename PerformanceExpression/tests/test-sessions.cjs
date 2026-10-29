const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const session = {};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../ExpressionSession.js'), 'utf8'), session);
const plain = value => JSON.parse(JSON.stringify(value));
const defaults = {velocityStrength:100, velocityWriteMode:'fixed'};
const original = plain(session.empty(defaults));
Object.assign(original, {midi:{path:'one.mid',notes:[{pitch:60,velocity:91}]},workspace:'one.json',
    candidate:{velocity:[{target:83}]},notes:[{pitch:60}],revision:'one',config:{velocityStrength:42},
    scope:{start:480,end:1920},retainedScope:{start:480,end:1920},dirtyProject:true,selected:2,
    links:[{scoreId:'score-note',midiId:'played-note'}],manualAnchors:[{scoreId:'anchor-note',midiId:'played-anchor'}],
    previewUndo:[{config:{velocityStrength:70},links:[]}],previewRedo:[{config:{velocityStrength:55}}],
    applicationRecords:{velocity:{'already-used':{type:1,raw:106}},tempos:{}},progressVersion:4,
    pendingProjectRestore:{url:'saved.json',data:{source:'original.mid'}},busy:false,stale:false,previewUpdating:false});
const saved = session.snapshot(original, 70);
original.midi.notes[0].velocity = 1;
assert.equal(saved.midi.notes[0].velocity,91);
assert.equal(saved.incomplete,false);
assert.equal(saved.scroll,70);
const restored = {};
session.restore(restored,saved,defaults);
for(const key of session.fields)assert.deepEqual(plain(restored[key]),plain(saved[key]),key);
session.restore(restored,{},defaults);
assert.equal(restored.midi,null);
assert.equal(restored.workspace,'');
assert.equal(restored.candidate,null);
assert.equal(restored.config.velocityStrength,100);
assert.equal(restored.selected,-1);
assert.equal(restored.pendingProjectRestore,null);
assert.equal(restored.recordingImport,false);
assert.equal(restored.recordedPath,'');
session.restore(restored,{appliedProgress:{velocity:{legacy:true},tempos:{}}},defaults);
assert.equal(restored.applicationRecords.velocity.legacy,true);
const pendingTake={...original,recordingImport:true,recordedPath:'previous.mid',requestedMidiPath:'new-take.mid',alignmentOnShow:true};
const pendingSaved=session.snapshot(pendingTake,0);session.restore(restored,pendingSaved,defaults);
assert.equal(restored.recordingImport,true);assert.equal(restored.recordedPath,'previous.mid');assert.equal(restored.requestedMidiPath,'new-take.mid');assert.equal(restored.alignmentOnShow,true);
assert.equal(session.snapshot({...original,busy:true},0).incomplete,true);
assert.equal(session.snapshot({...original,stale:true},0).incomplete,true);
assert.equal(session.snapshot({...original,previewUpdating:true},0).incomplete,true);
assert.equal(session.rangesKey([{start:0,end:480}]),session.rangesKey([{end:480,start:0}]));
assert.notEqual(session.rangesKey([{start:0,end:480}]),session.rangesKey([{start:480,end:960}]));
const withTempo={...original,config:{rubato:true},tempoTargetRanges:()=>[{start:480,end:960}]};
assert.equal(session.rangesKey(session.snapshot(withTempo,0).tempoRanges),'[[480,960]]');
console.log('Expression sessions: independent material, pending reads, defaults and unfinished work passed.');
