const fs = require('fs'), vm = require('vm'), path = require('path'), assert = require('assert');
function read(file, context = {}) {
    vm.createContext(context);
    vm.runInContext(fs.readFileSync(path.resolve(__dirname, file), 'utf8').replace(/^\.(pragma|import).*$/gm, ''), context);
    return context;
}
const Harmony = read('../../HarmonyAssistant/Harmony.js');
const Timeline = read('../../HarmonyAssistant/Timeline.js', {Harmony});
const rules = read('../Rules.js', {Harmony, Timeline});
function note(pitch, track = 4, play = true) {
    return {id: `${track}:${pitch}`, pitch, tpc: pitch % 12 ? 21 : 14, track, tick: 0, attackTick: 0,
        index: pitch % 12, end: 960, logicalEnd: 960, onSeconds: 0, endSeconds: 1,
        measure: 1, beat: 1, partId: 0, piano: true, play, velocity: 48};
}
function data(notes) {
    return {notes, scope: {start: 0, end: 1920, firstTrack: 0, endTrack: 8},
        meters: [{tick: 0, end: 1920, measure: 1, denominator: 4}], pedals: [], hands: [], harmonies: []};
}
function low(notes) {return rules.run(data(notes), rules.defaults()).issues.filter(issue => issue.code === 'low-cluster');}
assert.equal(low([note(36), note(37)]).length, 1);
for (const pitch of [36, 37]) {
    assert.equal(low([note(36, 4, pitch !== 36), note(37, 4, pitch !== 37)]).length, 0);
}
const doubled = [note(36), note(37), note(36, 0, false)];
const before = JSON.stringify(doubled), found = low(doubled);
assert.equal(found.length, 1);
assert.equal(found[0].notes.length, 2);
assert(found[0].notes.every(note => note.play));
assert.equal(JSON.stringify(doubled), before);
const legacy = [note(36), note(37)];
legacy.forEach(note => delete note.play);
assert.equal(low(legacy).length, 1);
const worker = rules.workerBundle(Object.fromEntries([
    ['harmony', '../../HarmonyAssistant/Harmony.js'], ['timeline', '../../HarmonyAssistant/Timeline.js'], ['rules', '../Rules.js']
].map(([name, file]) => [name, fs.readFileSync(path.resolve(__dirname, file), 'utf8')])));
const result = vm.runInNewContext(worker, {input: {data: data(doubled), config: rules.defaults(), imported: []}});
assert.equal(JSON.stringify(result.issues), JSON.stringify(rules.run(data(doubled), rules.defaults()).issues));
console.log('6 sounding-note checks passed: audible pair, either muted key, doubled key, legacy rows, worker');
