    // Fade in animation saat halaman load
    document.addEventListener("DOMContentLoaded", () => {
      const hiddenElements = document.querySelectorAll(".hidden");

      hiddenElements.forEach((element, index) => {
        setTimeout(() => {
          element.classList.add("fade-in");
        }, index * 300);
      });
    });

    // Hamburger menu toggle
    function toggleMenu() {
      const sidebar = document.getElementById("sidebar");
      const overlay = document.getElementById("sidebar-overlay");
      const hamburger = document.querySelector(".hamburger");
      sidebar.classList.toggle("active");
      overlay.classList.toggle("active");
      hamburger.classList.toggle("active");
      document.body.style.overflow = sidebar.classList.contains("active") ? "hidden" : "auto";
    }

    // Close sidebar when clicking on overlay
    function closeMenu() {
      const sidebar = document.getElementById("sidebar");
      const overlay = document.getElementById("sidebar-overlay");
      const hamburger = document.querySelector(".hamburger");
      sidebar.classList.remove("active");
      overlay.classList.remove("active");
      hamburger.classList.remove("active");
      document.body.style.overflow = "auto";
    }

    // Close sidebar when clicking on menu links
    document.addEventListener("DOMContentLoaded", () => {
      const menuLinks = document.querySelectorAll(".sidebar-nav a");
      menuLinks.forEach(link => {
        link.addEventListener("click", closeMenu);
      });
    });