export function Footer() {
  return (
    <footer className="relative py-12 px-6 md:px-12 bg-white/70 backdrop-blur-md border-t border-gray-100 z-10">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        
        <div className="flex items-center gap-3">
          <img src="/logo.svg" alt="MoodMate" className="w-8 h-8 opacity-80" />
          <span className="text-lg font-bold text-gray-800">MoodMate</span>
        </div>

        <p className="text-sm font-medium text-gray-500 text-center md:text-left">
          &copy; {new Date().getFullYear()} MoodMate AI. All rights reserved.
        </p>

        <div className="flex items-center gap-6 text-sm font-semibold text-gray-400">
          <a href="#" className="hover:text-gray-900 transition-colors">Privacy</a>
          <a href="#" className="hover:text-gray-900 transition-colors">Terms</a>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-gray-900 transition-colors">GitHub</a>
        </div>

      </div>
    </footer>
  );
}
