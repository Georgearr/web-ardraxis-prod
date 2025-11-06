// Simple Carousel Logic for Events Section
(function () {
  const eventsSection = document.querySelector(".events");
  if (!eventsSection) return;
  const track = eventsSection.querySelector(".carousel-track");
  const slides = Array.from(eventsSection.querySelectorAll(".carousel-slide"));
  const prevBtn = eventsSection.querySelector(".carousel-btn.prev");
  const nextBtn = eventsSection.querySelector(".carousel-btn.next");
  const dotsContainer = eventsSection.querySelector(".carousel-dots");

  if (!track || slides.length === 0) return;

  let currentIndex = 0;

  // Create dots
  slides.forEach((_, idx) => {
    const dot = document.createElement("button");
    dot.className = "carousel-dot" + (idx === 0 ? " active" : "");
    dot.setAttribute("aria-label", `Go to slide ${idx + 1}`);
    dot.addEventListener("click", () => goToSlide(idx));
    dotsContainer.appendChild(dot);
  });

  function update() {
    const offset = -currentIndex * 100;
    track.style.transform = `translateX(${offset}%)`;
    const dots = Array.from(dotsContainer.querySelectorAll(".carousel-dot"));
    dots.forEach((d, i) => d.classList.toggle("active", i === currentIndex));
  }

  function goToSlide(index) {
    currentIndex = (index + slides.length) % slides.length;
    update();
  }

  function next() {
    goToSlide(currentIndex + 1);
  }
  function prev() {
    goToSlide(currentIndex - 1);
  }

  nextBtn && nextBtn.addEventListener("click", next);
  prevBtn && prevBtn.addEventListener("click", prev);

  // Auto-play (optional). Pause on hover for accessibility.
  let autoPlayId = setInterval(next, 5000);
  eventsSection.addEventListener("mouseenter", () => clearInterval(autoPlayId));
  eventsSection.addEventListener(
    "mouseleave",
    () => (autoPlayId = setInterval(next, 5000))
  );

  // Initialize
  update();
})();