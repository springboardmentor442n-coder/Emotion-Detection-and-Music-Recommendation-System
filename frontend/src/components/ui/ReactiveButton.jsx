import { motion, AnimatePresence } from "framer-motion";

export function ReactiveButton({
  label,
  state = "idle",
  accent = "#7B72E0",
  ...props
}) {
  return (
    <motion.button
      {...props}
      whileHover={{ y: -2, boxShadow: `0 8px 24px ${accent}40` }}
      whileTap={{ y: 1, scale: 0.97, boxShadow: `0 2px 8px ${accent}30` }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      style={{ backgroundColor: accent, ...props.style }}
      className={`relative px-6 py-3 rounded-xl text-white text-base font-medium overflow-hidden ${props.className || ''}`}
    >
      <AnimatePresence mode="wait">
        {state === "idle" && (
          <motion.span key="label"
            initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.15 }}
            className="flex items-center justify-center"
          >
            {label}
          </motion.span>
        )}
        {state === "loading" && (
          <motion.span key="spinner"
            initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
            className="flex items-center gap-2 justify-center"
          >
            <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3"/>
              <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z"/>
            </svg>
            Loading…
          </motion.span>
        )}
        {state === "success" && (
          <motion.span key="check"
            initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 16 }}
            className="flex items-center gap-2 justify-center"
          >
            <svg viewBox="0 0 16 16" className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <motion.path d="M2.5 8.5l3.5 3.5 7-7"
                initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
                transition={{ duration: 0.35, ease: "easeOut" }}
              />
            </svg>
            Done!
          </motion.span>
        )}
      </AnimatePresence>
    </motion.button>
  );
}
