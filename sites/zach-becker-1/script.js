/* Zach Becker — Lake Light. Three responsibilities, nothing else:
   1. the mobile navigation drawer,
   2. the hero video (only where motion, bandwidth and viewport justify it),
   3. contact-form validation and delivery. */
(function () {
  "use strict";

  /* ---------- 1. navigation ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
      document.body.classList.toggle("nav-open", open);
      toggle.querySelector(".nav-toggle-label").textContent = open ? "Close" : "Menu";
      if (open) nav.querySelector("a").focus();
    };
    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) { setOpen(false); toggle.focus(); }
    });
    window.matchMedia("(min-width: 1081px)").addEventListener("change", function (m) {
      if (m.matches) setOpen(false);
    });
  }

  /* ---------- 2. hero video ---------- */
  var video = document.querySelector(".hero-video");
  var pause = document.querySelector(".hero-pause");
  if (video && pause) {
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var conn = navigator.connection || {};
    var saveData = conn.saveData === true || /(^|-)2g$/.test(conn.effectiveType || "");
    if (!reduced && !saveData && typeof video.play === "function") {
      var wide = window.matchMedia("(min-width: 900px)").matches;
      video.src = wide ? video.dataset.srcWide : video.dataset.srcNarrow;
      video.load();
      var attempt = video.play();
      if (attempt && typeof attempt.then === "function") {
        attempt.then(function () {
          video.classList.add("is-playing");
          pause.hidden = false;
        }).catch(function () { /* autoplay refused: the still stays */ });
      }
      pause.addEventListener("click", function () {
        var paused = pause.getAttribute("aria-pressed") === "true";
        if (paused) { video.play(); } else { video.pause(); }
        pause.setAttribute("aria-pressed", String(!paused));
        pause.querySelector(".hero-pause-label").textContent = paused ? "Pause video" : "Play video";
      });
      document.addEventListener("visibilitychange", function () {
        if (document.hidden) video.pause();
        else if (pause.getAttribute("aria-pressed") !== "true") video.play();
      });
    }
  }

  /* ---------- 3. contact form ---------- */
  var form = document.getElementById("contact-form");
  if (!form) return;
  var status = form.querySelector(".form-status");
  var SUCCESS = "Thank you! Your message has been sent.";
  var FAILURE = "Sorry, we were unable to send your message at this time. Please try again.";

  var show = function (kind, text) {
    status.textContent = text;
    status.className = "form-status is-" + kind;
    status.hidden = false;
  };

  var validate = function () {
    var ok = true, first = null;
    form.querySelectorAll("[required]").forEach(function (el) {
      var err = document.getElementById(el.id + "-err");
      var bad = !el.value.trim() || (el.type === "email" && !el.validity.valid);
      el.setAttribute("aria-invalid", bad ? "true" : "false");
      if (err) err.hidden = !bad;
      if (bad) { ok = false; if (!first) first = el; }
    });
    if (first) first.focus();
    return ok;
  };

  form.querySelectorAll("[required]").forEach(function (el) {
    el.addEventListener("input", function () {
      if (el.getAttribute("aria-invalid") === "true" && el.value.trim() && el.validity.valid) {
        el.setAttribute("aria-invalid", "false");
        var err = document.getElementById(el.id + "-err");
        if (err) err.hidden = true;
      }
    });
  });

  form.addEventListener("reset", function () {
    form.querySelectorAll("[aria-invalid]").forEach(function (el) { el.removeAttribute("aria-invalid"); });
    form.querySelectorAll(".field-error").forEach(function (el) { el.hidden = true; });
    status.hidden = true;
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    status.hidden = true;
    if (!validate()) return;
    var data = new FormData(form);
    var endpoint = form.dataset.endpoint;

    if (!endpoint) {
      /* No delivery endpoint is configured (see README). Hand the message to
         the visitor's mail client instead of pretending it was sent. */
      var body = ["Name: " + data.get("first_name") + " " + data.get("last_name"),
                  "Email: " + data.get("email"),
                  "Phone: " + (data.get("phone") || "—"),
                  "Contact me by: " + data.get("contact_by"), "", data.get("message")].join("\n");
      window.location.href = "mailto:" + form.dataset.mailto +
        "?subject=" + encodeURIComponent(data.get("subject")) +
        "&body=" + encodeURIComponent(body);
      show("success", "Your email app should open with the message ready to send. If it doesn't, email " + form.dataset.mailto + " directly.");
      return;
    }

    form.classList.add("is-sending");
    fetch(endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } })
      .then(function (r) { if (!r.ok) throw new Error(String(r.status)); show("success", SUCCESS); form.reset(); })
      .catch(function () { show("error", FAILURE); })
      .then(function () { form.classList.remove("is-sending"); });
  });
})();
