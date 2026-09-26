import React from 'react'
import {
  X,
  User,
  Phone,
  Building2,
  Truck,
  MapPin,
  Landmark,
  Calendar,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  ShieldAlert,
} from 'lucide-react'

const typeIconMap = {
  Person: User,
  Phone: Phone,
  Organization: Building2,
  Vehicle: Truck,
  Location: MapPin,
  BankAccount: Landmark,
  Event: Calendar,
}

export default function EntityInspector({ entity, onClose, onSelectEntity, onExploreConnections }) {
  if (!entity) return null

  const Icon = typeIconMap[entity.type] || User
  const [copied, setCopied] = React.useState(false)

  const handleCopyId = () => {
    if (entity.id) {
      navigator.clipboard?.writeText(entity.id)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    }
  }

  const betweennessScore = typeof entity.betweenness === 'number' ? entity.betweenness : 0
  const pagerankScore = typeof entity.pagerank === 'number' ? entity.pagerank : 0

  return (
    <div className="w-80 sm:w-96 border-l border-subtle bg-surface flex flex-col h-full shadow-drawer animate-in slide-in-from-right-4 duration-200 z-10 select-none">
      {/* Editorial Classification Banner */}
      <div className="px-5 py-2 border-b border-subtle/80 bg-surface-secondary/60 flex items-center justify-between text-[10px] text-secondary">
        <span className="font-mono uppercase tracking-widest text-[9px] font-semibold text-secondary/90 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald animate-pulse" />
          DOSSIER // LAW ENFORCEMENT SENSITIVE
        </span>
        <span className="font-mono text-[9px] text-secondary/70">
          ID: {entity.id}
        </span>
      </div>

      {/* Header */}
      <div className="p-5 border-b border-subtle flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-control bg-accent-violet/10 border border-accent-violet/25 flex items-center justify-center text-accent-violet shrink-0 mt-0.5 shadow-xs">
            <Icon className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-accent-violet/10 text-accent-violet border border-accent-violet/20">
                {entity.type}
              </span>
              <button
                type="button"
                onClick={handleCopyId}
                title="Click to copy identifier"
                className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-secondary text-secondary hover:text-primary border border-subtle hover:border-accent-violet/40 transition-colors"
              >
                {copied ? 'Copied ✓' : entity.id}
              </button>
            </div>
            <h3 className="font-display font-bold text-lg text-primary leading-tight tracking-tight">
              {entity.label || entity.name}
            </h3>
            {entity.role && (
              <span className="text-xs text-secondary block mt-1 font-medium">
                {entity.role}
              </span>
            )}
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-secondary hover:text-primary p-1.5 rounded-control hover:bg-surface-secondary transition-colors shrink-0"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6 text-xs">
        {/* Network Position Card with Micro-Meters */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-semibold text-secondary uppercase tracking-widest">
              Network Position & Centrality
            </span>
            <span className="text-[10px] font-mono text-secondary">METRIC-V1</span>
          </div>

          <div className="grid grid-cols-2 gap-2.5">
            <div className="p-3 rounded-card bg-surface-secondary/70 border border-subtle">
              <span className="text-[10px] text-secondary block font-medium">Degree Connections</span>
              <span className="font-display text-lg font-bold text-primary mt-0.5 block tabular-nums">
                {entity.degree ?? 0}
              </span>
              <div className="w-full bg-subtle/50 h-1 rounded-full mt-2 overflow-hidden">
                <div
                  className="bg-accent-violet h-full rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(100, ((entity.degree ?? 0) / 15) * 100)}%` }}
                />
              </div>
            </div>

            <div className="p-3 rounded-card bg-surface-secondary/70 border border-subtle">
              <span className="text-[10px] text-secondary block font-medium">Assigned Syndicate</span>
              <span className="font-display text-lg font-bold text-accent-violet mt-0.5 block">
                {entity.community_id ? `Cell 0${entity.community_id}` : 'General'}
              </span>
              <span className="text-[10px] text-secondary/70 block mt-1">Louvain Cluster</span>
            </div>

            <div className="p-3 rounded-card bg-surface-secondary/70 border border-subtle">
              <span className="text-[10px] text-secondary block font-medium">Betweenness Centrality</span>
              <span className="font-display text-lg font-bold text-primary mt-0.5 block tabular-nums">
                {betweennessScore.toFixed(3)}
              </span>
              <div className="w-full bg-subtle/50 h-1 rounded-full mt-2 overflow-hidden">
                <div
                  className="bg-accent-cyan h-full rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(100, betweennessScore * 100)}%` }}
                />
              </div>
            </div>

            <div className="p-3 rounded-card bg-surface-secondary/70 border border-subtle">
              <span className="text-[10px] text-secondary block font-medium">PageRank Score</span>
              <span className="font-display text-lg font-bold text-primary mt-0.5 block tabular-nums">
                {pagerankScore.toFixed(3)}
              </span>
              <div className="w-full bg-subtle/50 h-1 rounded-full mt-2 overflow-hidden">
                <div
                  className="bg-accent-emerald h-full rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(100, pagerankScore * 120)}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Graph Signal Callout */}
        <div className="p-3.5 rounded-card bg-accent-violet/5 border border-accent-violet/20 flex items-start gap-3">
          <div className="w-6 h-6 rounded-control bg-accent-violet/10 border border-accent-violet/25 flex items-center justify-center text-accent-violet shrink-0 mt-0.5">
            <TrendingUp className="w-3.5 h-3.5" />
          </div>
          <div className="text-secondary leading-relaxed">
            <span className="font-semibold text-primary block text-[11px] mb-0.5">Analytical Graph Signal</span>
            <p className="text-[11px] text-secondary">
              {betweennessScore > 0.3
                ? `High structural centrality (${betweennessScore.toFixed(3)}) — bridges distinct community communication channels.`
                : (entity.degree ?? 0) > 8
                ? `High-frequency coordination node with ${entity.degree} direct relational links.`
                : `Connected operational entity with verified evidentiary record links.`}
            </p>
          </div>
        </div>

        {/* Aliases */}
        {entity.aliases && entity.aliases.length > 0 && (
          <div>
            <span className="text-[10px] font-semibold text-secondary uppercase tracking-widest block mb-2">
              Recorded Aliases ({entity.aliases.length})
            </span>
            <div className="flex flex-wrap gap-1.5">
              {entity.aliases.map((alias, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-control bg-surface-secondary border border-subtle text-[11px] text-primary font-mono"
                >
                  "{alias}"
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Direct Connections */}
        {entity.connections && entity.connections.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-semibold text-secondary uppercase tracking-widest">
                Direct Connections ({entity.connections.length})
              </span>
              <span className="text-[10px] text-secondary">Tap to inspect</span>
            </div>
            <div className="space-y-1.5 max-h-52 overflow-y-auto pr-1">
              {entity.connections.map((conn, idx) => (
                <div
                  key={idx}
                  onClick={() => onSelectEntity && onSelectEntity(conn.target_id)}
                  className="p-2.5 rounded-control bg-surface-secondary/70 hover:bg-surface-secondary border border-subtle/80 hover:border-accent-violet/30 flex items-center justify-between cursor-pointer transition-colors group"
                >
                  <div className="overflow-hidden">
                    <span className="font-medium text-primary block truncate text-[11px] group-hover:text-accent-violet transition-colors">
                      {conn.target_name || conn.target_id}
                    </span>
                    <span className="text-[10px] text-secondary block font-mono">
                      {conn.type}
                    </span>
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 text-secondary group-hover:text-primary shrink-0 transition-transform group-hover:translate-x-0.5" />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Source Records Citation */}
        {entity.source_records && entity.source_records.length > 0 && (
          <div>
            <span className="text-[10px] font-semibold text-secondary uppercase tracking-widest block mb-1.5">
              Originating Evidentiary Sources
            </span>
            <div className="flex flex-wrap gap-1.5">
              {entity.source_records.map((rec, idx) => (
                <span
                  key={idx}
                  className="font-mono text-[10px] px-2 py-0.5 rounded bg-surface-secondary text-secondary border border-subtle/70"
                >
                  {rec}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer Actions & Ethical Disclaimer */}
      <div className="p-4 border-t border-subtle bg-surface-secondary/50 space-y-2">
        <button
          onClick={() => onExploreConnections && onExploreConnections(entity.id)}
          className="w-full py-2.5 px-3 rounded-control bg-accent-violet text-white text-xs font-semibold hover:opacity-90 transition-opacity flex items-center justify-center gap-2 shadow-soft"
        >
          <span>Explore Ego Network (1-Hop)</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </button>

        <p className="text-[10px] text-secondary/80 text-center leading-normal pt-1">
          Network metrics are descriptive analytical signals, not legal determinations.
        </p>
      </div>
    </div>
  )
}
