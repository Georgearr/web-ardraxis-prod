// Ardrazine invite modal (homepage)
// Modal hanya dibuka lewat CTA pemicu, tidak pernah otomatis saat halaman dimuat.
(function () {
  var modal = document.getElementById("ardrazine-modal");
  if (!modal) return;

  var panel = modal.querySelector(".ardrazine-modal-panel");
  var trigger = document.querySelector("[data-ardrazine-open]");
  var lastFocused = null;
  var bodyOverflow = "";
  var htmlOverflow = "";
  var closeTimer = null;
  var CLOSE_DELAY_MS = 320;

  function isOpen() {
    return !modal.hidden;
  }

  function lockScroll() {
    bodyOverflow = document.body.style.overflow;
    htmlOverflow = document.documentElement.style.overflow;
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";
  }

  function unlockScroll() {
    document.body.style.overflow = bodyOverflow;
    document.documentElement.style.overflow = htmlOverflow;
  }

  function openModal() {
    if (isOpen()) return;
    clearTimeout(closeTimer);
    lastFocused = document.activeElement;
    modal.hidden = false;
    lockScroll();
    requestAnimationFrame(function () {
      modal.classList.add("is-open");
    });
    var closeBtn = modal.querySelector("[data-ardrazine-close]");
    if (closeBtn && closeBtn.focus) closeBtn.focus();
  }

  function closeModal() {
    if (!isOpen()) return;
    modal.classList.remove("is-open");
    unlockScroll();
    closeTimer = setTimeout(function () {
      modal.hidden = true;
      if (lastFocused && lastFocused.focus) lastFocused.focus();
    }, CLOSE_DELAY_MS);
  }

  if (trigger) {
    trigger.addEventListener("click", openModal);
  }

  // Klik area di luar panel modal (backdrop) untuk menutup.
  modal.addEventListener("click", function (event) {
    if (!panel || !panel.contains(event.target)) closeModal();
  });

  Array.prototype.forEach.call(
    modal.querySelectorAll("[data-ardrazine-close]"),
    function (el) {
      el.addEventListener("click", closeModal);
    }
  );

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && isOpen()) closeModal();
  });
})();
