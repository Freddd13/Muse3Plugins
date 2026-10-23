// Optional external material: {notes, performance, truth:{scoreId:midiId}}.
// Reference scores and recordings are supplied separately under their licences.
const fs = require('fs'), vm = require('vm'), path = require('path');
if (process.argv.length < 3) throw new Error('Pass a JSON fixture followed by optional first:last measure ranges.');
const fixture = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const rules = vm.createContext({});
vm.runInContext(fs.readFileSync(path.join(__dirname, '../Alignment.js'), 'utf8'), rules);
const ranges = process.argv.slice(3).length ? process.argv.slice(3).map(r => r.split(':').map(Number)) : [[1, Infinity]];
const reports = ranges.map(([first, last]) => {
    const notes = fixture.notes.filter(n => n.measure >= first && n.measure <= last), started = Date.now();
    const result = rules.align({notes, performance: fixture.performance});
    const correct = result.matches.filter(m => fixture.truth[m.scoreId] === m.midiId);
    const wrong = result.matches.filter(m => fixture.truth[m.scoreId] !== m.midiId);
    const trusted = result.matches.filter(m => m.confidence >= .8 || m.confirmed);
    return {range: [first, Number.isFinite(last) ? last : 'end'], scoreNotes: notes.length,
        referencePairs: notes.filter(n => fixture.truth[n.id]).length, matched: result.matches.length,
        correct: correct.length, automatic: trusted.length,
        automaticCorrect: trusted.filter(m => fixture.truth[m.scoreId] === m.midiId).length,
        wrongHigh: wrong.filter(m => m.confidence >= .8 || m.confirmed).length,
        pending: result.pending, missing: result.missing.length, extra: result.extra.length,
        ms: Date.now() - started,
        passage: result.passage && [result.passage.from, result.passage.until],
        wrong: wrong.map(m => ({score: m.scoreId, matched: m.midiId, expected: fixture.truth[m.scoreId], confidence: m.confidence}))};
});
console.log(JSON.stringify(reports, null, 2));
