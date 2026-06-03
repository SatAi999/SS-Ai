import { motion } from 'framer-motion'

const BAR_COUNT = 9

const WaveformAnimation = ({
  isActive = false,
  audioLevel = 0,
  color = 'bg-primary-500',
  height = 'h-8',
}) => {
  if (!isActive) return null

  return (
    <motion.div
      initial={{ opacity: 0, scaleY: 0.5 }}
      animate={{ opacity: 1, scaleY: 1 }}
      exit={{ opacity: 0, scaleY: 0.5 }}
      className={`flex items-center justify-center gap-[3px] ${height}`}
    >
      {Array.from({ length: BAR_COUNT }).map((_, i) => {
        // Center bars slightly taller
        const baseDelay = Math.abs(i - Math.floor(BAR_COUNT / 2)) * 80
        const levelBoost = audioLevel > 0.1 ? 1 + audioLevel * 1.5 : 1

        return (
          <motion.div
            key={i}
            className={`w-1 rounded-full ${color}`}
            animate={{
              scaleY: isActive
                ? [0.3, levelBoost, 0.3]
                : [0.3],
            }}
            transition={{
              duration: 0.9,
              repeat: Infinity,
              delay: baseDelay / 1000,
              ease: 'easeInOut',
            }}
            style={{ height: '100%', transformOrigin: 'bottom' }}
          />
        )
      })}
    </motion.div>
  )
}

export default WaveformAnimation
