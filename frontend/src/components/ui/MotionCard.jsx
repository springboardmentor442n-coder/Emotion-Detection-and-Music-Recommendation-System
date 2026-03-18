import { useRef, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";

export function MotionCard({ children, className = "" }) {
  const ref = useRef(null);
  const [highlight, setHighlight] = useState({ x: 50, y: 50, opacity: 0 });

  const rawX = useSpring(0, { stiffness: 120, damping: 14 });
  const rawY = useSpring(0, { stiffness: 120, damping: 14 });
  const scale = useSpring(1, { stiffness: 200, damping: 20 });

  const rotateX = useTransform(rawY, [-0.5, 0.5], [15, -15]);
  const rotateY = useTransform(rawX, [-0.5, 0.5], [-15, 15]);

  function onMouseMove(e) {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const nx = (e.clientX - rect.left) / rect.width - 0.5;
    const ny = (e.clientY - rect.top) / rect.height - 0.5;
    rawX.set(nx);
    rawY.set(ny);
    scale.set(1.03);
    const hx = ((e.clientX - rect.left) / rect.width) * 100;
    const hy = ((e.clientY - rect.top) / rect.height) * 100;
    setHighlight({ x: hx, y: hy, opacity: 0.18 });
  }

  function onMouseLeave() {
    rawX.set(0);
    rawY.set(0);
    scale.set(1);
    setHighlight((h) => ({ ...h, opacity: 0 }));
  }

  function onMouseDown() { scale.set(0.98); }
  function onMouseUp()   { scale.set(1.03); }

  return (
    <motion.div
      ref={ref}
      style={{ rotateX, rotateY, scale, transformStyle: "preserve-3d", perspective: 800 }}
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      onMouseDown={onMouseDown}
      onMouseUp={onMouseUp}
      className={`relative rounded-2xl overflow-hidden ${className}`}
    >
      {/* Specular highlight */}
      <div
        className="pointer-events-none absolute inset-0 rounded-2xl transition-opacity duration-300"
        style={{
          background: `radial-gradient(circle at ${highlight.x}% ${highlight.y}%, rgba(255,255,255,0.55) 0%, transparent 60%)`,
          opacity: highlight.opacity,
          zIndex: 10,
        }}
      />
      {children}
    </motion.div>
  );
}
