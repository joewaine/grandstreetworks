(() => {
  const menuToggle = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-mobile-menu]");
  const menuLabel = document.querySelector("[data-menu-label]");

  const MENU_TRANSITION_MS = 300; // a little over the longest CSS transition

  const setMenu = (open, returnFocus = false) => {
    if (!menuToggle || !menu || !menuLabel) return;
    menuToggle.setAttribute("aria-expanded", String(open));
    menuLabel.textContent = open ? "Close ×" : "Menu";
    document.body.classList.toggle("menu-open", open);

    if (open) {
      menu.hidden = false;
      // Two frames: the first lets the browser paint the menu at opacity 0,
      // so adding the class on the second actually transitions it in.
      requestAnimationFrame(() =>
        requestAnimationFrame(() => {
          menu.classList.add("is-open");
          menu.querySelector("a")?.focus();
        })
      );
      return;
    }

    menu.classList.remove("is-open");
    if (returnFocus) menuToggle.focus();
    // Hide once the fade-out finishes. The timeout covers reduced-motion
    // (no transition, so no transitionend) and any missed event.
    const hideWhenDone = () => {
      if (!menu.classList.contains("is-open")) menu.hidden = true;
    };
    menu.addEventListener("transitionend", hideWhenDone, { once: true });
    window.setTimeout(hideWhenDone, MENU_TRANSITION_MS);
  };

  menuToggle?.addEventListener("click", () => {
    const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
    setMenu(!isOpen);
  });

  menu?.addEventListener("click", (event) => {
    if (event.target.closest("a")) setMenu(false);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuToggle?.getAttribute("aria-expanded") === "true") {
      setMenu(false, true);
    }
  });

  document.addEventListener("click", (event) => {
    if (
      menuToggle?.getAttribute("aria-expanded") === "true" &&
      !event.target.closest("[data-site-header]")
    ) {
      setMenu(false);
    }
  });

  const video = document.querySelector("[data-hero-video]");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const saveData = Boolean(navigator.connection?.saveData);

  const loadHeroVideo = () => {
    if (!video || reducedMotion.matches || saveData || video.src) return;
    video.src = video.dataset.src;
    video.addEventListener(
      "canplay",
      () => {
        video.play().catch(() => {
          // The poster remains the complete fallback when autoplay is unavailable.
        });
      },
      { once: true }
    );
    video.load();
  };

  const videoStartEvents = ["pointermove", "pointerdown", "touchstart", "scroll", "keydown"];
  const startVideoFromIntent = () => {
    loadHeroVideo();
    videoStartEvents.forEach((eventName) => window.removeEventListener(eventName, startVideoFromIntent));
  };

  window.addEventListener(
    "load",
    () => {
      videoStartEvents.forEach((eventName) =>
        window.addEventListener(eventName, startVideoFromIntent, { once: true, passive: true })
      );
      window.setTimeout(startVideoFromIntent, 12000);
    },
    { once: true }
  );

  reducedMotion.addEventListener?.("change", (event) => {
    if (event.matches) {
      video?.pause();
    } else if (!saveData) {
      loadHeroVideo();
      video?.play().catch(() => {});
    }
  });

  const form = document.querySelector("[data-estimate-form]");
  const submitButton = document.querySelector("[data-submit-button]");
  const formStatus = document.querySelector("[data-form-status]");

  const validators = {
    name: (control) => control.value.trim().length >= 2,
    email: (control) => control.validity.valid && control.value.trim().length > 0,
    project: (control) => control.value.trim().length >= 8,
  };

  const validateField = (field) => {
    const control = field.querySelector("input, textarea");
    const error = field.querySelector(".field-error");
    const validator = validators[field.dataset.field];
    const valid = Boolean(control && validator?.(control));

    field.classList.toggle("has-error", !valid);
    field.classList.toggle("is-valid", valid && control.value.trim().length > 0);
    if (control) control.setAttribute("aria-invalid", String(!valid));
    if (error) error.hidden = valid;

    return valid;
  };

  form?.querySelectorAll(".field").forEach((field) => {
    const control = field.querySelector("input, textarea");
    control?.addEventListener("blur", () => validateField(field));
    control?.addEventListener("input", () => {
      if (field.classList.contains("has-error")) validateField(field);
    });
  });

  form?.addEventListener("submit", (event) => {
    event.preventDefault();
    const fields = [...form.querySelectorAll(".field")];
    const invalidFields = fields.filter((field) => !validateField(field));

    if (invalidFields.length) {
      const firstControl = invalidFields[0].querySelector("input, textarea");
      formStatus.textContent = `Please review ${invalidFields.length} highlighted ${invalidFields.length === 1 ? "field" : "fields"}.`;
      formStatus.classList.add("is-error");
      firstControl?.focus({ preventScroll: true });
      firstControl?.scrollIntoView({ block: "center", inline: "nearest" });
      return;
    }

    formStatus.textContent = "";
    formStatus.classList.remove("is-error");
    submitButton.disabled = true;
    submitButton.textContent = "Working…";

    window.setTimeout(() => {
      submitButton.disabled = false;
      submitButton.textContent = "Send project details";
      formStatus.textContent =
        "Thanks—your details are ready. Connect this local prototype to Palm Construction’s production form endpoint before launch.";
      formStatus.focus();
    }, 700);
  });

  const year = document.querySelector("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());
})();
