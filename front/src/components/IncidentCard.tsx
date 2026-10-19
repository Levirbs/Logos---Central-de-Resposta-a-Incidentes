import type { Incident } from '../types/incident'
import { CriticalityBadge, StatusBadge } from './Badges'

const cardDateFormat = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
})

export function IncidentCard({ incident, onClick }: { incident: Incident; onClick: () => void }) {
  return (
    <button className={`incident-card ${incident.criticality === 'Alta' ? 'is-high' : ''}`} onClick={onClick}>
      <span className="severity-rail" aria-hidden="true" />
      <span className="incident-main">
        <span className="incident-topline">
          <span className="incident-category">{incident.category}</span>
          <span className="incident-badges">
            <CriticalityBadge value={incident.criticality} />
            <StatusBadge value={incident.status} />
          </span>
        </span>
        <span className="incident-meta">
          <strong>#{incident.code}</strong>
          <span>{cardDateFormat.format(new Date(incident.created_at))}</span>
          <span className="location">{incident.location}</span>
        </span>
      </span>
      <span className="card-action" aria-hidden="true">Ver detalhes</span>
    </button>
  )
}
