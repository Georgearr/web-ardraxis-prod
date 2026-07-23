(function () {
  var autosaveTimer = null;
  var isSubmitting = false;
  var apiPrefix = window.RECRUITMENT_API_PREFIX || "/recruitment";

  var els = {
    landing: document.getElementById("recruit-landing"),
    step1: document.getElementById("recruit-step1"),
    step2: document.getElementById("recruit-step2"),
    step3: document.getElementById("recruit-step3"),
    step4: document.getElementById("recruit-step4"),
    review: document.getElementById("recruit-review"),
    success: document.getElementById("recruit-success"),
    toast: document.getElementById("recruit-toast"),
    overlay: document.getElementById("recruit-loading"),
    progressBar: document.getElementById("recruit-progress-bar"),
    autosaveIndicator: document.getElementById("recruit-autosave"),
    formStep1: document.getElementById("recruit-form-step1"),
    formStep3: document.getElementById("recruit-form-step3"),
    formStep4: document.getElementById("recruit-form-step4"),
    step4Container: document.getElementById("recruit-step4-content"),
  };

  var stepNames = ["landing", "step1", "step2", "step3", "step4", "review", "success"];
  var stepMap = { landing: 0, step1: 1, step2: 2, step3: 3, step4: 4, review: 5, success: 6 };
  var stepIndexToSection = ["landing", "step1", "step2", "step3", "step4", "review"];

  function showSection(name, skipAutosave) {
    stepNames.forEach(function (s) {
      var el = document.getElementById("recruit-" + s);
      if (el) {
        if (s === name) {
          el.classList.remove("recruit-hidden");
          el.style.animation = "none";
          void el.offsetHeight;
          el.style.animation = "recruitFadeIn 0.5s ease-out";
        } else {
          el.classList.add("recruit-hidden");
        }
      }
    });
    updateProgressBar(name);
    if (!skipAutosave && name !== "success") {
      loadProgress();
    }
  }

  function updateProgressBar(current) {
    var currentIdx = stepMap[current] || 0;
    var steps = els.progressBar ? els.progressBar.querySelectorAll(".recruit-step") : [];
    steps.forEach(function (step, idx) {
      step.classList.remove("active", "done");
      if (idx < currentIdx) {
        step.classList.add("done");
      } else if (idx === currentIdx) {
        step.classList.add("active");
      }
    });
    var connectors = els.progressBar ? els.progressBar.querySelectorAll(".recruit-step-connector") : [];
    connectors.forEach(function (conn, idx) {
      conn.classList.toggle("done", idx < currentIdx);
    });
  }

  function getFormData(stepNum) {
    var formId = "recruit-form-step" + stepNum;
    var form = document.getElementById(formId);
    if (!form) return {};
    var fd = new FormData(form);
    var data = {};
    fd.forEach(function (value, key) {
      if (key === "sekbid") {
        if (!data[key]) data[key] = [];
        data[key].push(value);
      } else {
        data[key] = value;
      }
    });
    return data;
  }

  function populateForm(stepNum, data) {
    var formId = "recruit-form-step" + stepNum;
    var form = document.getElementById(formId);
    if (!form || !data) return;
    Object.keys(data).forEach(function (key) {
      var val = data[key];
      if (key === "sekbid" && Array.isArray(val)) {
        val.forEach(function (v) {
          var card = form.querySelector('.recruit-sekbid-card[data-value="' + v + '"]');
          if (card) {
            card.classList.add("selected");
            card.querySelector(".sekbid-check").textContent = "✓";
            var hi = card.querySelector(".sekbid-hidden-input");
            if (hi) hi.checked = true;
          }
        });
      } else {
        var input = form.querySelector('[name="' + key + '"]');
        if (input) {
          input.value = val;
        }
      }
    });
  }

  function showErrors(stepNum, errors) {
    var formId = "recruit-form-step" + stepNum;
    var form = document.getElementById(formId);
    if (!form) return;
    form.querySelectorAll(".recruit-error-text").forEach(function (el) {
      el.classList.remove("visible");
    });
    form.querySelectorAll(".recruit-input.error").forEach(function (el) {
      el.classList.remove("error");
    });
    Object.keys(errors).forEach(function (key) {
      var errEl = form.querySelector(".recruit-error-text[data-field='" + key + "']");
      var inputEl = form.querySelector("[name='" + key + "']");
      if (errEl) {
        errEl.textContent = errors[key];
        errEl.classList.add("visible");
      }
      if (inputEl) {
        inputEl.classList.add("error");
      }
    });
  }

  function validateStep1() {
    var data = getFormData(1);
    var errors = {};
    if (!data.nama || !data.nama.trim()) errors.nama = "Nama lengkap wajib diisi";
    else if (data.nama.trim().length < 3) errors.nama = "Nama lengkap minimal 3 karakter";
    if (!data.kelas || !data.kelas.trim()) errors.kelas = "Kelas wajib diisi";
    showErrors(1, errors);
    return Object.keys(errors).length === 0;
  }

  function validateStep2() {
    var data = getFormData(2);
    var errors = {};
    var sekbid = data.sekbid;
    if (!sekbid || !sekbid.length) errors.sekbid = "Pilih minimal satu Sekbid";
    else if (sekbid.length > 2) errors.sekbid = "Maksimal 2 Sekbid";
    showErrors(2, errors);
    return Object.keys(errors).length === 0;
  }

  function validateStep3() {
    var data = getFormData(3);
    var errors = {};
    if (!data.visi_misi || !data.visi_misi.trim()) errors.visi_misi = "Visi dan misi wajib diisi";
    else if (data.visi_misi.trim().length < 10) errors.visi_misi = "Visi dan misi minimal 10 karakter";
    if (!data.motivasi || !data.motivasi.trim()) errors.motivasi = "Motivasi wajib diisi";
    else if (data.motivasi.trim().length < 10) errors.motivasi = "Motivasi minimal 10 karakter";
    if (!data.kelebihan || !data.kelebihan.trim()) errors.kelebihan = "Kelebihan wajib diisi";
    else if (data.kelebihan.trim().length < 5) errors.kelebihan = "Kelebihan minimal 5 karakter";
    if (!data.kekurangan || !data.kekurangan.trim()) errors.kekurangan = "Kekurangan wajib diisi";
    if (!data.prioritas || !data.prioritas.trim()) errors.prioritas = "Skala prioritas wajib diisi";
    else if (!/^[1-5](?:-[1-5])*$/.test(data.prioritas.trim())) errors.prioritas = "Format: 1-2-3-4-5";
    showErrors(3, errors);
    return Object.keys(errors).length === 0;
  }

  function validateStep4() {
    var errors = {};
    var link = els.formStep4 ? els.formStep4.querySelector('[name="google_drive_link"]') : null;
    if (!link || !link.value.trim()) {
      errors.google_drive_link = "Link Google Drive wajib diisi";
    } else if (link.value.indexOf("drive.google.com") === -1 && link.value.indexOf("docs.google.com") === -1) {
      errors.google_drive_link = "Harap masukkan link Google Drive yang valid";
    }
    showErrors(4, errors);
    return Object.keys(errors).length === 0;
  }

  function showToast(message, type) {
    var toast = els.toast;
    if (!toast) return;
    var iconMap = { success: "bx bx-check-circle", error: "bx bx-x-circle", info: "bx bx-info-circle" };
    toast.className = "recruit-toast recruit-toast-" + type;
    toast.innerHTML = '<i class="' + (iconMap[type] || iconMap.info) + '"></i><span>' + message + "</span>";
    toast.classList.add("visible");
    clearTimeout(toast._hideTimer);
    toast._hideTimer = setTimeout(function () {
      toast.classList.remove("visible");
    }, 4000);
  }

  function showLoading(show) {
    if (els.overlay) {
      els.overlay.classList.toggle("active", show);
    }
  }

  function triggerAutosave() {
    clearTimeout(autosaveTimer);
    autosaveTimer = setTimeout(doAutosave, 1000);
  }

  function gatherAllData() {
    var data = {};
    for (var i = 1; i <= 4; i++) {
      var stepData = getFormData(i);
      Object.keys(stepData).forEach(function (k) {
        data[k] = stepData[k];
      });
    }
    return data;
  }

  function doAutosave() {
    var data = gatherAllData();
    if (!data.nama && !data.kelas) return;
    setAutosaveStatus("saving");
      fetch(apiPrefix + "/autosave", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ progress: data }),
    })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        setAutosaveStatus(res.success ? "saved" : "idle");
      })
      .catch(function () {
        setAutosaveStatus("idle");
      });
  }

  function setAutosaveStatus(status) {
    var el = els.autosaveIndicator;
    if (!el) return;
    el.classList.remove("saving", "saved");
    el.classList.add("visible");
    if (status === "saving") {
      el.classList.add("saving");
      el.innerHTML = '<div class="recruit-spinner"></div> Saving...';
    } else if (status === "saved") {
      el.classList.add("saved");
      el.innerHTML = '<i class="bx bx-check"></i> Saved';
      clearTimeout(el._hideTimer);
      el._hideTimer = setTimeout(function () {
        el.classList.remove("visible");
      }, 2000);
    } else {
      el.classList.remove("visible");
    }
  }

  function loadProgress() {
    fetch(apiPrefix + "/progress")
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.success || !res.progress) return;
        var p = res.progress;
        if (p.nama || p.kelas) populateForm(1, p);
        if (p.sekbid) {
          populateForm(2, p);
          setTimeout(function () {
            document.querySelectorAll("#recruit-form-step2 .recruit-sekbid-card.selected").forEach(function (c) {
              c.querySelector(".sekbid-check").textContent = "✓";
            });
          }, 50);
        }
        if (p.visi_misi || p.motivasi) populateForm(3, p);
        if (p.google_drive_link) populateForm(4, p);
        if (p.currentStep && p.currentStep !== "landing" && p.currentStep !== "success") {
          if (p.currentStep === "step4") {
            buildStep4().then(function () { showSection("step4", true); });
            return;
          }
          showSection(p.currentStep, true);
        }
      })
      .catch(function () {});
  }

  function clearProgress() {
    fetch(apiPrefix + "/clear", { method: "POST" }).catch(function () {});
  }

  function buildStep4() {
    var container = els.step4Container;
    if (!container) return Promise.resolve();

    var note = document.getElementById("recruit-step4-note");
    if (note) note.innerHTML = "";

    var data = getFormData(2);
    var sekbidKeys = data.sekbid || [];
    var allSekbid = window.RECRUIT_SEKBID_LIST || [];

    if (!sekbidKeys.length) {
      container.innerHTML = "";
      return Promise.resolve();
    }

    var selected = allSekbid.filter(function (s) {
      return sekbidKeys.indexOf(s.id) !== -1 || sekbidKeys.indexOf(s.key) !== -1;
    });

    console.log("[Step5 DEBUG] allSekbid:", allSekbid);
    console.log("[Step5 DEBUG] sekbidKeys:", sekbidKeys);
    console.log("[Step5 DEBUG] selected:", selected);

    var html = "";
    selected.forEach(function (sekbid, idx) {
      console.log("[Step5 DEBUG] sekbid[" + idx + "]:", sekbid);
      console.log("[Step5 DEBUG] sekbid[" + idx + "].youtube:", sekbid.youtube);
      var videoId = extractYoutubeId(sekbid.youtube || "");
      var embedUrl = videoId ? "https://www.youtube.com/embed/" + videoId : "";
      var watchUrl = videoId ? "https://www.youtube.com/watch?v=" + videoId : "";
      console.log("[Step5 DEBUG] sekbid[" + idx + "].embedUrl:", embedUrl);
      html += '<div class="recruit-step4-sekbid">';
      html += "<h3>" + (idx + 1) + ". " + (sekbid.label || sekbid.key) + "</h3>";
      html += '<div class="recruit-step4-desc">' + sekbid.description + "</div>";

      if (sekbid.requirements && sekbid.requirements.length) {
        html += '<ul class="recruit-step4-reqs">';
        sekbid.requirements.forEach(function (r) {
          html += "<li>" + r + "</li>";
        });
        html += "</ul>";
      }

      if (sekbid.questions && sekbid.questions.length) {
        html += '<div class="recruit-step4-questions">';
        html += "<p>Pertanyaan Tambahan:</p>";
        sekbid.questions.forEach(function (q) {
          html += '<div class="recruit-form-group">';
          html += '<label>' + q + "</label>";
          html += '<textarea name="jawaban_' + (sekbid.id || idx) + '" class="recruit-input recruit-textarea" placeholder="Tulis jawaban Anda..."></textarea>';
          html += "</div>";
        });
        html += "</div>";
      }

      if (embedUrl) {
        html += '<div class="recruit-video-wrap"><iframe src="' + embedUrl + '" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy" referrerpolicy="strict-origin-when-cross-origin"></iframe></div>';
        html += '<div class="recruit-video-fallback"><a href="' + watchUrl + '" target="_blank" rel="noopener noreferrer"><i class="bx bx-play-circle"></i> Tonton di YouTube</a></div>';
      }

      html += '<div class="recruit-form-group">';
      html += '<label for="google_drive_link_' + idx + '">Link Google Drive Tugas Sekbid</label>';
      if (idx === 0) {
        html += '<input type="url" id="google_drive_link" name="google_drive_link" class="recruit-input" placeholder="https://drive.google.com/..." />';
        html += '<div class="recruit-error-text" data-field="google_drive_link"></div>';
        html += '<div class="recruit-helper-text"><i class="bx bx-info-circle"></i> Upload seluruh tugas dan portofolio ke Google Drive. Pastikan akses <strong>Anyone with the link</strong> &mdash; <strong>View Only</strong></div>';
      } else {
        html += '<p class="recruit-helper-text" style="margin-top:4px;">Gunakan link yang sama seperti di atas.</p>';
      }
      html += "</div>";

      html += "</div>";
    });

    container.innerHTML = html;

    var linkInput = document.getElementById("google_drive_link");
    if (linkInput) {
      linkInput.addEventListener("input", triggerAutosave);
      linkInput.addEventListener("change", triggerAutosave);
    }

    var answers = document.querySelectorAll("#recruit-step4-content textarea");
    answers.forEach(function (ta) {
      ta.addEventListener("input", triggerAutosave);
      ta.addEventListener("change", triggerAutosave);
    });

    return Promise.resolve();
  }

  function extractYoutubeId(url) {
    if (!url) return "";
    var id = null;
    var m;
    m = url.match(/(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?(?:.*&)?v=([a-zA-Z0-9_-]+)/);
    if (m) id = m[1];
    if (!id) { m = url.match(/(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]+)/); if (m) id = m[1]; }
    if (!id) { m = url.match(/(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]+)/); if (m) id = m[1]; }
    if (!id && /^[a-zA-Z0-9_-]+$/.test(url)) id = url;
    return id;
  }

  function normalizeYoutubeUrl(url) {
    var id = extractYoutubeId(url);
    return id ? "https://www.youtube.com/embed/" + id : "";
  }

  function buildReview() {
    var data = gatherAllData();
    var container = document.getElementById("recruit-review-content");
    if (!container) return;

    var allSekbid = window.RECRUIT_SEKBID_LIST || [];
    var sekbidLabels = [];
    if (data.sekbid && Array.isArray(data.sekbid)) {
      data.sekbid.forEach(function (k) {
        var found = allSekbid.filter(function (s) { return s.id === k || s.key === k; });
        if (found.length) {
          sekbidLabels.push(found[0].label || found[0].key);
        } else {
          sekbidLabels.push(k);
        }
      });
    }

    var jawabanHtml = "";
    if (data.sekbid && Array.isArray(data.sekbid)) {
      data.sekbid.forEach(function (k, idx) {
        var found = allSekbid.filter(function (s) { return s.id === k || s.key === k; });
        if (!found.length) return;
        var sekbid = found[0];
        if (!sekbid.questions || !sekbid.questions.length) return;
        sekbid.questions.forEach(function (q, qi) {
          var answer = data["jawaban_" + (sekbid.id || idx)] || "-";
          jawabanHtml += '<div class="recruit-review-item full"><div class="recruit-review-label">' + sekbid.label + ' - Pertanyaan</div><div class="recruit-review-value"><strong>' + q + '</strong><br>' + escapeHtml(answer) + '</div></div>';
        });
      });
    }

    container.innerHTML =
      '<div class="recruit-review-grid">' +
        '<div class="recruit-review-group-title">Data Diri</div>' +
        reviewItem("Nama Lengkap", data.nama || "-") +
        reviewItem("Kelas", data.kelas || "-") +

        '<div class="recruit-review-group-title">Pilihan Sekbid</div>' +
        reviewItem("Sekbid", sekbidLabels.join(", ") || "-", true) +

        '<div class="recruit-review-group-title">Pertanyaan Umum</div>' +
        reviewItem("Visi dan Misi", data.visi_misi || "-", true) +
        reviewItem("Motivasi", data.motivasi || "-", true) +
        reviewItem("Kelebihan", data.kelebihan || "-", true) +
        reviewItem("Kekurangan", data.kekurangan || "-", true) +
        reviewItem("Pengalaman Organisasi", data.pengalaman || "-", true) +
        reviewItem("Skala Prioritas", data.prioritas || "-") +

        '<div class="recruit-review-group-title">Persyaratan Sekbid</div>' +
        jawabanHtml +

        '<div class="recruit-review-group-title">Google Drive</div>' +
        reviewItem("Link Google Drive Sertifikat", data.sertifikat_link || "-", true) +
        reviewItem("Link Google Drive Tugas Sekbid", data.google_drive_link || "-", true) +
      "</div>";
  }

  function reviewItem(label, value, full) {
    var cls = full ? ' class="recruit-review-item full"' : ' class="recruit-review-item"';
    return '<div' + cls + '><div class="recruit-review-label">' + label + '</div><div class="recruit-review-value">' + escapeHtml(value) + "</div></div>";
  }

  function escapeHtml(str) {
    if (!str) return "";
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function handleStart() {
    showSection("step1");
    loadProgress();
  }

  function handleStep1Next(e) {
    e.preventDefault();
    if (!validateStep1()) {
      showToast("Mohon periksa kembali data diri Anda", "error");
      return;
    }
    doAutosave();
    showSection("step2");
  }

  function handleStep1Back(e) {
    e.preventDefault();
    showSection("landing");
  }

  function handleStep2Next(e) {
    e.preventDefault();
    if (!validateStep2()) {
      showToast("Pilih minimal satu Sekbid", "error");
      return;
    }
    doAutosave();
    showLoading(true);
    buildStep4().then(function () {
      showLoading(false);
      showSection("step3");
    });
  }

  function handleStep2Back(e) {
    e.preventDefault();
    showSection("step1");
  }

  function handleStep3Next(e) {
    e.preventDefault();
    if (!validateStep3()) {
      showToast("Mohon periksa kembali jawaban Anda", "error");
      return;
    }
    doAutosave();
    showSection("step4");
  }

  function handleStep3Back(e) {
    e.preventDefault();
    showSection("step2");
  }

  function handleStep4Next(e) {
    e.preventDefault();
    if (!validateStep4()) {
      showToast("Mohon lengkapi link Google Drive", "error");
      return;
    }
    doAutosave();
    buildReview();
    showSection("review");
  }

  function handleStep4Back(e) {
    e.preventDefault();
    showSection("step3");
  }

  function handleReviewBack(e) {
    e.preventDefault();
    showSection("step4");
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (isSubmitting) return;
    isSubmitting = true;

    var fd = new FormData();
    for (var i = 1; i <= 4; i++) {
      var stepData = getFormData(i);
      Object.keys(stepData).forEach(function (k) {
        if (Array.isArray(stepData[k])) {
          stepData[k].forEach(function (v) { fd.append(k, v); });
        } else {
          fd.append(k, stepData[k]);
        }
      });
    }

    showLoading(true);
    var btn = e.target.closest(".recruit-btn-primary") || e.target;
    btn.disabled = true;
    btn.innerHTML = '<div class="recruit-spinner"></div> Mengirim...';

    fetch(apiPrefix + "/submit", {
      method: "POST",
      body: fd,
    })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        showLoading(false);
        if (res.success) {
          showSection("success");
          clearProgress();
          showToast(res.message, "success");
        } else {
          btn.disabled = false;
          btn.textContent = "Kirim Pendaftaran";
          showToast(res.message || "Pendaftaran gagal", "error");
        }
      })
      .catch(function () {
        showLoading(false);
        btn.disabled = false;
        btn.textContent = "Kirim Pendaftaran";
        showToast("Terjadi kesalahan. Silakan coba lagi.", "error");
      })
      .finally(function () {
        isSubmitting = false;
      });
  }

  function setupSekbidCards() {
    document.querySelectorAll("#recruit-form-step2 .recruit-sekbid-card").forEach(function (card) {
      card.addEventListener("click", function () {
        var isSelected = this.classList.contains("selected");
        var checkEl = this.querySelector(".sekbid-check");
        var hiddenInput = this.querySelector(".sekbid-hidden-input");

        if (isSelected) {
          this.classList.remove("selected");
          if (checkEl) checkEl.textContent = "";
          if (hiddenInput) hiddenInput.checked = false;
        } else {
          var selected = document.querySelectorAll("#recruit-form-step2 .recruit-sekbid-card.selected").length;
          if (selected >= 2) {
            showToast("Maksimal 2 pilihan Sekbid", "error");
            return;
          }
          this.classList.add("selected");
          if (checkEl) checkEl.textContent = "✓";
          if (hiddenInput) hiddenInput.checked = true;
        }
        triggerAutosave();
      });
    });
  }

  function setupAutosaveTriggers() {
    document.querySelectorAll("#recruit-form-step1 input, #recruit-form-step3 input, #recruit-form-step3 textarea, #recruit-form-step4 input, #recruit-form-step4 textarea").forEach(function (el) {
      el.addEventListener("input", triggerAutosave);
      el.addEventListener("change", triggerAutosave);
    });
  }

  function setupStep4Note() {
    var note = document.getElementById("recruit-step4-note");
    if (!note) return;
    var data = getFormData(2);
    var keys = data.sekbid || [];
    if (!keys.length) {
      note.innerHTML = '<div class="recruit-notice recruit-notice-warning"><i class="bx bx-info-circle"></i> Belum ada Sekbid dipilih. Silakan pilih Sekbid terlebih dahulu.</div>';
    }
  }

  function setupPersyaratanCheck() {
    var check = document.getElementById("recruit-persyaratan-check");
    var btn = document.getElementById("recruit-start-btn");
    if (!check || !btn) return;
    btn.disabled = true;
    check.addEventListener("change", function () {
      btn.disabled = !this.checked;
    });
  }

  function setupStepperClicks() {
    var bar = els.progressBar;
    if (!bar) return;
    bar.querySelectorAll(".recruit-step").forEach(function (step) {
      step.addEventListener("click", function () {
        if (!this.classList.contains("done")) return;
        var idx = parseInt(this.getAttribute("data-step"), 10);
        if (isNaN(idx)) return;
        var currentIdx = 0;
        var activeStep = bar.querySelector(".recruit-step.active");
        if (activeStep) currentIdx = parseInt(activeStep.getAttribute("data-step"), 10) || 0;
        if (idx >= currentIdx) return;
        showSection(stepIndexToSection[idx], true);
      });
    });
  }

  function init() {
    setupPersyaratanCheck();
    setupSekbidCards();
    setupAutosaveTriggers();
    setupStep4Note();
    setupStepperClicks();

    document.querySelectorAll("[data-recruit-action='start']").forEach(function (el) {
      el.addEventListener("click", handleStart);
    });
    document.querySelectorAll("[data-recruit-action='step1-next']").forEach(function (el) {
      el.addEventListener("click", handleStep1Next);
    });
    document.querySelectorAll("[data-recruit-action='step1-back']").forEach(function (el) {
      el.addEventListener("click", handleStep1Back);
    });
    document.querySelectorAll("[data-recruit-action='step2-next']").forEach(function (el) {
      el.addEventListener("click", handleStep2Next);
    });
    document.querySelectorAll("[data-recruit-action='step2-back']").forEach(function (el) {
      el.addEventListener("click", handleStep2Back);
    });
    document.querySelectorAll("[data-recruit-action='step3-next']").forEach(function (el) {
      el.addEventListener("click", handleStep3Next);
    });
    document.querySelectorAll("[data-recruit-action='step3-back']").forEach(function (el) {
      el.addEventListener("click", handleStep3Back);
    });
    document.querySelectorAll("[data-recruit-action='step4-next']").forEach(function (el) {
      el.addEventListener("click", handleStep4Next);
    });
    document.querySelectorAll("[data-recruit-action='step4-back']").forEach(function (el) {
      el.addEventListener("click", handleStep4Back);
    });
    document.querySelectorAll("[data-recruit-action='review-back']").forEach(function (el) {
      el.addEventListener("click", handleReviewBack);
    });
    document.querySelectorAll("[data-recruit-action='submit']").forEach(function (el) {
      el.addEventListener("click", handleSubmit);
    });

    loadProgress();
  }

  if (document.getElementById("recruit-landing")) {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
