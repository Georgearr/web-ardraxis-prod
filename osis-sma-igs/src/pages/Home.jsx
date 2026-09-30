// Modules
import { Link } from "react-router-dom";
import { useEffect } from "react";

// Assets
import meloria_banner from "../assets/meloria_banner.jpeg";
import festiora_banner from "../assets/festiora_banner.png";

// Components
import styles from "../components/css/Home.module.css";

const Home = () => {
  useEffect(() => {
    document.title = "Ardraxis | OSIS SMA IGS";
  }, []);

  // Carousel Logic
  useEffect(() => {
    const eventsSection = document.querySelector(`[class*="${styles["events"]}"]`);
    if (!eventsSection) return;
    const track = eventsSection.querySelector(`[class*="${styles["carousel-track"]}"]`);
    const slides = Array.from(eventsSection.querySelectorAll(`[class*="${styles["carousel-slide"]}"]`));
    const prevBtn = eventsSection.querySelector(`button[aria-label="Previous slide"]`);
    const nextBtn = eventsSection.querySelector(`button[aria-label="Next slide"]`);
    const dotsContainer = eventsSection.querySelector(`[class*="${styles["carousel-dots"]}"]`);

    if (!track || slides.length === 0) return;

    let currentIndex = 0;

    // Clear existing dots
    dotsContainer.innerHTML = "";

    // Create dots
    slides.forEach((_, idx) => {
      const dot = document.createElement("button");
      dot.className = idx === 0 ? `${styles["carousel-dot"]} ${styles["active"]}` : styles["carousel-dot"];
      dot.setAttribute("aria-label", `Go to slide ${idx + 1}`);
      dot.addEventListener("click", () => goToSlide(idx));
      dotsContainer.appendChild(dot);
    });

    function update() {
      const offset = -currentIndex * 100;
      track.style.transform = `translateX(${offset}%)`;
      const dots = Array.from(dotsContainer.querySelectorAll(`[class*="${styles["carousel-dot"]}"]`));
      dots.forEach((d, i) => d.classList.toggle(styles["active"], i === currentIndex));
    }

    function goToSlide(index) {
      currentIndex = (index + slides.length) % slides.length;
      update();
    }

    function next() {
      goToSlide(currentIndex + 1);
    }
    function prev() {
      goToSlide(currentIndex - 1);
    }

    nextBtn && nextBtn.addEventListener("click", next);
    prevBtn && prevBtn.addEventListener("click", prev);

    // Auto-play (optional). Pause on hover for accessibility.
    let autoPlayId = setInterval(next, 5000);
    eventsSection.addEventListener("mouseenter", () => clearInterval(autoPlayId));
    eventsSection.addEventListener(
      "mouseleave",
      () => (autoPlayId = setInterval(next, 5000))
    );

    // Initialize
    update();

    return () => {
      clearInterval(autoPlayId);
      nextBtn && nextBtn.removeEventListener("click", next);
      prevBtn && prevBtn.removeEventListener("click", prev);
    };
  }, [styles]);

  // Scroll Reveal Logic
  useEffect(() => {
    const ease = 'cubic-bezier(0.2, 0.65, 0.3, 1)';
    const baseDurationMs = 1000; // entrance animation duration
    const baseDistancePx = 60;  // noticeable movement
    const staggerMs = 70;       // slight stagger

    const setups = [
      { selector: '.home-image', origin: 'left' },
      { selector: '.home-text .hidden', origin: 'right', unhide: true },
      { selector: '.events-now-banner', origin: 'bottom', unhide: true },
      { selector: '.events-title', origin: 'bottom', unhide: true },
      { selector: '.carousel-slide', origin: 'bottom', rotateY: 6 },
      { selector: '.about .hidden', origin: 'bottom', unhide: true },
      { selector: '.about img', origin: 'right' },
      { selector: '.prior-cabinets-title', origin: 'bottom', unhide: true },
      { selector: '.prior-cabinets-container', origin: 'bottom' },
      { selector: '.cabinet-card', origin: 'bottom' }
    ];

    const computeTransform = (origin, distance, rotateY) => {
      const shift = (axis, val) => axis === 'x' ? `translateX(${val}px)` : `translateY(${val}px)`;
      let axis = 'y';
      if (origin === 'left' || origin === 'right') axis = 'x';
      const sign = (origin === 'left' || origin === 'top') ? -1 : 1;
      const base = shift(axis, sign * distance);
      const rot = rotateY ? ` rotateY(${rotateY}deg)` : '';
      return base + rot;
    };

    const prime = (el, origin, rotateY) => {
      el.style.opacity = '0';
      el.style.transform = computeTransform(origin, baseDistancePx, rotateY);
      el.style.transition = `transform ${baseDurationMs}ms ${ease}, opacity ${baseDurationMs}ms ${ease}`;
      el.style.willChange = 'transform, opacity';
    };

    const show = (el, unhide) => {
      if (unhide && el.classList) el.classList.remove('hidden');
      el.style.opacity = '1';
      el.style.transform = 'translateX(0) translateY(0)';
      // After entrance finishes, hand control back to CSS (hover transitions)
      setTimeout(() => {
        el.style.removeProperty('transform');
        el.style.removeProperty('transition');
        el.style.removeProperty('will-change');
        el.style.removeProperty('opacity');
      }, baseDurationMs + 50);
    };

    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const meta = el.__revealMeta || {};
        setTimeout(() => show(el, !!meta.unhide), meta.delay || 0);
        io.unobserve(el);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    setups.forEach(({ selector, origin, unhide, rotateY }) => {
      const nodes = document.querySelectorAll(selector);
      nodes.forEach((el, idx) => {
        // avoid double-priming if script injected twice
        if (el.__revealPrimed) return;
        el.__revealPrimed = true;
        prime(el, origin, rotateY);
        el.__revealMeta = { unhide, delay: idx * staggerMs };
        io.observe(el);
      });
    });

    return () => {
      io.disconnect();
    };
  }, []);

  return (
    <>
      {/* Home Section */}
			<section className={styles["home"]} id="home">
				<div className={styles["home-image"]}>
					<img className={styles["logo"]} src="/images/logo_ardraxis.png" alt="ARDRAXIS" />
				</div>
				<div className={styles["home-text"]}>
					<h1 className={`${styles["text-shadow"]} hidden`}>ARDRAXIS</h1>
					<p className={`${styles["text-shadow"]} hidden`}>Kabinet OSIS SMA Ignatius Global School Periode 2025/2026</p>
				</div>
			</section>
			{/* End Home Section */}

			{/* Events Section */}
			<section className={styles["events"]} id="events">
				{/* Event Happening Now Title */}
				<div className={`${styles["events-now-badge"]} ${styles["text-shadow"]} hidden`}>Happening Now</div>

				{/* Event Happening Now Banner */}
				<div className={`${styles["events-now-banner"]} ${styles["text-shadow"]} hidden`}>
					<div className={styles["events-now-content"]}>
						<div className={styles["events-now-image-wrapper"]}>
							<Link to="/coming_soon" className="events-now-link">
									<img
										src="/images/logo_ardraxis.png"
										alt="Happening Now"
										className={styles["events-now-image"]}
									/>
							</Link>
						</div>
						<div className={styles["events-now-info"]}>
							<h3 className={styles["events-now-title"]}>Coming Soon</h3>
							<p className={styles["events-now-date"]}>Coming Soon</p>
						</div>
					</div>
				</div>

				<h2 className={`${styles["events-title"]} ${styles["text-shadow"]} hidden`}>Events</h2>
				<div className={styles["events-carousel"]}>
					<button className={`${styles["carousel-btn"]} ${styles["prev"]}`} aria-label="Previous slide">&#10094;</button>
					<div className={styles["carousel-viewport"]}>
						<div className={styles["carousel-track"]}>
							<div className={styles["carousel-slide"]}>
								<div className={styles["slide-media"]}>
									<Link to="/coming_soon">
										<img src={meloria_banner} alt="Meloria" />
									</Link>
								</div>
								<div className={styles["slide-caption"]}>
									<h3>Meloria</h3>
									<p>14 November 2025</p>
								</div>
							</div>
							<div className={styles["carousel-slide"]}>
								<div className={styles["slide-media"]}>
									<Link to="/coming_soon">
										<img src={festiora_banner} alt="Festiora" />
									</Link>
								</div>
								<div className={styles["slide-caption"]}>
									<h3>Festiora</h3>
									<p>2 Desember 2025</p>
								</div>
							</div>
							<div className={styles["carousel-slide"]}>
								<div className={styles["slide-media"]}>
									<Link to="/coming_soon">
										<img src="/images/logo_ardraxis.png" alt="Coming Soon" />
									</Link>
								</div>
								<div className={styles["slide-caption"]}>
									<h3>Coming Soon</h3>
									<p>Coming Soon</p>
								</div>
							</div>
						</div>
					</div>
					<button className={`${styles["carousel-btn"]} ${styles["next"]}`} aria-label="Next slide">&#10095;</button>
					<div className={styles["carousel-dots"]} aria-label="Slide indicators"></div>
				</div>
			</section>
			{/* End Events Section */}

			{/* About Section */}
			<section className={styles["about"]} id="about">
				<div className={styles["about-text"]}>
					<h1 className={`${styles["text-shadow"]} hidden`}>ARDRAXIS</h1>
					<p className={`${styles["text-shadow"]} hidden`} style={{ color: "white" }}>
						Ardraxis merupakan nama kabinet OSIS SMA IGS periode 2025/2026.
						Ardraxis berarti "semangat dan inti" yang bermakna bahwa OSIS SMA IGS
						adalah organisasi yang gagah dan tegar dalam menghadapi berbagai macam
						masalah atau konflik apapun. Dan organisasi yang berani untuk bekerja,
						berani untuk lelah, dan berani untuk bertanggung jawab.
					</p>
				</div>
				<img src="/images/logo_ardraxis.png" alt="ARDRAXIS" />
			</section>
			{/* End About Section */}

			{/* Prior Cabinets Section */}
			{/* <section className="prior-cabinets" id="pc">
				<h2 className="prior-cabinets-title text-shadow hidden">Our Prior Cabinets</h2>
				<div className="prior-cabinets-container hidden">
					<div className="cabinet-card hidden">
						<div className="cabinet-card-image">
							<img src="{{ url_for('static', filename='img/valiance_logo.png') }}" alt="Valiance" className="cabinet-image" />
						</div>
						<h3 className="cabinet-card-title">Valiance</h3>
						<p className="cabinet-card-desc">Kabinet OSIS SMA Ignatius Global School periode 2024/2025</p>
						<button className="cabinet-card-button" onclick="window.location.assign('https://valiance.osissmaigs.com')">Click Here</button>
					</div>

					<div className="cabinet-card hidden">
						<div className="cabinet-card-image">
							<img src="{{ url_for('static', filename='img/asteration_logo.png') }}" alt="Asteration" className="cabinet-image" />
						</div>
						<h3 className="cabinet-card-title">Asteration</h3>
						<p className="cabinet-card-desc">Kabinet OSIS SMA Ignatius Global School periode 2023/2024</p>
						<button className="cabinet-card-button" onclick="window.location.assign('https://asteration.osissmaigs.com')">Click Here</button>
					</div>

					<div className="cabinet-card hidden">
						<div className="cabinet-card-image">
							<img src="{{ url_for('static', filename='img/credence_logo.png') }}" alt="Credence" className="cabinet-image" />
						</div>
						<h3 className="cabinet-card-title">Credence</h3>
						<p className="cabinet-card-desc">Kabinet OSIS SMA Ignatius Global School periode 2022/2023</p>
						<button className="cabinet-card-button" onclick="window.location.assign('https://osissmaigs.com/coming_soon')">Click Here</button>
					</div>
				</div>
			</section> */}
			{/* End Prior Cabinets Section */}
    </>
  );
};

export default Home;