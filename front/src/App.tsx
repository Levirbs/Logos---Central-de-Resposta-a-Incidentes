import { useCallback, useState } from 'react'
import { EmptyState, ErrorState, SkeletonList } from './components/FeedbackStates'
import { FilterBar } from './components/FilterBar'
import { Header, PageHeading } from './components/Header'
import { IncidentCard } from './components/IncidentCard'
import { StatusModal } from './components/StatusModal'
import { Toast, type ToastType } from './components/Toast'
import { useIncidents } from './hooks/useIncidents'
import { useUpdateStatus } from './hooks/useUpdateStatus'
import type { Category, Criticality, Status } from './types/incident'

type ToastState = { id: number; type: ToastType; message: string }

export default function App() {
  const [criticality, setCriticality] = useState<Criticality | null>(null)
  const [category, setCategory] = useState<Category | null>(null)
  const [statusFilter, setStatusFilter] = useState<Status | null>('Aberto')
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  const [toast, setToast] = useState<ToastState | null>(null)

  const { incidents, phase, refreshing, refresh, retry, replaceIncident } = useIncidents(
    criticality,
    category,
    statusFilter,
  )
  const { saving, updateStatus } = useUpdateStatus()

  // Derivado da lista para que o modal sempre envie a versão mais recente conhecida.
  const selected = incidents.find((incident) => incident.id === selectedId) ?? null

  const closeModal = useCallback(() => setSelectedId(null), [])
  const closeToast = useCallback(() => setToast(null), [])
  const showToast = useCallback((type: ToastType, message: string) => setToast({ id: Date.now(), type, message }), [])

  async function handleSave(status: Status) {
    if (!selected) return
    const result = await updateStatus(selected, status)
    switch (result.kind) {
      case 'success':
        replaceIncident(result.incident)
        setSelectedId(null)
        showToast('success', 'Status atualizado com sucesso')
        break
      case 'conflict':
        // O servidor devolve o estado atual; a lista passa a refleti-lo sem novo GET.
        replaceIncident(result.current)
        setSelectedId(null)
        showToast('warning', 'Incidente atualizado por outro analista. Os dados foram atualizados.')
        break
      case 'error':
        showToast('error', result.message)
        break
      case 'aborted':
        break
    }
  }

  async function handleRefresh() {
    const result = await refresh()
    if (result === 'failed') showToast('error', 'Não foi possível atualizar a lista. Tente novamente.')
  }

  return (
    <div className={theme === 'dark' ? 'app dark' : 'app'}>
      <Header
        theme={theme}
        refreshing={refreshing}
        onToggleTheme={() => setTheme(theme === 'light' ? 'dark' : 'light')}
        onRefresh={handleRefresh}
      />

      <main>
        <PageHeading count={phase === 'ready' ? incidents.length : 0} />

        <FilterBar
          criticality={criticality}
          category={category}
          status={statusFilter}
          onCriticalityChange={setCriticality}
          onCategoryChange={setCategory}
          onStatusChange={setStatusFilter}
        />

        <div className="list-toolbar">
          <div>
            <span className="live-dot" />
            <strong>Fila ativa</strong>
            <span>Ordenada por criticidade e antiguidade</span>
          </div>
        </div>

        <section className="incident-list" aria-live="polite" aria-busy={phase === 'loading'}>
          {phase === 'loading' && <SkeletonList />}
          {phase === 'error' && <ErrorState onRetry={retry} />}
          {phase === 'ready' && incidents.length === 0 && <EmptyState />}
          {phase === 'ready' &&
            incidents.map((incident) => (
              <IncidentCard key={incident.id} incident={incident} onClick={() => setSelectedId(incident.id)} />
            ))}
        </section>
      </main>

      {selected && (
        <StatusModal key={selected.id} incident={selected} saving={saving} onClose={closeModal} onSave={handleSave} />
      )}
      {toast && <Toast key={toast.id} type={toast.type} message={toast.message} onClose={closeToast} />}
    </div>
  )
}
