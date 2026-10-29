const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = path.resolve(__dirname, '..');
const builtIn = path.resolve(base, '../P2/native/share/workflow/panels/PerformanceExpression');
const marker = ' Rectangle {anchors.fill:parent;color:theme.background}';
const read = name => fs.readFileSync(name,'utf8').replace(/\r\n/g,'\n');
const independent = read(path.join(base,'PerformanceExpression.view.qml'));
const native = read(path.join(builtIn,'PerformanceExpression.view.qml'));
assert.equal(native.split(marker).length,2);
assert.equal(independent.split(marker).length,2);
assert.equal(native.split(marker)[0],independent.split(marker)[0], 'Built-in and independent pages use the same controller');
for (const name of ['Alignment.js','ExpressionProgress.js','ExpressionRows.js','ExpressionSession.js','ExpressionSettings.js'])
    assert.equal(read(path.join(builtIn,name)),read(path.join(base,name)),name);
console.log('Built-in expression controller and rule modules match; each page keeps its own layout.');
