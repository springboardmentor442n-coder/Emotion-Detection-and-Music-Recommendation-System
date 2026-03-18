import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Hero } from "./components/Hero";
import { NavBar } from "./components/NavBar";
import { Features } from "./components/Features";
import { HowItWorks } from "./components/HowItWorks";
import { About } from "./components/About";
import { Footer } from "./components/Footer";
import { MainApp } from "./components/MainApp";

const pageVariants = {
  initial: { opacity: 0, scale: 0.98 },
  animate: { opacity: 1, scale: 1, transition: { duration: 0.4, ease: "easeOut" } },
  exit: { opacity: 0, scale: 1.02, transition: { duration: 0.3, ease: "easeIn" } },
};

function LandingView({ onLaunch }) {
  return (
    <main className="w-full min-h-[200vh] selection:bg-[#7b72e0]/30 selection:text-[#1a1a2e] relative bg-[#F8F6FF]">
      <NavBar onLaunch={onLaunch} />
      <Hero onLaunch={onLaunch} />
      <Features />
      <HowItWorks />
      <About />
      <Footer />
    </main>
  );
}

function App() {
  const [inApp, setInApp] = useState(false);
  const [pendingScroll, setPendingScroll] = useState(null);

  const goToLanding = useCallback((sectionId) => {
    if (inApp) {
      setPendingScroll(sectionId || null);
      setInApp(false);
    }
  }, [inApp]);

  const handleExitComplete = useCallback(() => {
    if (pendingScroll) {
      // Allow DOM to render landing sections before scrolling
      requestAnimationFrame(() => {
        setTimeout(() => {
          const el = document.getElementById(pendingScroll);
          if (el) el.scrollIntoView({ behavior: 'smooth' });
          setPendingScroll(null);
        }, 100);
      });
    }
  }, [pendingScroll]);

  return (
    <AnimatePresence mode="wait" onExitComplete={handleExitComplete}>
      {inApp ? (
        <motion.div key="app" variants={pageVariants} initial="initial" animate="animate" exit="exit">
          <MainApp 
            onBack={() => setInApp(false)} 
            onNavigate={(sectionId) => goToLanding(sectionId)}
          />
        </motion.div>
      ) : (
        <motion.div key="landing" variants={pageVariants} initial="initial" animate="animate" exit="exit">
          <LandingView onLaunch={() => setInApp(true)} />
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default App;
