import React, { useState } from 'react'
import { X, Search, GitFork, ArrowRight, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react'
import { getShortestPath } from '../../api/analyticsApi'
import { useToast } from '../../context/ToastContext'

export default function PathFinderModal({ isOpen, onClose, entities = [], onPathFound, onClearPath }) {
  const [source, setSource] = useState('P006')
  const [target, setTarget] = useState('P001')
  const [maxHops, setMaxHops] = useState(5)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const { addToast } = useToast()

  if (!isOpen) return null

  const handleTrace = async e => {
    e.preventDefault()
    if (!source || !target) {
      setError('Please select both a source and target entity.')
      return
    }
    if (source === target) {
      setError('Source and target must be distinct entities.')
      return
    }

    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await getShortestPath(source, target)
      const data = response.data
      if (data.found) {
        setResult(data)
        if (onPathFound) {
          onPathFound(data)
        }
        addToast(`Connection discovered across ${data.length} hops`, 'success')
      } else {
        setError('No connecting path found between the selected entities within maximum hops.')
        addToast('No connection path found', 'info')
      }
    } catch (err) {
      setError(err?.response?.data?.error?.message || 'Failed to compute shortest path.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
    if (onClearPath) onClearPath()
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-surface border border-subtle rounded-card shadow-drawer max-w-lg w-full p-6 text-sm text-primary flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-subtle">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-control bg-accent-coral/10 border border-accent-coral/20 flex items-center justify-center text-accent-coral">
              <GitFork className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-display font-semibold text-base">Find Connection Path</h3>
              <p className="text-[11px] text-secondary">
                Trace indirect multi-hop relationship chains between entities.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-secondary hover:text-primary p-1.5 rounded-control hover:bg-surface-secondary transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Inputs */}
        <form onSubmit={handleTrace} className="py-4 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] font-semibold text-secondary uppercase tracking-wider block mb-1">
                Source Entity
              </label>
              <select
                value={source}
                onChange={e => setSource(e.target.value)}
                className="w-full text-xs p-2.5 rounded-control bg-surface-secondary border border-subtle text-primary focus:outline-none focus:border-accent-violet"
              >
                {entities.map(e => (
                  <option key={e.id} value={e.id}>
                    {e.name || e.label} ({e.id})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[10px] font-semibold text-secondary uppercase tracking-wider block mb-1">
                Target Entity
              </label>
              <select
                value={target}
                onChange={e => setTarget(e.target.value)}
                className="w-full text-xs p-2.5 rounded-control bg-surface-secondary border border-subtle text-primary focus:outline-none focus:border-accent-violet"
              >
                {entities.map(e => (
                  <option key={e.id} value={e.id}>
                    {e.name || e.label} ({e.id})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center text-[10px] text-secondary mb-1">
              <span className="font-semibold uppercase tracking-wider">Maximum Search Hops</span>
              <span className="font-mono text-primary font-medium">{maxHops} Hops</span>
            </div>
            <input
              type="range"
              min="1"
              max="6"
              value={maxHops}
              onChange={e => setMaxHops(Number(e.target.value))}
              className="w-full accent-accent-violet cursor-pointer"
            />
          </div>

          <div className="flex gap-2 pt-1">
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 py-2 px-4 rounded-control bg-accent-violet text-white text-xs font-semibold hover:opacity-90 transition-opacity flex items-center justify-center gap-2 shadow-soft disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{isLoading ? 'Tracing Network...' : 'Trace Connection'}</span>
            </button>
            {result && (
              <button
                type="button"
                onClick={handleReset}
                className="py-2 px-3 rounded-control bg-surface-secondary text-secondary hover:text-primary border border-subtle text-xs font-medium transition-colors"
              >
                Clear
              </button>
            )}
          </div>
        </form>

        {/* Results / Error Area */}
        <div className="flex-1 overflow-y-auto pt-2 space-y-3">
          {error && (
            <div className="p-3 rounded-card bg-accent-red/10 border border-accent-red/20 text-accent-red text-xs flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {result && (
            <div className="space-y-3">
              <div className="p-3 rounded-card bg-accent-emerald/10 border border-accent-emerald/25 text-accent-emerald text-xs flex items-center justify-between">
                <span className="font-semibold flex items-center gap-1.5 font-display">
                  <CheckCircle2 className="w-4 h-4" />
                  Connection Chain Verified
                </span>
                <span className="font-mono font-bold text-xs">{result.length} Relational Hops</span>
              </div>

              {/* Step Sequence */}
              <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                {result.path_details.map((step, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-control bg-surface-secondary/80 border border-subtle text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between text-[10px] text-secondary font-mono">
                      <span className="font-semibold text-secondary/80">HOP 0{step.step}</span>
                      <span className="px-1.5 py-0.5 rounded bg-surface border border-subtle text-accent-violet font-semibold">
                        {step.relation}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px] font-semibold text-primary font-display">
                      <span className="truncate">{step.from}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-secondary shrink-0" />
                      <span className="truncate">{step.to}</span>
                    </div>
                    {step.evidence_snippet && (
                      <p className="font-serif italic text-primary/85 border-l-2 border-accent-violet/60 pl-2.5 mt-1.5 text-xs leading-relaxed">
                        "{step.evidence_snippet}"
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
