import { motion, useScroll, useTransform, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { MotionCard } from "./ui/MotionCard";
import { ReactiveButton } from "./ui/ReactiveButton";
import { AmbientBackground } from "./ui/AmbientBackground";

const words = ["Expressions.", "Thoughts.", "Vibe.", "Emotions."];

const CameraSVG = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
    <circle cx="12" cy="13" r="3"/>
  </svg>
);

const KeyboardSVG = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect width="20" height="16" x="2" y="4" rx="2" ry="2"/>
    <path d="M6 8h.001M10 8h.001M14 8h.001M18 8h.001M8 12h.001M12 12h.001M16 12h.001M7 16h10"/>
  </svg>
);

const SmileSVG = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <circle cx="12" cy="12" r="10" />
    <path d="M8 14s1.5 2 4 2 4-2 4-2" />
    <line x1="9" y1="9" x2="9.01" y2="9" />
    <line x1="15" y1="9" x2="15.01" y2="9" />
  </svg>
);

const MusicSVG = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M9 18V5l12-2v13" />
    <circle cx="6" cy="18" r="3" />
    <circle cx="18" cy="16" r="3" />
  </svg>
);

export function Hero({ onLaunch }) {
  const [index, setIndex] = useState(0);
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 500], [0, 150]);
  const y2 = useTransform(scrollY, [0, 500], [0, -150]);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % words.length);
    }, 2800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative min-h-screen flex items-center justify-center pt-20 px-6 md:px-12 overflow-hidden">
      <AmbientBackground accent="var(--mm-accent-pink)" />
      
      {/* Glow Effects Behind the Text */}
      <div className="absolute top-1/2 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-[#7B72E0]/20 to-[#FF6B9D]/10 blur-[120px] rounded-full pointer-events-none -z-10" />

      <div className="max-w-7xl w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-center z-10 pt-10">
        
        {/* Left Column: Typography & CTAs */}
        <motion.div 
          initial={{ opacity: 0, x: -40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="space-y-8"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2.5 rounded-full bg-white/70 border border-white/80 backdrop-blur-md shadow-sm">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-teal-500"></span>
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-gray-700">AI-Powered Curation Model Active</span>
          </div>

          <h1 className="text-6xl md:text-[5.5rem] font-black tracking-tighter text-[#1A1A2E] leading-[1.05]">
            We soundtrack <br />
            your <span className="relative inline-block w-full min-w-[300px] h-[1em] overflow-hidden align-bottom mt-2">
              <AnimatePresence mode="popLayout">
                <motion.div
                  key={index}
                  initial={{ y: 80, opacity: 0, scale: 0.95 }}
                  animate={{ y: 0, opacity: 1, scale: 1 }}
                  exit={{ y: -80, opacity: 0, scale: 1.05 }}
                  transition={{ type: "spring", stiffness: 300, damping: 25 }}
                  className="absolute inset-0 text-transparent bg-clip-text bg-gradient-to-r from-[#7B72E0] via-[#FF6B9D] to-[#FF6B9D] pb-2"
                >
                  {words[index]}
                </motion.div>
              </AnimatePresence>
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-600 font-medium max-w-lg leading-relaxed">
            An intelligent music companion that listens to your face and words to perfectly curate your listening experience in real-time.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 pt-6">
            <ReactiveButton 
              label={<span className="flex items-center gap-2">Try Face Scan <CameraSVG className="w-5 h-5"/></span>}
              accent="var(--mm-primary)" 
              className="text-lg px-8 py-4 shadow-xl shadow-[#7B72E0]/20"
              onClick={onLaunch}
            />
            <ReactiveButton 
              label={<span className="flex items-center gap-2">Type a Mood <KeyboardSVG className="w-5 h-5"/></span>}
              accent="var(--mm-surface)" 
              className="text-lg px-8 py-4 shadow-xl shadow-[#FF6B9D]/10 !text-gray-900 border border-gray-200"
              onClick={onLaunch}
            />
          </div>
        </motion.div>

        {/* Right Column: Dynamic Interactive Composition (Hidden on small screens) */}
        <div className="relative hidden lg:flex h-[600px] items-center justify-center">
          
          <motion.div style={{ y: y1 }} className="absolute z-20 left-0 top-16">
            <MotionCard className="bg-white/80 backdrop-blur-xl p-4 rounded-3xl shadow-2xl border border-white/60 pointer-events-auto cursor-pointer">
              <div className="flex items-center gap-4 px-2">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#FF6B9D] to-[#FFA07A] flex items-center justify-center text-white shadow-inner">
                  <SmileSVG className="w-6 h-6" />
                </div>
                <div>
                  <div className="text-sm font-extrabold text-[#1A1A2E]">Euphoria Detected</div>
                  <div className="text-xs text-gray-500 font-medium mt-0.5">Queueing upbeat pop...</div>
                </div>
              </div>
            </MotionCard>
          </motion.div>

          <motion.div 
            animate={{ y: [-15, 15, -15] }} 
            transition={{ repeat: Infinity, duration: 6, ease: "easeInOut" }}
            className="relative z-10"
          >
            <MotionCard className="bg-white/40 backdrop-blur-3xl p-10 rounded-[3rem] shadow-[0_30px_60px_rgba(123,114,224,0.15)] border border-white/60">
              <img src="/logo.svg" alt="MoodMate Application Core" className="w-72 h-72 drop-shadow-2xl hover:scale-105 transition-transform duration-500 ease-out" />
            </MotionCard>
          </motion.div>

          <motion.div style={{ y: y2 }} className="absolute z-20 -right-8 bottom-24">
            <MotionCard className="bg-[#1A1A2E]/90 backdrop-blur-xl p-5 rounded-3xl shadow-2xl border border-white/10 pointer-events-auto cursor-pointer flex flex-col gap-3 w-56">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-[10px] bg-gradient-to-tr from-purple-500 to-indigo-500 flex items-center justify-center text-white shadow-lg">
                  <MusicSVG className="w-5 h-5" />
                </div>
                <div className="flex-1 space-y-2">
                  <div className="h-2 w-20 bg-white/20 rounded-full" />
                  <div className="h-1.5 w-12 bg-white/10 rounded-full" />
                </div>
              </div>
              <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden mt-2 relative">
                <motion.div 
                  initial={{ width: "0%" }}
                  animate={{ width: "75%" }}
                  transition={{ duration: 2.5, repeat: Infinity, repeatType: "reverse", ease: "easeInOut" }}
                  className="absolute left-0 top-0 h-full bg-gradient-to-r from-[#7B72E0] to-[#FF6B9D] rounded-full shadow-[0_0_10px_#FF6B9D]"
                />
              </div>
            </MotionCard>
          </motion.div>

        </div>
      </div>
    </div>
  );
}
