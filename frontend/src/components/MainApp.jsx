import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { NavBar } from "./NavBar";
import { AmbientBackground } from "./ui/AmbientBackground";
import { Toggle } from "./inputs/Toggle";
import { ImageUpload } from "./inputs/ImageUpload";
import { TextInput } from "./inputs/TextInput";
import { EmotionResult } from "./results/EmotionResult";
import { PlaylistCard } from "./results/PlaylistCard";
import { predictFromImage, predictFromText } from "../api";

const inputOptions = [
  { id: "image", label: "Face Scan", icon: "📷" },
  { id: "text", label: "Type Mood", icon: "✍️" }
];

const moodOptions = [
  { id: "match", label: "Match Mood", icon: "🎯" },
  { id: "uplift", label: "Uplift Mood", icon: "🚀" }
];

export function MainApp({ onBack, onNavigate }) {
  const [mode, setMode] = useState("image");
  const [recMode, setRecMode] = useState("match");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const fetchRecommendations = async (action, payload) => {
    setLoading(true); 
    setError(null); 
    setData(null);
    try {
      const result = await action(payload, recMode);
      setData(result);
    } catch (err) {
      setError("Failed to analyze exactly. Ensure the backend is running & connected.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen relative flex flex-col bg-[#F8F6FF] selection:bg-[#7b72e0]/30 selection:text-[#1a1a2e] overflow-hidden">
      <NavBar onLaunch={onBack} forcedLabel="Return to Base" onNavigate={onNavigate} onLogoClick={onBack} />
      <AmbientBackground accent={mode === 'image' ? "var(--mm-primary)" : "var(--mm-accent-pink)"} />
      
      {/* Vibe Scanner Redesign: Asymmetrical Glass Control Center */}
      <main className="flex-1 w-full max-w-[1500px] mx-auto z-10 pt-20 pb-4 px-4 md:px-10 flex flex-col lg:flex-row gap-5 xl:gap-10 min-h-0">
        
        {/* Left Panel: The Input Console */}
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ type: "spring", stiffness: 200, damping: 25 }}
          className="lg:w-[380px] shrink-0 flex flex-col gap-5 bg-white/40 backdrop-blur-3xl p-6 rounded-[2.5rem] border border-white shadow-[0_40px_80px_rgba(123,114,224,0.15)] relative min-h-0"
        >
          {/* Decorative Internal Glows */}
          <div className="absolute -top-32 -left-32 w-64 h-64 bg-[#7B72E0]/20 blur-[80px] rounded-full pointer-events-none" />
          <div className="absolute -bottom-32 -right-32 w-64 h-64 bg-[#FF6B9D]/20 blur-[80px] rounded-full pointer-events-none" />
          
          {/* Header */}
          <div className="relative z-10">
            <h1 className="text-4xl font-black text-[#1A1A2E] tracking-tighter mb-2 leading-[1.1]">
              Vibe <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#7B72E0] to-[#FF6B9D]">Scanner</span>
            </h1>
            <p className="text-gray-500 font-medium text-sm leading-relaxed">
              Provide an emotional signature and let the AI curate your playlist.
            </p>
          </div>

          {/* Input Type Toggle */}
          <div className="relative z-10 w-full flex justify-center">
            <Toggle name="input" options={inputOptions} selected={mode} onChange={(m) => { setMode(m); setData(null); setError(null); }} />
          </div>

          {/* Recommendation Mode Toggle */}
          <div className="relative z-10 w-full">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3 text-center">Recommendation Strategy</p>
            <Toggle name="strategy" options={moodOptions} selected={recMode} onChange={setRecMode} />
          </div>

          {/* Dynamic Input Surface */}
          <div className="flex-1 relative z-10 w-full flex flex-col justify-center">
            <AnimatePresence mode="wait">
              {mode === "image" ? (
                <motion.div key="img" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} transition={{ duration: 0.2 }}>
                  <ImageUpload onSelect={(file) => file && fetchRecommendations(predictFromImage, file)} />
                </motion.div>
              ) : (
                <motion.div key="txt" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} transition={{ duration: 0.2 }}>
                  <TextInput onSubmit={(text) => fetchRecommendations(predictFromText, text)} />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Right Panel: The Results Canvas */}
        <motion.div 
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ type: "spring", stiffness: 200, damping: 25, delay: 0.1 }}
          className="flex-1 flex flex-col items-center justify-center relative min-h-0"
        >
          {/* Loading State */}
          {loading && (
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }} className="flex flex-col items-center gap-8 py-10 absolute z-20">
              <div className="relative w-32 h-32 flex items-center justify-center">
                <div className="absolute inset-0 border-[8px] border-[#E0DAF8] rounded-full" />
                <div className="absolute inset-0 border-[8px] border-[#7B72E0] rounded-full border-t-transparent animate-spin" />
                <div className="w-16 h-16 bg-gradient-to-tr from-[#7B72E0] to-[#FF6B9D] rounded-full animate-pulse blur-md" />
              </div>
              <p className="text-[#7B72E0] font-black text-2xl animate-pulse tracking-tight drop-shadow-sm">Tuning Frequencies...</p>
            </motion.div>
          )}

          {/* Error State */}
          {error && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white/80 backdrop-blur-md text-red-600 px-8 py-6 rounded-3xl font-bold border-2 border-red-100 flex items-center gap-4 max-w-lg text-center shadow-xl shadow-red-500/10 absolute z-20">
              <span className="text-3xl">⚠️</span> {error}
            </motion.div>
          )}

          {/* Empty State */}
          {!data && !loading && !error && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1 }} className="text-center opacity-30 select-none absolute z-10 w-full flex flex-col items-center">
              <div className="text-[12rem] leading-none mb-6 filter drop-shadow-xl saturate-50 grayscale transition-all duration-1000">📡</div>
              <h2 className="text-4xl font-black text-[#1A1A2E] tracking-tighter mix-blend-multiply">Awaiting Signal</h2>
            </motion.div>
          )}

          {/* Results Area */}
          <AnimatePresence>
            {data && !loading && (
              <motion.div key="results" initial={{ opacity: 0, filter: "blur(40px)", scale: 0.8 }} animate={{ opacity: 1, filter: "blur(0px)", scale: 1 }} exit={{ opacity: 0, scale: 0.9 }} transition={{ type: "spring", stiffness: 150, damping: 20 }} className="w-full flex flex-col z-20">
                
                {/* Emotion Badge */}
                <div className="w-full flex justify-center mb-6">
                  {data.emotion && <EmotionResult emotion={data.emotion} targetEmotion={data.target_emotion} mode={data.mode} />}
                </div>

                {/* Playlist */}
                <div className="w-full">
                  {data.recommendations && <PlaylistCard tracks={data.recommendations} />}
                </div>

              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

      </main>
    </div>
  );
}
