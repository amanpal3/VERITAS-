import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  Home as HomeIcon,
  LayoutDashboard,
  Network,
  Users,
  BarChart3,
  ShieldCheck,
  FileCode2,
  Lock,
  ChevronRight,
} from 'lucide-react'
import { DetectiveBadge, CrimeIntelligenceSeal } from '../common/DetectiveLogos'

export default function AppSidebar({ stats }) {
  const navItems = [
    { to: '/', label: 'Home Deck', icon: HomeIcon, end: true },
    { to: '/dashboard', label: 'Overview Dashboard', icon: LayoutDashboard },
    { to: '/network', label: 'Network Explorer', icon: Network },
    { to: '/entities', label: 'Suspect Directory', icon: Users },
    { to: '/analytics', label: 'Syndicate Analytics', icon: BarChart3 },
  ]

  return (
    <aside className="w-64 shrink-0 border-r border-subtle bg-surface flex flex-col justify-between h-screen sticky top-0 transition-all select-none z-20">
      <div>
        {/* Brand Header with Detective Badge */}
        <div className="p-5 border-b border-subtle">
          <div className="flex items-center gap-3">
            <DetectiveBadge className="w-8 h-10 text-accent-violet shrink-0 shadow-xs" />
            <div>
              <span className="font-display font-extrabold tracking-tight text-lg leading-none block text-primary">
                VERITAS
              </span>
              <span className="text-[9px] font-mono tracking-widest text-secondary uppercase block mt-1">
                CRIME INTEL // SEC-810
              </span>
            </div>
          </div>
          <p className="text-[11px] text-secondary mt-3 leading-relaxed">
            AI-powered criminal network intelligence for explainable investigation support.
          </p>
        </div>

        {/* Primary Navigation */}
        <nav className="p-3 space-y-1">
          <div className="px-3 py-1.5 text-[10px] font-mono font-semibold text-secondary/70 uppercase tracking-widest">
            OPERATIONS
          </div>
          {navItems.map(item => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2 rounded-control text-xs font-medium transition-all group relative ${
                    isActive
                      ? 'bg-surface-secondary text-primary font-semibold shadow-soft'
                      : 'text-secondary hover:text-primary hover:bg-surface-secondary/50'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-3">
                      {isActive && (
                        <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-4 bg-accent-violet rounded-r-full" />
                      )}
                      <Icon
                        className={`w-4 h-4 transition-colors ${
                          isActive ? 'text-accent-violet' : 'text-secondary group-hover:text-primary'
                        }`}
                      />
                      <span>{item.label}</span>
                    </div>
                    {isActive && <ChevronRight className="w-3 h-3 text-secondary" />}
                  </>
                )}
              </NavLink>
            )
          })}
        </nav>

        {/* Secondary Resources */}
        <div className="p-3 pt-2 border-t border-subtle/60 space-y-1">
          <div className="px-3 py-1 text-[10px] font-mono font-semibold text-secondary/70 uppercase tracking-widest">
            VERIFICATION
          </div>
          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2.5 px-3 py-1.5 rounded-control text-xs text-secondary hover:text-primary hover:bg-surface-secondary/50 transition-colors"
          >
            <FileCode2 className="w-3.5 h-3.5" />
            <span>API Specifications</span>
          </a>
          <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-control text-xs text-secondary">
            <ShieldCheck className="w-3.5 h-3.5 text-accent-emerald" />
            <span>Cryptographic Proof</span>
          </div>
        </div>
      </div>

      {/* Bottom Graph Status Card */}
      <div className="p-4 m-3 rounded-card bg-surface-secondary/70 border border-subtle space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-semibold text-secondary uppercase tracking-widest font-mono">
            Active Graph
          </span>
          <span className="w-2 h-2 rounded-full bg-accent-emerald animate-pulse" />
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <div className="p-1.5 rounded bg-surface border border-subtle/60 text-center">
            <span className="text-[10px] text-secondary block">Nodes</span>
            <span className="font-bold text-primary">{stats?.nodes ?? 29}</span>
          </div>
          <div className="p-1.5 rounded bg-surface border border-subtle/60 text-center">
            <span className="text-[10px] text-secondary block">Links</span>
            <span className="font-bold text-accent-violet">{stats?.edges ?? 33}</span>
          </div>
        </div>
        <div className="pt-1 flex items-center justify-between text-[10px] text-secondary">
          <span className="flex items-center gap-1">
            <Lock className="w-3 h-3 text-accent-emerald" />
            SEC-LEVEL 4
          </span>
          <span className="font-mono">FIPS-140-3</span>
        </div>
      </div>
    </aside>
  )
}
