const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const context={};vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../Presentation.js'),'utf8').replace(/^\.pragma.*$/gm,''),context);
const notes=[{tick:0,track:0},{tick:480,track:4}],issues=[{tick:480,notes:[notes[0]]},{tick:0,notes:[notes[0]]},{tick:480,notes:[notes[1]]}];
const before=JSON.stringify(issues),groups=context.groups(issues);assert.strictEqual(groups.length,2);assert.strictEqual(groups[1].indexes.length,2);assert.strictEqual(groups[1].note.track,4);assert.strictEqual(JSON.stringify(issues),before);
assert.strictEqual(context.groups([{tick:0,notes:[]}])[0].note,null);
console.log('Grouped problem locations retain all issues and the closest source note.');
