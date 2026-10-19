import type { Incident, IncidentFilters, Status, VersionConflictBody } from '../types/incident'

const API_BASE = '/api/v1'

export type ApiErrorKind = 'conflict' | 'not_found' | 'validation' | 'server' | 'network' | 'aborted'

export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly status: number | null
  /** Presente apenas em conflitos de versão (HTTP 409). */
  readonly current: Incident | null

  constructor(kind: ApiErrorKind, message: string, options: { status?: number; current?: Incident } = {}) {
    super(message)
    this.name = 'ApiError'
    this.kind = kind
    this.status = options.status ?? null
    this.current = options.current ?? null
  }
}

export function isAbortError(error: unknown): boolean {
  return error instanceof ApiError && error.kind === 'aborted'
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function isVersionConflict(body: unknown): body is VersionConflictBody {
  return isRecord(body) && body.code === 'VERSION_CONFLICT' && isRecord(body.current) && typeof body.current.id === 'number'
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json()
  } catch {
    return null
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { Accept: 'application/json', ...(init.body ? { 'Content-Type': 'application/json' } : {}) },
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('aborted', 'Requisição cancelada.')
    }
    throw new ApiError('network', 'Não foi possível conectar ao servidor.')
  }

  if (response.ok) {
    try {
      return (await response.json()) as T
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new ApiError('aborted', 'Requisição cancelada.')
      }
      throw new ApiError('server', 'Resposta inválida do servidor.', { status: response.status })
    }
  }

  const body = await readJson(response)
  if (response.status === 409 && isVersionConflict(body)) {
    throw new ApiError('conflict', body.message, { status: 409, current: body.current })
  }
  if (response.status === 404) throw new ApiError('not_found', 'Incidente não encontrado.', { status: 404 })
  if (response.status === 422) throw new ApiError('validation', 'Dados inválidos.', { status: 422 })
  throw new ApiError('server', 'O servidor não conseguiu processar a requisição.', { status: response.status })
}

export function fetchIncidents(filters: IncidentFilters, signal?: AbortSignal): Promise<Incident[]> {
  const params = new URLSearchParams()
  if (filters.criticality) params.set('criticality', filters.criticality)
  if (filters.category) params.set('category', filters.category)
  if (filters.status) params.set('status', filters.status)
  const query = params.toString()
  return request<Incident[]>(`/incidents${query ? `?${query}` : ''}`, { signal })
}

export function patchIncidentStatus(id: number, status: Status, version: number, signal?: AbortSignal): Promise<Incident> {
  return request<Incident>(`/incidents/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ status, version }),
    signal,
  })
}
