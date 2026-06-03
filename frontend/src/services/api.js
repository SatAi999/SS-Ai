import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
  headers: {
    Accept: 'application/json',
  },
})

// ── Request interceptor ──────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const sessionId = localStorage.getItem('sehatsakhi-session-id')
    if (sessionId) {
      config.headers['X-Session-ID'] = sessionId
    }
    return config
  },
  (error) => Promise.reject(error),
)

// ── Response interceptor ─────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || 'Network error'
    console.error('[SehatSakhi API]', message)
    return Promise.reject(new Error(message))
  },
)

// ── Voice APIs ────────────────────────────────────────────────
export const voiceAPI = {
  transcribe: (audioBlob, language = 'en') => {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')
    formData.append('language', language)
    return api.post('/api/voice/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000,
    })
  },

  synthesize: (text, language = 'en') =>
    api.post(
      '/api/voice/synthesize',
      { text, language },
      { responseType: 'blob', timeout: 30000 },
    ),
}

// ── Chat APIs ─────────────────────────────────────────────────
export const chatAPI = {
  sendMessage: (payload) =>
    api.post('/api/chat/message', payload, { timeout: 45000 }),

  getSession: (sessionId) => api.get(`/api/sessions/${sessionId}`),

  createSession: (language = 'en') =>
    api.post('/api/sessions/create', { language }),
}

// ── Vision APIs ───────────────────────────────────────────────
export const visionAPI = {
  analyzeImage: (formData) =>
    api.post('/api/vision/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    }),
}

// ── Session APIs ──────────────────────────────────────────────
export const sessionAPI = {
  getHistory: (page = 1, limit = 20) =>
    api.get(`/api/sessions/history?page=${page}&limit=${limit}`),

  getSession: (sessionId) => api.get(`/api/sessions/${sessionId}`),
}

// ── Health API ────────────────────────────────────────────────
export const healthAPI = {
  check: () => api.get('/api/health'),
}

export default api
