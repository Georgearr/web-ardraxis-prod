(function () {
  const form = document.getElementById("ravenith-form");
  if (!form) return;

  const cfg = window.RAVENITH_REGIST || {};
  const scriptUrl = cfg.scriptUrl;
  const competition = cfg.competition;
  const lineGroup = cfg.lineGroup || "#";
  const statusEl = document.getElementById("registration-status");
  const modal = document.getElementById("successModal");
  const closeBtn = document.querySelector("#successModal .close");
  const lineGroupLink = document.getElementById("lineGroupLink");
  const lineGroupUrl = document.getElementById("lineGroupUrl");

  function setStatus(html, variant) {
    if (!statusEl) return;
    statusEl.innerHTML = html;
    statusEl.classList.remove("status--full", "status--warn", "status--ok");
    if (variant) statusEl.classList.add("status--" + variant);
  }

  function loadStatus() {
    if (!scriptUrl || scriptUrl.includes("GANTI_DENGAN")) {
      setStatus("<p>Status pendaftaran: hubungkan URL Apps Script di <code>.env</code>.</p>", "warn");
      return;
    }
    setStatus("<p>Memuat status pendaftaran...</p>");
    fetch(scriptUrl + "?action=status&competition=" + encodeURIComponent(competition))
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (data.error) {
          setStatus("<p>Tidak dapat memuat status.</p>", "warn");
          return;
        }
        var label = data.limit_type === "participant" ? "peserta" : "tim";
        var html = "<p><strong>Pendaftaran:</strong> " + data.current_count;
        if (data.limit > 0) {
          html += " / " + data.limit + " " + label;
          if (data.spots_left > 0) {
            html += " (sisa " + data.spots_left + ")";
          } else if (data.is_full) {
            html += " <strong>(PENUH)</strong>";
          }
        } else {
          html += " (tanpa batas)";
        }
        html += "</p>";
        setStatus(html, data.is_full ? "full" : data.spots_left <= 3 && data.limit > 0 ? "warn" : "ok");

        var btn = form.querySelector('button[type="submit"]');
        if (data.is_full && btn) {
          btn.disabled = true;
          btn.textContent = "Pendaftaran Penuh";
        }
      })
      .catch(function () {
        setStatus("<p>Status tidak tersedia (pastikan Apps Script sudah di-deploy).</p>", "warn");
      });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!scriptUrl || scriptUrl.includes("GANTI_DENGAN")) {
      alert("URL Google Apps Script belum diatur. Isi RAVENITH_APPS_SCRIPT_URL di file .env");
      return;
    }

    var btn = form.querySelector('button[type="submit"]');
    var fd = new FormData(form);
    fd.append("competition", competition);
    fd.append("action", "register");

    btn.disabled = true;
    btn.textContent = "Mengirim...";

    fetch(scriptUrl, { method: "POST", body: fd })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (data.success) {
          if (lineGroupLink) lineGroupLink.href = lineGroup;
          if (lineGroupUrl) lineGroupUrl.textContent = lineGroup || "-";
          if (modal) modal.style.display = "block";
          form.reset();
          loadStatus();
        } else {
          alert(data.message || "Pendaftaran gagal.");
        }
      })
      .catch(function () {
        alert("Terjadi kesalahan. Coba lagi atau hubungi panitia.");
      })
      .finally(function () {
        btn.disabled = false;
        btn.textContent = "Daftar";
      });
  });

  if (closeBtn && modal) {
    closeBtn.onclick = function () {
      modal.style.display = "none";
    };
    window.addEventListener("click", function (ev) {
      if (ev.target === modal) modal.style.display = "none";
    });
  }

  loadStatus();
})();
