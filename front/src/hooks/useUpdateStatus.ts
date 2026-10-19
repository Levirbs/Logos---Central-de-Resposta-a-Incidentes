import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError, isAbortError, patchIncidentStatus } from '../api/client'
import type { Incident, Status } from '../types/incident'

export type UpdateStatusResult =
  | { kind: 'success'; incident: Incident }
  | { kind: 'conflict'; current: Incident }
  | { kind: 'error'; message: string }
  | { kind: 'aborted' }

export function useUpdateStatus() {
  const [saving, setSaving] = useState(false)
  const controllerRef = useRef<AbortController | null>(null)

  useEffect(() => () => controllerRef.current?.abort(), [])

  const updateStatus = useCallback(async (incident: Incident, status: Status): Promise<UpdateStatusResult> => {
    const controller = new AbortController()
    controllerRef.current = controller
    setSaving(true)
    try {
      const updated = await patchIncidentStatus(incident.id, status, incident.version, controller.signal)
      return { kind: 'success', incident: updated }
    } catch (error) {
      if (isAbortError(error)) return { kind: 'aborted' }
      if (error instanceof ApiError && error.kind === 'conflict' && error.current) {
        return { kind: 'conflict', current: error.current }
      }
      const message =
        error instanceof ApiError && error.kind === 'network'
          ? 'Sem conexão com o servidor. O status não foi alterado; tente novamente.'
          : 'Não foi possível salvar a alteração. Tente novamente.'
      return { kind: 'error', message }
    } finally {
      if (controllerRef.current === controller) setSaving(false)
    }
  }, [])

  return { saving, updateStatus }
}
