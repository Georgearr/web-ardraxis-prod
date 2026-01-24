// Modules
import { Link } from "react-router-dom";

// Assets
import logo from "../assets/logo_ardraxis.png";

// Components
import styles from "./css/Layout.module.css";

const Navbar = () => {
  return (
    <div className={styles["navbar"]}>
      <Link className={styles["nav-logo"]} to="/">
        <img
          src={logo}
          alt="ARDRAXIS"
        />
        <span className={styles["brand"]}>ARDRAXIS</span>
      </Link>
      <div className={styles["nav-nav"]}>
        <Link to="/#home">HOME</Link>
        <Link to="/#events">EVENTS</Link>
        <Link to="/about_us">ABOUT US</Link>
        <Link to="/">TRY D'RAX</Link>
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