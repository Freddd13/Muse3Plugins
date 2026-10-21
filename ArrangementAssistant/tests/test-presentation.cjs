const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const context={};vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../Presentation.js'),'utf8').replace(/^\.pragma.*$/gm,''),context);
const notes=[{tick:0,track:0},{tick:480,track:4}],issues=[{tick:480,notes:[notes[0]]},{tick:0,notes:[notes[0]]},{tick:480,notes:[notes[1]]}];
const before=JSON.stringify(issues),groups=context.groups(issues);assert.strictEqual(groups.length,2);assert.strictEqual(groups[1].indexes.length,2);assert.strictEqual(groups[1].note.track,4);assert.strictEqual(JSON.stringify(issues),before);
assert.strictEqual(context.groups([{tick:0,notes:[]}])[0].note,null);
console.log('Grouped problem locations retain all issues and the closest source note.');
assert.strictEqual(context.anchor({tick:1920,notes:[{tick:0,track:0},{tick:1920,track:1}]}).track,1);
assert.strictEqual(context.anchor({tick:1920,notes:[]}),null);

const typed=[{id:1,type:'harmony',severity:'注意'},{id:2,type:'counterpoint',severity:'需核查'},{id:3,type:'playability',severity:'注意'}];
assert.equal(context.filter(typed,7,0).length,3);assert.equal(context.filter(typed,0,0).length,0);
assert.equal(context.filter(typed,5,2).length,2);assert.equal(context.filter(typed,7,1)[0].id,2);
assert.equal(typed.length,3);console.log('Multiple issue categories and severity share the original results.');
