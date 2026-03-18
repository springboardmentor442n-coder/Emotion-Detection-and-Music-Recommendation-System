import { motion } from "framer-motion";
import { MotionCard } from "./ui/MotionCard";

const ScanSVG = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

const BrainSVG = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Zm5 0A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z" />
  </svg>
);

const PlaySVG = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
    <path d="M8 21h8" />
    <path d="M12 17v4" />
    <polygon points="10 8 16 10 10 12 10 8" />
  </svg>
);

const steps = [
  {
    title: "1. Capture the Vibe",
    desc: "Scan your facial expression or simply type out your current thoughts. We accurately detect your emotion using AI.",
    icon: <ScanSVG className="w-8 h-8 text-white relative z-10" />,
    color: "from-[#FF6B9D] to-[#FFA07A]"
  },
  {
    title: "2. Deep Analysis",
    desc: "Our neural networks instantly analyze your sentiment, mapping it precisely to a distinct emotional frequency.",
    icon: <BrainSVG className="w-8 h-8 text-white relative z-10" />,
    color: "from-[#7B72E0] to-[#AFA9EC]"
  },
  {
    title: "3. Curated Playlists",
    desc: "We generate a custom-tailored music queue designed to either match your current mood or actively uplift your vibe.",
    icon: <PlaySVG className="w-8 h-8 text-white relative z-10" />,
    color: "from-[#2DBFA0] to-[#1D9E75]"
  }
];

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.15, delayChildren: 0.1 } },
};

const item = {
  hidden: { opacity: 0, y: 40 },
  show:   { opacity: 1, y: 0, transition: { type: "spring", stiffness: 200, damping: 20 } },
};

export function HowItWorks() {
  return (
    <section id="how-it-works" className="relative py-24 px-6 md:px-12 backdrop-blur-sm z-10">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-20 space-y-4">
          <h2 className="text-4xl md:text-5xl font-black text-[#1A1A2E] tracking-tight">How it Works</h2>
          <p className="text-xl text-gray-600 font-medium max-w-2xl mx-auto">Three seamless steps to transform your emotional state into the perfect listening experience.</p>
        </div>

        <motion.div 
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-100px" }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          {steps.map((step, i) => (
            <motion.div key={i} variants={item}>
              <MotionCard className="bg-white/90 backdrop-blur-md p-10 rounded-[2rem] shadow-xl shadow-[#7B72E0]/10 border border-white flex flex-col items-start gap-8 h-full">
                <div className={`relative w-20 h-20 rounded-3xl bg-gradient-to-br ${step.color} flex items-center justify-center shadow-lg shadow-black/10 overflow-hidden`}>
                  <div className="absolute inset-0 bg-white/20 blur-sm brightness-150 rounded-full scale-150 transform -translate-y-4 translate-x-4"></div>
                  {step.icon}
                </div>
                <div>
                  <h3 className="text-2xl font-extrabold text-[#1A1A2E] mb-3">{step.title}</h3>
                  <p className="text-gray-600 leading-relaxed font-medium">{step.desc}</p>
                </div>
              </MotionCard>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
