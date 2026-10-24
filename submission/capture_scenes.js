const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SUBMISSION_DIR = path.resolve(__dirname);
const DEBUG_PORT = 9222;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.id = 1;
    this.callbacks = new Map();
  }

  async connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = () => resolve();
      this.ws.onerror = (err) => reject(err);
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && this.callbacks.has(msg.id)) {
          const cb = this.callbacks.get(msg.id);
          this.callbacks.delete(msg.id);
          if (msg.error) cb.reject(msg.error);
          else cb.resolve(msg.result);
        }
      };
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.id++;
      this.callbacks.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression) {
    const res = await this.send('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true
    });
    return res.result?.value;
  }

  async captureScreenshot(outputPath) {
    const res = await this.send('Page.captureScreenshot', {
      format: 'png',
      captureBeyondViewport: false
    });
    fs.writeFileSync(outputPath, Buffer.from(res.data, 'base64'));
    console.log(`Saved screenshot: ${outputPath}`);
  }

  close() {
    if (this.ws) this.ws.close();
  }
}

async function run() {
  console.log('Resetting backend state...');
  try {
    await fetch('http://127.0.0.1:8081/mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: 'home' })
    });
    await fetch('http://127.0.0.1:8081/alerts/clear', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alert_id: 'all' })
    });
  } catch (e) {
    console.error('Error resetting backend:', e);
  }

  console.log('Launching Chrome with remote debugging on port ' + DEBUG_PORT);
  const chromeProc = spawn(CHROME_PATH, [
    '--headless=new',
    `--remote-debugging-port=${DEBUG_PORT}`,
    '--window-size=1920,1080',
    '--hide-scrollbars',
    '--disable-gpu',
    '--user-data-dir=' + path.join(SUBMISSION_DIR, '.chrome_profile'),
    'http://localhost:5173'
  ]);

  let cdp = null;
  try {
    // Wait for Chrome debugging endpoint
    let targets = null;
    for (let i = 0; i < 30; i++) {
      await sleep(500);
      try {
        const res = await fetch(`http://127.0.0.1:${DEBUG_PORT}/json`);
        targets = await res.json();
        if (targets && targets.length > 0) break;
      } catch (e) {}
    }

    if (!targets) throw new Error('Could not connect to Chrome debugging endpoint');

    const pageTarget = targets.find(t => t.type === 'page' && t.url.includes('5173')) || targets.find(t => t.type === 'page');
    if (!pageTarget || !pageTarget.webSocketDebuggerUrl) throw new Error('No page target found');

    console.log('Connecting CDP to page:', pageTarget.url);
    cdp = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await cdp.connect();

    // Enable Page
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');

    console.log('Waiting for initial data load...');
    await sleep(2500);

    // SCENE 2: Clean Dashboard
    console.log('Capturing Scene 2: Clean Dashboard...');
    await cdp.captureScreenshot(path.join(SUBMISSION_DIR, 'scene2_dashboard.png'));

    // SCENE 3: User Intent - Set Temporary Watch
    console.log('Executing Scene 3: Watch front door for 30 minutes...');
    await cdp.evaluate(`
      (function() {
        const input = document.querySelector('input[placeholder*="Say something"]');
        if (!input) return 'Input not found';
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(input, 'Watch the front door for 30 minutes.');
        input.dispatchEvent(new Event('input', { bubbles: true }));
        const form = input.closest('form');
        form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        return 'Submitted watch utterance';
      })()
    `);
    await sleep(3000);
    console.log('Capturing Scene 3: Watch created with countdown...');
    await cdp.captureScreenshot(path.join(SUBMISSION_DIR, 'scene3_watch.png'));

    // SCENE 4A: Event Ingestion - Simulate Doorbell
    console.log('Executing Scene 4A: Simulate Doorbell...');
    await cdp.evaluate(`
      (function() {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Doorbell'));
        if (btn) { btn.click(); return 'Clicked doorbell'; }
        return 'Doorbell button not found';
      })()
    `);
    await sleep(3000);
    console.log('Capturing Scene 4A: Doorbell alert triggered...');
    await cdp.captureScreenshot(path.join(SUBMISSION_DIR, 'scene4_alert.png'));

    // SCENE 4B: Mode Change & Focus Mode Suppression
    console.log('Executing Scene 4B: Set Focus Mode & Simulate Motion...');
    await cdp.evaluate(`
      (function() {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim().toLowerCase() === 'focus');
        if (btn) btn.click();
        return 'Set focus mode';
      })()
    `);
    await sleep(2000);

    await cdp.evaluate(`
      (function() {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Motion'));
        if (btn) btn.click();
        return 'Clicked motion';
      })()
    `);
    await sleep(3000);
    console.log('Capturing Scene 4B: Focus mode with quiet context update...');
    await cdp.captureScreenshot(path.join(SUBMISSION_DIR, 'scene4_focus.png'));

    // SCENE 5: Conversational Recall via MCP
    console.log('Executing Scene 5: What happened at the front door?');
    await cdp.evaluate(`
      (function() {
        const input = document.querySelector('input[placeholder*="Say something"]');
        if (!input) return 'Input not found';
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(input, 'What happened at the front door?');
        input.dispatchEvent(new Event('input', { bubbles: true }));
        const form = input.closest('form');
        form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        return 'Submitted recall utterance';
      })()
    `);
    await sleep(3500);
    console.log('Capturing Scene 5: Conversational recall summary...');
    await cdp.captureScreenshot(path.join(SUBMISSION_DIR, 'scene5_recall.png'));

    console.log('All real app scenes captured successfully!');
  } finally {
    if (cdp) cdp.close();
    chromeProc.kill('SIGKILL');
  }
}

run().catch(err => {
  console.error('Capture pipeline failed:', err);
  process.exit(1);
});
