import { Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Header from './components/Header/Header'
import Home from './pages/Home/Home'
import VoiceChat from './pages/VoiceChat/VoiceChat'
import History from './pages/History/History'

function App() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-teal-50/30 to-emerald-50/20 bg-hero-pattern">
      <Header />
      <AnimatePresence mode="wait" initial={false}>
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<VoiceChat />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </AnimatePresence>
    </div>
  )
}

export default App
