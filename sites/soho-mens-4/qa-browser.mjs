const url = process.argv[2] || 'http://127.0.0.1:4173/';
const width = Number(process.argv[3] || 390);
const height = Number(process.argv[4] || 844);
const screenshotPath = process.argv[5];
const waitMs = Number(process.argv[6] || 1800);
const axePath = process.argv[7];
const target = await fetch(`http://127.0.0.1:9227/json/new?${encodeURIComponent(url)}`, { method: 'PUT' }).then(response => response.json());
const socket = new WebSocket(target.webSocketDebuggerUrl);
let nextId = 0;
const pending = new Map();
const consoleIssues = [];

socket.addEventListener('message', event => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) {
    pending.get(message.id)(message);
    pending.delete(message.id);
  }
  if (message.method === 'Runtime.exceptionThrown' || message.method === 'Log.entryAdded') {
    consoleIssues.push(message.params);
  }
});

await new Promise(resolve => socket.addEventListener('open', resolve, { once: true }));
const send = (method, params = {}) => new Promise(resolve => {
  const id = ++nextId;
  pending.set(id, resolve);
  socket.send(JSON.stringify({ id, method, params }));
});

await send('Runtime.enable');
await send('Log.enable');
await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: width < 700 });
await send('Emulation.setScrollbarsHidden', { hidden: true });
await send('Page.navigate', { url });
await new Promise(resolve => setTimeout(resolve, waitMs));

const expression = `(() => {
  const viewport = document.documentElement.clientWidth;
  const offenders = [...document.querySelectorAll('body *')].map(el => {
    const r = el.getBoundingClientRect();
    return {tag: el.tagName, cls: el.className || '', id: el.id || '', left: Math.round(r.left), right: Math.round(r.right), width: Math.round(r.width)};
  }).filter(item => item.right > viewport + 1 || item.left < -1).sort((a,b) => b.right - a.right).slice(0, 20);
  return {title: document.title, viewport, scrollWidth: document.documentElement.scrollWidth, offenders};
})()`;
const result = await send('Runtime.evaluate', { expression, returnByValue: true });
console.log(JSON.stringify({ page: result.result.result.value, consoleIssues }, null, 2));
if (axePath) {
  const { readFile } = await import('node:fs/promises');
  const axeSource = await readFile(axePath, 'utf8');
  await send('Runtime.evaluate', { expression: axeSource });
  const audit = await send('Runtime.evaluate', {
    expression: `axe.run(document).then(result => ({
      passes: result.passes.length,
      violations: result.violations.map(item => ({
        id: item.id,
        impact: item.impact,
        description: item.description,
        nodes: item.nodes.map(node => ({ target: node.target, html: node.html, summary: node.failureSummary }))
      }))
    }))`,
    awaitPromise: true,
    returnByValue: true
  });
  console.log(JSON.stringify({ axe: audit.result.result.value }, null, 2));
}
if (screenshotPath) {
  const capture = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false, fromSurface: true });
  const { writeFile } = await import('node:fs/promises');
  await writeFile(screenshotPath, Buffer.from(capture.result.data, 'base64'));
}
socket.close();
