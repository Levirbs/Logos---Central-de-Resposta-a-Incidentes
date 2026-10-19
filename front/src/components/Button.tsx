import type { ButtonHTMLAttributes } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost'
  loading?: boolean
  loadingLabel?: string
}

export function Button({
  variant = 'primary',
  loading = false,
  loadingLabel = 'Salvando...',
  disabled,
  children,
  className = '',
  ...props
}: ButtonProps) {
  return (
    <button className={`button button-${variant} ${className}`} disabled={loading || disabled} aria-busy={loading || undefined} {...props}>
      {loading ? <span className="button-loading"><span className="spinner" /> {loadingLabel}</span> : children}
    </button>
  )
}
