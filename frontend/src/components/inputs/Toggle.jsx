import { motion, LayoutGroup } from "framer-motion";

export function Toggle({ options, selected, onChange, name = "toggle" }) {
  return (
    <LayoutGroup id={name}>
      <div className="relative flex w-full bg-white/60 backdrop-blur-xl border border-white/60 p-1.5 rounded-full shadow-sm">
        {options.map((option) => (
          <button
            key={option.id}
            onClick={() => onChange(option.id)}
            className={`relative flex-1 flex justify-center py-3.5 rounded-full text-sm font-bold transition-colors z-10 ${
              selected === option.id ? "text-white" : "text-gray-500 hover:text-gray-800"
            }`}
          >
            {selected === option.id && (
              <motion.div
                layoutId={`pill-${name}`}
                className="absolute inset-0 bg-[#7B72E0] rounded-full shadow-[0_4px_12px_rgba(123,114,224,0.3)]"
                transition={{ type: "spring", stiffness: 350, damping: 25 }}
              />
            )}
            <span className="relative z-20 flex items-center gap-2">
              {option.icon} {option.label}
            </span>
          </button>
        ))}
      </div>
    </LayoutGroup>
  );
}
