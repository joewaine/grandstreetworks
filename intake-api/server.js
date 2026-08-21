/* Grand Street Works - intake service.
 *
 * One endpoint behind two static sites. grandstreetworks.com/start/ and
 * grandstreetai.com/start/ both POST their completed diagnostic here; this
 * validates it, emails it to the inbox, and optionally appends it to a
 * JSONL file on a mounted disk so there is a record that does not live in
 * a mailbox.
 *
 * No dependencies, deliberately. The whole point of the sites this serves
 * is that they have no plugin stack and no monthly platform fee, and a
 * form handler is not where to break that. Node 18+ for global fetch.
 *
 * Environment:
 *   PORT              listen port (Render sets this)
 *   RESEND_API_KEY    required to send mail; without it submissions are
 *                     still logged and still return 200, so a missing key
 *                     degrades to "silently recorded" rather than "lost"
 *   MAIL_FROM         verified sender, e.g. intake@send.grandstreetworks.com
 *   MAIL_TO           destination, e.g. joe@grandstreetworks.com
 *   INTAKE_LOG_PATH   optional JSONL path on a mounted disk
 *   ALLOWED_ORIGINS   optional comma-separated override of the CORS list
 */

'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 8080;
const RESEND_API_KEY = process.env.RESEND_API_KEY || '';
const MAIL_FROM = process.env.MAIL_FROM || 'intake@send.grandstreetworks.com';
const MAIL_TO = process.env.MAIL_TO || 'joe@grandstreetworks.com';
const LOG_PATH = process.env.INTAKE_LOG_PATH || '';

const ALLOWED_ORIGINS = new Set(
  (process.env.ALLOWED_ORIGINS ||
    [
      'https://grandstreetworks.com',
      'https://www.grandstreetworks.com',
      'https://grandstreetai.com',
      'https://www.grandstreetai.com',
      // tools/serve.py defaults to 8777; 8000 is python -m http.server.
      'http://localhost:8777',
      'http://127.0.0.1:8777',
      'http://localhost:8000',
      'http://127.0.0.1:8000'
    ].join(',')
  ).split(',').map((s) => s.trim()).filter(Boolean)
);

const MAX_BODY_BYTES = 32 * 1024;
const MAX_FIELD_CHARS = 2000;

/* ---------- rate limiting ------------------------------------------------
 * In-memory and per-instance, which is the right size for the problem: this
 * is a brake on a bot hammering one IP, not a distributed quota. A restart
 * clearing it costs nothing. */

const RATE_WINDOW_MS = 10 * 60 * 1000;
const RATE_MAX = 8;
const hits = new Map();

function rateLimited(ip) {
  const now = Date.now();
  const seen = (hits.get(ip) || []).filter((t) => now - t < RATE_WINDOW_MS);
  seen.push(now);
  hits.set(ip, seen);

  /* Opportunistic sweep so the map cannot grow without bound on a
   * long-lived instance. */
  if (hits.size > 5000) {
    for (const [key, times] of hits) {
      if (!times.some((t) => now - t < RATE_WINDOW_MS)) hits.delete(key);
    }
  }
  return seen.length > RATE_MAX;
}

function clientIp(req) {
  const fwd = req.headers['x-forwarded-for'];
  if (typeof fwd === 'string' && fwd.length) return fwd.split(',')[0].trim();
  return req.socket.remoteAddress || 'unknown';
}

/* ---------- helpers ------------------------------------------------------ */

/* Strip control characters before anything reaches an email header, an HTML
 * body or a log line, then bound the length. Everything a visitor typed
 * passes through here exactly once. */
function clean(value) {
  if (value == null) return '';
  return String(value)
    .replace(/[\u0000-\u001F\u007F]/g, ' ')
    .trim()
    .slice(0, MAX_FIELD_CHARS);
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        reject(Object.assign(new Error('body too large'), { statusCode: 413 }));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}

function send(res, status, payload, origin) {
  const headers = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-store'
  };
  if (origin) {
    headers['Access-Control-Allow-Origin'] = origin;
    headers.Vary = 'Origin';
  }
  res.writeHead(status, headers);
  res.end(JSON.stringify(payload));
}

