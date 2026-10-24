const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
function load(name,scope={}){vm.createContext(scope);vm.runInContext(fs.readFileSync(path.resolve(__dirname,'..',name),'utf8').replace(/^\.(pragma|import).*$/gm,''),scope);return scope;}
const rulesPath=process.env.ARRANGEMENT_RULES||path.join(__dirname,'../Rules.js');
const H=load('../HarmonyAssistant/Harmony.js'),T=load('../HarmonyAssistant/Timeline.js',{Harmony:H}),R=load(rulesPath,{Harmony:H,Timeline:T});
const corpus=JSON.parse(fs.readFileSync(path.join(__dirname,'../../P2/native/mtest/mscore/pluginhost/arrangement_115_cases.json'),'utf8'));
const bundle=R.workerBundle({harmony:fs.readFileSync(path.join(__dirname,'../../HarmonyAssistant/Harmony.js'),'utf8'),timeline:fs.readFileSync(path.join(__dirname,'../../HarmonyAssistant/Timeline.js'),'utf8'),rules:fs.readFileSync(rulesPath,'utf8')});
const results=[];
for(const item of corpus.cases){
 const config=R.defaults();config.playability=false;Object.assign(config,item.config||{});
 if(item.independent)config.roles={'0':{role:'melody',independent:true},'4':{role:'bass',independent:true}};
 const notes=item.notes.map(([pitch,tick,end,track,tpc],index)=>({id:`${track}:${tick}:${index}`,pitch,writtenPitch:pitch,tpc,tick,attackTick:tick,end,logicalEnd:end,track,index,partId:0,piano:true,measure:1,beat:1+tick/480,onSeconds:tick/960,endSeconds:end/960}));
 const data={notes,pedals:[],hands:[],harmonies:[],harmonyRegions:item.harmonyRegions||[],meters:[{tick:0,end:1920,measure:1,denominator:4}],scope:{start:item.scopeStart||0,end:1920,firstTrack:0,endTrack:8}};
 const before=JSON.stringify({data,config});const result=R.run(data,config);const worker=vm.runInNewContext(bundle,{input:{data,config,imported:[]}});
 assert.equal(JSON.stringify(result.issues),JSON.stringify(worker.issues),item.id+' worker result');assert.equal(before,JSON.stringify({data,config}),item.id+' read only');
 const failures=[];
 for(const [code,tick] of item.expect||[])if(!result.issues.some(issue=>issue.code===code&&issue.tick===tick))failures.push(`missing ${code} at ${tick}`);
 for(const code of item.absent||[])if(result.issues.some(issue=>issue.code===code))failures.push(`unexpected ${code}`);
 for(const [code,count] of Object.entries(item.minimumNotes||{}))if(!result.issues.some(issue=>issue.code===code&&issue.notes.length>=count))failures.push(`missing evidence for ${code}`);
 results.push({id:item.id,name:item.name,failures,issues:JSON.parse(JSON.stringify(result.issues))});console.log((failures.length?'FAIL ':'PASS ')+item.id+(failures.length?' '+failures.join('; '):''));
}
if(process.env.ARRANGEMENT_REPORT)fs.writeFileSync(process.env.ARRANGEMENT_REPORT,JSON.stringify({cases:results},null,2));
const failed=results.filter(row=>row.failures.length).length;console.log(`${results.length-failed}/${results.length} context cases passed`);if(failed)process.exitCode=1;
