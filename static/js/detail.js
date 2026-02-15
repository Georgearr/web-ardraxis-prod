function setupDetail(element) {
  const eventName = element.getAttribute("data-event-name");
  const classEvent = element.getAttribute("data-class-event");
  const descEvent = element.getAttribute("data-desc-event");
  showDetail(eventName, classEvent, descEvent);
}

function showDetail(eventName, classEvent, descEvent, imageUrl) {
  document.getElementById("detail").style.display = "block";
  var heading = document.getElementById("detail-heading");
  var desc = document.getElementById("detail-desc");
  var banner = document.getElementById("detail-banner");
  var logo = document.getElementById("detail-logo");

  heading.innerText = eventName;
  desc.innerText = descEvent;
  logo.className = "bx " + (classEvent || "").replace(/^bx\s*/, "");
  logo.style.display = "";

  if (imageUrl) {
    banner.src = imageUrl;
    banner.alt = eventName;
    banner.style.display = "";
    desc.style.display = "none";
  } else {
    banner.style.display = "none";
    desc.style.display = "";
  }
}

function closeDetail() {
  document.getElementById("detail").style.display = "none";
}

/** Buka modal: list-btn1 (Tempat Foto) = pakai img, list-btn2 (Info) = pakai icon */
function showDetailFromList(listEl, useImage) {
  if (!listEl) return;
  var name = listEl.getAttribute("data-event-name");
  var icon = listEl.getAttribute("data-class-event");
  var desc = listEl.getAttribute("data-desc-event");
  var imageUrl = useImage ? (listEl.getAttribute("data-image") || "") : "";
  showDetail(name, icon, desc, imageUrl);
}