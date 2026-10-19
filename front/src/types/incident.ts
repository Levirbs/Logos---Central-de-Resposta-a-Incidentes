export const CATEGORIES = [
  'Acidente com Veículo',
  'Problema Mecânico',
  'Bloqueio de Pista',
  'Acidente com Vítimas',
  'Condição Climática Atípica na Pista',
] as const

export const CRITICALITIES = ['Alta', 'Média', 'Baixa'] as const

export const STATUSES = ['Aberto', 'Em Investigação', 'Fechado', 'Inconclusivo'] as const

export type Category = (typeof CATEGORIES)[number]
export type Criticality = (typeof CRITICALITIES)[number]
export type Status = (typeof STATUSES)[number]

export type Incident = {
  id: number
  code: string
  title: string
  description: string
  category: Category
  criticality: Criticality
  status: Status
  location: string
  reporter: string
  /** ISO 8601 em UTC. */
  created_at: string
  updated_at: string
  version: number
}

export type IncidentFilters = {
  criticality: Criticality | null
  category: Category | null
  status: Status | null
}

export type UpdateStatusPayload = {
  status: Status
  version: number
}

export type VersionConflictBody = {
  code: 'VERSION_CONFLICT'
  message: string
  current: Incident
}
