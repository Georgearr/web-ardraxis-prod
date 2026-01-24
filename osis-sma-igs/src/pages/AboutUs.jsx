// Modules
import { useEffect } from "react";

const AboutUs = () => {
  useEffect(() => {
    document.title = "About Us | OSIS SMA IGS";
  }, []);

  return (
    <>
      <h1>about us</h1>
    </>
  );
};

export default AboutUs;