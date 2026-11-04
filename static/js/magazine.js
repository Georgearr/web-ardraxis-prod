// Ardrazine — inline SVG lazy mount
// Markup SVG sudah berada di dalam HTML (bukan hasil fetch), namun ditahan di
// dalam <template> supaya browser tidak merender/mendekode seluruh koleksi
// sekaligus. Elemen dipindahkan ke dalam dokumen hanya saat mendekati viewport.
(function () {
  var frames = document.querySelectorAll(".mag-item");
  if (!frames.length) return;

  function mount(item) {
    var source = item.querySelector(".mag-source");
    var frame = item.querySelector(".mag-frame");
    if (!source || !frame) return;

    frame.appendChild(source.content.cloneNode(true));
    frame.style.removeProperty("aspect-ratio");
    frame.classList.add("is-mounted");
    source.parentNode.removeChild(source);
  }

  if (!("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(frames, mount);
    return;
  }

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        mount(entry.target);
      });
    },
    { rootMargin: "800px 0px" }
  );

  Array.prototype.forEach.call(frames, function (frame) {
    observer.observe(frame);
  });
})();
