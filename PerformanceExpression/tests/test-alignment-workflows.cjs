// Ground truth is attached to independently generated performance events.
const fs = require('fs');
const vm = require('vm');
const assert = require('assert/strict');
const rules = vm.createContext({});
vm.runInContext(fs.readFileSync('PerformanceExpression/Alignment.js', 'utf8'), rules);
const settings = vm.createContext({});
vm.runInContext(fs.readFileSync('PerformanceExpression/ExpressionSettings.js', 'utf8'), settings);
const reports = [];
function fixture(roll = 0) {
    const notes = [], performance = [];
    let seconds = 0;
    for (let attack = 0; attack < 160; ++attack) {
        const bar = Math.floor(attack / 8), degree = (bar * 3 + attack * 2 + Math.floor(attack / 5)) % 12;
        [36 + (bar * 5) % 12, 55 + degree % 7, 72 + degree].forEach((pitch, voice) => {
            const id = `s${attack}-${voice}`;
            notes.push({id, logicalId: id, pitch, tick: attack * 240, track: voice ? 0 : 4,
                index: voice ? voice - 1 : 0, measure: bar + 1, beat: attack % 8 / 2 + 1,
                onSeconds: attack * .25, scoreSeconds: attack * .25,
                velocity: 80, velocityType: 0, velocityRaw: 0, velocityBase: 80, bpm: 120});
            performance.push({id: 'm' + id, truth: id, pitch, seconds: seconds + voice * roll,
                velocity: 55 + (attack + voice * 11) % 54});
        });
        seconds += .24 + .025 * Math.sin(attack * .17);
    }
    return {notes, performance};
}
function checked(name, notes, performance, extra = {}, expected) {
    const started = Date.now(), result = rules.align({notes, performance, mode: 'score', ...extra});
    const truth = new Map(performance.map(n => [n.id, n.truth]));
    const correct = result.matches.filter(m => truth.get(m.midiId) === m.scoreId);
    const wrongHigh = result.matches.filter(m => truth.get(m.midiId) !== m.scoreId && (m.confidence >= .8 || m.confirmed));
    assert.equal(wrongHigh.length, 0, name + ': wrong automatic correspondence');
    if (expected !== undefined) assert.equal(correct.length, expected, name);
    reports.push({name, scoreNotes: notes.length, performanceNotes: performance.length,
        correct: correct.length, pending: result.pending, missing: result.missing.length,
        extra: result.extra.length, wrongHigh: wrongHigh.length, ms: Date.now() - started});
    return result;
}
for (const roll of [0, .020, .035]) {
    const f = fixture(roll), notes = f.notes.filter(n => n.tick >= 48 * 240 && n.tick < 80 * 240);
    checked('whole MIDI to four bars, roll ' + roll, notes, f.performance, {}, 96);
    const errors = f.performance.filter(n => !['s54-2', 's62-0', 's73-1'].includes(n.truth))
        .map(n => ({...n, pitch: n.truth === 's69-2' ? n.pitch + 1 : n.pitch}));
    errors.push({id: 'extra', truth: '', pitch: 44,
        seconds: f.performance.find(n => n.truth === 's65-0').seconds + .09, velocity: 77});
    const result = checked('four bars with omissions, wrong and extra notes, roll ' + roll, notes, errors, {}, 93);
    assert.equal(result.pending, 1);
    assert.equal(result.missing.length, 3);
    assert.equal(result.extra.length, 1);
    checked('whole piece with omissions, wrong and extra notes, roll ' + roll, f.notes, errors, {}, 477);
    const candidate = rules.candidates({result, notes, config: settings.defaults()});
    assert.equal(candidate.velocity.length, 92);
    for (const v of candidate.velocity) {
        assert.equal(v.target, errors.find(n => n.id === result.matches.find(m => m.scoreId === v.id).midiId).velocity);
        assert.equal(v.writeMode, 'fixed');
    }
}
const f = fixture(.035), notes = f.notes.filter(n => n.tick >= 48 * 240 && n.tick < 80 * 240);
const anchored = checked('anchor inside a full recording', notes, f.performance,
    {anchors: [{scoreId: 's64-0', midiId: 'ms64-0'}]}, 96);
assert(anchored.extra.length < 4);
checked('two notes of the same anchored chord', notes, f.performance,
    {anchors: [{scoreId: 's64-0', midiId: 'ms64-0'}, {scoreId: 's64-1', midiId: 'ms64-1'}]}, 96);
