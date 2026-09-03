(() => {
  const header = document.querySelector(".site-header");
  const menuButton = document.querySelector(".menu-toggle");
  const menu = document.querySelector("#mobile-menu");
  const menuLabel = menuButton?.querySelector(".menu-label");

  const setMenu = (open) => {
    if (!header || !menuButton || !menu) return;
    header.dataset.state = open ? "open" : "closed";
    menuButton.setAttribute("aria-expanded", String(open));
    menu.hidden = !open;
    document.body.classList.toggle("menu-open", open);
    if (menuLabel) menuLabel.textContent = open ? "Close" : "Menu";
  };

  menuButton?.addEventListener("click", () => {
    setMenu(menuButton.getAttribute("aria-expanded") !== "true");
  });

  menu?.addEventListener("click", (event) => {
    if (event.target.closest("a")) setMenu(false);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuButton?.getAttribute("aria-expanded") === "true") {
      setMenu(false);
      menuButton.focus();
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 820) setMenu(false);
  });

  const serviceAreas = document.querySelector("#service-areas");
  const compactView = window.matchMedia("(max-width: 820px)");
  const syncServiceAreas = (event) => {
    if (!serviceAreas || serviceAreas.dataset.userToggled === "true") return;
    serviceAreas.open = event.matches;
  };
  syncServiceAreas(compactView);
  compactView.addEventListener("change", syncServiceAreas);
  serviceAreas?.addEventListener("toggle", () => {
    if (document.readyState === "complete") serviceAreas.dataset.userToggled = "true";
  });

  const form = document.querySelector("#consultation-form");
  const status = document.querySelector("#form-status");
  const submit = form?.querySelector(".submit-button");
  const fields = form ? [...form.querySelectorAll("input, textarea")] : [];

  const messages = {
    name: "Please enter your name.",
    email: "Please enter a valid email address.",
    message: "Please share a little about what you’re planning."
  };

  const validateField = (field) => {
    const wrapper = field.closest(".field");
    const message = wrapper?.querySelector(".field-message");
    const valid = field.checkValidity();

    wrapper?.classList.toggle("is-error", !valid);
    wrapper?.classList.toggle("is-success", valid && field.value.trim().length > 0);
    field.setAttribute("aria-invalid", String(!valid));
    if (message) message.textContent = valid ? "" : messages[field.name];
    return valid;
  };

  fields.forEach((field) => {
    field.addEventListener("blur", () => validateField(field));
    field.addEventListener("input", () => {
      if (field.closest(".field")?.classList.contains("is-error")) validateField(field);
      if (status?.classList.contains("is-error")) {
        status.textContent = "";
        status.className = "form-status";
      }
    });
  });

  form?.addEventListener("submit", (event) => {
    event.preventDefault();
    const valid = fields.map(validateField).every(Boolean);

    if (!valid) {
      status.textContent = "Please review the highlighted fields.";
      status.className = "form-status is-error";
      fields.find((field) => !field.checkValidity())?.focus();
      return;
    }

    submit.disabled = true;
    submit.classList.add("is-loading");
    status.textContent = "Preparing your message…";
    status.className = "form-status";

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.setTimeout(() => {
      submit.disabled = false;
      submit.classList.remove("is-loading");
      status.textContent = "Preview complete. Please call or email Zach to send your message securely.";
      status.className = "form-status is-success";
    }, reducedMotion ? 0 : 700);
  });

  const navLinks = [...document.querySelectorAll(".desktop-nav a")];
  const observedSections = navLinks
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      navLinks.forEach((link) => {
        const active = link.getAttribute("href") === `#${visible.target.id}`;
        if (active) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
    }, { rootMargin: "-20% 0px -65%", threshold: [0, 0.2, 0.6] });

    observedSections.forEach((section) => observer.observe(section));
  }
})();
