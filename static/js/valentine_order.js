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

    // ================= WORD COUNT =================
    function countWords(text) {
        return text.trim().split(/\s+/).filter(w => w.length > 0).length;
    }

    function updateWordCount() {
        const wc = countWords(notesTextarea.value || "");
        wordCount.textContent = `${wc} / 40 kata`;
    }

    notesTextarea.addEventListener("input", updateWordCount);

    // ================= ADDON =================
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

    // ================= FILE =================
    paymentProof.addEventListener("change", e => {
        const file = e.target.files[0];
        if (!file) return;

        if (file.size > 5 * 1024 * 1024) {
            alert("File maksimal 5MB");
            paymentProof.value = "";
            return;
        }

        fileUploadLabel.classList.add("has-file");
        fileName.textContent = file.name;
    });

    // ================= PRODUCT =================
    productRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            document.querySelectorAll(".product-card").forEach(c => c.classList.remove("selected"));
            radio.closest(".product-card").classList.add("selected");

            if (radio.value === "Flowers") {
                colorSelection.style.display = "block";
            } else {
                colorSelection.style.display = "none";
                colorRadios.forEach(r => r.checked = false);
            }
        });
    });

    colorRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            document.querySelectorAll(".color-option").forEach(o => o.classList.remove("selected"));
            radio.closest(".color-option").classList.add("selected");
        });
    });

    // ================= SUBMIT =================
    form.addEventListener("submit", e => {
        e.preventDefault();

        const selectedProduct = document.querySelector('input[name="product"]:checked');
        if (!selectedProduct) {
            alert("Pilih produk");
            return;
        }

        if (selectedProduct.value === "bouquet") {
            if (!document.querySelector('input[name="forever_flowers_color"]:checked')) {
                alert("Pilih warna Forever Flowers");
                return;
            }
        }

        if (chocobloomCheckbox.checked && countWords(notesTextarea.value) > 40) {
            alert("Pesan maksimal 40 kata");
            return;
        }

        const file = paymentProof.files[0];
        if (!file) {
            alert("Upload bukti transfer");
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = "Mengirim...";

        const reader = new FileReader();
        reader.onload = async () => {
            const base64 = reader.result.split(",")[1];

            const data = {
                product: form.product.value,
                forever_flowers_color: form.forever_flowers_color?.value || "",
                add_thought_card: chocobloomCheckbox.checked ? "yes" : "no",
                recipient_name: form.recipient_name.value,
                recipient_class: form.recipient_class.value,
                notes: notesTextarea.value || "",
                payment_name: file.name,
                payment_type: file.type,
                payment_proof: base64
            };

            const formData = new FormData();
            for (let key in data) {
                formData.append(key, data[key]);
            }

            try {
                const response = await fetch("https://script.google.com/macros/s/AKfycbxIcTiaRAmOcoOKs1bWjPomcrO9QC9dXwHuDfZCdTXKc8z_mS69Gba4VpC3sJ29-ySS8g/exec", {
                    method: "POST",
                    body: formData
                });

                const text = await response.text();
                console.log("SERVER:", text);

                const result = JSON.parse(text);

                if (result.status === "success") {
                    form.reset();
                    fileUploadLabel.classList.remove("has-file");
                    fileName.textContent = "";
                    notesSection.style.display = "none";
                    updateWordCount();
                    showSuccessModal();
                } else {
                    showErrorModal(result.message || "Gagal mengirim");
                }

            } catch (err) {
                console.error(err);
                showErrorModal("Server error");
            }

            submitButton.disabled = false;
            submitButton.textContent = "Kirim Pesanan";
        };

        reader.readAsDataURL(file);
    });

    // ================= MODAL =================
    function showSuccessModal() {
        document.getElementById("successModal").classList.add("active");
    }

    function showErrorModal(msg) {
        document.getElementById("errorMessage").textContent = msg;
        document.getElementById("errorModal").classList.add("active");
    }

    window.closeModal = () => {
        document.getElementById("successModal").classList.remove("active");
    };

    window.closeErrorModal = () => {
        document.getElementById("errorModal").classList.remove("active");
    };
});
