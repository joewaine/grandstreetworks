# intake-api

The endpoint behind `/start/` on **both** sites — grandstreetworks.com and
grandstreetai.com. One service, two origins on the CORS allowlist.

It takes the completed diagnostic, validates it, emails it to the inbox, and
appends it to a JSONL file on the mounted disk.

## Why it exists rather than a form service

Formspree, Basin and the rest would have been live in ten minutes. Both sites
sell "no page builder, no plugin stack, no monthly platform fee" and hand the
client the repository at the end; renting a form handler on those pages is a
quiet contradiction nobody would catch but us. It also means the submissions
land somewhere we own, which is what makes the lead-registry step below
possible at all.

**Zero dependencies** for the same reason. `package.json` has no `dependencies`
key, the build command is empty, and there is nothing to audit or upgrade.
Node 18+ for global `fetch`.

## Running it locally

    node server.js                       # port 8080, no mail, no log

    INTAKE_LOG_PATH=/tmp/intake.jsonl PORT=8099 node server.js

`http://localhost:8777` (what `tools/serve.py` uses) and `:8000` are already on
the allowlist, so the local site can post to a local service without setting
`ALLOWED_ORIGINS`.

## Environment

| Variable | Required | Notes |
|---|---|---|
| `PORT` | no | Render sets it. Default 8080. |
| `RESEND_API_KEY` | to send mail | `sync: false` in the blueprint — set it in the dashboard, never commit it. |
| `MAIL_FROM` | no | Default `intake@send.grandstreetworks.com`. Must be a sender Resend has verified. |
| `MAIL_TO` | no | Default `joe@grandstreetworks.com`. |
| `INTAKE_LOG_PATH` | no | JSONL append target. Set to the mounted disk in production. |
| `ALLOWED_ORIGINS` | no | Comma-separated override of the built-in list. |

Without `RESEND_API_KEY` the service still validates, logs and answers 200 —
it just does not email. That is deliberate: a missing key should mean
"silently recorded", never "lost". `GET /health` reports which of the two are
live.

## Mail and the apex MX

Resend verifies a **subdomain** (`send.grandstreetworks.com`), so its SPF and
DKIM records sit under `send.` and never touch the apex `MX 1 smtp.google.com`
that Google Workspace needs. The two coexist. Do not point Resend at the apex.

`reply_to` is set to the prospect's address, so hitting reply in the inbox
goes to them rather than to us.

## Routes

| Route | Behaviour |
|---|---|
| `GET /health`, `GET /` | `{ok, mail, log}` — also the Render health check |
| `POST /submit` | The only real route |
| anything else | 404 |

## What it refuses

- **Unknown `Origin`** → 403. A request carrying an origin that is not on the
  list did not come from either site. A *missing* `Origin` is allowed through
  so curl and uptime checks work; the honeypot and rate limit cover that path.
- **Honeypot** (`company_website` non-empty) → 200 and dropped on the floor.
  The 200 is on purpose: the bot records a success and stops retrying.
- **Rate limit** — 8 per IP per 10 minutes, in memory, per instance. A brake on
  one bot hammering one address, not a distributed quota; a restart clearing it
  costs nothing.
- **Body over 32KB** → 413. **Fields over 2000 chars** are truncated.
- **No valid email or no name** → 400.

Everything a visitor typed passes through `clean()` exactly once, which strips
control characters before anything reaches an email header, an HTML body or a
log line, then bounds the length.

## When mail fails

The submission is still written to the log, with `mailError` attached. The
front end falls back to a fully composed `mailto:` carrying every answer, so
the worst case for the prospect is one extra click — but the record on disk
means a send outage does not erase the fact that somebody filled the form in.

## Lead registry

Submissions here are **inbound**, so the `leadcheck` gate before outreach does
not apply to them. What does apply: after these start arriving, this JSONL is a
new lead source the machine-wide registry cannot see. Add a loader for it to
`SOURCES` in `~/fractal/lead_registry/ingest.py`, then `leadcheck --refresh`.
Otherwise a prospect who wrote in here can still be cold-emailed by another
channel, which is exactly what the registry exists to prevent.