checked('old anchor outside a new target', notes, f.performance,
    {anchors: [{scoreId: 's10-0', midiId: 'ms10-0'}]}, 96);
assert.throws(() => rules.align({notes, performance: f.performance, anchors: [
    {scoreId: 's55-0', midiId: 'ms60-0'}, {scoreId: 's60-0', midiId: 'ms55-0'}]}));
const repeatedNotes = f.notes.filter(n => n.tick < 8 * 240);
const first = f.performance.filter(n => n.truth && Number(n.truth.match(/^s(\d+)/)[1]) < 8);
const second = first.map(n => ({...n, id: 'second-' + n.id, seconds: n.seconds + 12}));
const repeated = checked('repeated passage stays available for a time choice', repeatedNotes, first.concat(second), {}, 24);
assert(repeated.passage.ambiguous);
assert.equal(repeated.pending, 24);
assert.equal(rules.candidates({result: repeated, config: settings.defaults()}).velocity.length, 0);
const index = repeated.passage.candidates.findIndex(c => c.from >= 12);
assert(index >= 0);
const chosen = checked('choose the second occurrence', repeatedNotes, first.concat(second), {passageChoice: index}, 24);
assert(chosen.matches.every(m => m.midiId.startsWith('second-')));
assert.equal(chosen.pending, 0);
const otherIndex = repeated.passage.candidates.findIndex(c => c.from < 12);
const cached = rules.align({notes: repeatedNotes, performance: first.concat(second), cacheKey: 'same', passageChoice: otherIndex});
const switched = rules.align({notes: repeatedNotes, performance: first.concat(second), cacheKey: 'same',
    previousKey: cached.cacheKey, segments: cached.segments, passageChoice: index});
assert(switched.matches.every(m => m.midiId.startsWith('second-')));
assert.notEqual(switched.cacheKey, cached.cacheKey);
const timeChosen = rules.align({notes: repeatedNotes, performance: first.concat(second),
    passageChoice: otherIndex, passageFrom: repeated.passage.candidates[index].from});
assert(timeChosen.matches.every(m => m.midiId.startsWith('second-')));
assert.equal(timeChosen.passage.chosenIndex, index);
const absentChoice = rules.align({notes: repeatedNotes, performance: first.concat(second), passageChoice: index, passageFrom: 1000});
assert.equal(absentChoice.passage.chosen, false);
assert.equal(absentChoice.pending, 24);
const longPrefix = Array.from({length: 500}, (_, i) => ({id: 'prefix' + i, truth: '', pitch: 30 + i % 4, seconds: i * .5, velocity: 45}));
const later = first.map(n => ({...n, seconds: n.seconds + 260}));
checked('fixed correspondence after a long unrelated introduction', repeatedNotes, longPrefix.concat(later),
    {anchors: [{scoreId: 's4-0', midiId: 'ms4-0'}]}, 24);
const trill = Array.from({length: 16}, (_, i) => ({id: 't' + i, logicalId: 't' + i, tick: i * 60,
    pitch: i % 2 ? 62 : 60, track: 0, index: 0, velocity: 80, velocityBase: 80}));
const trillPerformance = trill.filter((n, i) => ![3, 4, 5].includes(i)).map(n => ({id: 'm' + n.id, truth: n.id,
    pitch: n.pitch, seconds: Number(n.id.slice(1)) * .065, velocity: 60}));
const rapid = checked('missing attacks in a fast alternating figure', trill, trillPerformance);
assert(rapid.pending > 0);
const empty = rules.align({notes: [], performance: first});assert.equal(empty.matches.length, 0);
const melody = f.notes.filter(n => n.track === 0 && n.index === 1 && n.tick >= 48 * 240 && n.tick < 80 * 240);
const taps = f.performance.filter(n => n.truth.endsWith('-2')).map(n => ({...n, pitch: 40}));
const tapping = checked('uniform arbitrary-pitch tapping needs a passage choice', melody, taps, {mode: 'tap'});
assert.equal(tapping.pending, tapping.matches.length);
assert.equal(rules.candidates({result: tapping, config: settings.defaults()}).velocity.length, 0);
assert.equal(settings.defaults().velocityStrength, 100);
assert.equal(settings.restored({strength: 65}).velocityStrength, 65);
assert.equal(settings.restored({strength: 65}).velocityWriteMode, 'preserve');
fs.mkdirSync('P2/out/expression-095', {recursive: true});
fs.writeFileSync('P2/out/expression-095/workflows.json', JSON.stringify(reports, null, 2));
console.log(reports.length + ' alignment workflows passed.');
