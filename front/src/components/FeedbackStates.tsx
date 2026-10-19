import { Button } from './Button'

function SkeletonCard() {
  return (
    <div className="skeleton-card" aria-hidden="true">
      <span className="skeleton skeleton-title" />
      <span className="skeleton-badges"><span className="skeleton" /><span className="skeleton" /></span>
      <span className="skeleton skeleton-meta" />
    </div>
  )
}

export function SkeletonList({ count = 5 }: { count?: number }) {
  return <>{Array.from({ length: count }, (_, index) => <SkeletonCard key={index} />)}</>
}

export function EmptyState() {
  return (
    <div className="state-panel">
      <span className="state-mark">0</span>
      <h2>Nenhum incidente encontrado</h2>
      <p>Nenhum incidente encontrado com os filtros aplicados.</p>
    </div>
  )
}

export function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="state-panel error-state" role="alert">
      <span className="state-mark">!</span>
      <h2>Falha ao carregar incidentes</h2>
      <p>Não foi possível acessar os dados operacionais.</p>
      <Button variant="secondary" onClick={onRetry}>Tentar novamente</Button>
    </div>
  )
}
