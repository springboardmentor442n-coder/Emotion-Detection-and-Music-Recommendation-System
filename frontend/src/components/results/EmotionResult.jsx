import { motion } from "framer-motion";

const emotionMap = {
  happy: { color: "from-[#FF6B9D] to-[#FF907A]", icon: "😎", label: "Joy & Euphoria" },
  sad: { color: "from-[#378ADD] to-[#7B72E0]", icon: "🌧️", label: "Melancholy" },
  angry: { color: "from-[#D85A30] to-[#E93A3A]", icon: "🔥", label: "Intensity" },
  neutral: { color: "from-[#1D9E75] to-[#2DBFA0]", icon: "🌿", label: "Chill Vibes" },
  fear: { color: "from-[#EF9F27] to-[#F5C77E]", icon: "🌪️", label: "Suspense" },
  surprise: { color: "from-[#9B51E0] to-[#FF6B9D]", icon: "✨", label: "Electric Eclectic" },
};

export function EmotionResult({ emotion, targetEmotion, mode }) {
  const detected = emotionMap[emotion] || emotionMap.neutral;
  const isUplift = mode === 'uplift' && targetEmotion && targetEmotion !== emotion;
  const target = isUplift ? (emotionMap[targetEmotion] || emotionMap.neutral) : detected;
  
  return (
    <motion.div 
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
      className="flex items-center gap-4 mb-4 p-4 rounded-2xl bg-white/50 backdrop-blur-xl border border-white/60 w-full"
    >
      <div className="flex items-center gap-3 shrink-0">
        <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${detected.color} flex items-center justify-center text-xl border-2 border-white shadow-md`}>
          {detected.icon}
        </div>
        {isUplift && (
          <>
            <span className="text-lg font-black text-[#7B72E0]">→</span>
            <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${target.color} flex items-center justify-center text-xl border-2 border-white shadow-md`}>
              {target.icon}
            </div>
          </>
        )}
      </div>
      <div className="min-w-0">
        {isUplift ? (
          <>
            <h2 className="text-lg font-black text-[#1A1A2E] capitalize tracking-tight leading-tight">Uplifting to {targetEmotion}</h2>
            <p className="text-xs text-gray-400 font-semibold">Detected: {emotion} · {target.label} 🚀</p>
          </>
        ) : (
          <>
            <h2 className="text-lg font-black text-[#1A1A2E] capitalize tracking-tight leading-tight">{emotion} Detected</h2>
            <p className="text-xs text-gray-400 font-semibold">{detected.label} tuning engaged.</p>
          </>
        )}
      </div>
    </motion.div>
  );
}
