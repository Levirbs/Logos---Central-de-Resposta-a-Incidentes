import { CATEGORIES, CRITICALITIES, STATUSES, type Category, type Criticality, type Status } from '../types/incident'

export function FilterBar({
  criticality,
  category,
  status,
  onCriticalityChange,
  onCategoryChange,
  onStatusChange,
}: {
  criticality: Criticality | null
  category: Category | null
  status: Status | null
  onCriticalityChange: (value: Criticality | null) => void
  onCategoryChange: (value: Category | null) => void
  onStatusChange: (value: Status | null) => void
}) {
  return (
    <section className="filter-bar" aria-label="Filtros de incidentes">
      <div className="filter-group">
        <label htmlFor="criticality">Criticidade</label>
        <select
          id="criticality"
          value={criticality ?? ''}
          onChange={(event) => onCriticalityChange(CRITICALITIES.find((item) => item === event.target.value) ?? null)}
        >
          <option value="">Todos os níveis</option>
          {CRITICALITIES.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
      </div>
      <div className="filter-group category-filter">
        <label htmlFor="category">Categoria</label>
        <select
          id="category"
          value={category ?? ''}
          onChange={(event) => onCategoryChange(CATEGORIES.find((item) => item === event.target.value) ?? null)}
        >
          <option value="">Todas as categorias</option>
          {CATEGORIES.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
      </div>
      <div className="filter-group">
        <label htmlFor="status">Status</label>
        <select
          id="status"
          value={status ?? ''}
          onChange={(event) => onStatusChange(STATUSES.find((item) => item === event.target.value) ?? null)}
        >
          <option value="">Todos os status</option>
          {STATUSES.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
      </div>
    </section>
  )
}
