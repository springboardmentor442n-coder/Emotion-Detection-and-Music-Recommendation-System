import { useState } from "react";
import { motion } from "framer-motion";
import { ReactiveButton } from "../ui/ReactiveButton";

export function TextInput({ onSubmit }) {
  const [text, setText] = useState("");
  const [focused, setFocused] = useState(false);

  return (
    <div className="relative w-full max-w-2xl mx-auto flex flex-col gap-6">
      <div className="relative">
        <motion.textarea
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className="w-full pt-8 pb-6 px-8 rounded-[2.5rem] border-[3px] bg-white/40 backdrop-blur-xl outline-none transition-all duration-300 resize-none shadow-inner text-[#1A1A2E] text-2xl font-bold leading-relaxed placeholder:text-gray-400/80 placeholder:font-medium hover:bg-white/60 hover:border-white"
          style={{
            borderColor: focused ? "rgba(123, 114, 224, 0.5)" : "rgba(255, 255, 255, 0.6)",
            boxShadow: focused ? "inset 0 0 40px rgba(123, 114, 224, 0.1)" : "inset 0 0 0px rgba(0,0,0,0)",
          }}
          placeholder="Tell me how you're feeling right now..."
        />
      </div>

      <div className="flex justify-center">
        <ReactiveButton 
          label="Analyze Sentiment 🧠"
          accent="#FF6B9D"
          onClick={() => text.trim() && onSubmit(text)}
          disabled={!text.trim()}
          className={`px-10 py-4 text-lg w-full md:w-auto shadow-xl ${!text.trim() ? "opacity-50 cursor-not-allowed" : "shadow-[#FF6B9D]/30"}`}
        />
      </div>
    </div>
  );
}
