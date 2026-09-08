/* SoHo Men's Health — "The Member's Rooms" interactions.
   Progressive enhancement only; the site is fully usable without JS. */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Mobile nav overlay ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var overlay = document.getElementById("nav-overlay");
  var closeBtn = overlay && overlay.querySelector(".nav-close");

  function setNav(open) {
    if (!overlay || !toggle) return;
    overlay.setAttribute("data-open", open ? "true" : "false");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.style.overflow = open ? "hidden" : "";
    if (open && closeBtn) closeBtn.focus();
    if (!open) toggle.focus();
  }

  if (toggle && overlay) {
    toggle.addEventListener("click", function () { setNav(true); });
    if (closeBtn) closeBtn.addEventListener("click", function () { setNav(false); });
    overlay.addEventListener("click", function (e) {
      if (e.target.closest("a")) setNav(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && overlay.getAttribute("data-open") === "true") setNav(false);
    });
  }

  /* ---------- Concierge form states ---------- */
  var form = document.getElementById("concierge-form");
  if (form) {
    var note = document.getElementById("concierge-note");
    var office = document.getElementById("office");
    var officeField = document.getElementById("field-office");
    var submit = form.querySelector('button[type="submit"]');

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      // Reset states
      officeField.removeAttribute("data-state");
      officeField.querySelector(".hint").textContent = "";
      note.removeAttribute("data-state");

      if (!office.value) {
        officeField.setAttribute("data-state", "error");
        officeField.querySelector(".hint").textContent = "Please choose an office so we know where to host you.";
        office.focus();
        return;
      }

      // Loading state
      submit.disabled = true;
      submit.textContent = "Requesting…";

      window.setTimeout(function () {
        submit.disabled = false;
        submit.textContent = "Request appointment";
        officeField.setAttribute("data-state", "success");
        officeField.querySelector(".hint").textContent = "Office noted.";
        note.setAttribute("data-state", "success");
        note.textContent = "Thank you — the concierge will call 646-370-4050 within one business hour to confirm. (Demo state: no data was sent.)";
      }, reduceMotion ? 0 : 700);
    });
  }

  /* ---------- Subtle scroll reveals (motion-safe) ---------- */
  var revealEls = document.querySelectorAll(".reveal");
  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealEls.forEach(function (el) { io.observe(el); });
  }
})();
