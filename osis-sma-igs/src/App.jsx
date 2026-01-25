// Modules
import { Route, Routes } from "react-router-dom";

// Components
import ScrollToHash from "./components/ScrollToHash.jsx";
import Entrance from "./components/Entrance.jsx";
import Navbar from "./components/Navbar.jsx";
import Footer from "./components/Footer.jsx";
import Home from "./pages/Home.jsx";
import AboutUs from "./pages/AboutUs.jsx";
import Error404 from "./pages/404.jsx";
import ComingSoon from "./pages/ComingSoon.jsx";

const App = () => {
  return (
    <>
			<ScrollToHash />

      <Entrance />
      <Navbar />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about_us" element={<AboutUs />} />
        <Route path="/coming_soon" element={<ComingSoon />} />
        <Route path="*" element={<Error404 />} />
      </Routes>

      <Footer />
    </>
  );
};

export default App;