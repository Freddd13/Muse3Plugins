const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function read(file,scope={}) {
    vm.createContext(scope);
    vm.runInContext(fs.readFileSync(path.join(__dirname,'..',file),'utf8').replace(/^\.(pragma|import).*$/gm,''),scope);
    return scope;
}
const harmony=read('Harmony.js'),timeline=read('Timeline.js',{Harmony:harmony}),preferences=read('Preferences.js');
const tpc={0:14,1:21,2:16,3:23,4:18,5:13,6:20,7:15,8:22,9:17,10:24,11:19};
function notes(pitches) {return pitches.map((pitch,index)=>({tick:0,attackTick:0,end:1920,track:0,index,pitch,tpc:tpc[pitch%12]}));}

// The absolute bass must stay readable when it is outside the named harmony.
const outside=timeline.describe({root:0,definition:0},notes([42,48,52,55]),0,0,false,1,false);
assert.equal(outside.chord,'C/F♯');
assert.equal(outside.degree,'I/F♯');
const extended=timeline.describe({root:0,definition:13},notes([50,60,64,67]),0,0,false,1,false);
assert.equal(extended.chord,'Cadd9/D');
assert.equal(extended.degree,'Iadd9/D');

for(const [pitches,name,degree,inversion] of [
    [[47,51,54,57],'B7','IV7','原位'],
    [[51,54,57,59],'B7/D♯','IV⁶₅','第一转位'],
    [[63,54,57,59],'B7/F♯','IV⁴₃','第二转位'],
    [[45,47,51,54],'B7/A','IV⁴₂','第三转位']
]) {
    const detected=harmony.detect(pitches),result=timeline.describe(detected,notes(pitches),0,6,false,1,false);
    assert.equal(result.chord,name);assert.equal(result.degree,degree);assert.equal(result.inversion,inversion);
}

const regions=[{part:0,start:100,end:200,root:0},{part:4,start:100,end:200,root:7},{part:0,start:400,end:500,root:5}];
assert.equal(timeline.displayAtTick(regions,50,0,true),null,'a future harmony is never carried backwards');
assert.equal(timeline.displayAtTick(regions,250,0,false),null);
assert.equal(timeline.displayAtTick(regions,250,0,true).root,0);
assert.equal(timeline.displayAtTick(regions,250,4,true).root,7);
assert.equal(timeline.displayAtTick(regions,450,0,true).root,5);
assert.equal(timeline.atTick(regions,250,0),null,'display hold keeps the musical analysis range intact');
const blocked=timeline.suppressionIndex([{part:0,start:220,end:300,suppressed:true},{part:0,start:280,end:350,suppressed:true}]);
assert.equal(timeline.displayAtTick(regions,250,0,true,blocked),null,'a deliberately removed harmony stays removed');
assert.equal(timeline.displayAtTick(regions,350,0,true,blocked).root,0);
assert.equal(preferences.defaults().holdLastHarmony,false,'existing display defaults stay unchanged');
assert.equal(preferences.clean({...preferences.defaults(),holdLastHarmony:true}).holdLastHarmony,true);
console.log('Chord display: named bass, B7 inversions, display hold and manual removal passed');
const originalNotes=notes([60,64,67]);
originalNotes.forEach(n=>{n.track=0;n.tick=480;n.end=960});
const manual={part:0,start:480,end:960,root:0,definition:0,chord:'C',degree:'I',notes:originalNotes};
const updatedNotes=JSON.parse(JSON.stringify(originalNotes));
updatedNotes[0].pitch=61;updatedNotes[0].tpc=21;
updatedNotes.push({...updatedNotes[1],index:3,pitch:70,tpc:24});
const refreshed=timeline.refreshNotes([manual],[{notes:updatedNotes},{notes:updatedNotes}],[{startTrack:0,endTrack:8}]);
assert.equal(refreshed[0].notes.length,4,'current notes are de-duplicated across analysis frames');
assert.equal(refreshed[0].notes[0].pitch,61);
assert.equal(refreshed[0].chord,'C','the manual musical explanation is retained');
assert.equal(manual.notes[0].pitch,60,'reading does not rewrite saved user edits');
assert.equal(timeline.refreshNotes([manual],[{notes:[updatedNotes[3]]}],[{startTrack:0,endTrack:8}])[0].notes.length,1);
assert.equal(timeline.refreshNotes([manual],[],[{startTrack:8,endTrack:16}])[0].notes.length,3,'another part keeps its stored anchors');
console.log('Manual harmony: changed, added and removed notes follow the current score');
