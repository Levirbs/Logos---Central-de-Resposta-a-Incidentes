import { Button } from './Button'

type Theme = 'light' | 'dark'

export function Header({
  theme,
  refreshing,
  onToggleTheme,
  onRefresh,
}: {
  theme: Theme
  refreshing: boolean
  onToggleTheme: () => void
  onRefresh: () => void
}) {
  return (
    <header className="app-header">
      <div className="header-inner">
        <div className="brand-lockup">
          <div className="brand-mark">L</div>
          <div>
            <div className="brand-name">Logos</div>
            <div className="brand-subtitle">Central de Resposta a Incidentes</div>
          </div>
        </div>
        <div className="header-actions">
          <span className="system-status"><span /> Operação normal</span>
          <Button variant="secondary" onClick={onRefresh} loading={refreshing} loadingLabel="Atualizando...">
            Atualizar
          </Button>
          <Button variant="ghost" onClick={onToggleTheme}>
            {theme === 'light' ? 'Modo escuro' : 'Modo claro'}
          </Button>
        </div>
      </div>
    </header>
  )
}

export function PageHeading({ count }: { count: number }) {
  return (
    <section className="page-heading">
      <div>
        <span className="eyebrow">Visão operacional</span>
        <h1>Incidentes</h1>
        <p>Triagem e priorização em tempo real</p>
      </div>
      <div className="incident-count">
        <strong>{count.toString().padStart(2, '0')}</strong>
        <span>na visualização</span>
      </div>
    </section>
  )
}
