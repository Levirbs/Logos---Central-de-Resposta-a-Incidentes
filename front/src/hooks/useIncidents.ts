import { useCallback, useEffect, useRef, useState } from 'react'
import { fetchIncidents, isAbortError } from '../api/client'
import type { Criticality, Category, Incident, Status } from '../types/incident'

export type ListPhase = 'loading' | 'ready' | 'error'
export type LoadResult = 'ok' | 'failed' | 'aborted'

type LoadMode = 'initial' | 'refresh'

export function useIncidents(criticality: Criticality | null, category: Category | null, status: Status | null) {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [phase, setPhase] = useState<ListPhase>('loading')
  const [refreshing, setRefreshing] = useState(false)
  const controllerRef = useRef<AbortController | null>(null)

  const load = useCallback(
    async (mode: LoadMode): Promise<LoadResult> => {
      controllerRef.current?.abort()
      const controller = new AbortController()
      controllerRef.current = controller

      // Troca de filtro e primeira carga mostram skeleton; "Atualizar" mantém a lista visível.
      if (mode === 'initial') {
        setPhase('loading')
        setRefreshing(false)
      } else {
        setRefreshing(true)
      }

      try {
        const data = await fetchIncidents({ criticality, category, status }, controller.signal)
        if (controller.signal.aborted) return 'aborted'
        setIncidents(data)
        setPhase('ready')
        return 'ok'
      } catch (error) {
        if (isAbortError(error) || controller.signal.aborted) return 'aborted'
        if (mode === 'initial') setPhase('error')
        return 'failed'
      } finally {
        if (controllerRef.current === controller) setRefreshing(false)
      }
    },
    [criticality, category, status],
  )

  useEffect(() => {
    void load('initial')
    return () => controllerRef.current?.abort()
  }, [load])

  const refresh = useCallback(() => load(phase === 'error' ? 'initial' : 'refresh'), [load, phase])
  const retry = useCallback(() => load('initial'), [load])

  const replaceIncident = useCallback(
    (updated: Incident) => {
      setIncidents((current) => {
        if (status !== null && updated.status !== status) {
          return current.filter((item) => item.id !== updated.id)
        }
        return current.map((item) => (item.id === updated.id ? updated : item))
      })
    },
    [status],
  )

  return { incidents, phase, refreshing, refresh, retry, replaceIncident }
}
