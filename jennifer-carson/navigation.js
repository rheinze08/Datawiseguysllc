(() => {
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.getElementById("main-nav");
  const compact = window.matchMedia("(max-width: 740px)");

  function setMenu(open) {
    toggle.setAttribute("aria-expanded", String(open));
    nav.hidden = compact.matches && !open;
  }

  function adaptMenu() {
    toggle.hidden = !compact.matches;
    setMenu(false);
  }

  toggle.addEventListener("click", () => setMenu(nav.hidden));
  nav.addEventListener("click", (event) => {
    const link = event.target.closest("a");
    if (compact.matches && link) {
      const target = document.getElementById(link.hash.slice(1));
      if (target) {
        target.setAttribute("tabindex", "-1");
        target.focus({ preventScroll: true });
      }
      setMenu(false);
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && compact.matches && !nav.hidden) {
      setMenu(false);
      toggle.focus();
    }
  });
  document.addEventListener("click", (event) => {
    if (compact.matches && !nav.hidden && !event.target.closest(".masthead")) setMenu(false);
  });
  compact.addEventListener("change", adaptMenu);
  adaptMenu();
})();
