import { motion } from "framer-motion";
import { MotionCard } from "./ui/MotionCard";

export function About() {
  return (
    <section id="about" className="relative py-32 px-6 md:px-12 z-10">
      <div className="max-w-7xl mx-auto">
        <MotionCard className="relative overflow-hidden bg-gradient-to-br from-[#1A1A2E] to-[#2D2D44] p-10 md:p-16 rounded-[3rem] shadow-2xl flex flex-col md:flex-row items-center gap-12">
          
          {/* Background Ambient Glows inside the Card */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-[#7B72E0] opacity-30 blur-[100px] rounded-full pointer-events-none" />
          <div className="absolute bottom-0 left-10 w-64 h-64 bg-[#FF6B9D] opacity-20 blur-[80px] rounded-full pointer-events-none" />

          <div className="flex-1 space-y-6 relative z-10">
            <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight">
              Music is the deepest reflection of human emotion.
            </h2>
            <p className="text-lg text-gray-300 font-medium leading-relaxed max-w-xl">
              MoodMate was born from a simple idea: that technology should understand us better. Rather than endlessly scrolling to figure out what to listen to, our advanced neural networks read the unspoken subtleties of your mood and instantly map them to acoustic attributes.
            </p>
            <p className="text-lg text-gray-300 font-medium leading-relaxed max-w-xl">
              Whether you want to lean into the melancholy of a rainy Tuesday, or inject pure euphoria into your Friday night, MoodMate bridges the gap between hardware, AI, and raw human feeling.
            </p>
          </div>

          <div className="flex-1 relative z-10 w-full md:w-auto flex justify-center">
            <div className="relative w-64 h-64 md:w-80 md:h-80">
              <div className="absolute inset-0 bg-gradient-to-tr from-[#7B72E0] to-[#FF6B9D] rounded-full blur-2xl opacity-40 animate-pulse" />
              <img src="/logo.svg" alt="MoodMate Logic Core" className="w-full h-full relative z-10 drop-shadow-2xl" />
            </div>
          </div>
        </MotionCard>
      </div>
    </section>
  );
}
