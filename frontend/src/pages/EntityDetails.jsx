import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search,
  Filter,
  Download,
  User,
  Phone,
  Building2,
  Truck,
  MapPin,
  Landmark,
  ArrowUpRight,
  TrendingUp,
  SlidersHorizontal,
} from 'lucide-react'
import { getEntities, getEntityById } from '../api/entityApi'
import EntityInspector from '../components/evidence/EntityInspector'
import { useToast } from '../context/ToastContext'
import { DetectiveBadge } from '../components/common/DetectiveLogos'

const typeIconMap = {
  Person: User,
  Phone: Phone,
  Organization: Building2,
  Vehicle: Truck,
  Location: MapPin,
  BankAccount: Landmark,
}

export default function EntityDetails() {
  const [entities, setEntities] = useState([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('')
  const [selectedEntity, setSelectedEntity] = useState(null)
  const { addToast } = useToast()
  const navigate = useNavigate()

  useEffect(() => {
    setIsLoading(true)
    getEntities({
      q: searchQuery || undefined,
      type: selectedType || undefined,
      limit: 100,
    })
      .then(res => {
        setEntities(res.data.entities)
        setTotal(res.data.total)
        setIsLoading(false)
      })
      .catch(err => {
        console.error('Failed to load entities:', err)
        setIsLoading(false)
      })
  }, [searchQuery, selectedType])

  const handleInspect = async id => {
    try {
      const res = await getEntityById(id)
      setSelectedEntity(res.data.entity)
    } catch (e) {
      addToast('Failed to load dossier', 'error')
    }
  }

  const handleExportCSV = () => {
    const headers = 'ID,Name,Type,Role,RiskScore,CommunityID\n'
    const rows = entities
      .map(
        e =>
          `"${e.id}","${e.name || ''}","${e.type || ''}","${e.role || ''}",${e.risk_score || 0},${
            e.community_id || ''
          }`
      )
      .join('\n')
    const blob = new Blob([headers + rows], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `VERITAS_Entities_${Date.now()}.csv`
    a.click()
    addToast('Entities exported to CSV', 'success')
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-subtle/80 pb-6">
        <div className="flex items-start gap-4">
          <DetectiveBadge className="w-11 h-13 text-accent-violet shrink-0 hidden sm:block shadow-xs" />
          <div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-accent-violet block mb-1 font-mono">
              FORENSIC DIRECTORY // CENTRAL SUSPECT REPOSITORY
            </span>
            <h1 className="font-display font-bold text-2xl sm:text-3xl text-primary tracking-tight">
              Suspects & Entities Registry
            </h1>
            <p className="text-xs sm:text-sm text-secondary mt-1 max-w-2xl leading-relaxed">
              Explore entities discovered across criminal investigation dossiers, phone intercepts, and financial ledgers.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleExportCSV}
            className="px-3.5 py-2 rounded-control bg-surface border border-subtle text-xs text-secondary hover:text-primary transition-colors flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter / Search Bar */}
      <div className="p-4 rounded-card bg-surface border border-subtle shadow-soft space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="relative flex-1 min-w-[260px]">
            <Search className="w-3.5 h-3.5 text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by name, ID, role, or alias..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full text-xs pl-9 pr-4 py-2 rounded-control bg-surface-secondary border border-subtle text-primary placeholder:text-secondary focus:outline-none focus:border-accent-violet font-medium transition-colors"
            />
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-secondary px-2 font-mono">
              Showing <strong className="text-primary font-bold">{entities.length}</strong> of {total} records
            </span>
          </div>
        </div>

        {/* Quick Category Filter Chips */}
        <div className="flex items-center gap-1.5 overflow-x-auto pt-1 border-t border-subtle/60 text-xs">
          <span className="text-[10px] font-semibold text-secondary uppercase tracking-wider mr-1 shrink-0">
            Filter:
          </span>
          {[
            { id: '', label: 'All Entities' },
            { id: 'Person', label: 'Person' },
            { id: 'Phone', label: 'Phone' },
            { id: 'Organization', label: 'Organization' },
            { id: 'Vehicle', label: 'Vehicle' },
            { id: 'Location', label: 'Location' },
            { id: 'BankAccount', label: 'BankAccount' },
          ].map(chip => (
            <button
              key={chip.id}
              onClick={() => setSelectedType(chip.id)}
              className={`px-2.5 py-1 rounded-control text-[11px] font-medium transition-all shrink-0 border ${
                selectedType === chip.id
                  ? 'bg-accent-violet/10 border-accent-violet/40 text-accent-violet font-semibold'
                  : 'bg-surface-secondary/60 border-transparent text-secondary hover:text-primary hover:bg-surface-secondary'
              }`}
            >
              {chip.label}
            </button>
          ))}
        </div>
      </div>

      {/* Directory Table */}
      <div className="rounded-card bg-surface border border-subtle shadow-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-secondary/70 border-b border-subtle text-[10px] uppercase font-semibold text-secondary tracking-wider">
              <tr>
                <th className="py-3 px-4">Entity</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Role / Title</th>
                <th className="py-3 px-4">Cell Cluster</th>
                <th className="py-3 px-4">Analytical Risk</th>
                <th className="py-3 px-4">Signal</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-subtle/60 text-secondary">
              {isLoading ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-secondary">
                    <span className="w-5 h-5 border-2 border-accent-violet border-t-transparent rounded-full animate-spin inline-block mr-2 align-middle" />
                    Querying entity database...
                  </td>
                </tr>
              ) : entities.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-secondary">
                    No entities match these filters. Try a broader search.
                  </td>
                </tr>
              ) : (
                entities.map(ent => {
                  const Icon = typeIconMap[ent.type] || User
                  return (
                    <tr
                      key={ent.id}
                      onClick={() => handleInspect(ent.id)}
                      className="hover:bg-surface-secondary/40 cursor-pointer transition-colors"
                    >
                      {/* Entity Name & ID */}
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-control bg-surface-secondary border border-subtle flex items-center justify-center text-primary shrink-0">
                            <Icon className="w-3.5 h-3.5" />
                          </div>
                          <div>
                            <span className="font-semibold text-primary block leading-tight">
                              {ent.name}
                            </span>
                            <span className="font-mono text-[10px] text-secondary">
                              {ent.id}
                            </span>
                          </div>
                        </div>
                      </td>

                      {/* Type */}
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-surface-secondary border border-subtle text-primary">
                          {ent.type}
                        </span>
                      </td>

                      {/* Role */}
                      <td className="py-3 px-4 text-primary font-medium">
                        {ent.role || '—'}
                      </td>

                      {/* Community */}
                      <td className="py-3 px-4">
                        {ent.community_id ? (
                          <span className="text-accent-violet font-semibold">
                            Cell {ent.community_id}
                          </span>
                        ) : (
                          'General'
                        )}
                      </td>

                      {/* Analytical Risk with Micro-Meter */}
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-primary tabular-nums">
                            {ent.risk_score}
                          </span>
                          <div className="w-12 bg-subtle/50 h-1.5 rounded-full overflow-hidden hidden sm:block">
                            <div
                              className={`h-full rounded-full transition-all duration-300 ${
                                ent.risk_score >= 85
                                  ? 'bg-accent-coral'
                                  : ent.risk_score >= 60
                                  ? 'bg-accent-amber'
                                  : 'bg-accent-emerald'
                              }`}
                              style={{ width: `${ent.risk_score}%` }}
                            />
                          </div>
                        </div>
                      </td>

                      {/* Signal */}
                      <td className="py-3 px-4">
                        {ent.risk_score >= 85 ? (
                          <span className="px-2 py-0.5 rounded text-[10px] bg-accent-coral/10 text-accent-coral border border-accent-coral/20 font-medium inline-flex items-center gap-1">
                            <span className="w-1 h-1 rounded-full bg-accent-coral animate-pulse" />
                            Priority Focus
                          </span>
                        ) : ent.community_id === 2 ? (
                          <span className="px-2 py-0.5 rounded text-[10px] bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 font-medium inline-flex items-center gap-1">
                            <span className="w-1 h-1 rounded-full bg-accent-cyan" />
                            Financial Channel
                          </span>
                        ) : (
                          <span className="text-secondary text-[11px]">Monitored Link</span>
                        )}
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={e => {
                            e.stopPropagation()
                            navigate('/network')
                          }}
                          className="p-1.5 rounded-control text-secondary hover:text-accent-violet hover:bg-surface-secondary transition-colors"
                          title="View on Canvas"
                        >
                          <ArrowUpRight className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Inspector Modal if an entity is clicked */}
      {selectedEntity && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex justify-end">
          <EntityInspector
            entity={selectedEntity}
            onClose={() => setSelectedEntity(null)}
            onSelectEntity={id => handleInspect(id)}
            onExploreConnections={id => {
              setSelectedEntity(null)
              navigate('/network')
            }}
          />
        </div>
      )}
    </div>
  )
}
