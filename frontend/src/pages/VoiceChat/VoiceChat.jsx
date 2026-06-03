import { useRef, useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Plus, RotateCcw, X } from 'lucide-react'

import VoiceButton from '../../components/VoiceButton/VoiceButton'
import ConversationBubble from '../../components/ConversationBubble/ConversationBubble'
import WaveformAnimation from '../../components/WaveformAnimation/WaveformAnimation'
import EmergencyAlerts from '../../components/EmergencyCard/EmergencyCard'
import ImageUpload from '../../components/ImageUpload/ImageUpload'

import useVoiceRecorder from '../../hooks/useVoiceRecorder'
import useConversation from '../../hooks/useConversation'
import useAppStore from '../../store/useAppStore'
import { useTranslation } from '../../i18n/translations'

const PAGE_VARIANTS = {
  initial: { opacity: 0, x: 30 },
  animate: { opacity: 1, x: 0, transition: { duration: 0.35, ease: 'easeOut' } },
  exit: { opacity: 0, x: -20, transition: { duration: 0.2 } },
}

const VoiceChat = () => {
  const {
    messages,
    isListening,
    isProcessing,
    isSpeaking,
    setIsListening,
    clearMessages,
    clearSession,
    language,
    uploadedImage,
  } = useAppStore()

  const { t } = useTranslation(language)
  const { processVoiceInput, processTextInput, stopAudio, saveSession, isTranscribing } =
    useConversation()

  const { isRecording, audioBlob, error: micError, audioLevel, startRecording, stopRecording, clearAudio } =
    useVoiceRecorder()

  const [textInput, setTextInput] = useState('')
  const [showImageUpload, setShowImageUpload] = useState(false)
  const messagesEndRef = useRef(null)
  const textRef = useRef(null)

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isProcessing])

  // Process audio blob when recording stops
  useEffect(() => {
    if (audioBlob && !isRecording) {
      processVoiceInput(audioBlob)
      clearAudio()
      setIsListening(false)
    }
  }, [audioBlob, isRecording]) // eslint-disable-line

  const handleVoiceToggle = () => {
    if (isSpeaking) {
      stopAudio()
      return
    }
    if (isRecording) {
      stopRecording()
      setIsListening(false)
    } else {
      startRecording()
      setIsListening(true)
    }
  }

  const handleSendText = () => {
    if (!textInput.trim() || isProcessing) return
    processTextInput(textInput.trim())
    setTextInput('')
    textRef.current?.focus()
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendText()
    }
  }

  const handleNewSession = () => {
    saveSession()
    clearMessages()
    clearSession()
    setShowImageUpload(false)
    stopAudio()
  }

  const isInputDisabled = isProcessing || isTranscribing

  return (
    <motion.div
      variants={PAGE_VARIANTS}
      initial="initial"
      animate="animate"
      exit="exit"
      className="flex flex-col h-[calc(100vh-56px)] max-w-2xl mx-auto"
    >
      {/* ── Top bar ──────────────────────────────────── */}
      <div className="flex-shrink-0 px-4 pt-3 pb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-slate-500 font-medium">
            {language === 'hi' ? 'परामर्श सत्र' : 'Consultation Session'}
          </span>
        </div>
        <button
          onClick={handleNewSession}
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg px-2.5 py-1.5 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          {t.newSession}
        </button>
      </div>

      {/* ── Emergency alerts ──────────────────────────── */}
      <div className="flex-shrink-0 px-4 pb-2">
        <EmergencyAlerts />
      </div>

      {/* ── Conversation area ─────────────────────────── */}
      <div className="flex-1 overflow-y-auto scrollbar-hide px-4 py-2 flex flex-col gap-3">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center h-full gap-4 text-center py-8"
          >
            <div className="w-16 h-16 rounded-3xl bg-gradient-to-br from-primary-100 to-emerald-100 flex items-center justify-center">
              <span className="text-3xl">👋</span>
            </div>
            <div>
              <p className="text-base font-semibold text-slate-700">
                {language === 'hi'
                  ? 'नमस्ते! मैं सेहत सखी हूं'
                  : 'Hello! I\'m SehatSakhi'}
              </p>
              <p className="text-sm text-slate-500 mt-1 max-w-xs">
                {language === 'hi'
                  ? 'बोलने के लिए माइक्रोफ़ोन दबाएं, या नीचे लिखें।'
                  : 'Press the microphone to speak, or type below.'}
              </p>
            </div>
          </motion.div>
        )}

        {messages.map((msg) => (
          <ConversationBubble key={msg.id} message={msg} />
        ))}

        {/* Typing indicator */}
        {(isProcessing || isTranscribing) && (
          <ConversationBubble isTyping />
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* ── Image preview strip (if image uploaded) ──── */}
      <AnimatePresence>
        {uploadedImage && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="flex-shrink-0 px-4 pb-1 overflow-hidden"
          >
            <div className="bg-primary-50 border border-primary-200 rounded-xl px-3 py-2 flex items-center gap-2">
              <span className="text-xs text-primary-700 font-medium flex-1">
                {t.analyzeImageLabel}
              </span>
              <button
                onClick={() => useAppStore.getState().clearImage()}
                className="text-primary-500 hover:text-red-500"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Image upload panel (collapsible) ─────────── */}
      <AnimatePresence>
        {showImageUpload && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="flex-shrink-0 px-4 pb-2 overflow-hidden"
          >
            <ImageUpload />
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Bottom controls ───────────────────────────── */}
      <div className="flex-shrink-0 px-4 pt-2 pb-5 space-y-3">
        {/* Waveform */}
        <div className="flex justify-center h-8">
          <WaveformAnimation
            isActive={isRecording || isSpeaking}
            audioLevel={audioLevel}
            color={isSpeaking ? 'bg-emerald-500' : 'bg-red-400'}
          />
        </div>

        {/* Mic error */}
        {micError && (
          <p className="text-center text-xs text-red-500">{micError}</p>
        )}

        {/* Voice button + image toggle */}
        <div className="flex items-center justify-center gap-6">
          {/* Image upload shortcut */}
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={() => setShowImageUpload((v) => !v)}
            className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-colors ${
              showImageUpload
                ? 'bg-primary-100 text-primary-600'
                : 'bg-white border border-slate-200 text-slate-500 hover:border-primary-300 hover:text-primary-600'
            } shadow-sm`}
            aria-label={t.uploadImage}
          >
            <Plus className="w-5 h-5" />
          </motion.button>

          {/* Main voice button */}
          <VoiceButton
            onClick={handleVoiceToggle}
            disabled={isInputDisabled}
            size="lg"
          />

          {/* Placeholder spacer (symmetry) */}
          <div className="w-12 h-12" />
        </div>

        {/* Text input */}
        <div className="flex items-end gap-2">
          <textarea
            ref={textRef}
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isInputDisabled}
            placeholder={t.typeMessage}
            rows={1}
            className="flex-1 resize-none rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-100 transition-all disabled:opacity-50 scrollbar-hide"
            style={{ maxHeight: '100px', overflowY: 'auto' }}
          />
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={handleSendText}
            disabled={!textInput.trim() || isInputDisabled}
            className="w-11 h-11 rounded-2xl bg-primary-600 text-white flex items-center justify-center disabled:opacity-40 hover:bg-primary-700 transition-colors flex-shrink-0 shadow-md"
            aria-label={t.send}
          >
            <Send className="w-4 h-4" />
          </motion.button>
        </div>

        {/* Disclaimer */}
        <p className="text-center text-[10px] text-slate-400">
          {t.disclaimer}
        </p>
      </div>
    </motion.div>
  )
}

export default VoiceChat
