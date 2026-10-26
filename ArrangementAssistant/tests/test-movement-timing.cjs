const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function load(file,context={}){vm.createContext(context);vm.runInContext(fs.readFileSync(path.resolve(__dirname,file),'utf8').replace(/^\.(pragma|import).*$/gm,''),context);return context;}
const Harmony=load('../../HarmonyAssistant/Harmony.js'),Timeline=load('../../HarmonyAssistant/Timeline.js',{Harmony});
function note(id,pitch,tick,end){return {id,pitch,writtenPitch:pitch,tpc:14,tick,attackTick:tick,end,logicalEnd:end,track:4,index:0,partId:0,onSeconds:tick/960,endSeconds:end/960,physicalStart:tick,physicalEnd:end};}
const old=note('old',36,0,470),next=note('next',72,480,960);
function run(changes={},frameNotes=[next]){
    const side={hand:'left',before:{count:1,low:72,high:72},after:{count:1,low:72,high:72,fits:true,maximum:16},notes:[0],released:[],attacks:[0],travel:20,available:.01,movementFrom:[old],...changes};
    const PianoHands={playbackFieldsVersion:1,analyse:()=>({sides:[side],possible:true})};
    const Rules=load('../Rules.js',{Harmony,Timeline,PianoHands}),config=Rules.defaults();config.roles={'4':{hand:'left'}};
    const data={scope:{start:0,end:1920,firstTrack:0,endTrack:8},notes:[old,next],hands:[],meters:[{tick:0,end:1920,measure:1,denominator:4}]};
    const before=JSON.stringify(data),state=Rules.create(data,config);Rules.physicalPlayability(state,{tick:480,playbackTick:480,seconds:.5,notes:frameNotes,lookahead:[]});
    assert.equal(JSON.stringify(data),before,'input score data remains unchanged');return state.issues;
}
let passed=0,failed=0;function test(name,body){try{body();++passed;console.log('PASS '+name);}catch(error){++failed;console.error('FAIL '+name+'\n'+error.stack);}}
test('a short movement identifies the released key and the actual time',()=>{const issue=run()[0];assert.equal(issue.code,'transition-left');assert(issue.basis.includes('C2'));assert(issue.basis.includes('10 ms'));assert(issue.basis.includes('20 半音'));assert.deepEqual(Array.from(issue.notes,n=>n.id),['next','old']);});
test('pedal-assisted movement explains the usable earlier release',()=>{const issue=run({pedalTravel:20,pedalAvailable:.38,pedalReleaseNotes:[old]})[0];assert(issue.title.includes('借踏板'));assert(issue.basis.includes('380 ms'));assert(issue.basis.includes('演奏编辑器'));assert(!issue.basis.includes('即使提前松手'));assert.equal(issue.notes.length,2);});
test('a slower pedal alternative does not claim to improve the move',()=>{const issue=run({travel:8,available:.1,pedalTravel:20,pedalAvailable:.12,pedalReleaseNotes:[old]})[0];assert(!issue.title.includes('借踏板'));assert(!issue.basis.includes('可留出约'));});
test('the chosen hand is also recorded on the issue note',()=>{const issue=run({hand:'right'})[0];assert.equal(issue.code,'transition-right');assert.equal(issue.notes[0].analysisHand,'right');});
test('older host reports retain their interval explanation',()=>{const issue=run({available:.5,movementFrom:[]})[0];assert.equal(issue.code,'travel-left');assert(issue.basis.includes('500 ms'));assert(!issue.basis.includes('实际松键'));});
test('small movements leave the existing threshold unchanged',()=>{assert.equal(run({travel:2,available:.01}).length,0);});
test('release and movement at one position appear as one explanation',()=>{const held={...old,physicalEnd:960,physicalEndSeconds:1};const issues=run({notes:[0,1],released:[1],available:0,pedalTravel:20,pedalAvailable:.38,pedalReleaseNotes:[held]},[next,held]);assert.equal(issues.length,1);assert.equal(issues[0].code,'release-left');assert(issues[0].basis.includes('380 ms'));});
console.log(`${passed} movement-display checks passed; ${failed} failed`);if(failed)process.exitCode=1;
