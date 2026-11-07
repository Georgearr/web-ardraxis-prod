/**
 * ARDRAZINE — DIGITAL MAGAZINE CONTROLLER
 * High-performance interactive reader, zoom/pan engine, keyboard & touch navigation.
 */
(function () {
  "use strict";

  // Cache DOM elements
  const cards = Array.from(document.querySelectorAll(".mag-card"));
  if (!cards.length) return;

  const totalPages = cards.length;
  const pagesData = cards.map((card, idx) => {
    return {
      order: parseInt(card.dataset.page || (idx + 1), 10),
      title: card.dataset.title || `Halaman ${idx + 1}`,
      webp: card.dataset.webp || "",
      jpg: card.dataset.jpg || "",
    };
  });

  // Modal & Controls
  const modal = document.getElementById("reader-modal");
  const backdrop = document.getElementById("reader-backdrop");
  const closeBtn = document.getElementById("reader-close");
  const prevBtn = document.getElementById("reader-prev-btn");
  const nextBtn = document.getElementById("reader-next-btn");
  const stepPrevBtn = document.getElementById("reader-step-prev");
  const stepNextBtn = document.getElementById("reader-step-next");
  const slider = document.getElementById("reader-slider");
  const activeImg = document.getElementById("reader-active-img");
  const curPageLabel = document.getElementById("reader-cur-page");
  const pageTitleLabel = document.getElementById("reader-page-title");
  const downloadBtn = document.getElementById("reader-download");

  // Zoom & Pan
  const zoomInBtn = document.getElementById("reader-zoom-in");
  const zoomOutBtn = document.getElementById("reader-zoom-out");
  const zoomResetBtn = document.getElementById("reader-zoom-reset");
  const zoomVal = document.getElementById("reader-zoom-val");
  const fullscreenBtn = document.getElementById("reader-fullscreen");
  const viewport = document.getElementById("reader-viewport");
  const canvas = document.getElementById("reader-canvas");

  // Hero / FAB Triggers
  const startReadingBtn = document.getElementById("btn-start-reading");
  const heroCoverCard = document.getElementById("hero-cover-card");
  const quickJumpSelect = document.getElementById("quick-jump-select");
  const fabReader = document.getElementById("fab-open-reader");
  const fabTop = document.getElementById("fab-scroll-top");

  // State
  let currentIndex = 0;
  let zoomLevel = 1.0;
  let isDragging = false;
  let startX = 0, startY = 0;
  let translateX = 0, translateY = 0;

  // Touch swipe detection
  let touchStartX = 0;
  let touchStartY = 0;

  // Preloader cache
  const preloadedImages = new Set();

  function preloadImage(url) {
    if (!url || preloadedImages.has(url)) return;
    const img = new Image();
    img.src = url;
    preloadedImages.add(url);
  }

  function preloadAdjacent() {
    if (currentIndex + 1 < totalPages) {
      preloadImage(pagesData[currentIndex + 1].webp || pagesData[currentIndex + 1].jpg);
    }
    if (currentIndex + 2 < totalPages) {
      preloadImage(pagesData[currentIndex + 2].webp || pagesData[currentIndex + 2].jpg);
    }
    if (currentIndex - 1 >= 0) {
      preloadImage(pagesData[currentIndex - 1].webp || pagesData[currentIndex - 1].jpg);
    }
  }

  // Transform apply
  function applyTransform() {
    if (zoomLevel <= 1.0) {
      translateX = 0;
      translateY = 0;
      canvas.style.transform = `scale(1)`;
      if (viewport) viewport.classList.remove("is-dragging");
    } else {
      canvas.style.transform = `translate(${translateX}px, ${translateY}px) scale(${zoomLevel})`;
    }
    if (zoomVal) {
      zoomVal.textContent = `${Math.round(zoomLevel * 100)}%`;
    }
  }

  function resetZoom() {
    zoomLevel = 1.0;
    translateX = 0;
    translateY = 0;
    applyTransform();
  }

  function setZoom(newZoom) {
    zoomLevel = Math.max(1.0, Math.min(3.0, newZoom));
    if (zoomLevel <= 1.0) {
      translateX = 0;
      translateY = 0;
    }
    applyTransform();
  }

  // Display page
  function showPage(index) {
    if (index < 0 || index >= totalPages) return;
    currentIndex = index;
    const page = pagesData[currentIndex];

    // Reset zoom when switching pages
    resetZoom();

    // Set active image with smooth transition
    const targetUrl = page.webp || page.jpg;
    activeImg.src = targetUrl;
    activeImg.alt = `Ardrazine - ${page.title}`;

    if (downloadBtn) {
      downloadBtn.href = page.webp || page.jpg;
      downloadBtn.setAttribute("download", `Ardrazine_${page.order}.webp`);
    }

    if (curPageLabel) curPageLabel.textContent = page.order;
    if (pageTitleLabel) pageTitleLabel.textContent = page.title;
    if (slider) slider.value = page.order;

    // Update nav button states
    if (prevBtn) prevBtn.disabled = (currentIndex === 0);
    if (nextBtn) nextBtn.disabled = (currentIndex === totalPages - 1);
    if (stepPrevBtn) stepPrevBtn.disabled = (currentIndex === 0);
    if (stepNextBtn) stepNextBtn.disabled = (currentIndex === totalPages - 1);

    preloadAdjacent();
  }

  function openReader(pageNumber = 1) {
    const targetIdx = Math.max(0, Math.min(totalPages - 1, pageNumber - 1));
    modal.hidden = false;
    document.body.style.overflow = "hidden";
    showPage(targetIdx);
  }

  function closeReader() {
    modal.hidden = true;
    document.body.style.overflow = "";
    resetZoom();
  }

  function nextPage() {
    if (currentIndex < totalPages - 1) {
      showPage(currentIndex + 1);
    }
  }

  function prevPage() {
    if (currentIndex > 0) {
      showPage(currentIndex - 1);
    }
  }

  // Attach card clicks
  cards.forEach((card, idx) => {
    card.addEventListener("click", () => {
      openReader(idx + 1);
    });
  });

  // Action button triggers
  if (startReadingBtn) {
    startReadingBtn.addEventListener("click", () => openReader(1));
  }
  if (heroCoverCard) {
    heroCoverCard.addEventListener("click", () => openReader(1));
  }
  if (fabReader) {
    fabReader.addEventListener("click", () => openReader(currentIndex + 1 || 1));
  }

  // Quick jump dropdown
  if (quickJumpSelect) {
    quickJumpSelect.addEventListener("change", (e) => {
      const pageVal = parseInt(e.target.value, 10);
      if (pageVal) {
        openReader(pageVal);
        quickJumpSelect.value = "";
      }
    });
  }

  // Navigation handlers
  if (prevBtn) prevBtn.addEventListener("click", prevPage);
  if (nextBtn) nextBtn.addEventListener("click", nextPage);
  if (stepPrevBtn) stepPrevBtn.addEventListener("click", () => showPage(0));
  if (stepNextBtn) stepNextBtn.addEventListener("click", () => showPage(totalPages - 1));

  if (slider) {
    slider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      showPage(val - 1);
    });
  }

  // Zoom handlers
  if (zoomInBtn) {
    zoomInBtn.addEventListener("click", () => setZoom(zoomLevel + 0.35));
  }
  if (zoomOutBtn) {
    zoomOutBtn.addEventListener("click", () => setZoom(zoomLevel - 0.35));
  }
  if (zoomResetBtn) {
    zoomResetBtn.addEventListener("click", resetZoom);
  }

  // Double click to toggle zoom
  if (viewport) {
    viewport.addEventListener("dblclick", (e) => {
      e.preventDefault();
      if (zoomLevel > 1.0) {
        resetZoom();
      } else {
        setZoom(1.85);
      }
    });
  }

  // Drag & Pan when zoomed
  if (viewport) {
    viewport.addEventListener("mousedown", (e) => {
      if (zoomLevel <= 1.0) return;
      isDragging = true;
      startX = e.clientX - translateX;
      startY = e.clientY - translateY;
      viewport.classList.add("is-dragging");
    });

    window.addEventListener("mousemove", (e) => {
      if (!isDragging) return;
      translateX = e.clientX - startX;
      translateY = e.clientY - startY;
      applyTransform();
    });

    window.addEventListener("mouseup", () => {
      isDragging = false;
      if (viewport) viewport.classList.remove("is-dragging");
    });

    // Mouse wheel zoom
    viewport.addEventListener("wheel", (e) => {
      if (modal.hidden) return;
      if (e.ctrlKey || e.metaKey || zoomLevel > 1.0) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.2 : 0.2;
        setZoom(zoomLevel + delta);
      }
    }, { passive: false });
  }

  // Fullscreen toggle
  if (fullscreenBtn) {
    fullscreenBtn.addEventListener("click", () => {
      if (!document.fullscreenElement) {
        modal.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    });
  }

  // Close handlers
  if (closeBtn) closeBtn.addEventListener("click", closeReader);
  if (backdrop) backdrop.addEventListener("click", closeReader);

  // Keyboard navigation
  document.addEventListener("keydown", (e) => {
    if (modal.hidden) return;

    switch (e.key) {
      case "Escape":
        closeReader();
        break;
      case "ArrowLeft":
      case "a":
      case "A":
        prevPage();
        break;
      case "ArrowRight":
      case "d":
      case "D":
        nextPage();
        break;
      case " ":
        e.preventDefault();
        nextPage();
        break;
      case "+":
      case "=":
        setZoom(zoomLevel + 0.35);
        break;
      case "-":
      case "_":
        setZoom(zoomLevel - 0.35);
        break;
      case "0":
        resetZoom();
        break;
      case "f":
      case "F":
        if (fullscreenBtn) fullscreenBtn.click();
        break;
    }
  });

  // Mobile Touch Swipe Navigation
  if (viewport) {
    viewport.addEventListener("touchstart", (e) => {
      if (e.touches.length === 1 && zoomLevel <= 1.0) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
      }
    }, { passive: true });

    viewport.addEventListener("touchend", (e) => {
      if (zoomLevel > 1.0 || !touchStartX) return;
      const touchEndX = e.changedTouches[0].clientX;
      const touchEndY = e.changedTouches[0].clientY;
      const diffX = touchEndX - touchStartX;
      const diffY = touchEndY - touchStartY;

      // Check if horizontal swipe was dominant
      if (Math.abs(diffX) > 45 && Math.abs(diffX) > Math.abs(diffY)) {
        if (diffX < 0) {
          nextPage(); // swipe left -> next page
        } else {
          prevPage(); // swipe right -> prev page
        }
      }
      touchStartX = 0;
      touchStartY = 0;
    }, { passive: true });
  }

  // Floating Controls scroll visibility (appears when scrolled past hero)
  const floatingControls = document.querySelector(".floating-controls");
  window.addEventListener("scroll", () => {
    if (window.scrollY > 350) {
      if (floatingControls) floatingControls.classList.add("is-visible");
      if (fabTop) fabTop.classList.add("is-visible");
    } else {
      if (floatingControls) floatingControls.classList.remove("is-visible");
      if (fabTop) fabTop.classList.remove("is-visible");
    }
  }, { passive: true });

  if (fabTop) {
    fabTop.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // Initial preload of cover & first 2 pages
  preloadImage(pagesData[0].webp || pagesData[0].jpg);
  if (pagesData[1]) preloadImage(pagesData[1].webp || pagesData[1].jpg);
})();
