import { useState, useRef } from "react";
import { motion } from "framer-motion";

const ImageIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-8 h-8">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
    <circle cx="8.5" cy="8.5" r="1.5" />
    <polyline points="21 15 16 10 5 21" />
  </svg>
);

export function ImageUpload({ onSelect }) {
  const [drag, setDrag] = useState(false);
  const [preview, setPreview] = useState(null);
  const fileInput = useRef(null);

  const handleFile = (file) => {
    if (!file || !file.type.startsWith("image/")) return;
    setPreview(URL.createObjectURL(file));
    onSelect(file);
  };

  return (
    <div 
      className={`relative border-[3px] rounded-[2rem] p-6 flex flex-col items-center justify-center transition-all duration-300 min-h-[200px] w-full mx-auto overflow-hidden group cursor-pointer ${
        drag ? 'border-[#7B72E0]/50 bg-[#7B72E0]/5 shadow-[inset_0_0_50px_rgba(123,114,224,0.1)]' : 'border-white/60 bg-white/40 hover:bg-white/70 hover:border-white hover:shadow-xl hover:shadow-[#7B72E0]/10'
      }`}
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => { e.preventDefault(); setDrag(false); handleFile(e.dataTransfer.files[0]); }}
      onClick={() => fileInput.current?.click()}
    >
      <input type="file" ref={fileInput} className="hidden" accept="image/*" onChange={(e) => handleFile(e.target.files[0])} />
      
      {preview ? (
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center gap-6 z-10">
          <img src={preview} alt="Selected face" className="w-56 h-56 object-cover rounded-[2rem] shadow-xl border-4 border-white" />
          <button 
            onClick={(e) => { e.stopPropagation(); setPreview(null); onSelect(null); }}
            className="text-sm font-semibold text-red-500 hover:text-red-700 bg-red-50 px-4 py-2 rounded-full"
          >
            Remove & Reselect
          </button>
        </motion.div>
      ) : (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center gap-4 cursor-pointer z-10">
          <div className="w-20 h-20 rounded-full bg-white shadow-sm flex items-center justify-center text-[#7B72E0]">
            <ImageIcon />
          </div>
          <p className="text-[#1A1A2E] font-bold text-lg">Click to scan face</p>
          <p className="text-gray-500 font-medium text-sm">or drag your photo here</p>
        </motion.div>
      )}
    </div>
  );
}
