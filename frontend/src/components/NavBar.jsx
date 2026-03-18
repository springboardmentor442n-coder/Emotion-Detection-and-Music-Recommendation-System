import { motion, useScroll, useTransform } from "framer-motion";
import { ReactiveButton } from "./ui/ReactiveButton";

export function NavBar({ onLaunch, forcedLabel, onNavigate, onLogoClick }) {
  const { scrollY } = useScroll();
  const bgOpacity = useTransform(scrollY, [0, 50], ["rgba(255,255,255,0)", "rgba(248, 246, 255, 0.75)"]);
  const borderColor = useTransform(scrollY, [0, 50], ["rgba(255,255,255,0)", "rgba(0,0,0,0.06)"]);
  const backdropBlur = useTransform(scrollY, [0, 50], ["blur(0px)", "blur(12px)"]);

  const handleNavClick = (sectionId) => {
    if (onNavigate) {
      onNavigate(sectionId);
    } else {
      const el = document.getElementById(sectionId);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <motion.nav
      style={{
        backgroundColor: bgOpacity,
        borderColor,
        backdropFilter: backdropBlur,
        WebkitBackdropFilter: backdropBlur,
      }}
      className="fixed top-0 left-0 right-0 z-50 border-b flex items-center justify-between px-6 md:px-12 py-4 transition-all"
    >
      <div className="flex items-center gap-3 cursor-pointer" onClick={onLogoClick || onLaunch}>
        <motion.img 
          src="/logo.svg" 
          alt="MoodMate" 
          className="w-10 h-10 drop-shadow-md rounded-xl"
          whileHover={{ rotate: 15, scale: 1.1 }}
          transition={{ type: "spring", stiffness: 300 }}
        />
        <span className="text-xl font-extrabold tracking-tight text-gray-900 drop-shadow-sm">MoodMate</span>
      </div>
      
      <div className="hidden md:flex items-center gap-10 text-sm font-semibold text-gray-500">
        <NavLink onClick={() => handleNavClick('features')}>Features</NavLink>
        <NavLink onClick={() => handleNavClick('how-it-works')}>How It Works</NavLink>
        <NavLink onClick={() => handleNavClick('about')}>About</NavLink>
      </div>

      <div>
        <ReactiveButton 
          label={forcedLabel || "Start Listening"} 
          accent="var(--mm-primary)" 
          className="px-5 py-2.5 !text-sm shadow-md" 
          onClick={onLaunch}
        />
      </div>
    </motion.nav>
  );
}

function NavLink({ children, onClick }) {
  return (
    <motion.button 
      onClick={onClick}
      className="relative text-gray-500 hover:text-gray-900 transition-colors bg-transparent border-none cursor-pointer"
      whileHover="hover"
    >
      {children}
      <motion.div 
        variants={{ hover: { opacity: 1, scaleX: 1 } }}
        initial={{ opacity: 0, scaleX: 0 }}
        transition={{ type: "spring", bounce: 0, duration: 0.3 }}
        className="absolute -bottom-1.5 left-0 right-0 h-0.5 bg-gradient-to-r from-[#7B72E0] to-[#FF6B9D] origin-left rounded-full"
      />
    </motion.button>
  );
}
