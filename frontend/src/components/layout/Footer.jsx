import React from 'react'
import { Link } from 'react-router-dom'
import { Shield, Lock, FileCheck, CheckCircle2, Users, Code2 } from 'lucide-react'
import {
  DetectiveBadge,
  CrimeIntelligenceSeal,
  FinancialCrimesBadge,
  EvidenceVaultSeal,
} from '../common/DetectiveLogos'

export default function Footer() {
  return (
    <footer className="border-t border-subtle bg-surface/90 backdrop-blur-xs mt-16 pt-12 pb-8 px-6 sm:px-8 select-none transition-colors">
      <div className="max-w-7xl mx-auto space-y-10">
        {/* Top Bureau Accreditation & Badges Strip */}
        <div className="flex flex-wrap items-center justify-between gap-4 pb-8 border-b border-subtle/70">
          <div className="flex items-center gap-3">
            <DetectiveBadge className="w-9 h-11 text-accent-violet shrink-0" />
            <div>
              <span className="font-display font-extrabold text-sm tracking-tight text-primary block">
                BUREAU OF CRIMINAL NETWORK INTELLIGENCE
              </span>
              <span className="text-[10px] font-mono text-secondary flex items-center gap-1.5 mt-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald animate-pulse" />
                CENTRAL FORENSIC REPOSITORY // FED-SPEC 810
              </span>
            </div>
          </div>

          {/* Crime Division Insignias */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 p-1.5 px-3 rounded-control bg-surface-secondary border border-subtle" title="Criminal Intelligence Division">
              <CrimeIntelligenceSeal className="w-6 h-6 shrink-0" />
              <span className="text-[10px] font-mono font-medium text-secondary">CRIME-INTEL</span>
            </div>
            <div className="flex items-center gap-2 p-1.5 px-3 rounded-control bg-surface-secondary border border-subtle" title="Financial Crimes & Hawala Enforcement">
              <FinancialCrimesBadge className="w-6 h-6 shrink-0" />
              <span className="text-[10px] font-mono font-medium text-secondary">FIN-CRIMES</span>
            </div>
            <div className="flex items-center gap-2 p-1.5 px-3 rounded-control bg-surface-secondary border border-subtle" title="Chain-of-Custody Verified">
              <EvidenceVaultSeal className="w-6 h-6 shrink-0" />
              <span className="text-[10px] font-mono font-medium text-accent-emerald">ADMISSIBLE</span>
            </div>
          </div>
        </div>

        {/* Multi-column Grid (4 Columns) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 pb-10 border-b border-subtle/60 text-xs">
          {/* Col 1: Mission */}
          <div className="space-y-3">
            <span className="font-display font-extrabold text-xl tracking-tight text-primary flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-accent-violet" />
              V E R I T A S
            </span>
            <p className="text-xs text-secondary leading-relaxed">
              AI-powered network intelligence for explainable investigation support.
              Synthesizing unstructured FIR narratives, telecommunication intercepts, and multi-hop banking escrows into an explainable relationship graph.
            </p>
            <div className="text-[11px] text-secondary/80 pt-2 flex items-center gap-2">
              <Shield className="w-3.5 h-3.5 text-accent-violet shrink-0" />
              <span>Investigative signals are analytical indicators, not legal determinations of guilt.</span>
            </div>
          </div>

          {/* Col 2: Navigation */}
          <div className="space-y-2.5">
            <span className="text-[10px] font-semibold text-secondary uppercase tracking-widest block font-mono">
              Investigation Workspace
            </span>
            <ul className="space-y-2 text-xs text-secondary">
              <li>
                <Link to="/" className="hover:text-accent-violet transition-colors flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-accent-violet" />
                  Home Landing Deck
                </Link>
              </li>
              <li>
                <Link to="/dashboard" className="hover:text-accent-violet transition-colors flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-accent-cyan" />
                  Overview Dashboard
                </Link>
              </li>
              <li>
                <Link to="/network" className="hover:text-accent-violet transition-colors flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-[#B28DFF]" />
                  Network Explorer Canvas
                </Link>
              </li>
              <li>
                <Link to="/entities" className="hover:text-accent-violet transition-colors flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-accent-amber" />
                  Entities & Suspects Directory
                </Link>
              </li>
              <li>
                <Link to="/analytics" className="hover:text-accent-violet transition-colors flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-accent-emerald" />
                  Network Structure & Analytics
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Compliance & Integrity */}
          <div className="space-y-2.5">
            <span className="text-[10px] font-semibold text-secondary uppercase tracking-widest block font-mono">
              Judicial Standards
            </span>
            <ul className="space-y-2 text-xs text-secondary font-mono">
              <li className="flex items-center gap-1.5 text-primary/80">
                <CheckCircle2 className="w-3.5 h-3.5 text-accent-emerald" />
                <span>NIST SP 800-86 Compliant</span>
              </li>
              <li className="flex items-center gap-1.5 text-primary/80">
                <CheckCircle2 className="w-3.5 h-3.5 text-accent-emerald" />
                <span>FED Rule 902(14) Custody</span>
              </li>
              <li className="flex items-center gap-1.5 text-primary/80">
                <CheckCircle2 className="w-3.5 h-3.5 text-accent-emerald" />
                <span>FIPS 140-3 HSM Signed</span>
              </li>
              <li className="flex items-center gap-1.5 text-primary/80">
                <CheckCircle2 className="w-3.5 h-3.5 text-accent-emerald" />
                <span>CJIS Security Policy v5.9</span>
              </li>
            </ul>
          </div>

          {/* Col 4: Engineering Team - TeamMETX */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="p-1 rounded bg-accent-violet/15 text-accent-violet border border-accent-violet/30">
                <Users className="w-3.5 h-3.5" />
              </span>
              <div>
                <span className="text-[10px] font-semibold text-accent-violet uppercase tracking-widest block font-mono">
                  ENGINEERING TEAM
                </span>
                <span className="font-display font-extrabold text-sm text-primary tracking-tight">
                  TeamMETX
                </span>
              </div>
            </div>

            <p className="text-[11px] text-secondary">
              Architects and developers of Project VERITAS:
            </p>

            <ul className="space-y-2 text-xs font-mono">
              <li className="flex items-center gap-2 p-1.5 px-2.5 rounded bg-surface-secondary/70 border border-subtle hover:border-accent-violet/40 transition-colors">
                <span className="w-4 h-4 rounded-full bg-accent-violet/20 text-accent-violet text-[10px] font-bold flex items-center justify-center shrink-0">
                  1
                </span>
                <span className="text-primary font-medium font-sans text-xs">Aman Pal</span>
              </li>
              <li className="flex items-center gap-2 p-1.5 px-2.5 rounded bg-surface-secondary/70 border border-subtle hover:border-accent-cyan/40 transition-colors">
                <span className="w-4 h-4 rounded-full bg-accent-cyan/20 text-accent-cyan text-[10px] font-bold flex items-center justify-center shrink-0">
                  2
                </span>
                <span className="text-primary font-medium font-sans text-xs">Armaan Dwivedi</span>
              </li>
              <li className="flex items-center gap-2 p-1.5 px-2.5 rounded bg-surface-secondary/70 border border-subtle hover:border-accent-emerald/40 transition-colors">
                <span className="w-4 h-4 rounded-full bg-accent-emerald/20 text-accent-emerald text-[10px] font-bold flex items-center justify-center shrink-0">
                  3
                </span>
                <span className="text-primary font-medium font-sans text-xs">Om Upadhyay</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Oversized Signature Wordmark & TeamMETX Accreditation */}
        <div className="pt-4 text-center overflow-hidden">
          <div
            className="font-display font-black tracking-tighter text-primary/10 select-none leading-none pointer-events-none transition-colors"
            style={{ fontSize: 'clamp(64px, 14vw, 190px)' }}
          >
            VERITAS
          </div>
          <div className="text-[11px] font-mono text-secondary/80 mt-2 flex flex-wrap items-center justify-center gap-x-3 gap-y-1">
            <span className="font-bold text-accent-violet uppercase tracking-wider">TeamMETX</span>
            <span className="text-secondary/40">•</span>
            <span className="text-primary/90 font-medium">1. Aman Pal</span>
            <span className="text-secondary/40">•</span>
            <span className="text-primary/90 font-medium">2. Armaan Dwivedi</span>
            <span className="text-secondary/40">•</span>
            <span className="text-primary/90 font-medium">3. Om Upadhyay</span>
          </div>
          <div className="text-[10px] font-mono text-secondary/60 mt-1.5">
            CONFIDENTIAL LAW ENFORCEMENT INTELLIGENCE PLATFORM — ALL RIGHTS RESERVED
          </div>
        </div>
      </div>
    </footer>
  )
}
