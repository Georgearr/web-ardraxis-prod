document.addEventListener("DOMContentLoaded", function() {
    const loadingScreen = document.getElementById("loading-screen");
    if (loadingScreen) {
        setTimeout(() => loadingScreen.classList.add("hide"), 500);
    }

    const searchInput = document.getElementById("searchInput");
    const suggestions = document.getElementById("suggestions");
    const studentCard = document.getElementById("studentCard");

    const studentName = document.getElementById("studentName");
    const studentClass = document.getElementById("studentClass");
    const studentSekolah = document.getElementById("studentSekolah");
    const studentKelompok = document.getElementById("studentKelompok");
    const studentMentor = document.getElementById("studentMentor");
    const qrcodeContainer = document.getElementById("qrcode");
    const attendanceSummary = document.getElementById("attendanceSummary");

    let activeStudentId = null;

    const savedStudentId = localStorage.getItem("my_student_id");
    if (savedStudentId) {
        showStudentDetail(savedStudentId);
    }

    searchInput.addEventListener("input", function() {
        const val = searchInput.value.trim();
        if (val.length < 1) {
            suggestions.innerHTML = "";
            suggestions.style.display = "none";
            return;
        }
        fetch(`/api/students/search?q=${encodeURIComponent(val)}`)
            .then(res => res.json())
            .then(data => {
                suggestions.innerHTML = "";
                if (data.length > 0) {
                    data.forEach(student => {
                        const item = document.createElement("div");
                        item.classList.add("suggestion");
                        item.innerHTML = `<strong>${student.nama}</strong> - ${student.kelas} <span class="text-muted small">(${student.sekolah || '-'})</span>`;
                        item.addEventListener("click", () => {
                            searchInput.value = student.nama;
                            suggestions.innerHTML = "";
                            suggestions.style.display = "none";
                            showStudentDetail(student.id);
                        });
                        suggestions.appendChild(item);
                    });
                    suggestions.style.display = "block";
                } else {
                    suggestions.innerHTML = `<div class="suggestion text-muted">Siswa tidak ditemukan</div>`;
                    suggestions.style.display = "block";
                }
            })
            .catch(err => console.error("Error searching students:", err));
    });

    document.addEventListener("click", function(e) {
        if (e.target !== searchInput && e.target !== suggestions) {
            suggestions.innerHTML = "";
            suggestions.style.display = "none";
        }
    });

    function showStudentDetail(studentId) {
        studentCard.classList.remove("show");

        fetch(`/api/students/${studentId}`)
            .then(res => res.json())
            .then(res => {
                if (res.success) {
                    const student = res.student;
                    activeStudentId = student.id;

                    localStorage.setItem("my_student_id", student.id);
                    localStorage.setItem("my_student_name", student.nama);

                    studentName.innerText = student.nama;
                    studentClass.innerText = student.kelas;
                    studentSekolah.innerText = student.sekolah || '-';
                    studentKelompok.innerText = student.kelompok || '-';
                    studentMentor.innerText = student.mentor || '-';

                    // Render 5-day attendance
                    const days = student.attendance_5day || [];
                    days.forEach((d, i) => {
                        const dayEl = document.getElementById(`day-${i}`);
                        const timeEl = document.getElementById(`time-${i}`);
                        if (dayEl) {
                            if (d.status === "Hadir") {
                                dayEl.innerHTML = `<span class="badge-status present">Hadir</span>`;
                            } else if (d.status === "Tidak Hadir") {
                                dayEl.innerHTML = `<span class="badge-status" style="background:#f8d7da;color:#721c24;">Tidak Hadir</span>`;
                            } else if (d.status === "Belum Absen") {
                                dayEl.innerHTML = `<span class="badge-status absent">Belum</span>`;
                            } else {
                                dayEl.innerHTML = `<span class="text-muted">-</span>`;
                            }
                        }
                        if (timeEl) {
                            timeEl.innerText = d.timestamp ? d.timestamp.split(' ')[1] : '';
                        }
                    });

                    if (attendanceSummary) {
                        attendanceSummary.innerHTML = `<strong>Total Hadir:</strong> ${student.total_hadir} / ${student.total_days} hari`;
                    }

                    // Generate QR Code (hanya jika SHOW_QRIS aktif)
                    if (typeof SHOW_QRIS !== 'undefined' && SHOW_QRIS && typeof QRCode !== 'undefined' && qrcodeContainer) {
                        qrcodeContainer.innerHTML = "";
                        new QRCode(qrcodeContainer, {
                            text: student.id,
                            width: 180,
                            height: 180,
                            colorDark: "#1d696e",
                            colorLight: "#ffffff",
                            correctLevel: QRCode.CorrectLevel.H
                        });
                    }

                    studentCard.classList.remove("d-none");
                    setTimeout(() => studentCard.classList.add("show"), 50);
                    setTimeout(() => studentCard.scrollIntoView({ behavior: 'smooth', block: 'start' }), 150);
                } else {
                    alert(res.message);
                }
            })
            .catch(err => console.error("Error loading student details:", err));
    }

    function playBeep() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = "sine";
            osc.frequency.value = 880;
            gain.gain.setValueAtTime(0.25, ctx.currentTime);
            osc.start();
            osc.stop(ctx.currentTime + 0.12);
        } catch (e) {
            console.error("Audio beep failed:", e);
        }
    }

    const scannerModalElement = document.getElementById("scannerModal");
    const openScannerBtn = document.getElementById("openScanner");
    const closeScannerBtn = document.getElementById("closeScannerBtn");
    let html5Qrcode = null;

    if (scannerModalElement && openScannerBtn && closeScannerBtn) {
        openScannerBtn.addEventListener("click", function() {
            scannerModalElement.classList.add("show");
            html5Qrcode = new Html5Qrcode("reader");
            const config = { fps: 10, qrbox: { width: 250, height: 250 } };
            html5Qrcode.start(
                { facingMode: "environment" },
                config,
                onScanSuccess,
                onScanFailure
            ).catch(err => {
                console.error("Camera access error:", err);
                document.getElementById("reader").innerHTML = `
                    <div style="padding:15px;background:#f8d7da;color:#721c24;border-radius:8px;text-align:center;margin:15px;">
                        <i class="bi bi-exclamation-triangle-fill"></i><br>
                        Kamera tidak dapat diakses.<br>
                        Pastikan izin kamera telah diberikan.
                    </div>
                `;
            });
        });

        const closeModal = function() {
            if (html5Qrcode) {
                if (html5Qrcode.isScanning) {
                    html5Qrcode.stop().then(() => {
                        html5Qrcode.clear();
                        html5Qrcode = null;
                        scannerModalElement.classList.remove("show");
                    }).catch(err => {
                        console.error("Error stopping scanner:", err);
                        scannerModalElement.classList.remove("show");
                    });
                } else {
                    html5Qrcode = null;
                    scannerModalElement.classList.remove("show");
                }
            } else {
                scannerModalElement.classList.remove("show");
            }
        };

        closeScannerBtn.addEventListener("click", closeModal);
        scannerModalElement.addEventListener("click", function(e) {
            if (e.target === scannerModalElement) closeModal();
        });
        window.closeCustomScannerModal = closeModal;
    }

    function onScanSuccess(decodedText, decodedResult) {
        playBeep();
        if (window.closeCustomScannerModal) window.closeCustomScannerModal();

        const dataStr = decodedText.trim();
        if (dataStr.startsWith("STUDENT_")) {
            processCheckin(dataStr);
        } else if (dataStr.startsWith("SESSION_") || dataStr.includes("/absen") || dataStr.toLowerCase().includes("absen")) {
            const myId = localStorage.getItem("my_student_id");
            if (myId) {
                processCheckin(myId, true);
            } else {
                alert("Absen Mandiri Gagal: Silakan cari nama Anda terlebih dahulu!");
            }
        } else {
            processCheckin(dataStr);
        }
    }

    function onScanFailure(error) {}

    function processCheckin(studentId, isSelfScan = false) {
        fetch("/api/attendance/checkin", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ student_id: studentId })
        })
        .then(res => res.json())
        .then(res => {
            if (res.success) {
                alert(isSelfScan ? `Absen Mandiri Berhasil!\n${res.message}` : `Berhasil scan absensi!\n${res.message}`);
                if (activeStudentId === studentId) showStudentDetail(studentId);
            } else {
                alert(`Absen Gagal: ${res.message}`);
            }
        })
        .catch(err => {
            console.error("Check-in error:", err);
            alert("Terjadi kesalahan jaringan saat mencatat absensi.");
        });
    }
});
