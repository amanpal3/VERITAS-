import React, { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Sun, Moon, HelpCircle, RefreshCw, Shield, X, Command } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext'
import { useToast } from '../../context/ToastContext'

export default function AppHeader({ onRefresh, isRefreshing }) {
  const location = useLocation()
  const { theme, toggleTheme } = useTheme()
  const { addToast } = useToast()
  const [showHelp, setShowHelp] = useState(false)

  const routeNames = {
    '/': 'Home Intelligence Deck',
    '/dashboard': 'Investigation Overview',
    '/network': 'Network Explorer Canvas',
    '/entities': 'Entities Directory',
    '/analytics': 'Network Analytics',
  }
  const currentTitle = routeNames[location.pathname] || 'Workspace'

  const handleRefresh = () => {
    if (onRefresh) onRefresh()
    addToast('Graph intelligence synced with backend', 'success')
  }

  const handleToggleTheme = () => {
    toggleTheme()
    addToast(`${theme === 'dark' ? 'Day' : 'Night'} mode active`, 'info')
  }

  return (
    <>
      <header className="h-14 border-b border-subtle bg-surface/85 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30 transition-colors">
        {/* Left: Breadcrumbs & Classification */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-secondary font-medium">Workspace</span>
            <span className="text-subtle text-[11px]">/</span>
            <span className="text-primary font-semibold font-display">{currentTitle}</span>
          </div>

          <span className="hidden md:inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-surface-secondary border border-subtle text-[10px] font-mono text-secondary tracking-wide">
            <Shield className="w-2.5 h-2.5 text-accent-violet" />
            <span>CASE #4092-B // OP-CERBERUS</span>
          </span>
        </div>

        {/* Right: Telemetry Signal & Actions */}
        <div className="flex items-center gap-2.5">
          {/* Live System Signal */}
          <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full bg-accent-emerald/10 border border-accent-emerald/20 text-[11px] font-mono text-accent-emerald">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald animate-pulse" />
            <span className="tracking-wide font-medium">TELEMETRY READY</span>
          </div>

          {/* Refresh Action */}
          <button
            onClick={handleRefresh}
            title="Refresh Knowledge Graph"
            className="p-2 rounded-control text-secondary hover:text-primary hover:bg-surface-secondary transition-all active:scale-95"
          >
            <RefreshCw className={`w-3.5 h-3.5 transition-transform ${isRefreshing ? 'animate-spin text-accent-violet' : ''}`} />
          </button>

          {/* Day / Night Theme Toggle */}
          <button
            onClick={handleToggleTheme}
            title={theme === 'dark' ? 'Switch to Day Mode' : 'Switch to Night Mode'}
            className="p-2 rounded-control text-secondary hover:text-primary hover:bg-surface-secondary transition-all active:scale-95 group"
          >
            {theme === 'dark' ? (
              <Sun className="w-3.5 h-3.5 text-accent-amber transition-transform duration-300 group-hover:rotate-90" />
            ) : (
              <Moon className="w-3.5 h-3.5 text-accent-violet transition-transform duration-300 group-hover:-rotate-45" />
            )}
          </button>

          {/* Methodology / Help Dialog */}
          <button
            onClick={() => setShowHelp(true)}
            title="Investigation Principles & Methodology"
            className="p-2 rounded-control text-secondary hover:text-primary hover:bg-surface-secondary transition-all active:scale-95"
          >
            <HelpCircle className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      {/* Methodology Modal */}
      {showHelp && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-surface border border-subtle rounded-surface shadow-drawer max-w-lg w-full p-6 text-sm text-primary transition-all animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-subtle">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-accent-violet" />
                <h3 className="font-display font-bold text-base">VERITAS — Analytical Methodology</h3>
              </div>
              <button
                onClick={() => setShowHelp(false)}
                className="text-secondary hover:text-primary p-1.5 rounded-control hover:bg-surface-secondary"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-4 py-4 text-xs text-secondary leading-relaxed">
              <div className="p-3 rounded-card bg-surface-secondary/60 border border-subtle">
                <span className="font-semibold text-primary block text-xs mb-1">
                  1. Structural Signals, Not Guilt Determinations
                </span>
                VERITAS calculates relational graph metrics (PageRank, Betweenness Centrality, Louvain Communities). All scores represent positional relevance in communication and transactional datasets—not legal guilt.
              </div>
              <div className="p-3 rounded-card bg-surface-secondary/60 border border-subtle">
                <span className="font-semibold text-primary block text-xs mb-1">
                  2. Strict Evidentiary Provenance
                </span>
                Every single edge displayed on the canvas links to underlying verified source material (e.g. verbatim FIR police reports, telecommunication CDR records, or bank ledger transfers).
              </div>
              <div className="p-3 rounded-card bg-surface-secondary/60 border border-subtle">
                <span className="font-semibold text-primary block text-xs mb-1">
                  3. Multi-Hop Investigation Navigation
                </span>
                Use the Path Finder to discover indirect links bridging street couriers to syndicate controllers across multiple communication and banking hops.
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setShowHelp(false)}
                className="px-4 py-2 rounded-control bg-primary text-canvas text-xs font-semibold hover:opacity-90 transition-opacity active:scale-97"
              >
                Acknowledge Principles
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
