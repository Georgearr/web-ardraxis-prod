document.addEventListener('DOMContentLoaded', () => {
  let currentStep = 1;
  const totalSteps = 9;

  const form = document.getElementById('dutaForm');
  const globalAlert = document.getElementById('globalAlert');
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  const btnSubmit = document.getElementById('btnSubmit');

  const programsContainer = document.getElementById('programsContainer');
  const btnAddProgram = document.getElementById('btnAddProgram');
  const certificatesContainer = document.getElementById('certificatesContainer');
  const btnAddCertificate = document.getElementById('btnAddCertificate');
  const talentVideosContainer = document.getElementById('talentVideosContainer');
  const btnAddTalentVideo = document.getElementById('btnAddTalentVideo');
  const reviewContainer = document.getElementById('reviewContainer');

  const successModal = document.getElementById('successModal');
  const successAppId = document.getElementById('successAppId');
  const btnCopyId = document.getElementById('btnCopyId');

  const visionMissionInput = document.getElementById('vision_mission');
  const vmCounter = document.getElementById('vmCounter');
  const motivationInput = document.getElementById('motivation_letter');
  const paraCounter = document.getElementById('paraCounter');
  const motivationWarning = document.getElementById('motivationWarning');

  const expRadioYes = document.getElementById('expRadioYes');
  const expRadioNo = document.getElementById('expRadioNo');
  const expDetailContainer = document.getElementById('expDetailContainer');
  const noExpInfo = document.getElementById('noExpInfo');

  initDynamicPrograms();
  initDynamicCertificates();
  initDynamicTalentVideos();
  updateStepView();

  // Smooth scroll Hero CTA
  document.getElementById('btnHeroCta')?.addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('formSection').scrollIntoView({ behavior: 'smooth' });
  });

  // Progress Paper Tab Navigation
  document.querySelectorAll('.progress-paper-tab').forEach(tab => {
    tab.addEventListener('click', function() {
      const targetStep = parseInt(this.getAttribute('data-tab'));
      if (targetStep < currentStep || validateStep(currentStep)) {
        currentStep = targetStep;
        if (currentStep === 9) renderReviewPage();
        updateStepView();
      }
    });
  });

  // Vision Mission Char Counter
  visionMissionInput?.addEventListener('input', () => {
    vmCounter.textContent = visionMissionInput.value.length;
  });

  // Motivation Letter Paragraph Counter
  motivationInput?.addEventListener('input', () => {
    const text = motivationInput.value.trim();
    const paragraphs = text ? text.split(/\n\s*\n/).filter(p => p.trim().length > 0) : [];
    const count = paragraphs.length;
    paraCounter.textContent = count;

    if (count > 3) {
      motivationWarning.style.display = 'block';
    } else {
      motivationWarning.style.display = 'none';
    }
  });

  // Experience Toggle Radio Card
  document.querySelectorAll('input[name="has_experience"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
      if (e.target.value === 'Ya') {
        expDetailContainer.classList.remove('hidden');
        noExpInfo.classList.add('hidden');
        expRadioYes.classList.add('selected');
        expRadioNo.classList.remove('selected');
      } else {
        expDetailContainer.classList.add('hidden');
        noExpInfo.classList.remove('hidden');
        expRadioNo.classList.add('selected');
        expRadioYes.classList.remove('selected');
      }
    });
  });

  // Radio Paper Card Selection Styling
  document.querySelectorAll('.radio-paper-item input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', function() {
      const parentName = this.getAttribute('name');
      document.querySelectorAll(`input[name="${parentName}"]`).forEach(r => {
        r.closest('.radio-paper-item')?.classList.remove('selected');
      });
      if (this.checked) {
        this.closest('.radio-paper-item')?.classList.add('selected');
      }
    });
  });

  // --- Dynamic Programs ---
  function initDynamicPrograms() {
    addProgramItem();
  }

  btnAddProgram?.addEventListener('click', () => addProgramItem());

  function addProgramItem(data = {}) {
    const count = programsContainer.children.length + 1;
    const div = document.createElement('div');
    div.className = 'dynamic-paper-card program-item';
    div.innerHTML = `
      <div class="dynamic-card-header">
        <span class="dynamic-card-title">PROGRAM KERJA #${count}</span>
        ${count > 1 ? '<button type="button" class="btn-remove-dynamic">REMOVE</button>' : ''}
      </div>
      <div class="form-group-item">
        <label class="input-label">Nama Program <span class="req">*</span></label>
        <input type="text" class="input-control prog-name" placeholder="Nama program kerja..." value="${data.nama_program || ''}" required>
      </div>
      <div class="form-group-item">
        <label class="input-label">Tujuan</label>
        <input type="text" class="input-control prog-tujuan" placeholder="Tujuan utama program..." value="${data.tujuan || ''}">
      </div>
      <div class="form-group-item">
        <label class="input-label">Target</label>
        <input type="text" class="input-control prog-target" placeholder="Sasaran peserta..." value="${data.target || ''}">
      </div>
      <div class="form-group-item" style="margin-bottom:0;">
        <label class="input-label">Deskripsi Program</label>
        <textarea class="input-control prog-deskripsi" rows="2" placeholder="Deskripsi singkat cara pelaksanaan...">${data.deskripsi || ''}</textarea>
      </div>
    `;

    div.querySelector('.btn-remove-dynamic')?.addEventListener('click', () => {
      div.remove();
      renumberPrograms();
    });

    programsContainer.appendChild(div);
  }

  function renumberPrograms() {
    Array.from(programsContainer.children).forEach((card, idx) => {
      const titleSpan = card.querySelector('.dynamic-card-title');
      if (titleSpan) titleSpan.textContent = `PROGRAM KERJA #${idx + 1}`;
    });
  }

  function getProgramsData() {
    const list = [];
    document.querySelectorAll('.program-item').forEach(card => {
      const name = card.querySelector('.prog-name')?.value.trim();
      const tujuan = card.querySelector('.prog-tujuan')?.value.trim();
      const target = card.querySelector('.prog-target')?.value.trim();
      const deskripsi = card.querySelector('.prog-deskripsi')?.value.trim();
      if (name) list.push({ nama_program: name, tujuan, target, deskripsi });
    });
    return list;
  }

  // --- Dynamic Certificates ---
  function initDynamicCertificates() {
    addCertificateItem();
  }

  btnAddCertificate?.addEventListener('click', () => addCertificateItem());

  function addCertificateItem(url = '') {
    const count = certificatesContainer.children.length + 1;
    const div = document.createElement('div');
    div.className = 'dynamic-paper-card cert-item';
    div.innerHTML = `
      <div class="dynamic-card-header">
        <span class="dynamic-card-title">🔗 LINK SERTIFIKAT #${count}</span>
        ${count > 1 ? '<button type="button" class="btn-remove-dynamic">REMOVE</button>' : ''}
      </div>
      <div class="form-group-item" style="margin-bottom:0;">
        <input type="url" class="input-control cert-url" placeholder="https://drive.google.com/..." value="${url}">
        <div class="link-preview-tag hidden cert-preview">
          🔗 <a href="#" target="_blank" rel="noopener noreferrer">Buka Link Sertifikat ↗</a>
        </div>
      </div>
    `;

    div.querySelector('.btn-remove-dynamic')?.addEventListener('click', () => {
      div.remove();
      renumberCertificates();
    });

    const urlInput = div.querySelector('.cert-url');
    const previewBox = div.querySelector('.cert-preview');
    const previewAnchor = previewBox.querySelector('a');

    urlInput.addEventListener('input', () => {
      const val = urlInput.value.trim();
      if (isValidHttpUrl(val)) {
        previewAnchor.href = val;
        previewBox.classList.remove('hidden');
      } else {
        previewBox.classList.add('hidden');
      }
    });

    certificatesContainer.appendChild(div);
  }

  function renumberCertificates() {
    Array.from(certificatesContainer.children).forEach((card, idx) => {
      const titleSpan = card.querySelector('.dynamic-card-title');
      if (titleSpan) titleSpan.textContent = `🔗 LINK SERTIFIKAT #${idx + 1}`;
    });
  }

  function getCertificatesData() {
    const list = [];
    document.querySelectorAll('.cert-url').forEach(input => {
      const val = input.value.trim();
      if (val && isValidHttpUrl(val)) list.push(val);
    });
    return list;
  }

  // --- Dynamic Talent Videos ---
  function initDynamicTalentVideos() {
    addTalentVideoItem();
  }

  btnAddTalentVideo?.addEventListener('click', () => addTalentVideoItem());

  function addTalentVideoItem(url = '') {
    const count = talentVideosContainer.children.length + 1;
    const div = document.createElement('div');
    div.className = 'dynamic-paper-card talent-item';
    div.innerHTML = `
      <div class="dynamic-card-header">
        <span class="dynamic-card-title">🎬 LINK VIDEO BAKAT #${count}</span>
        ${count > 1 ? '<button type="button" class="btn-remove-dynamic">REMOVE</button>' : ''}
      </div>
      <div class="form-group-item" style="margin-bottom:0;">
        <input type="url" class="input-control talent-url" placeholder="https://drive.google.com/... atau https://youtube.com/..." value="${url}">
        <div class="link-preview-tag hidden talent-preview">
          🎬 <a href="#" target="_blank" rel="noopener noreferrer">OPEN VIDEO ↗</a>
        </div>
      </div>
    `;

    div.querySelector('.btn-remove-dynamic')?.addEventListener('click', () => {
      div.remove();
      renumberTalentVideos();
    });

    const urlInput = div.querySelector('.talent-url');
    const previewBox = div.querySelector('.talent-preview');
    const previewAnchor = previewBox.querySelector('a');

    urlInput.addEventListener('input', () => {
      const val = urlInput.value.trim();
      if (isValidHttpUrl(val)) {
        previewAnchor.href = val;
        previewBox.classList.remove('hidden');
      } else {
        previewBox.classList.add('hidden');
      }
    });

    talentVideosContainer.appendChild(div);
  }

  function renumberTalentVideos() {
    Array.from(talentVideosContainer.children).forEach((card, idx) => {
      const titleSpan = card.querySelector('.dynamic-card-title');
      if (titleSpan) titleSpan.textContent = `🎬 LINK VIDEO BAKAT #${idx + 1}`;
    });
  }

  function getTalentVideosData() {
    const list = [];
    document.querySelectorAll('.talent-url').forEach(input => {
      const val = input.value.trim();
      if (val && isValidHttpUrl(val)) list.push(val);
    });
    return list;
  }

  function isValidHttpUrl(string) {
    let url;
    try { url = new URL(string); } catch (_) { return false; }
    return url.protocol === "http:" || url.protocol === "https:";
  }

  // --- Step Navigation & View Handler ---
  btnPrev.addEventListener('click', () => {
    if (currentStep > 1) {
      currentStep--;
      updateStepView();
    }
  });

  btnNext.addEventListener('click', () => {
    if (validateStep(currentStep)) {
      currentStep++;
      if (currentStep === 9) renderReviewPage();
      updateStepView();
    }
  });

  function updateStepView() {
    hideGlobalAlert();

    // Progress paper tabs
    document.querySelectorAll('.progress-paper-tab').forEach(tab => {
      const tNum = parseInt(tab.getAttribute('data-tab'));
      tab.classList.remove('active', 'completed');
      if (tNum === currentStep) tab.classList.add('active');
      else if (tNum < currentStep) tab.classList.add('completed');
    });

    // Step views
    document.querySelectorAll('.form-step-view').forEach(view => {
      const sNum = parseInt(view.getAttribute('data-step'));
      if (sNum === currentStep) view.classList.add('active');
      else view.classList.remove('active');
    });

    // Navigation buttons
    btnPrev.style.visibility = (currentStep === 1) ? 'hidden' : 'visible';

    if (currentStep === 9) {
      btnNext.classList.add('hidden');
      btnSubmit.classList.remove('hidden');
    } else {
      btnNext.classList.remove('hidden');
      btnSubmit.classList.add('hidden');
    }

    const targetEl = document.getElementById('formSection');
    if (targetEl) {
      window.scrollTo({ top: targetEl.offsetTop - 40, behavior: 'smooth' });
    }
  }

  // --- Step Validation ---
  function validateStep(step) {
    hideGlobalAlert();

    if (step === 1) {
      const name = document.getElementById('full_name').value.trim();
      const cls = document.getElementById('class').value.trim();
      if (!name) return alertError('Nama Lengkap wajib diisi.');
      if (!cls) return alertError('Kelas wajib diisi.');
      if (cls.length > 30) return alertError('Kelas maksimal 30 karakter.');
    } else if (step === 2) {
      const vm = visionMissionInput.value.trim();
      if (!vm) return alertError('Visi dan Misi Duta IGS wajib diisi.');
      if (vm.length > 1000) return alertError('Visi dan Misi maksimal 1000 karakter.');
    } else if (step === 3) {
      const progs = getProgramsData();
      if (progs.length === 0) return alertError('Minimal harus menambahkan 1 nama program kerja.');
    } else if (step === 4) {
      const motiv = motivationInput.value.trim();
      if (!motiv) return alertError('Motivation Letter wajib diisi.');
      const paragraphs = motiv.split(/\n\s*\n/).filter(p => p.trim().length > 0);
      if (paragraphs.length > 3) return alertError('Motivation letter maksimal 3 paragraf.');
    } else if (step === 5) {
      const expChoice = document.querySelector('input[name="has_experience"]:checked')?.value;
      if (expChoice === 'Ya') {
        const expText = document.getElementById('experiences').value.trim();
        if (!expText) return alertError('Silakan ceritakan pengalaman kamu.');
      }
    } else if (step === 6) {
      let valid = true;
      document.querySelectorAll('.cert-url').forEach((input, idx) => {
        const val = input.value.trim();
        if (val && !isValidHttpUrl(val)) {
          alertError(`Link Sertifikat #${idx + 1} tidak valid. Masukkan URL HTTP/HTTPS yang benar.`);
          valid = false;
        }
      });
      if (!valid) return false;
    } else if (step === 7) {
      const videos = getTalentVideosData();
      if (videos.length === 0) return alertError('Silakan masukkan minimal 1 link video bakat yang valid.');
    } else if (step === 8) {
      const comm = document.querySelector('input[name="commitment"]:checked')?.value;
      const agree = document.getElementById('agreement').checked;
      if (comm !== 'Ya, saya yakin.') return alertError('Anda harus memilih "Ya, saya yakin." untuk dapat mengirim pendaftaran.');
      if (!agree) return alertError('Anda wajib mengonfirmasi persetujuan kebenaran data.');
    }

    return true;
  }

  function alertError(msg) {
    globalAlert.textContent = '⚠️ ' + msg;
    globalAlert.style.display = 'block';
    globalAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return false;
  }

  function hideGlobalAlert() {
    globalAlert.style.display = 'none';
  }

  // --- Step 9 (Review Page) ---
  function renderReviewPage() {
    const fullName = document.getElementById('full_name').value.trim();
    const studentClass = document.getElementById('class').value.trim();
    const visionMission = visionMissionInput.value.trim();
    const programs = getProgramsData();
    const motivation = motivationInput.value.trim();
    const hasExp = document.querySelector('input[name="has_experience"]:checked')?.value;
    const experiences = document.getElementById('experiences').value.trim();
    const certs = getCertificatesData();
    const videos = getTalentVideosData();
    const commitment = document.querySelector('input[name="commitment"]:checked')?.value;

    let html = `
      <div class="review-summary-card">
        <div class="review-card-head">
          <span class="review-card-title">01. Personal Information</span>
          <button type="button" class="btn-review-edit" data-target="1">EDIT</button>
        </div>
        <div><strong>Nama:</strong> ${escapeHtml(fullName)}</div>
        <div><strong>Kelas:</strong> ${escapeHtml(studentClass)}</div>
      </div>

      <div class="review-summary-card">
        <div class="review-card-head">
          <span class="review-card-title">02. Vision & Mission</span>
          <button type="button" class="btn-review-edit" data-target="2">EDIT</button>
        </div>
        <div style="white-space: pre-wrap;">${escapeHtml(visionMission)}</div>
      </div>

      <div class="review-summary-card">
        <div class="review-card-head">
          <span class="review-card-title">03. Program Kerja</span>
          <button type="button" class="btn-review-edit" data-target="3">EDIT</button>
        </div>
        ${programs.map((p, i) => `
          <div style="margin-bottom:8px;">
            <div><strong>Program #${i + 1}:</strong> ${escapeHtml(p.nama_program)}</div>
            ${p.tujuan ? `<div>Tujuan: ${escapeHtml(p.tujuan)}</div>` : ''}
            ${p.target ? `<div>Target: ${escapeHtml(p.target)}</div>` : ''}
            ${p.deskripsi ? `<div>Deskripsi: ${escapeHtml(p.deskripsi)}</div>` : ''}
          </div>
        `).join('')}
      </div>

      <div class="review-summary-card">
        <div class="review-card-head">
          <span class="review-card-title">04. Motivation Letter</span>
          <button type="button" class="btn-review-edit" data-target="4">EDIT</button>
        </div>
        <div style="white-space: pre-wrap;">${escapeHtml(motivation)}</div>
      </div>

      <div class="review-summary-card">
        <div class="review-card-head">
          <span class="review-card-title">05. Experience</span>
          <button type="button" class="btn-review-edit" data-target="5">EDIT</button>
        </div>
        <div><strong>Memiliki Pengalaman:</strong> ${escapeHtml(hasExp)}</div>
        ${hasExp === 'Ya' ? `<div style="white-space: pre-wrap; margin-top:4px;">${escapeHtml(experiences)}</div>` : ''}
      </div>

      <div class="review-summary-card">
        <div class="review-card-head">
          <span class="review-card-title">06. Certificates</span>
          <button type="button" class="btn-review-edit" data-target="6">EDIT</button>
        </div>
        ${certs.length > 0 ? certs.map((c, i) => `
          <div>Sertifikat #${i + 1}: <a href="${escapeHtml(c)}" target="_blank" rel="noopener noreferrer">${truncateUrl(c)} ↗</a></div>
        `).join('') : '<em>Tidak ada sertifikat dilampirkan</em>'}
      </div>

      <div class="review-summary-card">
        <div class="review-card-head">
          <span class="review-card-title">07. Talent Video</span>
          <button type="button" class="btn-review-edit" data-target="7">EDIT</button>
        </div>
        ${videos.map((v, i) => `
          <div>Video #${i + 1}: <a href="${escapeHtml(v)}" target="_blank" rel="noopener noreferrer">${truncateUrl(v)} ↗</a></div>
        `).join('')}
      </div>

      <div class="review-summary-card">
        <div class="review-card-head">
          <span class="review-card-title">08. Commitment</span>
          <button type="button" class="btn-review-edit" data-target="8">EDIT</button>
        </div>
        <div><strong>Komitmen:</strong> ${escapeHtml(commitment)}</div>
        <div><strong>Persetujuan Data:</strong> Ya, sudah disetujui.</div>
      </div>
    `;

    reviewContainer.innerHTML = html;

    document.querySelectorAll('.btn-review-edit').forEach(btn => {
      btn.addEventListener('click', function() {
        currentStep = parseInt(this.getAttribute('data-target'));
        updateStepView();
      });
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }

  function truncateUrl(url) {
    if (!url) return '';
    return url.length > 40 ? url.substring(0, 35) + '...' : url;
  }

  // --- Submission Handler ---
  btnSubmit.addEventListener('click', async () => {
    hideGlobalAlert();

    const payload = {
      full_name: document.getElementById('full_name').value.trim(),
      class: document.getElementById('class').value.trim(),
      vision_mission: visionMissionInput.value.trim(),
      programs: getProgramsData(),
      motivation_letter: motivationInput.value.trim(),
      has_experience: document.querySelector('input[name="has_experience"]:checked')?.value === 'Ya',
      experiences: document.getElementById('experiences').value.trim(),
      certificate_urls: getCertificatesData(),
      talent_video_urls: getTalentVideosData(),
      commitment: document.querySelector('input[name="commitment"]:checked')?.value,
      agreement: document.getElementById('agreement').checked
    };

    btnSubmit.disabled = true;
    btnSubmit.innerHTML = 'SUBMITTING APPLICATION...';

    try {
      const response = await fetch('/dutasmaigs/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (response.ok && result.success) {
        successAppId.textContent = result.applicationId;
        successModal.classList.remove('hidden');
        successModal.style.display = 'flex';
      } else {
        alertError(result.message || 'Pendaftaran belum berhasil dikirim. Silakan coba kembali.');
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = 'SUBMIT APPLICATION →';
      }
    } catch (err) {
      alertError('Terjadi kesalahan koneksi. Silakan periksa jaringan dan coba lagi.');
      btnSubmit.disabled = false;
      btnSubmit.innerHTML = 'SUBMIT APPLICATION →';
    }
  });

  // Copy Application ID
  btnCopyId?.addEventListener('click', () => {
    const textToCopy = successAppId.textContent.trim();
    navigator.clipboard.writeText(textToCopy).then(() => {
      btnCopyId.textContent = '✅ COPIED TO CLIPBOARD!';
      setTimeout(() => {
        btnCopyId.textContent = '📋 Copy Application ID';
      }, 2500);
    });
  });
});