/* ---------- formatting ---------------------------------------------------
 * The email is the product here - it is what Joe actually reads, on a phone,
 * deciding whether to spend an afternoon on a free rebuild. Lead with the
 * verdict and the contact details; put the raw answers underneath. */

function flatten(answers) {
  const rows = [];
  for (const [key, value] of Object.entries(answers || {})) {
    if (key === 'contact') continue;
    if (value == null || value === '') continue;
    if (Array.isArray(value)) {
      rows.push([key, value.map(clean).join(', ')]);
    } else if (typeof value === 'object') {
      for (const [sub, subValue] of Object.entries(value)) {
        if (subValue) rows.push([key + '.' + sub, clean(subValue)]);
      }
    } else {
      rows.push([key, clean(value)]);
    }
  }
  return rows;
}

function formatEmail(data) {
  const c = data.contact;
  const answerRows = flatten(data.answers);

  const subject =
    '[' + data.site + '] ' + (c.business || c.name) + ' - ' + data.recommendation;

  const textLines = [
    'Suggested: ' + data.recommendation + (data.secondary ? ' (then ' + data.secondary + ')' : ''),
    '',
    'Name:     ' + c.name,
    'Business: ' + (c.business || '-'),
    'Email:    ' + c.email,
    'Metro:    ' + (c.metro || '-'),
    'Phone:    ' + (c.phone || '-'),
    '',
    '--- answers ---',
    ...answerRows.map(([k, v]) => k + ': ' + v),
    '',
    c.notes ? '--- their note ---\n' + c.notes + '\n' : '',
    '--- context ---',
    'scores:   ' + JSON.stringify(data.scores),
    'page:     ' + data.page,
    'referrer: ' + (data.referrer || '-')
  ];

  const contactRows = [
    ['Name', c.name], ['Business', c.business], ['Email', c.email],
    ['Metro', c.metro], ['Phone', c.phone]
  ].filter(([, v]) => v);

  const html = [
    '<div style="font-family:ui-monospace,Menlo,Consolas,monospace;font-size:14px;line-height:1.55">',
    '<p style="margin:0 0 4px"><strong>Suggested:</strong> ' + escapeHtml(data.recommendation) +
      (data.secondary ? ' &rarr; then ' + escapeHtml(data.secondary) : '') + '</p>',
    '<table cellpadding="4" style="border-collapse:collapse;margin:16px 0">',
    contactRows.map(([k, v]) =>
      '<tr><td style="opacity:.6">' + k + '</td><td><strong>' +
      escapeHtml(v) + '</strong></td></tr>').join(''),
    '</table>',
    '<table cellpadding="4" style="border-collapse:collapse;margin:16px 0">',
    answerRows.map(([k, v]) =>
      '<tr><td style="opacity:.6">' + escapeHtml(k) + '</td><td>' +
      escapeHtml(v) + '</td></tr>').join(''),
    '</table>',
    c.notes ? '<p style="margin:16px 0"><em>' + escapeHtml(c.notes) + '</em></p>' : '',
    '<p style="opacity:.55;font-size:12px">' + escapeHtml(data.page) +
      ' &middot; ref ' + escapeHtml(data.referrer || '-') + '</p>',
    '</div>'
  ].join('');

  return { subject, text: textLines.join('\n'), html };
}

/* ---------- side effects ------------------------------------------------- */

async function mail(data) {
  if (!RESEND_API_KEY) {
    console.warn('RESEND_API_KEY unset - submission logged but not emailed');
    return;
  }
  const { subject, text, html } = formatEmail(data);
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: 'Bearer ' + RESEND_API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      from: MAIL_FROM,
      to: [MAIL_TO],
      /* So hitting reply in the inbox goes to the prospect, not to us. */
      reply_to: data.contact.email,
      subject,
      text,
      html
    })
  });
  if (!res.ok) {
    throw new Error('resend ' + res.status + ': ' + (await res.text()));
  }
}

