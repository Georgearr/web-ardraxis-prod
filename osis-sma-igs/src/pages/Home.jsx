// Modules
import { useEffect } from "react";

// Assets
import logo from "../assets/logo_ardraxis.png";

// Components
import styles from "../components/css/Layout.module.css";

const Home = () => {
  useEffect(() => {
    document.title = "Ardraxis | OSIS SMA IGS";
  }, []);

  return (
    <>
      {/* Home Section */}
			<section className={styles["home"]} id="home">
				<div className={styles["home-image"]}>
					<img className={styles["logo"]} src={logo} alt="ARDRAXIS" />
				</div>
				<div className={styles["home-text"]}>
					<h1 className={`${styles["text-shadow"]} hidden`}>ARDRAXIS</h1>
					<p className={`${styles["text-shadow"]} hidden`}>Kabinet OSIS SMA Ignatius Global School Periode 2025/2026</p>
				</div>
			</section>
			{/* End Home Section */}

			{/* Events Section
			<section className="events" id="events">
				Event Happening Now Title
				<div className="events-now-badge text-shadow hidden">Happening Now</div>

				Event Happening Now Banner
				<div className="events-now-banner text-shadow hidden">
					<div className="events-now-content">
						<div className="events-now-image-wrapper">
							<a href="{{ url_for('festiora') }}" className="events-now-link">
									<img
									src="{{ url_for('static', filename='img/banner/festiora_banner.png') }}"
									alt="Festiora - Happening Now"
									className="events-now-image"
									/>
							</a>
						</div>
						<div className="events-now-info">
							<h3 className="events-now-title">Festiora</h3>
							<p className="events-now-date">2 Desember 2025</p>
						</div>
					</div>
				</div>

				<h2 className="events-title text-shadow hidden">Events</h2>
				<div className="events-carousel">
					<button className="carousel-btn prev" aria-label="Previous slide">&#10094;</button>
					<div className="carousel-viewport">
						<div className="carousel-track">
							<div className="carousel-slide">
								<div className="slide-media">
									<a href="{{ url_for('meloria') }}">
										<img src="{{ url_for('static', filename='img/banner/meloria_banner.jpeg') }}" alt="Meloria" />
									</a>
								</div>
								<div className="slide-caption">
									<h3>Meloria</h3>
									<p>14 November 2025</p>
								</div>
							</div>
							<div className="carousel-slide">
								<div className="slide-media">
									<a href="{{ url_for('festiora') }}">
										<img src="{{ url_for('static', filename='img/banner/festiora_banner.png') }}" alt="Festiora" />
									</a>
								</div>
								<div className="slide-caption">
									<h3>Festiora</h3>
									<p>2 Desember 2025</p>
								</div>
							</div>
							<div className="carousel-slide">
								<div className="slide-media">
									<a href="{{ url_for('coming_soon') }}">
										<img src={logo} alt="Coming Soon" />
									</a>
								</div>
								<div className="slide-caption">
									<h3>Coming Soon</h3>
									<p>Coming Soon</p>
								</div>
							</div>
						</div>
					</div>
					<button className="carousel-btn next" aria-label="Next slide">&#10095;</button>
					<div className="carousel-dots" aria-label="Slide indicators"></div>
				</div>
			</section>
			End Events Section */}

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
				<img src={logo} alt="ARDRAXIS" />
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