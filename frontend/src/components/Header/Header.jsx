import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Activity, History, MessageSquare } from 'lucide-react'
import LanguageToggle from '../LanguageToggle/LanguageToggle'
import useAppStore from '../../store/useAppStore'
import { useTranslation } from '../../i18n/translations'

const Header = () => {
  const location = useLocation()
  const { language } = useAppStore()
  const { t } = useTranslation(language)

  return (
    <header className="sticky top-0 z-50 glass border-b border-teal-100/60 shadow-sm">
      <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo + Name */}
        <Link to="/" className="flex items-center gap-2 group">
          <motion.div
            whileHover={{ rotate: 10, scale: 1.05 }}
            transition={{ type: 'spring', stiffness: 300 }}
            className="w-8 h-8 bg-gradient-to-br from-primary-600 to-emerald-500 rounded-xl flex items-center justify-center shadow-md"
          >
            <Activity className="w-4 h-4 text-white" strokeWidth={2.5} />
          </motion.div>
          <span className="font-bold text-base text-primary-800 tracking-tight leading-none">
            {t.appName}
          </span>
        </Link>

        {/* Nav + Language */}
        <div className="flex items-center gap-1">
          {location.pathname !== '/chat' && (
            <Link
              to="/chat"
              className="touch-target rounded-xl text-primary-700 hover:bg-primary-50 transition-colors px-3 py-1.5 text-sm font-medium flex items-center gap-1.5"
            >
              <MessageSquare className="w-4 h-4" />
              <span className="hidden sm:inline">
                {language === 'hi' ? 'परामर्श' : 'Consult'}
              </span>
            </Link>
          )}

          {location.pathname !== '/history' && (
            <Link
              to="/history"
              className="touch-target rounded-xl text-slate-500 hover:bg-slate-100 transition-colors px-3 py-1.5 text-sm font-medium flex items-center gap-1.5"
            >
              <History className="w-4 h-4" />
              <span className="hidden sm:inline">
                {language === 'hi' ? 'इतिहास' : 'History'}
              </span>
            </Link>
          )}

          <LanguageToggle />
        </div>
      </div>
    </header>
  )
}

export default Header
