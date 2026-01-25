// Modules
import { Link } from "react-router-dom";
import { useEffect } from "react";

// Components
import styles from "../components/css/Coming_Soon.module.css";

const ComingSoon = () => {
  useEffect(() => {
    document.title = "Coming Soon | OSIS SMA IGS";
  }, []);

  return (
    <>
      <section className={styles["fullpage-center"]}>
        <div className={styles["center-content"]}>
          <img
            className={styles["logo"]}
            src="/images/logo_ardraxis.png"
            alt="ARDRAXIS"
          />
          <h1 className={styles["title"]}>Coming Soon</h1>
          <p className={styles["subtitle"]}>Feature is under construction. Stay tuned!</p>
          <Link className={styles["back-home"]} to="/#home" aria-label="Back to home">
            Kembali ke Home
          </Link>
        </div>
      </section>
    </>
  );
};

export default ComingSoon;