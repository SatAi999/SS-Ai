import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, X, Phone, ChevronRight } from 'lucide-react'
import useAppStore from '../../store/useAppStore'
import { useTranslation } from '../../i18n/translations'

const severityConfig = {
  low: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-400',
    icon: 'text-yellow-500',
    title: 'text-yellow-900',
    badge: 'bg-yellow-100 text-yellow-800',
  },
  medium: {
    bg: 'bg-orange-50',
    border: 'border-orange-400',
    icon: 'text-orange-500',
    title: 'text-orange-900',
    badge: 'bg-orange-100 text-orange-800',
  },
  high: {
    bg: 'bg-red-50',
    border: 'border-red-500',
    icon: 'text-red-500',
    title: 'text-red-900',
    badge: 'bg-red-100 text-red-800',
  },
  critical: {
    bg: 'bg-red-100',
    border: 'border-red-700',
    icon: 'text-red-700',
    title: 'text-red-900',
    badge: 'bg-red-700 text-white',
  },
}

const EmergencyCard = ({ alert }) => {
  const { dismissAlert, language } = useAppStore()
  const { t } = useTranslation(language)

  const severity = alert.severity || 'medium'
  const cfg = severityConfig[severity] || severityConfig.medium

  return (
    <motion.div
      initial={{ opacity: 0, y: -10, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.97 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      className={`rounded-2xl border-l-4 ${cfg.border} ${cfg.bg} p-4 shadow-md`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <AlertTriangle className={`w-5 h-5 mt-0.5 flex-shrink-0 ${cfg.icon}`} />
          <div className="flex-1 min-w-0">
            {/* Header */}
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <span className={`text-sm font-bold ${cfg.title}`}>
                {t.emergencyAlert}
              </span>
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${cfg.badge}`}>
                {t.severity?.[severity] || severity}
              </span>
            </div>

            {/* Message */}
            <p className={`text-sm leading-relaxed ${cfg.title} opacity-90`}>
              {alert.message}
            </p>

            {/* Action advice */}
            {t.severityAction?.[severity] && (
              <div className="flex items-center gap-1.5 mt-2 text-xs font-medium opacity-80">
                <ChevronRight className="w-3.5 h-3.5" />
                {t.severityAction[severity]}
              </div>
            )}

            {/* Call button for critical */}
            {(severity === 'critical' || severity === 'high') && (
              <a
                href="tel:108"
                className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 bg-red-600 text-white text-xs font-semibold rounded-xl hover:bg-red-700 transition-colors"
              >
                <Phone className="w-3.5 h-3.5" />
                {language === 'hi' ? '108 कॉल करें' : 'Call 108 Emergency'}
              </a>
            )}
          </div>
        </div>

        {/* Dismiss */}
        <button
          onClick={() => dismissAlert(alert.id)}
          aria-label="Dismiss alert"
          className="flex-shrink-0 w-7 h-7 rounded-full bg-white/70 hover:bg-white flex items-center justify-center text-slate-500 hover:text-slate-700 transition-colors shadow-sm"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  )
}

const EmergencyAlerts = () => {
  const { emergencyAlerts } = useAppStore()

  return (
    <AnimatePresence>
      {emergencyAlerts.length > 0 && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="flex flex-col gap-2 overflow-hidden"
        >
          {emergencyAlerts.map((alert) => (
            <EmergencyCard key={alert.id} alert={alert} />
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export { EmergencyCard, EmergencyAlerts }
export default EmergencyAlerts
