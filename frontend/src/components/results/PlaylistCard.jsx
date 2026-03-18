import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { MotionCard } from "../ui/MotionCard";

const listAttr = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } }
};

const itemAttr = {
  hidden: { opacity: 0, x: 20, scale: 0.95 },
  show: { opacity: 1, x: 0, scale: 1, transition: { type: "spring", stiffness: 260, damping: 20 } }
};

function TrackArtwork({ track }) {
  const [imgUrl, setImgUrl] = useState(null);

  useEffect(() => {
    // Attempt to silently fetch the real album art from iTunes Search API (requires no auth)
    const fetchArt = async () => {
      try {
        const query = encodeURIComponent(`${track.name} ${track.artist}`);
        const response = await fetch(`https://itunes.apple.com/search?term=${query}&entity=song&limit=1`);
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
          // Upgrade the default low-res 100x100 format to crisp 400x400 imagery
          const highResUrl = data.results[0].artworkUrl100.replace('100x100bb.jpg', '400x400bb.jpg');
          setImgUrl(highResUrl);
        }
      } catch (err) {
        // Silently let the placeholder persist if network failure
      }
    };
    fetchArt();
  }, [track.name, track.artist]);

  return (
    <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center shrink-0 overflow-hidden shadow-inner">
      <img 
        src={imgUrl || `https://ui-avatars.com/api/?name=${track.artist}&background=random&color=fff&bold=true`} 
        alt={track.artist} 
        className="w-full h-full object-cover"
      />
    </div>
  );
}

export function PlaylistCard({ tracks }) {
  const [playingId, setPlayingId] = useState(null);
  const audioRef = useRef(null);

  if (!tracks || tracks.length === 0) return null;

  const handlePlayToggle = (track, trackIndex) => {
    const hasPreview = track.preview_url && track.preview_url !== 'nan' && track.preview_url.trim() !== '';
    
    if (!hasPreview) {
      if (track.spotify_id && track.spotify_id !== 'nan') {
        window.open(`https://open.spotify.com/track/${track.spotify_id}`, '_blank');
      } else {
         // Fallback if no spotify ID exists 
         window.open(`https://youtube.com/results?search_query=${encodeURIComponent(track.name + ' ' + track.artist)}`, '_blank');
      }
      return;
    }

    if (playingId === trackIndex) {
      audioRef.current.pause();
      setPlayingId(null);
    } else {
      if (audioRef.current) {
        audioRef.current.src = track.preview_url;
        audioRef.current.play();
        setPlayingId(trackIndex);
      }
    }
  };

  return (
    <div className="w-full">
      <audio ref={audioRef} onEnded={() => setPlayingId(null)} />
      
      <h3 className="text-lg font-black text-[#1A1A2E] mb-3 text-center">
        🎵 AI Curated Setlist
      </h3>
      
      <motion.div 
        variants={listAttr} 
        initial="hidden" 
        animate="show" 
        className="flex flex-col gap-2"
      >
        {tracks.map((track, i) => {
          const isPlaying = playingId === i;
          const hasPreview = track.preview_url && track.preview_url !== 'nan' && track.preview_url.trim() !== '';
          const songName = track.name || track.title || 'Unknown Title';
          const artistName = track.artist || 'Unknown Artist';

          return (
            <motion.div key={i} variants={itemAttr}>
              <div className={`flex items-center gap-3 px-3 py-2.5 rounded-xl backdrop-blur-xl transition-all duration-200 ${
                isPlaying 
                  ? 'bg-[#7B72E0]/10 border border-[#7B72E0]/30' 
                  : 'bg-white/50 border border-white/60 hover:bg-white/80'
              }`}>
                
                {/* Track Number */}
                <span className="w-6 text-center text-sm font-black text-gray-400 shrink-0">{i + 1}</span>
                
                {/* Album Art */}
                <TrackArtwork track={{...track, name: songName, artist: artistName}} />
                
                {/* Song Info */}
                <div className="flex-1 min-w-0 flex flex-col justify-center">
                  <h4 className="text-[#1A1A2E] font-bold text-base leading-tight truncate" title={songName}>
                    {songName}
                  </h4>
                  <p className="text-gray-500 font-medium text-sm truncate mt-0.5" title={artistName}>
                    {artistName}
                  </p>
                </div>
                
                {/* Play Button */}
                <button 
                  onClick={() => handlePlayToggle(track, i)}
                  className={`w-9 h-9 rounded-full text-white flex items-center justify-center transition-all duration-200 shrink-0 ${
                    isPlaying 
                      ? 'bg-[#FF6B9D] animate-pulse' 
                      : 'bg-gradient-to-br from-[#1A1A2E] to-[#2D2D44] hover:scale-110'
                  }`}
                  title={hasPreview ? (isPlaying ? "Pause Preview" : "Play Preview") : "Open externally"}
                >
                  {!hasPreview ? (
                     <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" /><polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" /></svg>
                  ) : isPlaying ? (
                     <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4"><path d="M6 4h4v16H6zm8 0h4v16h-4z" /></svg>
                  ) : (
                     <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 ml-0.5"><path d="M5 3v18l15-9L5 3z" /></svg>
                  )}
                </button>
              </div>
            </motion.div>
          );
        })}
      </motion.div>
    </div>
  );
}
