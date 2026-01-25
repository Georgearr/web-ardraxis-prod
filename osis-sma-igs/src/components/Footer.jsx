// Components
import styles from "./css/Layout.module.css";

const Footer = () => {
  return (
    <footer className={`${styles["footer"]} reveal-on-scroll`}>
      <div className={styles["footerbawah"]}>
        <div className={styles["footerkiri"]}>
          <div className={styles["footerkiriutama"]}>
            <div className={styles["footerkiriatas"]}>
              <img
                src="/images/logo_ardraxis.png"
                alt="ARDRAXIS"
              />
            </div>
            <div className={styles["footerkiritengah"]}>
              <h1>Ardraxis</h1>
            </div>
            <div className={styles["footerkiribawah"]}>
              <p>
                Kabinet OSIS SMA Ignatius Global <br />
                School periode 2025/2026
              </p>
            </div>
          </div>
        </div>
        <div className={styles["footertengah"]}>
          <div className={styles["footertengah1"]}></div>
          <div className={styles["footertengah2"]}>
            <div className={styles["footertengah2"]}>
              <i
                className="bx bx-map"
                style={{ color: "white", fontSize: "70px" }}
              ></i>
            </div>
            <div className={styles["footertengah2-bawah"]}>
              <p>
                Jl. Mayor Ruslan No. 118, 20 Ilir I, Kec. Ilir Timur I,
                Palembang
              </p>
            </div>
          </div>
        </div>
        <div className={styles["footerkanan"]}>
          <div className={styles["footerkanan-isi"]}>
            <a href="https://www.instagram.com/osis.smaigs/">
              <div className={styles["isi1"]}>
                <i className="bi bi-instagram"></i>
                <p>Instagram</p>
              </div>
            </a>

            <a href="https://x.com/osis_smaigs?t=L-SgwLESUY_a6ViBCYIlTw&s=09">
              <div className={styles["isi1"]}>
                <i className="bi bi-twitter-x"></i>
                <p>Twitter</p>
              </div>
            </a>

            <a href="https://www.tiktok.com/@osis.smaigs">
              <div className={styles["isi1"]}>
                <i className="bi bi-tiktok"></i>
                <p>Tiktok</p>
              </div>
            </a>

            <a href="https://line.me/R/ti/p/@053dzdrl?from=page">
              <div className={styles["isi1"]}>
                <i className="bi bi-line"></i>
                <p>Line</p>
              </div>
            </a>

            <a href="https://www.youtube.com/channel/UCJcG1VCjXHNig5JIDEgYH7w">
              <div className={styles["isi1"]}>
                <i className="bi bi-youtube"></i>
                <p>Youtube</p>
              </div>
            </a>

            <a href="https://github.com/OSISSMAIGS">
              <div className={styles["isi1"]}>
                <i className="bi bi-github"></i>
                <p>Github</p>
              </div>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;