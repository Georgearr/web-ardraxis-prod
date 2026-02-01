function testAuth() {
  DriveApp.getRootFolder();
}
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("valentineOrderForm");
    const notesSection = document.getElementById("notesSection");
    const notesTextarea = document.getElementById("notesTextarea");
    const wordCount = document.getElementById("wordCount");
    const paymentProof = document.getElementById("paymentProof");
    const fileUploadLabel = document.getElementById("fileUploadLabel");
    const fileName = document.getElementById("fileName");
    const submitButton = document.getElementById("submitButton");
    const productRadios = document.querySelectorAll('input[name="product"]');
    const chocobloomCheckbox = document.getElementById("chocobloomCheckbox");
    const colorSelection = document.getElementById("colorSelection");
    const colorRadios = document.querySelectorAll('input[name="forever_flowers_color"]');

    // Show/hide notes section based on Chocobloom checkbox
    if (chocobloomCheckbox) {
        chocobloomCheckbox.addEventListener("change", () => {
            if (chocobloomCheckbox.checked) {
                notesSection.style.display = "block";
                notesTextarea.required = true;
            } else {
                notesSection.style.display = "none";
                notesTextarea.required = false;
                notesTextarea.value = "";
                updateWordCount();
            }
        });
    }

    // Word count for notes (max 40 words)
    function countWords(text) {
        return text.trim().split(/\s+/).filter(word => word.length > 0).length;
    }

    function updateWordCount() {
        const text = notesTextarea.value;
        const wordCountValue = countWords(text);
        const maxWords = 40;
        
        wordCount.textContent = `${wordCountValue} / ${maxWords} kata`;
        
        if (wordCountValue > maxWords) {
            wordCount.className = "word-count error";
        } else if (wordCountValue > maxWords * 0.8) {
            wordCount.className = "word-count warning";
        } else {
            wordCount.className = "word-count";
        }
    }

    notesTextarea.addEventListener("input", updateWordCount);

    // File upload handling
    paymentProof.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
            const maxSize = 5 * 1024 * 1024; // 5MB
            if (file.size > maxSize) {
                alert("File terlalu besar! Maksimal ukuran file adalah 5MB.");
                paymentProof.value = "";
                fileUploadLabel.classList.remove("has-file");
                fileName.textContent = "";
                return;
            }
            
            fileUploadLabel.classList.add("has-file");
            fileName.textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
        } else {
            fileUploadLabel.classList.remove("has-file");
            fileName.textContent = "";
        }
    });

    // Product card selection visual feedback
    productRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            document.querySelectorAll(".product-card").forEach(card => {
                card.classList.remove("selected");
            });
            if (radio.checked) {
                radio.closest(".product-card").classList.add("selected");
            }

            // Show/hide color selection for Forever Flowers
            if (radio.value === "bouquet" && radio.checked) {
                if (colorSelection) {
                    colorSelection.style.display = "block";
                }
            } else {
                if (colorSelection) {
                    colorSelection.style.display = "none";
                    // Reset color selection
                    colorRadios.forEach(colorRadio => {
                        colorRadio.checked = false;
                    });
                    document.querySelectorAll(".color-option").forEach(option => {
                        option.classList.remove("selected");
                    });
                }
            }
        });
    });

    // Color option selection visual feedback
    colorRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            document.querySelectorAll(".color-option").forEach(option => {
                option.classList.remove("selected");
            });
            if (radio.checked) {
                radio.closest(".color-option").classList.add("selected");
            }
        });
    });

    // Check deadline
    function checkDeadline() {
        const deadline = new Date("2026-02-07T23:59:00+07:00"); // WIB timezone
        const now = new Date();
        
        if (now > deadline) {
            submitButton.disabled = true;
            submitButton.textContent = "Pendaftaran Telah Ditutup";
            submitButton.style.opacity = "0.6";
            alert("Maaf, deadline pre-order telah berakhir pada 7 Februari 2026, 23:59 WIB.");
            return false;
        }
        return true;
    }

   // Form submission
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!checkDeadline()) return;

    const selectedProduct = document.querySelector('input[name="product"]:checked');
    if (selectedProduct && selectedProduct.value === "bouquet") {
        const selectedColor = document.querySelector('input[name="forever_flowers_color"]:checked');
        if (!selectedColor) {
            alert("Harap pilih warna untuk Forever Flowers!");
            colorSelection.scrollIntoView({ behavior: "smooth", block: "center" });
            return;
        }
    }

    if (chocobloomCheckbox && chocobloomCheckbox.checked) {
        const notes = notesTextarea.value.trim();
        if (!notes) {
            alert("Harap isi pesan untuk Thought Card!");
            return;
        }

        const wc = countWords(notes);
        if (wc > 40) {
            alert("Pesan maksimal 40 kata! Saat ini " + wc + " kata.");
            return;
        }
    }

    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = "Mengirim...";
    submitButton.style.opacity = "0.7";

    try {
        const file = paymentProof.files[0];
        if (!file) {
            alert("Upload bukti transfer dulu");
            return;
        }

        const reader = new FileReader();

        reader.onload = async () => {
            const base64 = reader.result.split(",")[1];

            const data = {
                product: form.product.value,
                forever_flowers_color: form.forever_flowers_color?.value || "",
                add_thought_card: chocobloomCheckbox?.checked ? "yes" : "no",
                recipient_name: form.recipient_name.value,
                recipient_class: form.recipient_class.value,
                notes: notesTextarea?.value || "",
                payment_proof: base64,
                payment_name: file.name,
                payment_type: file.type
            };

            const response = await fetch(
                "",
                {
                    method: "POST",
                    body: JSON.stringify(data)
                }
            );

            const result = await response.json();

            if (result.status === "success") {
                form.reset();
                fileUploadLabel.classList.remove("has-file");
                fileName.textContent = "";
                notesSection.style.display = "none";
                updateWordCount();
                showSuccessModal();
            } else {
                showErrorModal(result.message || "Gagal mengirim.");
            }
        };

        reader.readAsDataURL(file);

    } catch (err) {
        console.error(err);
        showErrorModal("Gagal mengirim data.");
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        submitButton.style.opacity = "1";
    }
});


    // Modal functions
    function showSuccessModal() {
        const modal = document.getElementById("successModal");
        if (modal) {
            modal.classList.add("active");
            document.body.style.overflow = "hidden";
        }
    }

    function closeModal() {
        const modal = document.getElementById("successModal");
        if (modal) {
            modal.classList.remove("active");
            document.body.style.overflow = "";
        }
    }

    function showErrorModal(message) {
        const modal = document.getElementById("errorModal");
        const errorMessage = document.getElementById("errorMessage");
        if (modal && errorMessage) {
            errorMessage.textContent = message;
            modal.classList.add("active");
            document.body.style.overflow = "hidden";
        }
    }

    function closeErrorModal() {
        const modal = document.getElementById("errorModal");
        if (modal) {
            modal.classList.remove("active");
            document.body.style.overflow = "";
        }
    }

    // Close modals on backdrop click
    document.querySelectorAll(".modal").forEach(modal => {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                if (modal.id === "successModal") {
                    closeModal();
                } else if (modal.id === "errorModal") {
                    closeErrorModal();
                }
            }
        });
    });

    // Close modals on ESC key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeModal();
            closeErrorModal();
        }
    });

    // Expose functions to global scope for onclick handlers
    window.closeModal = closeModal;
    window.closeErrorModal = closeErrorModal;
});



