document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("festioraForm");
    if (!form) return;

    // Fungsi untuk menampilkan modal dengan animasi
    function showSuccessModal(lineLink = "#") {
        const modal = document.getElementById("successModal");
        const lineGroupLink = document.getElementById("lineGroupLink");
        
        if (lineGroupLink && lineLink !== "#") {
            lineGroupLink.href = lineLink;
        }
        
        if (modal) {
            modal.classList.add("active");
            document.body.style.overflow = "hidden";
        }
    }

    // Fungsi untuk menutup modal
    function closeModal() {
        const modal = document.getElementById("successModal");
        if (modal) {
            modal.classList.remove("active");
            document.body.style.overflow = "";
        }
    }

    // Fungsi untuk menampilkan modal pendaftaran ditutup
    function showClosedModal() {
        const modal = document.getElementById("closedModal");
        if (modal) {
            modal.classList.add("active");
            document.body.style.overflow = "hidden";
        }
    }

    // Fungsi untuk menutup modal pendaftaran ditutup
    function closeClosedModal() {
        const modal = document.getElementById("closedModal");
        if (modal) {
            modal.classList.remove("active");
            document.body.style.overflow = "";
        }
    }

    // Event listener untuk tombol tutup modal
    const closeBtn = document.querySelector(".modal-close");
    if (closeBtn) {
        closeBtn.addEventListener("click", closeModal);
    }

    // Event listener untuk backdrop modal success
    const modalOverlay = document.getElementById("successModal");
    if (modalOverlay) {
        modalOverlay.addEventListener("click", (e) => {
            if (e.target === modalOverlay) {
                closeModal();
            }
        });
    }

    // Event listener untuk backdrop modal closed
    const closedModalOverlay = document.getElementById("closedModal");
    if (closedModalOverlay) {
        closedModalOverlay.addEventListener("click", (e) => {
            if (e.target === closedModalOverlay) {
                closeClosedModal();
            }
        });
    }

    // Event listener untuk tombol tutup modal closed
    const closedCloseBtn = document.querySelector("#closedModal .modal-close");
    if (closedCloseBtn) {
        closedCloseBtn.addEventListener("click", closeClosedModal);
    }

    // Event listener untuk ESC key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeModal();
            closeClosedModal();
        }
    });

    // Expose closeModal ke global scope untuk onclick di HTML
    window.closeModal = closeModal;
    window.closeClosedModal = closeClosedModal;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const submitButton = form.querySelector("button[type='submit']");
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = "Mengirim...";
        submitButton.style.opacity = "0.7";

        try {
            // Ambil nama lomba dari data-lomba
            const formType = form.dataset.lomba;
            const formData = new FormData(form);

            // Kirim data ke Flask
            const response = await fetch(`/festiora_submit/${formType}`, {
                method: "POST",
                body: formData
            });

            // Parse response JSON (termasuk jika status code 403)
            const result = await response.json().catch(() => {
                // Jika gagal parse, return default error
                return { status: "error", message: "Terjadi kesalahan pada server" };
            });

            if (result.status === "ok") {
                // Ambil link LINE dari response atau dari data attribute form
                const lineLink = result.line_link || form.dataset.lineLink || "#";
                
                // Reset form
                form.reset();
                
                // Tampilkan modal dengan animasi
                showSuccessModal(lineLink);
            } else if (result.status === "closed") {
                // Pendaftaran ditutup
                showClosedModal();
            } else {
                alert("Terjadi kesalahan. Coba lagi.");
            }
            
        } catch (err) {
            console.error("Error:", err);
            alert("Gagal mengirim data. Cek koneksi atau server.");
        } finally {
            // Re-enable button
            submitButton.disabled = false;
            submitButton.textContent = originalText;
            submitButton.style.opacity = "1";
        }
    });
});
