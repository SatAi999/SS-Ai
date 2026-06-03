import { useCallback, useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import imageCompression from 'browser-image-compression'
import { voiceAPI, chatAPI, visionAPI } from '../services/api'
import useAppStore from '../store/useAppStore'

const COMPRESSION_OPTIONS = {
  maxSizeMB: 1,
  maxWidthOrHeight: 1024,
  useWebWorker: true,
}

const useConversation = () => {
  const {
    language,
    addMessage,
    setIsProcessing,
    setIsSpeaking,
    sessionId,
    setSessionId,
    uploadedImage,
    clearImage,
    addEmergencyAlert,
    addToHistory,
    messages,
  } = useAppStore()

  const audioRef = useRef(null)

  // ── Mutations ────────────────────────────────────────────────
  const transcribeMutation = useMutation({
    mutationFn: (blob) => voiceAPI.transcribe(blob, language),
  })

  const chatMutation = useMutation({
    mutationFn: (payload) => chatAPI.sendMessage(payload),
  })

  const visionMutation = useMutation({
    mutationFn: (fd) => visionAPI.analyzeImage(fd),
  })

  const ttsMutation = useMutation({
    mutationFn: (text) => voiceAPI.synthesize(text, language),
  })

  // ── Audio playback ───────────────────────────────────────────
  const stopAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setIsSpeaking(false)
    }
  }, [setIsSpeaking])

  const playTTS = useCallback(
    async (text) => {
      if (!text) return
      try {
        setIsSpeaking(true)
        const response = await ttsMutation.mutateAsync(text)
        const url = URL.createObjectURL(response.data)
        const audio = new Audio(url)
        audioRef.current = audio
        audio.onended = () => {
          setIsSpeaking(false)
          URL.revokeObjectURL(url)
        }
        audio.onerror = () => {
          setIsSpeaking(false)
          URL.revokeObjectURL(url)
        }
        await audio.play()
      } catch {
        setIsSpeaking(false)
      }
    },
    [ttsMutation, setIsSpeaking],
  )

  // ── Core send logic ──────────────────────────────────────────
  const sendToBackend = useCallback(
    async (text) => {
      let response
      if (uploadedImage) {
        let compressed = uploadedImage
        if (uploadedImage.size > 1024 * 1024) {
          compressed = await imageCompression(uploadedImage, COMPRESSION_OPTIONS)
        }
        const formData = new FormData()
        formData.append('image', compressed, compressed.name || 'image.jpg')
        formData.append('query', text)
        formData.append('language', language)
        if (sessionId) formData.append('session_id', sessionId)
        response = await visionMutation.mutateAsync(formData)
        clearImage()
      } else {
        response = await chatMutation.mutateAsync({
          message: text,
          language,
          session_id: sessionId || undefined,
        })
      }
      return response.data
    },
    [
      uploadedImage,
      language,
      sessionId,
      visionMutation,
      chatMutation,
      clearImage,
    ],
  )

  const handleResponse = useCallback(
    async (aiData) => {
      if (aiData.session_id && !sessionId) {
        setSessionId(aiData.session_id)
        localStorage.setItem('sehatsakhi-session-id', aiData.session_id)
      }
      if (aiData.emergency_alert) {
        addEmergencyAlert(aiData.emergency_alert)
      }
      addMessage({
        role: 'assistant',
        content: aiData.response,
        type: 'ai',
        severity: aiData.severity || null,
        suggestions: aiData.suggestions || [],
        agentUsed: aiData.agent_used,
      })
      await playTTS(aiData.response)
    },
    [sessionId, setSessionId, addEmergencyAlert, addMessage, playTTS],
  )

  const getErrorMessage = () =>
    language === 'hi'
      ? 'माफ़ कीजिए, कुछ गड़बड़ी हुई। कृपया दोबारा कोशिश करें।'
      : 'Sorry, something went wrong. Please try again.'

  // ── Voice input flow ─────────────────────────────────────────
  const processVoiceInput = useCallback(
    async (audioBlob) => {
      setIsProcessing(true)
      try {
        const txRes = await transcribeMutation.mutateAsync(audioBlob)
        const userText = (txRes.data.text || '').trim()
        if (!userText) {
          setIsProcessing(false)
          return
        }
        addMessage({ role: 'user', content: userText, type: 'voice' })
        const aiData = await sendToBackend(userText)
        await handleResponse(aiData)
      } catch {
        addMessage({ role: 'assistant', content: getErrorMessage(), type: 'error' })
      } finally {
        setIsProcessing(false)
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [language, sessionId, uploadedImage],
  )

  // ── Text input flow ──────────────────────────────────────────
  const processTextInput = useCallback(
    async (text) => {
      if (!text?.trim()) return
      setIsProcessing(true)
      addMessage({ role: 'user', content: text.trim(), type: 'text' })
      try {
        const aiData = await sendToBackend(text.trim())
        await handleResponse(aiData)
      } catch {
        addMessage({ role: 'assistant', content: getErrorMessage(), type: 'error' })
      } finally {
        setIsProcessing(false)
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [language, sessionId, uploadedImage],
  )

  // ── Save to history on session end ───────────────────────────
  const saveSession = useCallback(() => {
    if (messages.length > 0 && sessionId) {
      addToHistory({
        sessionId,
        messages: [...messages],
        timestamp: new Date().toISOString(),
        summary: messages.find((m) => m.role === 'user')?.content?.slice(0, 80) || '',
        language,
      })
    }
  }, [messages, sessionId, addToHistory, language])

  return {
    processVoiceInput,
    processTextInput,
    stopAudio,
    saveSession,
    isTranscribing: transcribeMutation.isPending,
    isChatting: chatMutation.isPending || visionMutation.isPending,
    isSynthesizing: ttsMutation.isPending,
  }
}

export default useConversation
