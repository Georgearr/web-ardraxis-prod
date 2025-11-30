document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("festioraForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const submitButton = form.querySelector("button[type='submit']");
        submitButton.disabled = true; // disable button saat submit
        submitButton.textContent = "Mengirim...";

        try {
            // Ambil nama lomba dari data-lomba
            const formType = form.dataset.lomba;
            const formData = new FormData(form);

            // Kirim data ke Flask
            const response = await fetch(`/festiora_submit/${formType}`, {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            if (result.status === "ok") {
                alert("Pendaftaran berhasil!");
                form.reset();
            } else {
                alert("Terjadi kesalahan. Coba lagi.");
            }
        } catch (err) {
            console.error("Error:", err);
            alert("Gagal mengirim data. Cek koneksi atau server.");
        } finally {
            // Re-enable button
            submitButton.disabled = false;
            submitButton.textContent = "Kirim";
        }
    });
});
