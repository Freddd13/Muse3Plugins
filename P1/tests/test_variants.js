const fs=require('fs'),vm=require('vm'),assert=require('assert');
const ctx={};vm.createContext(ctx);vm.runInContext(fs.readFileSync('ArrangementVariants/Variants.js','utf8'),ctx);
const base={staves:2,measures:[0,1,2,3].map(i=>({tick:i*1920,end:(i+1)*1920,signature:'4/4',hash:'h'+i}))},scope={start:1920,end:5760};
const current=JSON.parse(JSON.stringify(base));assert(ctx.compare(base,current,scope).same);
current.measures[1].hash='edited';let c=ctx.compare(base,current,scope);assert(c.same);assert.equal(c.inside,1);
current.measures[0].hash='outside';c=ctx.compare(base,current,scope);assert(!c.same);assert.equal(c.outside,1);
current.measures[2].signature='3/4';c=ctx.compare(base,current,scope);assert(!c.same);assert(c.reasons.some(r=>r.includes('拍号')));
current.measures.pop();assert(!ctx.compare(base,current,scope).same);current.staves=3;assert(!ctx.compare(base,current,scope).same);
console.log('Variant range, outside edits, meter/length and staff comparison passed.');
