import { motion, AnimatePresence } from 'framer-motion'
import { Calendar, MessageSquare, ChevronDown, ChevronUp, Activity, User, Trash2 } from 'lucide-react'
import { useState } from 'react'
import useAppStore from '../../store/useAppStore'
import { useTranslation } from '../../i18n/translations'

const HistoryItem = ({ session, index }) => {
  const [expanded, setExpanded] = useState(false)
  const { language } = useAppStore()
  const { t } = useTranslation(language)

  const date = new Date(session.timestamp)
  const formatted = date.toLocaleDateString(
    language === 'hi' ? 'hi-IN' : 'en-IN',
    { day: 'numeric', month: 'short', year: 'numeric' },
  )
  const time = date.toLocaleTimeString(
    language === 'hi' ? 'hi-IN' : 'en-IN',
    { hour: '2-digit', minute: '2-digit' },
  )

  const msgCount = session.messages?.length || 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden"
    >
      {/* Header */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-slate-50 transition-colors"
      >
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-emerald-500 flex items-center justify-center flex-shrink-0">
          <MessageSquare className="w-5 h-5 text-white" />
        </div>

        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-slate-800 truncate">
            {session.summary || (language === 'hi' ? 'बातचीत' : 'Conversation')}
          </p>
          <div className="flex items-center gap-2 mt-0.5 text-xs text-slate-500">
            <Calendar className="w-3 h-3" />
            <span>{formatted}</span>
            <span>·</span>
            <span>{time}</span>
            <span>·</span>
            <span>{msgCount} {language === 'hi' ? 'संदेश' : 'messages'}</span>
          </div>
        </div>

        {expanded ? (
          <ChevronUp className="w-4 h-4 text-slate-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400 flex-shrink-0" />
        )}
      </button>

      {/* Expanded messages */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 flex flex-col gap-2 max-h-72 overflow-y-auto scrollbar-hide">
              <div className="h-px bg-slate-100 mb-1" />
              {session.messages?.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex items-start gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                >
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                      msg.role === 'user'
                        ? 'bg-primary-100'
                        : 'bg-gradient-to-br from-primary-500 to-emerald-500'
                    }`}
                  >
                    {msg.role === 'user' ? (
                      <User className="w-3 h-3 text-primary-600" />
                    ) : (
                      <Activity className="w-3 h-3 text-white" />
                    )}
                  </div>
                  <div
                    className={`px-3 py-2 rounded-xl text-xs leading-relaxed max-w-[75%] ${
                      msg.role === 'user'
                        ? 'bg-primary-600 text-white rounded-br-sm'
                        : 'bg-slate-100 text-slate-700 rounded-tl-sm'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

const ConversationHistory = () => {
  const { conversationHistory, clearHistory, language } = useAppStore()
  const { t } = useTranslation(language)

  if (conversationHistory.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4 text-slate-400">
        <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center">
          <MessageSquare className="w-8 h-8" />
        </div>
        <p className="text-sm font-medium">{t.noHistory}</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-600">
          {conversationHistory.length}{' '}
          {language === 'hi' ? 'पिछली बातचीत' : 'past conversations'}
        </h2>
        <button
          onClick={clearHistory}
          className="flex items-center gap-1 text-xs text-red-400 hover:text-red-600 transition-colors px-2 py-1 rounded-lg hover:bg-red-50"
        >
          <Trash2 className="w-3.5 h-3.5" />
          {language === 'hi' ? 'सब हटाएं' : 'Clear all'}
        </button>
      </div>

      {conversationHistory.map((session, i) => (
        <HistoryItem key={session.sessionId || i} session={session} index={i} />
      ))}
    </div>
  )
}

export default ConversationHistory
