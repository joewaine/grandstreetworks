/* Grand Street Works / Grand Street AI — stepped intake diagnostic.
   Zero dependencies. The engine is generic; everything site-specific
   (questions, options, scoring weights, verdict copy) lives in the
   window.INTAKE_CONFIG object defined by the page that loads this file,
   so both sites run the same engine with different content.

   Shared with grandstreetai as a copy, not a link — same rule as the
   design system. Change it in both places or don't change it. */

(function () {
  'use strict';

  var cfg = window.INTAKE_CONFIG;
  if (!cfg) return;

  var root = document.getElementById('intake');
  if (!root) return;

  var STORAGE_KEY = 'gsw-intake-' + cfg.site;
  var answers = restore();
  var index = 0;
  var submitting = false;

  /* ---------- persistence -------------------------------------------
     A half-finished diagnostic survives a refresh or an accidental back
     gesture. Session-scoped on purpose: it should not follow someone
     into next week. Every access is guarded — private windows and
     storage-blocking settings throw on the accessor itself. */

  function restore() {
    try {
      var raw = window.sessionStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw) || {};
    } catch (e) { /* storage unavailable — run without it */ }
    return {};
  }

  function persist() {
    try {
      window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(answers));
    } catch (e) { /* non-fatal */ }
  }

  function clearPersisted() {
    try { window.sessionStorage.removeItem(STORAGE_KEY); } catch (e) {}
  }

  /* ---------- helpers ------------------------------------------------ */

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function qs(name) {
    var match = new RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
    return match ? decodeURIComponent(match[1].replace(/\+/g, ' ')) : '';
  }

  /* Accepts what an owner actually types: "acme.com", "www.acme.com",
     "https://acme.com/about". Rejects anything without a dot in the host,
     which is the only check worth making client-side — the server does
     the rest and a human reads it either way. */
  function normaliseUrl(raw) {
    var value = String(raw || '').trim();
    if (!value) return '';
    value = value.replace(/^https?:\/\//i, '').replace(/^\/+/, '');
    var host = value.split(/[\/?#]/)[0];
    if (!/^[a-z0-9.-]+\.[a-z]{2,}$/i.test(host)) return null;
    return 'https://' + value;
  }

  function validEmail(raw) {
    return /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(String(raw || '').trim());
  }

  var steps = cfg.steps;

  /* ---------- scoring ------------------------------------------------
     Every option may carry a `scores` map. The engine sums them across
     all answered steps, then hands the totals to the config's optional
     adjust() hook for site-specific nudges (site age, headcount) before
     picking a winner. Ties break by the order services are declared,
     which puts the cheapest honest answer first. */

  function computeVerdict() {
    var totals = {};
    Object.keys(cfg.services).forEach(function (key) { totals[key] = 0; });

    steps.forEach(function (step) {
      if (!step.options) return;
      var picked = answers[step.id];
      if (picked == null) return;
      var list = Array.isArray(picked) ? picked : [picked];
      list.forEach(function (value, rank) {
        var option = step.options.filter(function (o) { return o.value === value; })[0];
        if (!option || !option.scores) return;
        /* First pick counts full, later picks count half — the order
           someone ranks their problems in is signal, not noise. */
        var weight = rank === 0 ? 1 : 0.5;
        Object.keys(option.scores).forEach(function (svc) {
          if (totals[svc] == null) return;
          totals[svc] += option.scores[svc] * weight;
        });
      });
    });

    if (typeof cfg.adjust === 'function') cfg.adjust(totals, answers);

    var order = Object.keys(cfg.services);
    var ranked = order.slice().sort(function (a, b) {
      if (totals[b] !== totals[a]) return totals[b] - totals[a];
      return order.indexOf(a) - order.indexOf(b);
    });

    var primary = ranked[0];
    var secondary = null;
    /* Only name a second thing when it is genuinely close and is not
       the "nothing" verdict. Recommending everything recommends nothing. */
    if (ranked[1] && totals[ranked[1]] > 0 && totals[ranked[1]] >= totals[primary] * 0.55 &&
        !cfg.services[ranked[1]].terminal && !cfg.services[primary].terminal) {
      secondary = ranked[1];
    }

    return { primary: primary, secondary: secondary, totals: totals };
  }

  /* ---------- analytics ---------------------------------------------
     Umami, when it is there. It is deferred, ad-blockable and entirely
     optional, so every call is guarded: the diagnostic must not care
     whether it loaded. These three events are the funnel that answers
     the question the plain mailto never could - which trades start the
     read, which finish it, and which actually send. */

  var pendingEvents = [];
  var flushed = false;

  function track(event, data) {
    pendingEvents.push([event, data || {}]);
    flushEvents();
  }

  function flushEvents() {
    var umami = window.umami;
    if (!umami || typeof umami.track !== 'function') return;
    while (pendingEvents.length) {
      var item = pendingEvents.shift();
      try {
        umami.track(item[0], item[1]);
      } catch (e) { /* analytics must never break the form */ }
    }
    flushed = true;
  }

  /* Umami's tag is deferred, so it executes AFTER this file - which runs
     during parsing - and window.umami does not exist yet when the first
     question renders. Without this queue the "started" event, the top of
     the funnel and the only one that counts everybody, would never fire.
     If the tag is blocked or down the queue simply stays full and nothing
     else notices. */
  if (!flushed) {
    window.addEventListener('load', flushEvents);
    window.setTimeout(flushEvents, 2000);
  }

  /* ---------- rendering ---------------------------------------------- */

  var progressCount, progressFill;

  function renderChrome() {
    var bar = el('div', 'intake-progress');
    progressCount = el('span', 'label', '');
    var track = el('div', 'intake-progress-bar');
    progressFill = el('span');
    progressFill.style.width = '0%';
    track.appendChild(progressFill);
    var exit = el('a', 'label');
    exit.href = cfg.homeHref || '/';
    exit.textContent = 'Leave';
    exit.style.textDecoration = 'underline';
    bar.appendChild(progressCount);
    bar.appendChild(track);
    bar.appendChild(exit);
    root.appendChild(bar);
  }

  function updateProgress() {
    var total = steps.length;
    var human = Math.min(index + 1, total);
    progressCount.textContent =
      String(human).padStart(2, '0') + ' / ' + String(total).padStart(2, '0');
    progressFill.style.width = ((index) / (total - 1) * 100).toFixed(1) + '%';
  }

  var stage;

  function render() {
    if (!stage) {
      stage = el('div');
      root.appendChild(stage);
    }
    stage.innerHTML = '';
    var step = steps[index];
    var node = el('section', 'intake-step');

    var eyebrow = el('span', 'label');
    eyebrow.style.display = 'block';
    eyebrow.style.marginBottom = '1.5rem';
    eyebrow.textContent = step.eyebrow || '';
    node.appendChild(eyebrow);

    node.appendChild(el('h2', null, typeof step.title === 'function'
      ? step.title(answers) : step.title));

    if (step.help) {
      node.appendChild(el('p', 'intake-help text-large',
        typeof step.help === 'function' ? step.help(answers) : step.help));
    }

    var builder = builders[step.type];
    if (builder) builder(node, step);

    stage.appendChild(node);
    updateProgress();

    /* Keep the viewport at the top of the new question rather than
       wherever the previous one happened to leave it. */
    window.scrollTo({ top: 0, behavior: index === 0 ? 'auto' : 'smooth' });

    var focusTarget = node.querySelector('input:not([type=hidden]), textarea, button');
    if (focusTarget && step.type !== 'result' && window.innerWidth > 640) {
      try { focusTarget.focus({ preventScroll: true }); } catch (e) {}
    }
  }

  function navRow(node, step, opts) {
    opts = opts || {};
    var nav = el('div', 'intake-nav');

    var next = el('button', 'intake-btn', opts.nextLabel || step.nextLabel || 'Continue →');
    next.type = 'button';
    next.addEventListener('click', function () {
      if (opts.validate && !opts.validate()) return;
      advance();
    });
    nav.appendChild(next);

    if (index > 0) {
      var back = el('button', 'intake-btn ghost', '← Back');
      back.type = 'button';
      back.addEventListener('click', function () { index -= 1; render(); });
      nav.appendChild(back);
    }

    if (step.skipLabel) {
      var skip = el('button', 'intake-skip', step.skipLabel);
      skip.type = 'button';
      skip.addEventListener('click', function () {
        answers[step.id] = step.skipValue != null ? step.skipValue : '';
        persist();
        advance();
      });
      nav.appendChild(skip);
    }

    node.appendChild(nav);
    return { next: next };
  }

  function advance() {
    if (index < steps.length - 1) {
      index += 1;
      render();
    }
  }

  var builders = {};

  /* Free-text fields — one or several on a single screen. */
  builders.fields = function (node, step) {
    var errors = {};

    step.fields.forEach(function (field) {
      var wrap = el('div', 'intake-field');
      var id = 'f-' + step.id + '-' + field.name;
      var label = el('label', null, field.label);
      label.setAttribute('for', id);
      wrap.appendChild(label);

      var input = field.multiline
        ? el('textarea')
        : el('input');
      if (!field.multiline) input.type = field.inputType || 'text';
      input.id = id;
      input.placeholder = field.placeholder || '';
      if (field.autocomplete) input.setAttribute('autocomplete', field.autocomplete);
      input.value = (answers[step.id] && answers[step.id][field.name]) || '';
      input.addEventListener('input', function () {
        answers[step.id] = answers[step.id] || {};
        answers[step.id][field.name] = input.value;
        persist();
        errors[field.name].hidden = true;
      });
      input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !field.multiline) {
          e.preventDefault();
          node.querySelector('.intake-btn').click();
        }
      });
      wrap.appendChild(input);

      var err = el('p', 'intake-field-error');
      err.hidden = true;
      errors[field.name] = err;
      wrap.appendChild(err);

      node.appendChild(wrap);
    });

    navRow(node, step, {
      validate: function () {
        var ok = true;
        step.fields.forEach(function (field) {
          if (!field.required) return;
          var value = ((answers[step.id] || {})[field.name] || '').trim();
          if (!value) {
            errors[field.name].textContent = field.requiredMessage || 'This one we do need.';
            errors[field.name].hidden = false;
            ok = false;
          }
        });
        return ok;
      }
    });
  };

  /* The URL capture. Its own type because it normalises and because
     "we don't have a site" is a real and useful answer. */
  builders.url = function (node, step) {
    var wrap = el('div', 'intake-field');
    var input = el('input');
    input.type = 'text';
    input.id = 'f-url';
    input.placeholder = step.placeholder || 'yourfirm.com';
    input.setAttribute('autocomplete', 'url');
    input.setAttribute('inputmode', 'url');
    var label = el('label', null, step.fieldLabel || 'Your website');
    label.setAttribute('for', 'f-url');
    input.value = answers[step.id] || '';

    var err = el('p', 'intake-field-error');
    err.hidden = true;

    input.addEventListener('input', function () { err.hidden = true; });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); node.querySelector('.intake-btn').click(); }
    });

    wrap.appendChild(label);
    wrap.appendChild(input);
    wrap.appendChild(err);
    node.appendChild(wrap);

    navRow(node, step, {
      validate: function () {
        var raw = input.value.trim();
        if (!raw) {
          err.textContent = 'Type it in, or use the link below if there isn\'t one.';
          err.hidden = false;
          return false;
        }
        var url = normaliseUrl(raw);
        if (url === null) {
          err.textContent = 'That doesn\'t look like a web address. Try acmeroofing.com';
          err.hidden = false;
          return false;
        }
        answers[step.id] = url;
        persist();
        return true;
      }
    });
  };

  /* Trade picker — doubles as the key into the reference builds, so the
     verdict can link someone straight at six homepages in their trade. */
  builders.trades = function (node, step) {
    var grid = el('div', 'intake-trades');
    step.options.forEach(function (option) {
      var btn = el('button', null, option.label);
      btn.type = 'button';
      if (answers[step.id] === option.value) btn.classList.add('is-on');
      btn.addEventListener('click', function () {
        answers[step.id] = option.value;
        persist();
        advance();
      });
      grid.appendChild(btn);
    });
    node.appendChild(grid);
    navRow(node, step, {
      nextLabel: 'Continue →',
      validate: function () {
        if (!answers[step.id]) {
          answers[step.id] = 'other';
          persist();
        }
        return true;
      }
    });
  };

  /* Single-choice and multi-choice share one renderer; `max` decides. */
  function choiceBuilder(multi) {
    return function (node, step) {
      var max = multi ? (step.max || 2) : 1;
      var current = answers[step.id];
      var selected = multi
        ? (Array.isArray(current) ? current.slice() : [])
        : (current != null ? [current] : []);

      var list = el('div', 'intake-options' + (step.columns === 2 ? ' cols-2' : ''));
      var err = el('p', 'intake-field-error');
      err.hidden = true;

      step.options.forEach(function (option) {
        var row = el('label', 'intake-option');
        var marker = el('span', 'marker');
        var body = el('span');
        body.appendChild(el('span', 'opt-title', option.label));
        if (option.note) body.appendChild(el('span', 'opt-note', option.note));

        var input = el('input');
        input.type = multi ? 'checkbox' : 'radio';
        input.name = step.id;
        input.value = option.value;

        function paint() {
          var pos = selected.indexOf(option.value);
          var on = pos > -1;
          row.classList.toggle('is-on', on);
          input.checked = on;
          /* In a ranked multi-select the number is the whole point —
             it tells the reader their first pick outweighs the second. */
          marker.textContent = on ? (multi && max > 1 ? String(pos + 1) : '×') : '';
        }

        row.addEventListener('click', function (e) {
          e.preventDefault();
          var pos = selected.indexOf(option.value);
          if (pos > -1) {
            selected.splice(pos, 1);
          } else if (multi) {
            if (selected.length >= max) selected.shift();
            selected.push(option.value);
          } else {
            selected = [option.value];
          }
          answers[step.id] = multi ? selected.slice() : (selected[0] != null ? selected[0] : null);
          persist();
          err.hidden = true;
          Array.prototype.forEach.call(list.querySelectorAll('.intake-option'), function (r) {
            if (r.repaint) r.repaint();
          });
          if (!multi) advance();
        });

        row.repaint = paint;
        row.appendChild(input);
        row.appendChild(marker);
        row.appendChild(body);
        paint();
        list.appendChild(row);
      });

      node.appendChild(list);
      node.appendChild(err);

      navRow(node, step, {
        validate: function () {
          if (!step.optional && selected.length === 0) {
            err.textContent = step.requiredMessage || 'Pick the closest one.';
            err.hidden = false;
            return false;
          }
          return true;
        }
      });
    };
  }

  builders.choice = choiceBuilder(false);
  builders.multi = choiceBuilder(true);

  /* ---------- the verdict + contact capture --------------------------
     Deliberately ungated: the recommendation is shown before anything is
     asked for. A site whose pitch is "no call required, no obligation"
     cannot put the answer behind an email field. */

  builders.result = function (node, step) {
    var verdict = computeVerdict();
    var service = cfg.services[verdict.primary];

    track('intake_verdict', {
      site: cfg.site,
      recommendation: verdict.primary,
      trade: answers.trade || '',
      terminal: service.terminal ? 'yes' : 'no'
    });

    var card = el('div', 'intake-verdict');
    var head = el('div', 'intake-verdict-head');
    var kicker = el('span', 'label');
    kicker.textContent = service.kicker || 'What we\'d suggest';
    head.appendChild(kicker);
    head.appendChild(el('h3', null, service.headline));
    card.appendChild(head);

    var body = el('div', 'intake-verdict-body');
    (typeof service.body === 'function' ? service.body(answers) : service.body)
      .forEach(function (para) {
        var p = el('p', null, para);
        body.appendChild(p);
      });

    if (service.links) {
      service.links(answers).forEach(function (link) {
        if (!link) return;
        var a = el('a', 'callout', link.label);
        a.href = link.href;
        a.style.marginRight = '0.75rem';
        body.appendChild(a);
      });
    }
    card.appendChild(body);

    if (verdict.secondary) {
      var second = cfg.services[verdict.secondary];
      var sec = el('div', 'intake-secondary');
      var secLabel = el('span', 'label');
      secLabel.textContent = 'And after that';
      sec.appendChild(secLabel);
      sec.appendChild(el('p', null, second.secondaryLine || second.headline));
      card.appendChild(sec);
    }

    node.appendChild(card);

    if (service.terminal) {
      /* The "you don't need us" branch still offers a way to talk, but
         it does not ask for a phone number or pretend to be a lead form. */
      var out = el('div', 'intake-nav');
      var back = el('button', 'intake-btn ghost', '← Change an answer');
      back.type = 'button';
      back.addEventListener('click', function () { index -= 1; render(); });
      out.appendChild(back);
      var mail = el('a', 'intake-btn');
      mail.href = 'mailto:' + cfg.fallbackEmail + '?subject=' +
        encodeURIComponent(cfg.fallbackSubject || 'Question');
      mail.textContent = 'Email us anyway →';
      mail.style.textDecoration = 'none';
      out.appendChild(mail);
      node.appendChild(out);
      return;
    }

    renderContact(node, verdict);
  };

  function renderContact(node, verdict) {
    var heading = el('h2', null, cfg.contact.title);
    heading.style.marginTop = '4rem';
    node.appendChild(heading);
    node.appendChild(el('p', 'intake-help text-large', cfg.contact.help));

    var state = answers.contact || {};
    var inputs = {};
    var errs = {};

    cfg.contact.fields.forEach(function (field) {
      var wrap = el('div', 'intake-field');
      var id = 'c-' + field.name;
      var label = el('label', null, field.label + (field.required ? '' : ' (optional)'));
      label.setAttribute('for', id);
      wrap.appendChild(label);

      var input = field.multiline ? el('textarea') : el('input');
      if (!field.multiline) input.type = field.inputType || 'text';
      input.id = id;
      input.placeholder = field.placeholder || '';
      if (field.autocomplete) input.setAttribute('autocomplete', field.autocomplete);
      input.value = state[field.name] || '';
      input.addEventListener('input', function () {
        state[field.name] = input.value;
        answers.contact = state;
        persist();
        errs[field.name].hidden = true;
      });
      wrap.appendChild(input);

      var err = el('p', 'intake-field-error');
      err.hidden = true;
      errs[field.name] = err;
      inputs[field.name] = input;
      wrap.appendChild(err);
      node.appendChild(wrap);
    });

    /* Honeypot. Real people never fill this; bots fill everything. */
    var trap = el('div');
    trap.style.cssText = 'position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden';
    trap.setAttribute('aria-hidden', 'true');
    var trapInput = el('input');
    trapInput.type = 'text';
    trapInput.name = 'company_website';
    trapInput.tabIndex = -1;
    trapInput.setAttribute('autocomplete', 'off');
    trap.appendChild(trapInput);
    node.appendChild(trap);

    var status = el('p', 'intake-help');
    status.hidden = true;

    var nav = el('div', 'intake-nav');
    var submit = el('button', 'intake-btn', cfg.contact.submitLabel);
    submit.type = 'button';
    var back = el('button', 'intake-btn ghost', '← Change an answer');
    back.type = 'button';
    back.addEventListener('click', function () { index -= 1; render(); });

    submit.addEventListener('click', function () {
      if (submitting) return;
      var ok = true;
      cfg.contact.fields.forEach(function (field) {
        var value = (state[field.name] || '').trim();
        if (field.required && !value) {
          errs[field.name].textContent = 'We need this one to reply.';
          errs[field.name].hidden = false;
          ok = false;
        } else if (field.inputType === 'email' && value && !validEmail(value)) {
          errs[field.name].textContent = 'That address has a typo in it.';
          errs[field.name].hidden = false;
          ok = false;
        }
      });
      if (!ok) return;

      submitting = true;
      submit.disabled = true;
      submit.textContent = 'Sending…';
      status.hidden = true;

      send(verdict, trapInput.value).then(function () {
        clearPersisted();
        track('intake_sent', {
          site: cfg.site,
          recommendation: verdict.primary,
          trade: answers.trade || ''
        });
        showDone(node, verdict);
      }).catch(function () {
        track('intake_send_failed', { site: cfg.site });
        /* The endpoint is down or blocked. Rather than lose the lead,
           hand them a fully composed email — every answer already in the
           body — so the worst case is one extra click, not a dead form. */
        submitting = false;
        submit.disabled = false;
        submit.textContent = cfg.contact.submitLabel;
        status.hidden = false;
        status.innerHTML = '';
        status.appendChild(document.createTextNode(
          'That didn\'t go through — our end, not yours. '));
        var a = el('a', null, 'Send it as an email instead →');
        a.href = mailtoFallback(verdict);
        a.style.textDecoration = 'underline';
        status.appendChild(a);
      });
    });

    nav.appendChild(submit);
    nav.appendChild(back);
    node.appendChild(nav);
    node.appendChild(status);
  }

  function payload(verdict, trap) {
    return {
      site: cfg.site,
      recommendation: verdict.primary,
      secondary: verdict.secondary,
      scores: verdict.totals,
      answers: answers,
      referrer: document.referrer || '',
      page: window.location.href,
      company_website: trap || ''
    };
  }

  function send(verdict, trap) {
    if (!cfg.endpoint) return Promise.reject(new Error('no endpoint configured'));
    var controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
    var timer = controller ? window.setTimeout(function () { controller.abort(); }, 20000) : null;

    return window.fetch(cfg.endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload(verdict, trap)),
      signal: controller ? controller.signal : undefined
    }).then(function (res) {
      if (timer) window.clearTimeout(timer);
      if (!res.ok) throw new Error('intake responded ' + res.status);
      return res;
    });
  }

  function mailtoFallback(verdict) {
    var lines = [];
    steps.forEach(function (step) {
      if (step.type === 'result') return;
      var value = answers[step.id];
      if (value == null || value === '') return;
      var label = step.summaryLabel || (typeof step.title === 'function' ? step.id : step.title);
      if (Array.isArray(value)) {
        value = value.map(function (v) { return labelFor(step, v); }).join(', ');
      } else if (typeof value === 'object') {
        value = Object.keys(value).map(function (k) { return k + ': ' + value[k]; }).join(' · ');
      } else {
        value = labelFor(step, value);
      }
      lines.push(label + ': ' + value);
    });
    var contact = answers.contact || {};
    Object.keys(contact).forEach(function (k) {
      if (contact[k]) lines.push(k + ': ' + contact[k]);
    });
    lines.push('Suggested: ' + verdict.primary);
    return 'mailto:' + cfg.fallbackEmail +
      '?subject=' + encodeURIComponent(cfg.contact.mailSubject || 'Intake') +
      '&body=' + encodeURIComponent(lines.join('\n'));
  }

  function labelFor(step, value) {
    if (!step.options) return value;
    var match = step.options.filter(function (o) { return o.value === value; })[0];
    return match ? match.label : value;
  }

  function showDone(node, verdict) {
    node.innerHTML = '';
    var eyebrow = el('span', 'label');
    eyebrow.style.display = 'block';
    eyebrow.style.marginBottom = '1.5rem';
    eyebrow.textContent = 'Sent // ' + new Date().toISOString().slice(0, 10);
    node.appendChild(eyebrow);
    node.appendChild(el('h2', null, cfg.contact.doneTitle));
    node.appendChild(el('p', 'intake-help text-large', cfg.contact.doneBody));

    var nav = el('div', 'intake-nav');
    (cfg.contact.doneLinks || []).forEach(function (link, i) {
      var a = el('a', 'intake-btn' + (i > 0 ? ' ghost' : ''), link.label);
      a.href = link.href;
      a.style.textDecoration = 'none';
      nav.appendChild(a);
    });
    node.appendChild(nav);
    progressFill.style.width = '100%';
  }

  /* ---------- boot --------------------------------------------------- */

  /* Steps can arrive pre-answered in the query string: both sites' heroes
     post their first answer, and the work galleries add the trade they were
     showing. Asking someone a question they just answered on the previous
     page is the fastest way to lose them, so anything seeded here is
     accepted and skipped past.

     Which parameter feeds which step is derived from the step itself - a
     url step reads ?url, a trade picker reads ?trade, and a fields step
     reads one parameter per field name - so a config gets this for free
     without declaring anything. */
  seedFromQuery();

  function seedParamFor(step) {
    if (step.seedParam) return step.seedParam;
    if (step.type === 'url') return 'url';
    if (step.type === 'trades') return 'trade';
    return null;
  }

  function seedFromQuery() {
    steps.forEach(function (step) {
      if (step.type === 'fields') {
        step.fields.forEach(function (field) {
          var raw = qs(field.seedParam || field.name);
          if (!raw) return;
          answers[step.id] = answers[step.id] || {};
          answers[step.id][field.name] = raw.slice(0, 200);
        });
        return;
      }

      var param = seedParamFor(step);
      if (!param) return;
      var value = qs(param);
      if (!value) return;

      if (step.type === 'url') {
        var normalised = normaliseUrl(value);
        if (normalised) answers[step.id] = normalised;
        return;
      }

      /* Only honour a value the picker actually offers - the query string is
         user-editable and ends up in an email a human reads. */
      if (step.options && step.options.some(function (o) { return o.value === value; })) {
        answers[step.id] = value;
      }
    });

    persist();

    /* Land on the first question that still has no answer, never past the
       last question into the verdict - a seeded first answer should not skip
       someone straight to a recommendation built from nothing. */
    var last = steps.length - 1;
    for (var i = 0; i < last; i++) {
      if (!isAnswered(answers[steps[i].id])) { index = i; return; }
    }
    index = last - 1;
  }

  function isAnswered(value) {
    if (value == null || value === '') return false;
    if (Array.isArray(value)) return value.length > 0;
    if (typeof value === 'object') {
      return Object.keys(value).some(function (k) {
        return String(value[k] || '').trim() !== '';
      });
    }
    return true;
  }

  renderChrome();
  render();
  track('intake_started', { site: cfg.site, from: index > 0 ? 'seeded' : 'cold' });
})();
