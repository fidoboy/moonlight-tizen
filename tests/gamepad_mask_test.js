'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

let pads = [];
const context = vm.createContext({
  navigator: { getGamepads: () => pads },
  console: { log() {} }
});
vm.runInContext(
  fs.readFileSync(path.join(__dirname, '../wasm/static/js/utils.js'), 'utf8'),
  context
);
const mask = () => context.getConnectedGamepadMask();
const pad = (index, id, timestamp = 1) => ({ index, id, timestamp, connected: true });

assert.equal(mask(), 0);
pads = [null, null, pad(2, 'DualSense'), null];
assert.equal(mask(), 4, 'Preserve sparse physical indices');
pads[3] = pad(3, 'Xbox Wireless Controller');
assert.equal(mask(), 12, 'Two simultaneous controllers keep distinct bits');
pads[2].timestamp = 0;
assert.equal(mask(), 12, 'A previously real device may return timestamp zero');
pads[2] = null;
assert.equal(mask(), 8, 'Null slot disconnects');
pads[2] = pad(2, 'placeholder', 0);
assert.equal(mask(), 8, 'A new placeholder must not inherit a real device slot');
pads[3] = pad(3, 'DualSense', 0);
assert.equal(mask(), 0, 'A replacement with no activity is not treated as a real device');
pads[3].timestamp = 2;
assert.equal(mask(), 8);
pads[3].connected = false;
assert.equal(mask(), 0);
pads = Array(17).fill(null);
pads[15] = pad(15, 'Xbox');
pads[16] = pad(16, 'DualSense');
assert.equal(mask(), 0x8000, 'Only the 16 protocol-supported controller slots are used');
pads = [];
assert.equal(mask(), 0, 'An empty browser array clears every previously tracked slot');
pads[15] = pad(15, 'Xbox', 0);
assert.equal(mask(), 0);
console.log('Gamepad mask regression tests passed');
