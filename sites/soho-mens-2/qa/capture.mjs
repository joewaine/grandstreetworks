import { spawn } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { extname, join, normalize, resolve } from 'node:path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const projectDir = resolve(import.meta.dirname, '..');
const prefix = process.argv[2] || 'capture';
const profileDir = `/private/tmp/soho-qa-${process.pid}`;

const mimeTypes = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.jpg': 'image/jpeg',
  '.js': 'text/javascript; charset=utf-8',
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.woff2': 'font/woff2'
};

const server = createServer((request, response) => {
  const requestedPath = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
  const relativePath = requestedPath === '/' ? 'index.html' : requestedPath.replace(/^\/+/, '');
  const filePath = normalize(join(projectDir, relativePath));
  if (!filePath.startsWith(projectDir)) {
    response.writeHead(403).end('Forbidden');
    return;
  }
  try {
    const body = readFileSync(filePath);
    response.writeHead(200, { 'Content-Type': mimeTypes[extname(filePath)] || 'application/octet-stream' });
    response.end(body);
  } catch {
    response.writeHead(404).end('Not found');
  }
});

await new Promise((resolveListen) => server.listen(0, '127.0.0.1', resolveListen));
const pageUrl = `http://127.0.0.1:${server.address().port}/`;

mkdirSync(profileDir, { recursive: true });

const chrome = spawn(chromePath, [
  '--headless=new',
  '--disable-gpu',
  '--hide-scrollbars',
  '--no-first-run',
  '--allow-file-access-from-files',
  `--user-data-dir=${profileDir}`,
  '--remote-debugging-port=0',
  'about:blank'
], { stdio: 'ignore' });

const delay = (ms) => new Promise((resolveDelay) => setTimeout(resolveDelay, ms));

let port;
for (let attempt = 0; attempt < 100; attempt += 1) {
  try {
    [port] = readFileSync(`${profileDir}/DevToolsActivePort`, 'utf8').trim().split('\n');
    break;
  } catch {
    await delay(100);
  }
}

if (!port) {
  chrome.kill('SIGTERM');
  throw new Error('Chrome DevTools port was not created.');
}

const targets = await fetch(`http://127.0.0.1:${port}/json`).then((response) => response.json());
const target = targets.find((item) => item.type === 'page');
if (!target) throw new Error('No page target found.');

const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolveOpen, rejectOpen) => {
  socket.addEventListener('open', resolveOpen, { once: true });
  socket.addEventListener('error', rejectOpen, { once: true });
});

let messageId = 0;
const pending = new Map();
const listeners = new Map();
const consoleIssues = [];

socket.addEventListener('message', ({ data }) => {
  const message = JSON.parse(data);
  if (message.id && pending.has(message.id)) {
    const { resolve: resolveMessage, reject } = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) reject(new Error(message.error.message));
    else resolveMessage(message.result);
    return;
  }
  if (message.method === 'Runtime.exceptionThrown' || message.method === 'Log.entryAdded') {
    consoleIssues.push(message);
  }
  const queue = listeners.get(message.method);
  if (queue?.length) queue.shift()(message.params);
});

const send = (method, params = {}) => new Promise((resolveMessage, reject) => {
  const id = ++messageId;
  pending.set(id, { resolve: resolveMessage, reject });
  socket.send(JSON.stringify({ id, method, params }));
});

const once = (method) => new Promise((resolveEvent) => {
  const queue = listeners.get(method) || [];
  queue.push(resolveEvent);
  listeners.set(method, queue);
});

await send('Page.enable');
await send('Runtime.enable');
await send('Log.enable');

const viewports = [
  [1440, 1000],
  [1024, 768],
  [768, 1024],
  [390, 844],
  [360, 800]
];

