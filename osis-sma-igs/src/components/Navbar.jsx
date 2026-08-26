// Modules
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useEffect } from "react";

// Components
import styles from "./css/Layout.module.css";

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Scroll to top whenever route changes (except when hash-scrolling)
  useEffect(() => {
    if (!location.hash) {
      window.scrollTo(0, 0);
    }
  }, [location.pathname]);

  // Scroll to #home when URL is "/" and hash is present
  useEffect(() => {
    if (location.pathname === "/" && location.hash === "#home") {
      const homeElement = document.getElementById("home");
      if (homeElement) {
        homeElement.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [location]);

  const handleHomeClick = (e) => {
    e.preventDefault();
    navigate("/");
    // Scroll to home element after navigation
    setTimeout(() => {
      const homeElement = document.getElementById("home");
      if (homeElement) {
        homeElement.scrollIntoView({ behavior: "smooth" });
      }
    }, 0);
  };

  const handleEventsClick = (e) => {
    e.preventDefault();
    
    // If already on home page, scroll smoothly
    if (location.pathname === "/") {
      const eventsElement = document.getElementById("events");
      if (eventsElement) {
        eventsElement.scrollIntoView({ behavior: "smooth" });
      }
    } else {
      // If on another page, navigate to home and scroll instantly after delay
      navigate("/");
      setTimeout(() => {
        const eventsElement = document.getElementById("events");
        if (eventsElement) {
          eventsElement.scrollIntoView({ behavior: "auto" });
        }
      }, 100);
    }
  };

  const handleLinkClick = (e) => {
    // Scroll to top after a brief delay to let navigation complete
    setTimeout(() => {
      window.scrollTo(0, 0);
    }, 0);
  };

  return (
    <div className={styles["navbar"]}>
      <Link className={styles["nav-logo"]} to="/">
        <img
          src="/images/logo_ardraxis.png"
          alt="ARDRAXIS"
        />
        <span className={styles["brand"]}>ARDRAXIS</span>
      </Link>
      <div className={styles["nav-nav"]}>
        <a href="/" onClick={handleHomeClick}>HOME</a>
        <a href="/#events" onClick={handleEventsClick}>EVENTS</a>
        <Link to="/about_us" onClick={handleLinkClick}>ABOUT US</Link>
        <Link to="/coming_soon" onClick={handleLinkClick}>TRY D'RAX</Link>
      </div>
      {/* <button className="hamburger" onClick={toggleMenu} aria-label="Toggle menu">
        <span></span>
        <span></span>
        <span></span>
      </button> */}
    </div>
  );
};

export default Navbar;