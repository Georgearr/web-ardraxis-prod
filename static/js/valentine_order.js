document.addEventListener("DOMContentLoaded", () => {

  const prices = {
    Flowers: 15000,
    Bundle: 20000,
    Chocobloom: 18000
  };

  const qtyInputs = document.querySelectorAll(".qty-input");
  const radios = document.querySelectorAll('input[name="product"]');
  const colorSection = document.getElementById("colorSelection");
  const colorRadios = document.querySelectorAll('input[name="forever_flowers_color"]');
  const thoughtCardCheckbox = document.getElementById("thoughtCardCheckbox");
  const notesSection = document.getElementById("notesSection");
  const notesTextarea = document.getElementById("notesTextarea");
  const wordCount = document.getElementById("wordCount");
  const totalPriceEl = document.getElementById("totalPrice");
  const paymentInput = document.getElementById("paymentProof");
  const fileName = document.getElementById("fileName");
  const form = document.getElementById("valentineOrderForm");

  // Helper
  function formatRupiah(num) {
    return "Rp " + num.toLocaleString("id-ID");
  }

  function getSelectedProduct() {
    return document.querySelector('input[name="product"]:checked');
  }

  function getQty(product) {
    const input = document.querySelector(`input[data-product="${product}"]`);
    return input ? Math.max(1, parseInt(input.value || 1)) : 1;
  }

  function disableAllQty() {
    qtyInputs.forEach(input => input.disabled = true);
  }

  function enableQty(product) {
    disableAllQty();
    const input = document.querySelector(`input[data-product="${product}"]`);
    if (input) input.disabled = false;
  }

  function calculateTotal() {
    let total = 0;
    const selected = getSelectedProduct();
    if (selected) total += prices[selected.value] * getQty(selected.value);
    if (thoughtCardCheckbox.checked) total += 2000;
    totalPriceEl.textContent = formatRupiah(total);
  }

  // Product change
  radios.forEach(radio => {
    radio.addEventListener("change", () => {
      enableQty(radio.value);
      if (radio.value === "Flowers") {
        colorSection.style.display = "block";
        colorRadios.forEach(r => r.required = true);
      } else {
        colorSection.style.display = "none";
        colorRadios.forEach(r => { r.required = false; r.checked = false; });
      }
      calculateTotal();
    });
  });

  qtyInputs.forEach(input => {
    input.disabled = true;
    input.addEventListener("input", calculateTotal);
  });

  // Thought Card toggle
  thoughtCardCheckbox.addEventListener("change", () => {
    notesSection.style.display = thoughtCardCheckbox.checked ? "block" : "none";
    calculateTotal();
  });

  // Limit words in notes
  notesTextarea.addEventListener("input", () => {
    let words = notesTextarea.value.trim().split(/\s+/).filter(Boolean);
    if (words.length > 40) words = words.slice(0,40);
    notesTextarea.value = words.join(" ");
    wordCount.textContent = `${words.length} / 40 kata`;
  });

  // File upload display
  paymentInput.addEventListener("change", () => {
    fileName.textContent = paymentInput.files.length ? paymentInput.files[0].name : "";
  });

  // Form submit
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);

    try {
      const res = await fetch(form.action || window.location.href, {
        method: "POST",
        body: formData
      });

      const data = await res.json();
      if (data.status === "success") {
        document.getElementById("successModal").style.display = "flex";
        form.reset();
        totalPriceEl.textContent = "Rp 0";
        disableAllQty();
        colorSection.style.display = "none";
        notesSection.style.display = "none";
        wordCount.textContent = "0 / 40 kata";
        fileName.textContent = "";
      } else {
        throw new Error(data.message || "Terjadi kesalahan");
      }
    } catch (err) {
      document.getElementById("errorMessage").textContent = err.message;
      document.getElementById("errorModal").style.display = "flex";
    }
  });

  calculateTotal();
});

// Modals
function closeModal(type) {
  if (type === "success") document.getElementById("successModal").style.display = "none";
  else if (type === "error") document.getElementById("errorModal").style.display = "none";
}
