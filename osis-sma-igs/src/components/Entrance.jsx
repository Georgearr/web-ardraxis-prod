// Modules
import { useEffect, useState } from "react";

// Components
import styles from "./css/Layout.module.css";

const INTRO_DURATION = 2600;

const Entrance = () => {
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setHidden(true);
    }, INTRO_DURATION);

    return () => clearTimeout(timer);
  }, []);

  const handleSkip = () => {
    setHidden(true);
  };

  return (
    <div className={`${styles["intro"]} ${hidden ? styles["hide"] : ""}`}>
      <div className={styles["intro-bg"]}></div>

      <div className={styles["intro-inner"]}>
        <img className={styles["intro-dragon"]} src="/images/logo_ardraxis.png" alt="ARDRAXIS" />
        <h1 className={styles["intro-title"]}>ARDRAXIS</h1>
        <p className={styles["intro-slogan"]}>Born To Lead, Bound To Rise</p>
      </div>

      <button onClick={handleSkip} className={styles["intro-skip"]}>
        Skip
      </button>
    </div>
  );
};

export default Entrance;