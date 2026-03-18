export function AmbientBackground({ accent = "var(--mm-accent-pink)" }) {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none" aria-hidden="true">
      <div
        className="absolute animate-[drift1_18s_ease-in-out_infinite]"
        style={{
          width: 500, height: 500,
          left: '15%', top: '10%',
          background: accent,
          borderRadius: '50%',
          opacity: 0.12,
          filter: 'blur(80px)',
          willChange: 'transform',
          transform: 'translate3d(0,0,0)',
        }}
      />
      <div
        className="absolute animate-[drift2_22s_ease-in-out_infinite]"
        style={{
          width: 350, height: 350,
          left: '70%', top: '60%',
          background: accent,
          borderRadius: '50%',
          opacity: 0.1,
          filter: 'blur(80px)',
          willChange: 'transform',
          transform: 'translate3d(0,0,0)',
        }}
      />
    </div>
  );
}
