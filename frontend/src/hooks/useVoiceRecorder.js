import { useState, useRef, useCallback, useEffect } from 'react'

const PREFERRED_MIME = 'audio/webm;codecs=opus'
const FALLBACK_MIME = 'audio/webm'

const useVoiceRecorder = () => {
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState(null)
  const [error, setError] = useState(null)
  const [audioLevel, setAudioLevel] = useState(0)
  const [duration, setDuration] = useState(0)

  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const streamRef = useRef(null)
  const audioCtxRef = useRef(null)
  const analyzerRef = useRef(null)
  const animFrameRef = useRef(null)
  const durationTimerRef = useRef(null)

  const cleanup = useCallback(() => {
    cancelAnimationFrame(animFrameRef.current)
    clearInterval(durationTimerRef.current)
    streamRef.current?.getTracks().forEach((t) => t.stop())
    if (audioCtxRef.current?.state !== 'closed') {
      audioCtxRef.current?.close()
    }
    setAudioLevel(0)
  }, [])

  const startRecording = useCallback(async () => {
    try {
      setError(null)
      setAudioBlob(null)
      setDuration(0)
      chunksRef.current = []

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
          channelCount: 1,
        },
      })

      streamRef.current = stream

      // Audio level analyzer
      const audioCtx = new AudioContext()
      audioCtxRef.current = audioCtx
      const source = audioCtx.createMediaStreamSource(stream)
      const analyzer = audioCtx.createAnalyser()
      analyzer.fftSize = 256
      analyzer.smoothingTimeConstant = 0.8
      source.connect(analyzer)
      analyzerRef.current = analyzer

      const dataArray = new Uint8Array(analyzer.frequencyBinCount)
      const updateLevel = () => {
        analyzer.getByteFrequencyData(dataArray)
        const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length
        setAudioLevel(Math.min(avg / 128, 1))
        animFrameRef.current = requestAnimationFrame(updateLevel)
      }
      updateLevel()

      // Duration timer
      durationTimerRef.current = setInterval(() => {
        setDuration((d) => d + 1)
      }, 1000)

      const mimeType = MediaRecorder.isTypeSupported(PREFERRED_MIME)
        ? PREFERRED_MIME
        : FALLBACK_MIME

      const mediaRecorder = new MediaRecorder(stream, { mimeType })
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType })
        setAudioBlob(blob)
        cleanup()
      }
      mediaRecorder.onerror = (e) => {
        setError(`Recording error: ${e.error?.message || 'Unknown'}`)
        cleanup()
        setIsRecording(false)
      }

      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.start(100)
      setIsRecording(true)
    } catch (err) {
      const msg =
        err.name === 'NotAllowedError'
          ? 'Microphone access denied. Please allow microphone permissions.'
          : err.message || 'Failed to start recording'
      setError(msg)
    }
  }, [cleanup])

  const stopRecording = useCallback(() => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== 'inactive'
    ) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }, [])

  // Auto-stop after 60 seconds to prevent huge uploads
  useEffect(() => {
    if (duration >= 60 && isRecording) {
      stopRecording()
    }
  }, [duration, isRecording, stopRecording])

  useEffect(() => {
    return cleanup
  }, [cleanup])

  return {
    isRecording,
    audioBlob,
    error,
    audioLevel,
    duration,
    startRecording,
    stopRecording,
    clearAudio: () => setAudioBlob(null),
    clearError: () => setError(null),
  }
}

export default useVoiceRecorder
