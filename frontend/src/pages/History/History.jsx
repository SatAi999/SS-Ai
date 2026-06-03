import { motion } from 'framer-motion'
import { ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'
import ConversationHistory from '../../components/ConversationHistory/ConversationHistory'
import useAppStore from '../../store/useAppStore'
import { useTranslation } from '../../i18n/translations'

const PAGE_VARIANTS = {
  initial: { opacity: 0, x: 30 },
  animate: { opacity: 1, x: 0, transition: { duration: 0.35, ease: 'easeOut' } },
  exit: { opacity: 0, x: -20, transition: { duration: 0.2 } },
}

const History = () => {
  const { language } = useAppStore()
  const { t } = useTranslation(language)

  return (
    <motion.main
      variants={PAGE_VARIANTS}
      initial="initial"
      animate="animate"
      exit="exit"
      className="max-w-2xl mx-auto px-4 pt-4 pb-16"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <Link
          to="/"
          className="w-9 h-9 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-slate-500 hover:text-primary-600 hover:border-primary-300 transition-colors shadow-sm"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <h1 className="text-lg font-bold text-slate-800">{t.conversationHistory}</h1>
      </div>

      <ConversationHistory />
    </motion.main>
  )
}

export default History
