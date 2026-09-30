// Modules
import { Link } from "react-router-dom";
import { useEffect } from "react";

// Components
import styles from "../components/css/Error404.module.css";

const Error404 = () => {
  useEffect(() => {
    document.title = "Page Not Found | OSIS SMA IGS";
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
          <h1 className={styles["title"]}>Page Not Found</h1>
          <p className={styles["subtitle"]}>The page you are looking for doesn't exist.</p>
          <Link className={styles["back-home"]} to="/#home" aria-label="Back to home">
            Kembali ke Home
          </Link>
        </div>
      </section>
    </>
  );
};

export default Error404;