import { motion } from 'framer-motion'
import useAppStore from '../../store/useAppStore'

const LanguageToggle = () => {
  const { language, setLanguage } = useAppStore()

  return (
    <div className="relative flex items-center bg-slate-100 rounded-xl p-0.5 gap-0 h-8">
      {/* Sliding indicator */}
      <motion.div
        layout
        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
        className="absolute h-7 w-11 bg-white rounded-[10px] shadow-sm"
        style={{ left: language === 'en' ? '2px' : 'calc(50% - 2px)' }}
      />

      <button
        onClick={() => setLanguage('en')}
        className={`relative z-10 w-11 h-7 text-xs font-semibold rounded-[10px] transition-colors duration-150 ${
          language === 'en' ? 'text-primary-700' : 'text-slate-500'
        }`}
        aria-label="Switch to English"
      >
        EN
      </button>
      <button
        onClick={() => setLanguage('hi')}
        className={`relative z-10 w-11 h-7 text-xs font-semibold rounded-[10px] transition-colors duration-150 ${
          language === 'hi' ? 'text-primary-700' : 'text-slate-500'
        }`}
        aria-label="हिंदी में बदलें"
      >
        हिं
      </button>
    </div>
  )
}

export default LanguageToggle
