import React, { createContext, useContext, useState, useCallback } from 'react'
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react'

const ToastContext = createContext()

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now() + Math.random()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 3500)
  }, [])

  const removeToast = useCallback(id => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      {/* Toast Notification Container */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
        {toasts.map(toast => (
          <div
            key={toast.id}
            className="pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-card bg-surface border border-subtle shadow-card text-primary text-sm transition-all duration-200 animate-in fade-in slide-in-from-bottom-2"
          >
            {toast.type === 'success' && <CheckCircle2 className="w-4 h-4 text-accent-emerald shrink-0" />}
            {toast.type === 'error' && <AlertCircle className="w-4 h-4 text-accent-red shrink-0" />}
            {toast.type === 'info' && <Info className="w-4 h-4 text-accent-violet shrink-0" />}
            <span className="font-medium">{toast.message}</span>
            <button
              onClick={() => removeToast(toast.id)}
              className="ml-2 text-secondary hover:text-primary transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}