const report = [];
for (const [width, height] of viewports) {
  await send('Emulation.setDeviceMetricsOverride', {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: width <= 430,
    screenWidth: width,
    screenHeight: height
  });
  const loaded = once('Page.loadEventFired');
  await send('Page.navigate', { url: pageUrl });
  await loaded;
  await send('Runtime.evaluate', {
    awaitPromise: true,
    expression: `Promise.all([document.fonts.ready, ...Array.from(document.images, image => image.complete ? true : new Promise(resolveImage => { image.addEventListener('load', resolveImage, { once: true }); image.addEventListener('error', resolveImage, { once: true }); }))])`
  });
  await send('Runtime.evaluate', { expression: 'window.scrollTo(0, 0)' });
  await delay(250);
  const { result: metricsResult } = await send('Runtime.evaluate', {
    returnByValue: true,
    expression: `({ innerWidth, innerHeight, scrollWidth: document.documentElement.scrollWidth, scrollHeight: document.documentElement.scrollHeight, title: document.title, fonts: document.fonts.status, images: Array.from(document.images, image => ({src: image.currentSrc, complete: image.complete, naturalWidth: image.naturalWidth})) })`
  });
  const screenshot = await send('Page.captureScreenshot', {
    format: 'png',
    fromSurface: true,
    captureBeyondViewport: false
  });
  const filename = `${projectDir}/qa/${prefix}-${width}x${height}.png`;
  writeFileSync(filename, Buffer.from(screenshot.data, 'base64'));
  report.push({ viewport: `${width}x${height}`, file: filename, ...metricsResult.value });
}

const inspectionStates = [
  [1440, 1000, 'care-paths', `document.querySelector('#care-paths').scrollIntoView()`],
  [1440, 1000, 'doctor', `document.querySelector('#doctor').scrollIntoView()`],
  [1440, 1000, 'services', `document.querySelector('#services').scrollIntoView()`],
  [1440, 1000, 'reviews', `document.querySelector('#reviews').scrollIntoView()`],
  [1440, 1000, 'locations', `document.querySelector('#locations').scrollIntoView()`],
  [390, 844, 'care-paths', `document.querySelector('#care-paths').scrollIntoView()`],
  [390, 844, 'doctor', `document.querySelector('#doctor').scrollIntoView()`],
  [390, 844, 'services', `document.querySelector('#services').scrollIntoView()`],
  [390, 844, 'services-open', `document.querySelector('#sexual-services').open = true; document.querySelector('#sexual-services').scrollIntoView()`],
  [390, 844, 'reviews', `document.querySelector('#reviews').scrollIntoView()`],
  [390, 844, 'locations', `document.querySelector('#locations').scrollIntoView()`],
  [390, 844, 'menu-open', `window.scrollTo(0, 0); document.querySelector('.menu-button').click()`]
];

for (const [width, height, stateName, expression] of inspectionStates) {
  await send('Emulation.setDeviceMetricsOverride', {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: width <= 430,
    screenWidth: width,
    screenHeight: height
  });
  const loaded = once('Page.loadEventFired');
  await send('Page.navigate', { url: pageUrl });
  await loaded;
  await send('Runtime.evaluate', { awaitPromise: true, expression: 'document.fonts.ready' });
  await send('Runtime.evaluate', { expression: `document.documentElement.style.scrollBehavior = 'auto'; ${expression}` });
  await delay(200);
  const screenshot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
  writeFileSync(`${projectDir}/qa/${prefix}-${width}-${stateName}.png`, Buffer.from(screenshot.data, 'base64'));
}

const issueSummary = consoleIssues.map((issue) => ({
  method: issue.method,
  level: issue.params?.entry?.level,
  text: issue.params?.entry?.text || issue.params?.exceptionDetails?.text || 'Unknown browser issue'
}));
writeFileSync(`${projectDir}/qa/${prefix}-browser-report.json`, JSON.stringify({ report, consoleIssueCount: consoleIssues.length, consoleIssues: issueSummary }, null, 2));
socket.close();
chrome.kill('SIGTERM');
server.close();
console.log(JSON.stringify({ report, consoleIssueCount: consoleIssues.length, consoleIssues: issueSummary }, null, 2));
