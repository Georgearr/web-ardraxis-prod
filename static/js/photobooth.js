/**
 * Ravenith Photobooth — fetch galeri dari Flask API (Google Drive via GAS)
 */

(function () {
  const cfg = window.PHOTOBOOTH_CONFIG || {};
  const API_URL = cfg.apiPhotosUrl || "/api/photobooth/photos";
  const PAGE_SIZE = cfg.pageSize || 12;

  const els = {
    grid: document.getElementById("galleryGrid"),
    loading: document.getElementById("stateLoading"),
    error: document.getElementById("stateError"),
    empty: document.getElementById("stateEmpty"),
    errorMsg: document.getElementById("errorMessage"),
    meta: document.getElementById("galleryMeta"),
    search: document.getElementById("searchInput"),
    refresh: document.getElementById("btnRefresh"),
    retry: document.getElementById("btnRetry"),
    loadMoreWrap: document.getElementById("loadMoreWrap"),
    loadMore: document.getElementById("btnLoadMore"),
    lightbox: document.getElementById("lightbox"),
    lightboxImg: document.getElementById("lightboxImg"),
    lightboxCaption: document.getElementById("lightboxCaption"),
    lightboxDownload: document.getElementById("lightboxDownload"),
    lightboxClose: document.getElementById("lightboxClose"),
    lightboxPrev: document.getElementById("lightboxPrev"),
    lightboxNext: document.getElementById("lightboxNext"),
  };

  let allPhotos = [];
  let displayedCount = 0;
  let lightboxIndex = 0;
  let searchDebounce = null;

  function showOnly(state) {
    const map = { loading: els.loading, error: els.error, empty: els.empty, grid: els.grid };
    Object.keys(map).forEach(function (key) {
      const el = map[key];
      if (!el) return;
      if (key === state) {
        el.classList.remove("d-none");
      } else {
        el.classList.add("d-none");
      }
    });
    if (state !== "grid") {
      els.loadMoreWrap.classList.add("d-none");
    }
  }

  function buildCard(photo, index) {
    const col = document.createElement("div");
    col.className = "col-6 col-md-4 col-lg-3";
    const url = photo.url || "";
    const downloadUrl = photo.downloadUrl || photo.url || "#";
    const name = photo.name || "Foto";

    col.innerHTML =
      '<article class="photo-card" data-index="' +
      index +
      '" tabindex="0" role="button" aria-label="Buka ' +
      escapeHtml(name) +
      '">' +
      '<div class="photo-card-inner">' +
      '<img src="' +
      escapeAttr(url) +
      '" alt="' +
      escapeAttr(name) +
      '" loading="lazy" decoding="async" onerror="this.onerror=null;this.classList.add(\'img-broken\');this.parentElement&&this.parentElement.classList.add(\'img-broken\')" />' +
      "</div>" +
      '<div class="photo-card-footer">' +
      escapeHtml(name) +
      "</div>" +
      "</article>";

    const card = col.querySelector(".photo-card");
    card.addEventListener("click", function () {
      openLightbox(index);
    });
    card.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openLightbox(index);
      }
    });

    return col;
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function escapeAttr(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;")
      .replace(/</g, "&lt;");
  }

  function renderPage(append) {
    if (!append) {
      els.grid.innerHTML = "";
      displayedCount = 0;
    }

    const slice = allPhotos.slice(displayedCount, displayedCount + PAGE_SIZE);
    slice.forEach(function (photo, i) {
      const globalIndex = displayedCount + i;
      els.grid.appendChild(buildCard(photo, globalIndex));
    });

    displayedCount += slice.length;

    if (displayedCount < allPhotos.length) {
      els.loadMoreWrap.classList.remove("d-none");
    } else {
      els.loadMoreWrap.classList.add("d-none");
    }

    updateMeta();
  }

  function updateMeta() {
    const total = allPhotos.length;
    const q = (els.search.value || "").trim();
    let text = total + " foto";
    if (q) text += ' untuk "' + q + '"';
    if (displayedCount < total) {
      text += " · menampilkan " + displayedCount + " dari " + total;
    }
    els.meta.textContent = text;
  }

  function openLightbox(index) {
    lightboxIndex = index;
    const photo = allPhotos[index];
    if (!photo) return;

    els.lightboxImg.src = photo.url || "";
    els.lightboxImg.alt = photo.name || "";
    els.lightboxCaption.textContent = photo.name || "";
    els.lightboxDownload.href = photo.downloadUrl || photo.url || "#";
    els.lightboxDownload.download = photo.name || "photo.jpg";

    els.lightbox.classList.remove("d-none");
    document.body.style.overflow = "hidden";
  }

  function closeLightbox() {
    els.lightbox.classList.add("d-none");
    document.body.style.overflow = "";
    els.lightboxImg.src = "";
  }

  function lightboxStep(delta) {
    if (!allPhotos.length) return;
    lightboxIndex = (lightboxIndex + delta + allPhotos.length) % allPhotos.length;
    openLightbox(lightboxIndex);
  }

  async function fetchPhotos(refresh, keyword) {
    showOnly("loading");

    let url = API_URL;
    const params = new URLSearchParams();
    if (refresh) params.set("refresh", "1");
    if (keyword) params.set("q", keyword);
    if (params.toString()) {
      url += (url.indexOf("?") >= 0 ? "&" : "?") + params.toString();
    }

    try {
      const res = await fetch(url, { headers: { Accept: "application/json" } });
      const data = await res.json();

      if (!data.success) {
        els.errorMsg.textContent = data.message || "Gagal memuat foto.";
        showOnly("error");
        return;
      }

      allPhotos = data.photos || [];

      if (allPhotos.length === 0) {
        showOnly("empty");
        els.meta.textContent = "0 foto";
        return;
      }

      showOnly("grid");
      renderPage(false);
    } catch (err) {
      els.errorMsg.textContent =
        "Tidak dapat terhubung ke server. Periksa koneksi atau URL Apps Script.";
      console.error(err);
      showOnly("error");
    }
  }

  function onSearchInput() {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(function () {
      const q = (els.search.value || "").trim();
      fetchPhotos(false, q);
    }, 400);
  }

  if (els.search) {
    els.search.addEventListener("input", onSearchInput);
  }

  if (els.refresh) {
    els.refresh.addEventListener("click", function () {
      fetchPhotos(true, (els.search.value || "").trim());
    });
  }

  if (els.retry) {
    els.retry.addEventListener("click", function () {
      fetchPhotos(true, (els.search.value || "").trim());
    });
  }

  if (els.loadMore) {
    els.loadMore.addEventListener("click", function () {
      renderPage(true);
    });
  }

  if (els.lightboxClose) {
    els.lightboxClose.addEventListener("click", closeLightbox);
  }

  if (els.lightbox) {
    els.lightbox.addEventListener("click", function (e) {
      if (e.target === els.lightbox) closeLightbox();
    });
  }

  if (els.lightboxPrev) {
    els.lightboxPrev.addEventListener("click", function (e) {
      e.stopPropagation();
      lightboxStep(-1);
    });
  }

  if (els.lightboxNext) {
    els.lightboxNext.addEventListener("click", function (e) {
      e.stopPropagation();
      lightboxStep(1);
    });
  }

  document.addEventListener("keydown", function (e) {
    if (els.lightbox.classList.contains("d-none")) return;
    if (e.key === "Escape") closeLightbox();
    if (e.key === "ArrowLeft") lightboxStep(-1);
    if (e.key === "ArrowRight") lightboxStep(1);
  });

  fetchPhotos(false, "");
})();
