import React from 'react'
import { X, RotateCcw, Filter } from 'lucide-react'

const entityTypeOptions = [
  { label: 'Person', color: 'bg-accent-violet' },
  { label: 'Phone', color: 'bg-accent-cyan' },
  { label: 'Organization', color: 'bg-[#B28DFF]' },
  { label: 'Vehicle', color: 'bg-accent-amber' },
  { label: 'Location', color: 'bg-accent-emerald' },
  { label: 'BankAccount', color: 'bg-accent-blue' },
]

export default function GraphFilters({
  isOpen,
  onClose,
  selectedTypes,
  onToggleType,
  minRisk,
  onChangeMinRisk,
  minWeight,
  onChangeMinWeight,
  onResetFilters,
}) {
  if (!isOpen) return null

  return (
    <div className="absolute top-16 right-6 z-30 w-72 p-4 rounded-card bg-surface/95 backdrop-blur-md border border-subtle shadow-card text-xs text-primary space-y-4 animate-in fade-in zoom-in-95 duration-150 select-none">
      <div className="flex items-center justify-between pb-2 border-b border-subtle">
        <div className="flex items-center gap-2 font-display font-bold text-xs text-primary">
          <Filter className="w-3.5 h-3.5 text-accent-violet" />
          <span>Graph Filters</span>
        </div>
        <button
          onClick={onClose}
          className="text-secondary hover:text-primary p-1 rounded-control hover:bg-surface-secondary transition-colors"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Entity Types */}
      <div>
        <span className="text-[10px] font-semibold text-secondary uppercase tracking-widest block mb-2">
          Entity Categories
        </span>
        <div className="grid grid-cols-2 gap-1.5">
          {entityTypeOptions.map(opt => {
            const active = selectedTypes.includes(opt.label)
            return (
              <button
                key={opt.label}
                type="button"
                onClick={() => onToggleType(opt.label)}
                className={`flex items-center gap-2 p-1.5 rounded-control text-[11px] border transition-colors ${
                  active
                    ? 'bg-surface-secondary border-subtle text-primary font-medium'
                    : 'bg-transparent border-transparent text-secondary hover:bg-surface-secondary/50'
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${opt.color} shrink-0`} />
                <span className="truncate">{opt.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Minimum Risk Score */}
      <div>
        <div className="flex justify-between items-center text-[10px] text-secondary mb-1">
          <span className="font-semibold uppercase tracking-wider">Minimum Analytical Risk</span>
          <span className="font-mono text-primary font-medium">{minRisk}+</span>
        </div>
        <input
          type="range"
          min="0"
          max="100"
          step="5"
          value={minRisk}
          onChange={e => onChangeMinRisk(Number(e.target.value))}
          className="w-full accent-accent-violet cursor-pointer"
        />
      </div>

      {/* Reset Actions */}
      <div className="pt-2 border-t border-subtle flex justify-between items-center">
        <button
          type="button"
          onClick={onResetFilters}
          className="flex items-center gap-1.5 text-[11px] text-secondary hover:text-primary transition-colors"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Reset all</span>
        </button>
        <button
          type="button"
          onClick={onClose}
          className="px-3 py-1 rounded-control bg-accent-violet text-white text-[11px] font-medium hover:opacity-90 transition-opacity"
        >
          Apply
        </button>
      </div>
    </div>
  )
}
