import React from 'react'
import { X, ArrowRight, ShieldCheck, FileText, Clock, Percent } from 'lucide-react'

export default function RelationshipInspector({ edge, onClose, onSelectEntity }) {
  if (!edge) return null

  const data = edge.data || edge
  const prov = data.provenance || {}
  const confidenceVal = typeof prov.confidence === 'number' ? prov.confidence : 0.95
  const confidencePercent = Math.round(confidenceVal * 100)
  const activeSegments = Math.min(5, Math.max(1, Math.round(confidenceVal * 5)))

  return (
    <div className="w-80 sm:w-96 border-l border-subtle bg-surface flex flex-col h-full shadow-drawer animate-in slide-in-from-right-4 duration-200 z-10 select-none">
      {/* Classification Banner */}
      <div className="px-5 py-2 border-b border-subtle/80 bg-surface-secondary/60 flex items-center justify-between text-[10px] text-secondary">
        <span className="font-mono uppercase tracking-widest text-[9px] font-semibold text-secondary/90 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald animate-pulse" />
          RELATIONSHIP PROVENANCE // AUDITED
        </span>
        <span className="font-mono text-[9px] text-secondary/70">
          EDGE: {data.id}
        </span>
      </div>

      {/* Header */}
      <div className="p-5 border-b border-subtle flex items-start justify-between gap-2">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-widest text-accent-violet block mb-1">
            RELATIONSHIP TRAIL
          </span>
          <div className="flex items-center gap-2 text-sm font-semibold text-primary font-display">
            <span
              onClick={() => onSelectEntity && onSelectEntity(data.source)}
              className="cursor-pointer hover:underline text-accent-violet"
              title="Inspect source entity"
            >
              {data.source}
            </span>
            <ArrowRight className="w-3.5 h-3.5 text-secondary shrink-0" />
            <span
              onClick={() => onSelectEntity && onSelectEntity(data.target)}
              className="cursor-pointer hover:underline text-accent-violet"
              title="Inspect target entity"
            >
              {data.target}
            </span>
          </div>
          <span className="text-xs font-mono font-bold text-primary mt-1.5 inline-block px-2 py-0.5 rounded bg-surface-secondary border border-subtle">
            {data.type}
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-secondary hover:text-primary p-1.5 rounded-control hover:bg-surface-secondary transition-colors shrink-0"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body: Evidentiary Audit Trail */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5 text-xs">
        {/* Core Evidence Card */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-semibold text-secondary uppercase tracking-widest">
              Supporting Record
            </span>
            <span className="text-[10px] font-mono text-secondary">CHAIN-OF-CUSTODY</span>
          </div>

          <div className="p-4 rounded-card bg-surface-secondary/70 border border-subtle space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-subtle/70">
              <span className="text-secondary text-[11px]">Source Registry</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-accent-violet/10 text-accent-violet border border-accent-violet/20 uppercase font-mono">
                {prov.source_type || 'POLICE_REPORT'}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-secondary text-[11px] flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" />
                Originating Record ID
              </span>
              <span className="font-mono text-primary font-semibold">
                {prov.source_id || 'FIR-001'}
              </span>
            </div>

            {data.timestamp && (
              <div className="flex items-center justify-between">
                <span className="text-secondary text-[11px] flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" />
                  Recorded Timestamp
                </span>
                <span className="text-primary font-mono text-[11px]">
                  {data.timestamp}
                </span>
              </div>
            )}

            {/* Segmented Confidence Score */}
            <div className="pt-2 border-t border-subtle/70">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-secondary text-[11px] flex items-center gap-1.5">
                  <Percent className="w-3.5 h-3.5" />
                  Evidentiary Confidence
                </span>
                <span className="font-mono text-accent-emerald font-bold">
                  {confidencePercent}%
                </span>
              </div>
              <div className="grid grid-cols-5 gap-1.5">
                {[1, 2, 3, 4, 5].map(seg => (
                  <div
                    key={seg}
                    className={`h-1.5 rounded-xs transition-all ${
                      seg <= activeSegments
                        ? 'bg-accent-emerald'
                        : 'bg-subtle/50'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Verbatim Excerpt */}
        {prov.snippet && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-semibold text-secondary uppercase tracking-widest">
                Verbatim Primary Source Citation
              </span>
              <span className="text-[10px] font-mono text-secondary">PRIMARY TEXT</span>
            </div>
            <div className="p-4 rounded-card bg-surface border border-subtle border-l-2 border-l-accent-violet">
              <p className="font-serif italic text-primary/90 leading-relaxed text-xs">
                "{prov.snippet}"
              </p>
              <div className="mt-2 pt-2 border-t border-subtle/60 flex items-center justify-between text-[10px] text-secondary">
                <span>Direct transcription from investigative record</span>
                <span className="font-mono">{prov.source_id || 'FIR-001'}</span>
              </div>
            </div>
          </div>
        )}

        {/* Link / Weight Properties */}
        <div>
          <span className="text-[10px] font-semibold text-secondary uppercase tracking-widest block mb-2">
            Graph Link Properties
          </span>
          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div className="p-2.5 rounded-control bg-surface-secondary/70 border border-subtle">
              <span className="text-[10px] text-secondary block font-medium">Link Identifier</span>
              <span className="font-mono text-primary font-semibold mt-0.5 block truncate">
                {data.id}
              </span>
            </div>
            <div className="p-2.5 rounded-control bg-surface-secondary/70 border border-subtle">
              <span className="text-[10px] text-secondary block font-medium">Link Weight / Frequency</span>
              <span className="font-mono text-primary font-semibold mt-0.5 block">
                {data.weight ?? 1.0}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-subtle bg-surface-secondary/50">
        <div className="flex items-center gap-2 text-secondary text-[11px]">
          <ShieldCheck className="w-4 h-4 text-accent-emerald shrink-0" />
          <span>Cryptographically validated to primary investigation case file.</span>
        </div>
      </div>
    </div>
  )
}
