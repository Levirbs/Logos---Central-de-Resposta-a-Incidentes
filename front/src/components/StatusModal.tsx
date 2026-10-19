import { useEffect, useState } from 'react'
import { STATUSES, type Incident, type Status } from '../types/incident'
import { CriticalityBadge, StatusBadge } from './Badges'
import { Button } from './Button'

const detailDateFormat = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

export function StatusModal({
  incident,
  saving,
  onClose,
  onSave,
}: {
  incident: Incident
  saving: boolean
  onClose: () => void
  onSave: (status: Status) => void
}) {
  const [status, setStatus] = useState<Status>(incident.status)
  const unchanged = status === incident.status

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !saving) onClose()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose, saving])

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && !saving && onClose()}>
      <section className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <header className="modal-header">
          <div>
            <span className="eyebrow">#{incident.code}</span>
            <h2 id="modal-title">Detalhes do Incidente</h2>
          </div>
          <Button variant="ghost" onClick={onClose} disabled={saving} aria-label="Fechar modal">Fechar</Button>
        </header>

        <div className="modal-body">
          <div className="modal-badges">
            <CriticalityBadge value={incident.criticality} />
            <StatusBadge value={incident.status} />
          </div>
          <dl className="details-grid">
            <div className="detail-wide"><dt>Título</dt><dd>{incident.title}</dd></div>
            <div className="detail-wide"><dt>Categoria</dt><dd>{incident.category}</dd></div>
            <div><dt>Data e hora</dt><dd>{detailDateFormat.format(new Date(incident.created_at))}</dd></div>
            <div><dt>Origem</dt><dd>{incident.reporter}</dd></div>
            <div className="detail-wide"><dt>Localização</dt><dd>{incident.location}</dd></div>
            <div className="detail-wide"><dt>Descrição</dt><dd>{incident.description}</dd></div>
          </dl>

          <fieldset className="status-fieldset" disabled={saving}>
            <legend>Novo status</legend>
            <div className="radio-list">
              {STATUSES.map((option) => (
                <label key={option} className={`radio-option ${status === option ? 'selected' : ''}`}>
                  <input type="radio" name="status" value={option} checked={status === option} onChange={() => setStatus(option)} />
                  <span>{option}</span>
                </label>
              ))}
            </div>
          </fieldset>
        </div>

        <footer className="modal-footer">
          <Button variant="secondary" onClick={onClose} disabled={saving}>Cancelar</Button>
          <Button onClick={() => onSave(status)} loading={saving} disabled={unchanged}>Salvar alteração</Button>
        </footer>
      </section>
    </div>
  )
}
