import { motion } from 'framer-motion'
import { User, Activity, AlertTriangle, ChevronRight } from 'lucide-react'
import useAppStore from '../../store/useAppStore'
import { useTranslation } from '../../i18n/translations'

const severityStyles = {
  low: 'border-l-4 border-yellow-400 bg-yellow-50 text-yellow-800',
  medium: 'border-l-4 border-orange-400 bg-orange-50 text-orange-800',
  high: 'border-l-4 border-red-500 bg-red-50 text-red-800',
  critical: 'border-l-4 border-red-700 bg-red-100 text-red-900',
}

const SeverityBadge = ({ severity, t }) => {
  if (!severity) return null
  const styles = {
    low: 'bg-yellow-100 text-yellow-700',
    medium: 'bg-orange-100 text-orange-700',
    high: 'bg-red-100 text-red-700',
    critical: 'bg-red-200 text-red-900 font-bold',
  }
  return (
    <span
      className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium ${styles[severity] || styles.low}`}
    >
      <AlertTriangle className="w-3 h-3" />
      {t.severity?.[severity] || severity}
    </span>
  )
}

const TypingIndicator = () => (
  <div className="flex items-center gap-1 px-4 py-3">
    {[0, 1, 2].map((i) => (
      <span
        key={i}
        className="w-2 h-2 rounded-full bg-slate-400 typing-dot"
        style={{ animationDelay: `${i * 160}ms` }}
      />
    ))}
  </div>
)

const ConversationBubble = ({ message, isTyping = false }) => {
  const { language } = useAppStore()
  const { t } = useTranslation(language)

  const isUser = message?.role === 'user'
  const isError = message?.type === 'error'

  const timestamp = message?.timestamp
    ? new Date(message.timestamp).toLocaleTimeString(
        language === 'hi' ? 'hi-IN' : 'en-IN',
        { hour: '2-digit', minute: '2-digit' },
      )
    : ''

  if (isTyping) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start gap-3 max-w-[85%]"
      >
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-emerald-500 flex items-center justify-center shadow-sm">
          <Activity className="w-4 h-4 text-white" />
        </div>
        <div className="bg-white rounded-2xl rounded-tl-sm shadow-sm border border-slate-100">
          <TypingIndicator />
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex items-end gap-2 ${isUser ? 'flex-row-reverse' : 'flex-row'} max-w-[88%] ${isUser ? 'ml-auto' : 'mr-auto'}`}
    >
      {/* Avatar */}
      <div className="flex-shrink-0 mb-1">
        {isUser ? (
          <div className="w-7 h-7 rounded-full bg-primary-100 flex items-center justify-center">
            <User className="w-4 h-4 text-primary-600" />
          </div>
        ) : (
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-emerald-500 flex items-center justify-center shadow-sm">
            <Activity className="w-3.5 h-3.5 text-white" />
          </div>
        )}
      </div>

      {/* Bubble */}
      <div className={`flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Severity bar (AI only) */}
        {!isUser && message?.severity && (
          <div className={`w-full rounded-xl p-2.5 mb-1 text-xs ${severityStyles[message.severity] || ''}`}>
            <span className="font-semibold">
              {t.severity?.[message.severity]}
            </span>
            {' — '}
            {t.severityAction?.[message.severity]}
          </div>
        )}

        {/* Main bubble */}
        <div
          className={`
            px-4 py-3 rounded-2xl max-w-xs sm:max-w-sm leading-relaxed text-sm
            ${isUser
              ? 'bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-br-sm shadow-md'
              : isError
              ? 'bg-red-50 text-red-700 border border-red-200 rounded-tl-sm'
              : 'bg-white text-slate-800 rounded-tl-sm shadow-sm border border-slate-100'
            }
          `}
        >
          {/* Voice indicator */}
          {isUser && message?.type === 'voice' && (
            <span className="inline-flex items-center gap-1 text-primary-200 text-xs mb-1 block">
              🎙 {language === 'hi' ? 'आवाज़' : 'Voice'}
            </span>
          )}
          <p className="whitespace-pre-wrap">{message?.content}</p>
        </div>

        {/* Severity badge */}
        {!isUser && message?.severity && (
          <SeverityBadge severity={message.severity} t={t} />
        )}

        {/* Suggestions */}
        {!isUser && message?.suggestions?.length > 0 && (
          <div className="flex flex-col gap-1 mt-1">
            {message.suggestions.slice(0, 3).map((s, i) => (
              <div
                key={i}
                className="flex items-center gap-1.5 text-xs text-primary-700 bg-primary-50 rounded-lg px-2.5 py-1.5"
              >
                <ChevronRight className="w-3 h-3 flex-shrink-0" />
                <span>{s}</span>
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <span className="text-[10px] text-slate-400 px-1">{timestamp}</span>
      </div>
    </motion.div>
  )
}

export default ConversationBubble
