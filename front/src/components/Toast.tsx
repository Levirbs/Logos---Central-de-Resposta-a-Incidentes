import { useEffect } from 'react'

export type ToastType = 'success' | 'error' | 'warning'

export function Toast({ type, message, onClose }: { type: ToastType; message: string; onClose: () => void }) {
  useEffect(() => {
    const timer = window.setTimeout(onClose, 4500)
    return () => window.clearTimeout(timer)
  }, [onClose])

  return (
    <div className={`toast toast-${type}`} role={type === 'success' ? 'status' : 'alert'}>
      <span className="toast-symbol">{type === 'success' ? '✓' : '!'}</span>
      <span>{message}</span>
      <button onClick={onClose} aria-label="Fechar notificação">×</button>
    </div>
  )
}