function record(data) {
  if (!LOG_PATH) return;
  try {
    fs.mkdirSync(path.dirname(LOG_PATH), { recursive: true });
    fs.appendFileSync(LOG_PATH, JSON.stringify(data) + '\n');
  } catch (err) {
    /* A disk problem must not cost us the lead - the email is the primary
     * record and it has already been sent by this point. */
    console.error('intake log write failed:', err.message);
  }
}

/* ---------- validation --------------------------------------------------- */

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i;

function validate(raw) {
  if (!raw || typeof raw !== 'object') return { error: 'malformed payload' };

  const answers = raw.answers && typeof raw.answers === 'object' ? raw.answers : {};
  const nested = answers.contact && typeof answers.contact === 'object' ? answers.contact : {};
  const top = raw.contact && typeof raw.contact === 'object' ? raw.contact : {};
  const merged = Object.assign({}, top, nested);

  const out = {
    site: clean(raw.site) || 'unknown',
    recommendation: clean(raw.recommendation) || 'unspecified',
    secondary: clean(raw.secondary),
    scores: raw.scores && typeof raw.scores === 'object' ? raw.scores : {},
    answers,
    page: clean(raw.page),
    referrer: clean(raw.referrer),
    contact: {
      name: clean(merged.name),
      business: clean(merged.business),
      email: clean(merged.email),
      metro: clean(merged.metro),
      phone: clean(merged.phone),
      notes: clean(merged.notes)
    },
    receivedAt: new Date().toISOString()
  };

  if (!out.contact.email || !EMAIL_RE.test(out.contact.email)) {
    return { error: 'a valid email is required' };
  }
  if (!out.contact.name) return { error: 'a name is required' };

  return { value: out };
}

/* ---------- server ------------------------------------------------------- */

const server = http.createServer(async (req, res) => {
  const origin = req.headers.origin;
  const allowed = origin && ALLOWED_ORIGINS.has(origin) ? origin : null;

  if (req.method === 'OPTIONS') {
    if (!allowed) { res.writeHead(403); res.end(); return; }
    res.writeHead(204, {
      'Access-Control-Allow-Origin': allowed,
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
      Vary: 'Origin'
    });
    res.end();
    return;
  }

  const route = (req.url || '').split('?')[0];

  if (req.method === 'GET' && (route === '/health' || route === '/')) {
    send(res, 200, { ok: true, mail: Boolean(RESEND_API_KEY), log: Boolean(LOG_PATH) });
    return;
  }

  if (req.method !== 'POST' || route !== '/submit') {
    send(res, 404, { error: 'not found' }, allowed);
    return;
  }

  /* An unrecognised Origin is a request that did not come from either site.
   * Refuse it rather than emailing whatever it contains. A missing Origin
   * header is allowed through so curl and uptime checks still work; the
   * honeypot and the rate limit cover that path. */
  if (origin && !allowed) {
    send(res, 403, { error: 'origin not allowed' });
    return;
  }

  if (rateLimited(clientIp(req))) {
    send(res, 429, { error: 'too many submissions - email us instead' }, allowed);
    return;
  }

  let raw;
  try {
    raw = JSON.parse(await readBody(req));
  } catch (err) {
    send(res, err.statusCode || 400, { error: 'could not read that' }, allowed);
    return;
  }

  /* Honeypot. Answer 200 so the bot records a success and moves on, but do
   * nothing with it. Anything that reaches here is not a person. */
  if (clean(raw.company_website)) {
    send(res, 200, { ok: true }, allowed);
    return;
  }

  const { error, value } = validate(raw);
  if (error) {
    send(res, 400, { error }, allowed);
    return;
  }

  try {
    await mail(value);
    record(value);
    send(res, 200, { ok: true }, allowed);
  } catch (err) {
    console.error('intake submit failed:', err.message);
    /* Record it even though the mail failed - the front end falls back to a
     * composed mailto, but this means a send outage does not erase the fact
     * that somebody filled the form in. */
    record(Object.assign({}, value, { mailError: err.message }));
    send(res, 502, { error: 'could not deliver that' }, allowed);
  }
});

server.listen(PORT, () => {
  console.log('intake listening on ' + PORT + '; mail=' + Boolean(RESEND_API_KEY) +
    ' log=' + (LOG_PATH || 'off'));
});
