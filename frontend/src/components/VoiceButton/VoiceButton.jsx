import { motion, AnimatePresence } from 'framer-motion'
import { Mic, Square, Loader2, Volume2 } from 'lucide-react'
import useAppStore from '../../store/useAppStore'
import { useTranslation } from '../../i18n/translations'

const stateConfig = {
  idle: {
    bg: 'bg-gradient-to-br from-primary-500 to-primary-700',
    shadow: 'shadow-glow-teal',
    icon: Mic,
    pulse: false,
    rings: false,
  },
  listening: {
    bg: 'bg-gradient-to-br from-red-500 to-rose-600',
    shadow: 'shadow-glow-red',
    icon: Square,
    pulse: true,
    rings: true,
  },
  processing: {
    bg: 'bg-gradient-to-br from-amber-400 to-orange-500',
    shadow: 'shadow-lg',
    icon: Loader2,
    pulse: false,
    rings: false,
  },
  speaking: {
    bg: 'bg-gradient-to-br from-emerald-500 to-teal-600',
    shadow: 'shadow-glow-green',
    icon: Volume2,
    pulse: true,
    rings: false,
  },
}

const VoiceButton = ({ onClick, disabled = false, size = 'lg' }) => {
  const { isListening, isProcessing, isSpeaking, language } = useAppStore()
  const { t } = useTranslation(language)

  const state = isListening
    ? 'listening'
    : isProcessing
    ? 'processing'
    : isSpeaking
    ? 'speaking'
    : 'idle'

  const config = stateConfig[state]
  const Icon = config.icon

  const sizeClass = size === 'lg' ? 'w-24 h-24' : 'w-16 h-16'
  const iconSize = size === 'lg' ? 'w-9 h-9' : 'w-6 h-6'

  const labelMap = {
    idle: t.tapToSpeak,
    listening: t.listening,
    processing: t.processing,
    speaking: t.speaking,
  }

  return (
    <div className="flex flex-col items-center gap-3 select-none">
      <div className="relative flex items-center justify-center">
        {/* Ripple rings */}
        <AnimatePresence>
          {config.rings && (
            <>
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className={`absolute rounded-full ${config.bg} opacity-20`}
                  style={{
                    width: `${(i + 2) * 48}px`,
                    height: `${(i + 2) * 48}px`,
                  }}
                  initial={{ scale: 0.8, opacity: 0.3 }}
                  animate={{ scale: 1.4 + i * 0.3, opacity: 0 }}
                  transition={{
                    duration: 1.8,
                    repeat: Infinity,
                    delay: i * 0.5,
                    ease: 'easeOut',
                  }}
                />
              ))}
            </>
          )}
        </AnimatePresence>

        {/* Main button */}
        <motion.button
          onClick={onClick}
          disabled={disabled || isProcessing || isSpeaking}
          aria-label={labelMap[state]}
          whileHover={
            !disabled && state === 'idle'
              ? { scale: 1.06 }
              : undefined
          }
          whileTap={!disabled ? { scale: 0.94 } : undefined}
          animate={
            config.pulse
              ? { scale: [1, 1.04, 1], transition: { repeat: Infinity, duration: 1.2 } }
              : { scale: 1 }
          }
          className={`
            relative z-10 ${sizeClass} rounded-full
            ${config.bg} ${config.shadow}
            flex items-center justify-center
            transition-all duration-300
            disabled:opacity-60 disabled:cursor-not-allowed
            focus:outline-none focus:ring-4 focus:ring-primary-300
          `}
        >
          <Icon
            className={`${iconSize} text-white ${state === 'processing' ? 'animate-spin' : ''}`}
            strokeWidth={2.2}
          />
        </motion.button>
      </div>

      {/* State label */}
      <AnimatePresence mode="wait">
        <motion.p
          key={state}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.2 }}
          className="text-sm font-medium text-slate-500 tracking-wide"
        >
          {labelMap[state]}
        </motion.p>
      </AnimatePresence>
    </div>
  )
}

export default VoiceButton
