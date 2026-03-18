import { motion } from "framer-motion";
import { MotionCard } from "./ui/MotionCard";

const EyeSVG = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

const MessageSVG = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z" />
  </svg>
);

const CheckSVG = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
    <path d="m9 12 2 2 4-4" />
  </svg>
);

const SparklesSVG = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="m12 3-1.9 5.8a2 2 0 0 1-1.2 1.2L3 12l5.8 1.9a2 2 0 0 1 1.2 1.2L12 21l1.9-5.8a2 2 0 0 1 1.2-1.2L21 12l-5.8-1.9a2 2 0 0 1-1.2-1.2Z" />
  </svg>
);

const features = [
  {
    title: "Facial Emotion Recognition",
    desc: "Our proprietary CNN model analyzes micro-expressions from your live camera feed in mere milliseconds, mapping them securely and privately.",
    icon: <EyeSVG className="w-7 h-7 text-[#7B72E0]" />,
    bg: "bg-[#7B72E0]/10"
  },
  {
    title: "RoBERTa Text Engine",
    desc: "Prefer to type? Our NLP engine utilizes advanced HuggingFace Transformers to infer your exact emotional wavelength from text input.",
    icon: <MessageSVG className="w-7 h-7 text-[#FF6B9D]" />,
    bg: "bg-[#FF6B9D]/10"
  },
  {
    title: "Bi-Directional Filtering",
    desc: "Choose to 'Match' your current vibe to lean into the feeling, or 'Uplift' to let our AI gently guide your mood to a brighter state.",
    icon: <SparklesSVG className="w-7 h-7 text-[#2DBFA0]" />,
    bg: "bg-[#2DBFA0]/10"
  },
  {
    title: "Hybrid Recommendations",
    desc: "We cross-reference your diagnosed emotion with acoustic attributes to generate the perfect mathematical curve for your listening session.",
    icon: <CheckSVG className="w-7 h-7 text-[#1A1A2E]" />,
    bg: "bg-[#1A1A2E]/10"
  }
];

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
};

const item = {
  hidden: { opacity: 0, y: 30 },
  show:   { opacity: 1, y: 0, transition: { type: "spring", stiffness: 200, damping: 20 } },
};

export function Features() {
  return (
    <section id="features" className="relative py-24 px-6 md:px-12 z-10">
      <div className="max-w-7xl mx-auto">
        <div className="mb-16">
          <h2 className="text-4xl md:text-5xl font-black text-[#1A1A2E] tracking-tight mb-4">Core Features</h2>
          <p className="text-xl text-gray-600 font-medium max-w-2xl text-left">The intelligence behind the curtain. Discover what makes our AI engine industry-leading.</p>
        </div>

        <motion.div 
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-100px" }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
        >
          {features.map((feature, i) => (
            <motion.div key={i} variants={item}>
              <MotionCard className="bg-white/60 backdrop-blur-md p-8 rounded-3xl shadow-xl shadow-[#7B72E0]/5 border border-white flex gap-6 items-start h-full">
                <div className={`shrink-0 w-14 h-14 rounded-2xl flex items-center justify-center ${feature.bg}`}>
                  {feature.icon}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-[#1A1A2E] mb-2">{feature.title}</h3>
                  <p className="text-gray-600 font-medium leading-relaxed">{feature.desc}</p>
                </div>
              </MotionCard>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
