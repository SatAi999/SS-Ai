import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Mic,
  Eye,
  AlertTriangle,
  Languages,
  ArrowRight,
  Activity,
  Heart,
  Shield,
} from 'lucide-react'
import useAppStore from '../../store/useAppStore'
import { useTranslation } from '../../i18n/translations'

const PAGE_VARIANTS = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
  exit: { opacity: 0, y: -10, transition: { duration: 0.2 } },
}

const FEATURE_ICONS = {
  voice: Mic,
  vision: Eye,
  emergency: AlertTriangle,
  multilingual: Languages,
}

const FeatureCard = ({ featureKey, t, index }) => {
  const Icon = FEATURE_ICONS[featureKey]
  const feature = t.features?.[featureKey]

  const colors = [
    'bg-teal-50 text-teal-700 border-teal-200',
    'bg-violet-50 text-violet-700 border-violet-200',
    'bg-rose-50 text-rose-700 border-rose-200',
    'bg-amber-50 text-amber-700 border-amber-200',
  ]
  const iconColors = [
    'bg-teal-100 text-teal-600',
    'bg-violet-100 text-violet-600',
    'bg-rose-100 text-rose-600',
    'bg-amber-100 text-amber-600',
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 + index * 0.08 }}
      className={`rounded-2xl border p-4 flex items-start gap-3 ${colors[index]}`}
    >
      <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${iconColors[index]}`}>
        <Icon className="w-4.5 h-4.5" strokeWidth={2} />
      </div>
      <div>
        <p className="text-sm font-semibold">{feature?.title}</p>
        <p className="text-xs opacity-75 mt-0.5">{feature?.desc}</p>
      </div>
    </motion.div>
  )
}

const Home = () => {
  const { language } = useAppStore()
  const { t } = useTranslation(language)

  return (
    <motion.main
      variants={PAGE_VARIANTS}
      initial="initial"
      animate="animate"
      exit="exit"
      className="max-w-md mx-auto px-4 pt-6 pb-16"
    >
      {/* Hero */}
      <div className="text-center mb-10">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
          className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-emerald-500 rounded-3xl shadow-glow-teal mb-5"
        >
          <Activity className="w-10 h-10 text-white" strokeWidth={2} />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-3xl font-bold text-gradient mb-2"
        >
          {t.appName}
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.18 }}
          className="text-base font-medium text-slate-700"
        >
          {t.tagline}
        </motion.p>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.24 }}
          className="text-sm text-slate-500 mt-1.5 max-w-xs mx-auto leading-relaxed"
        >
          {t.taglineSub}
        </motion.p>
      </div>

      {/* CTA */}
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
        className="mb-8"
      >
        <Link to="/chat">
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            className="flex items-center justify-center gap-3 w-full py-4 bg-gradient-to-r from-primary-600 to-emerald-500 text-white font-bold text-lg rounded-2xl shadow-glow-teal"
          >
            <Mic className="w-5 h-5" />
            {t.startConsultation}
            <ArrowRight className="w-5 h-5" />
          </motion.div>
        </Link>

        <p className="text-center text-xs text-slate-400 mt-3">
          {t.disclaimer}
        </p>
      </motion.div>

      {/* Trust badges */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.35 }}
        className="flex justify-center gap-6 mb-8"
      >
        {[
          { icon: Heart, label: language === 'hi' ? 'सुरक्षित' : 'Safe', color: 'text-rose-500' },
          { icon: Shield, label: language === 'hi' ? 'विश्वसनीय' : 'Trusted', color: 'text-primary-600' },
          { icon: Mic, label: language === 'hi' ? 'आवाज़-प्रथम' : 'Voice-First', color: 'text-violet-500' },
        ].map(({ icon: Icon, label, color }) => (
          <div key={label} className="flex flex-col items-center gap-1">
            <Icon className={`w-5 h-5 ${color}`} />
            <span className="text-xs font-medium text-slate-500">{label}</span>
          </div>
        ))}
      </motion.div>

      {/* Feature grid */}
      <div className="grid grid-cols-2 gap-3 mb-8">
        {Object.keys(t.features || {}).map((key, i) => (
          <FeatureCard key={key} featureKey={key} t={t} index={i} />
        ))}
      </div>

      {/* History link */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="text-center"
      >
        <Link
          to="/history"
          className="text-sm text-primary-600 font-medium hover:underline inline-flex items-center gap-1"
        >
          {t.viewHistory}
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </motion.div>
    </motion.main>
  )
}

export default Home
