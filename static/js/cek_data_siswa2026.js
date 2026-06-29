document.addEventListener("DOMContentLoaded", function() {
    // Hide loading screen
    const loadingScreen = document.getElementById("loading-screen");
    if (loadingScreen) {
        setTimeout(() => {
            loadingScreen.classList.add("hide");
        }, 500);
    }

    const searchInput = document.getElementById("searchInput");
    const suggestions = document.getElementById("suggestions");
    const studentCard = document.getElementById("studentCard");
    
    const studentName = document.getElementById("studentName");
    const studentClass = document.getElementById("studentClass");
    const studentGroup = document.getElementById("studentGroup");
    const studentType = document.getElementById("studentType");
    const studentMentor = document.getElementById("studentMentor");
    const attendanceStatus = document.getElementById("studentAttendanceStatus");
    const checkinTime = document.getElementById("studentCheckinTime");
    const qrcodeContainer = document.getElementById("qrcode");

    let activeStudentId = null;

    // Load last searched student from localStorage
    const savedStudentId = localStorage.getItem("my_student_id");
    if (savedStudentId) {
        showStudentDetail(savedStudentId);
    }

    // Auto-suggestion Search
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
                        item.innerHTML = `<strong>${student.nama}</strong> - ${student.kelas} (${student.kelompok} ${student.jenis})`;
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

    // Close suggestions dropdown when clicking outside
    document.addEventListener("click", function(e) {
        if (e.target !== searchInput && e.target !== suggestions) {
            suggestions.innerHTML = "";
            suggestions.style.display = "none";
        }
    });

    // Show student detail card
    function showStudentDetail(studentId) {
        studentCard.classList.remove("show"); // Reset transition state
        
        fetch(`/api/students/${studentId}`)
            .then(res => res.json())
            .then(res => {
                if (res.success) {
                    const student = res.student;
                    activeStudentId = student.id;
                    
                    // Save to localstorage as identified user
                    localStorage.setItem("my_student_id", student.id);
                    localStorage.setItem("my_student_name", student.nama);

                    studentName.innerText = student.nama;
                    studentClass.innerText = student.kelas;
                    studentGroup.innerText = student.kelompok;
                    studentType.innerText = `${student.jenis} (Sub-kelompok ${student.sub_kelompok})`;
                    studentMentor.innerText = student.mentor;

                    // Update attendance badge with custom styling classes
                    if (student.is_present) {
                        attendanceStatus.innerText = "Hadir";
                        attendanceStatus.className = "badge-status present";
                        checkinTime.innerText = `Absen pada: ${student.checkin_time}`;
                        checkinTime.classList.remove("d-none");
                    } else {
                        attendanceStatus.innerText = "Belum Absen";
                        attendanceStatus.className = "badge-status absent";
                        checkinTime.innerText = "";
                        checkinTime.classList.add("d-none");
                    }

                    // Display total days attended
                    if (student.total_days_present > 0) {
                        const daysInfo = document.createElement("p");
                        daysInfo.className = "mt-2 small text-muted";
                        daysInfo.innerHTML = `<i class="bi bi-calendar-check"></i> Total hadir: ${student.total_days_present} hari`;
                        checkinTime.parentNode.insertBefore(daysInfo, checkinTime.nextSibling);
                    }

                    // Generate QR Code containing the student ID
                    qrcodeContainer.innerHTML = "";
                    new QRCode(qrcodeContainer, {
                        text: student.id,
                        width: 180,
                        height: 180,
                        colorDark: "#1d696e",
                        colorLight: "#ffffff",
                        correctLevel: QRCode.CorrectLevel.H
                    });

                    studentCard.classList.remove("d-none");
                    
                    // Trigger fade-in / slide-up animation
                    setTimeout(() => {
                        studentCard.classList.add("show");
                    }, 50);
                    
                    // Scroll to card
                    setTimeout(() => {
                        studentCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 150);
                } else {
                    alert(res.message);
                }
            })
            .catch(err => console.error("Error loading student details:", err));
    }

    // Dynamic Sound Beep on scan success
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

    // Modal Camera Scanner Integration
    const scannerModalElement = document.getElementById("scannerModal");
    const openScannerBtn = document.getElementById("openScanner");
    const closeScannerBtn = document.getElementById("closeScannerBtn");
    let html5Qrcode = null;

    if (scannerModalElement && openScannerBtn && closeScannerBtn) {
        openScannerBtn.addEventListener("click", function() {
            scannerModalElement.classList.add("show");
            
            // Start camera scanning
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
                    <div style="padding: 15px; background-color: #f8d7da; color: #721c24; border-radius: 8px; text-align: center; margin: 15px;">
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

        // Close modal when clicking outside custom-modal-content
        scannerModalElement.addEventListener("click", function(e) {
            if (e.target === scannerModalElement) {
                closeModal();
            }
        });

        // Expose close function globally to use inside scan success
        window.closeCustomScannerModal = closeModal;
    }

    function onScanSuccess(decodedText, decodedResult) {
        playBeep();
        
        // Stop scanning immediately and close modal
        if (window.closeCustomScannerModal) {
            window.closeCustomScannerModal();
        }

        const dataStr = decodedText.trim();

        // Evaluate code type:
        if (dataStr.startsWith("STUDENT_")) {
            // Case A: Supervisor scanning a student's card
            processCheckin(dataStr);
        } else if (dataStr.startsWith("SESSION_") || dataStr.includes("/absen") || dataStr.toLowerCase().includes("absen")) {
            // Case B: Student scanning an event's session QR code to self check-in
            const myId = localStorage.getItem("my_student_id");
            if (myId) {
                processCheckin(myId, true);
            } else {
                alert("Absen Mandiri Gagal: Silakan cari nama Anda terlebih dahulu sebelum memindai QR Sesi Absen!");
            }
        } else {
            // Default check-in trigger
            processCheckin(dataStr);
        }
    }

    function onScanFailure(error) {
        // Silent failure (expected when QR code is not detected in frame)
    }

    function processCheckin(studentId, isSelfScan = false) {
        fetch("/api/attendance/checkin", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ student_id: studentId })
        })
        .then(res => res.json())
        .then(res => {
            if (res.success) {
                alert(isSelfScan ? `Absen Mandiri Berhasil!\n${res.message}` : `Berhasil scan absensi!\n${res.message}`);
                
                // If the updated student is the one currently displayed on screen, refresh details
                if (activeStudentId === studentId) {
                    showStudentDetail(studentId);
                }
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