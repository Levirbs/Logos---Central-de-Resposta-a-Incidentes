import type { Criticality, Status } from '../types/incident'

export function CriticalityBadge({ value }: { value: Criticality }) {
  return <span className={`badge criticality criticality-${value.toLowerCase()}`}>{value}</span>
}

export function StatusBadge({ value }: { value: Status }) {
  // As classes CSS não têm acentos nem espaços: "Em Investigação" -> "em-investigacao".
  const key = value.toLowerCase().replace(' ', '-').replace('ç', 'c').replace('ã', 'a')
  return <span className={`badge status status-${key}`}>{value}</span>
}
