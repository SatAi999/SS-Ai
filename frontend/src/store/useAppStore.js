import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useAppStore = create(
  persist(
    (set, get) => ({
      // ── Language ─────────────────────────────────────
      language: 'en',
      setLanguage: (lang) => set({ language: lang }),

      // ── Session ──────────────────────────────────────
      sessionId: null,
      setSessionId: (id) => set({ sessionId: id }),
      clearSession: () => set({ sessionId: null, messages: [] }),

      // ── Conversation messages ─────────────────────────
      messages: [],
      addMessage: (message) =>
        set((state) => ({
          messages: [
            ...state.messages,
            {
              ...message,
              id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
              timestamp: new Date().toISOString(),
            },
          ],
        })),
      clearMessages: () => set({ messages: [] }),

      // ── Voice UI state ────────────────────────────────
      isListening: false,
      isSpeaking: false,
      isProcessing: false,
      setIsListening: (val) => set({ isListening: val }),
      setIsSpeaking: (val) => set({ isSpeaking: val }),
      setIsProcessing: (val) => set({ isProcessing: val }),

      // ── Image ─────────────────────────────────────────
      uploadedImage: null,
      imagePreview: null,
      setUploadedImage: (file, preview) =>
        set({ uploadedImage: file, imagePreview: preview }),
      clearImage: () => set({ uploadedImage: null, imagePreview: null }),

      // ── Emergency alerts ──────────────────────────────
      emergencyAlerts: [],
      addEmergencyAlert: (alert) =>
        set((state) => ({
          emergencyAlerts: [
            ...state.emergencyAlerts,
            {
              ...alert,
              id: `alert-${Date.now()}`,
              timestamp: new Date().toISOString(),
            },
          ],
        })),
      dismissAlert: (id) =>
        set((state) => ({
          emergencyAlerts: state.emergencyAlerts.filter((a) => a.id !== id),
        })),
      clearAlerts: () => set({ emergencyAlerts: [] }),

      // ── Conversation history (persisted) ─────────────
      conversationHistory: [],
      addToHistory: (conversation) =>
        set((state) => ({
          conversationHistory: [
            conversation,
            ...state.conversationHistory,
          ].slice(0, 50),
        })),
      clearHistory: () => set({ conversationHistory: [] }),
    }),
    {
      name: 'sehatsakhi-storage',
      partialize: (state) => ({
        language: state.language,
        conversationHistory: state.conversationHistory,
      }),
    },
  ),
)

export default useAppStore
