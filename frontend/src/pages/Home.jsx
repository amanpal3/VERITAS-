import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Shield,
  GitFork,
  Users,
  Layers,
  ArrowRight,
  CheckCircle2,
  FileText,
  Search,
  Zap,
  Activity,
  ChevronRight,
  TrendingUp,
  Cpu,
  Lock,
  ExternalLink,
} from 'lucide-react'
import {
  DetectiveBadge,
  CrimeIntelligenceSeal,
  FinancialCrimesBadge,
  TelecomForensicsLogo,
  EvidenceVaultSeal,
  FingerprintIcon,
} from '../components/common/DetectiveLogos'

export default function Home() {
  const navigate = useNavigate()

  return (
    <div className="space-y-16 max-w-7xl mx-auto py-4 select-none">
      {/* 1. Hero Section */}
      <section className="relative overflow-hidden rounded-card border border-subtle bg-surface p-8 sm:p-12 md:p-16 shadow-card">
        {/* Ambient Bloom Background Elements */}
        <div className="absolute -top-32 -right-32 w-96 h-96 rounded-full bg-accent-violet/10 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-32 -left-32 w-96 h-96 rounded-full bg-accent-cyan/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-4xl space-y-6">
          {/* Official Agency Insignia Header */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="p-2 rounded-control bg-accent-violet/10 border border-accent-violet/25 shadow-xs flex items-center gap-2.5">
              <DetectiveBadge className="w-6 h-7 text-accent-violet" />
              <span className="font-mono text-[10px] font-bold tracking-widest text-primary uppercase">
                BUREAU OF CRIMINAL INTELLIGENCE // SEC-LE-810
              </span>
            </div>
            <span className="px-2.5 py-1 rounded-control bg-accent-emerald/10 border border-accent-emerald/25 text-accent-emerald font-mono text-[10px] font-bold flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald animate-pulse" />
              SYSTEM 100% OPERATIONAL
            </span>
          </div>

          {/* Main Headline */}
          <h1 className="font-display font-extrabold text-3xl sm:text-5xl lg:text-6xl text-primary tracking-tight leading-[1.08]">
            Explainable Criminal <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-violet via-[#B28DFF] to-accent-cyan">
              Network Intelligence
            </span>{' '}
            for Law Enforcement.
          </h1>

          {/* Subtitle */}
          <p className="text-secondary text-sm sm:text-base max-w-2xl leading-relaxed">
            VERITAS synthesizes unstructured intelligence dossiers, multi-hop hawala escrow ledgers, and burner telecommunications into an auditable relationship graph. Dismantle organized syndicates with mathematical proof.
          </p>

          {/* Real-Time Telemetry Chips */}
          <div className="flex flex-wrap gap-2 pt-1 font-mono text-[10px] text-secondary">
            <span className="px-2.5 py-1 rounded bg-surface-secondary border border-subtle">
              412 Syndicates Monitored
            </span>
            <span className="px-2.5 py-1 rounded bg-surface-secondary border border-subtle">
              2.8M Subpoenaed Records
            </span>
            <span className="px-2.5 py-1 rounded bg-surface-secondary border border-subtle">
              NIST SP 800-86 Compliant
            </span>
            <span className="px-2.5 py-1 rounded bg-surface-secondary border border-subtle text-accent-cyan font-semibold">
              Louvain Modularity Q=0.814
            </span>
          </div>

          {/* Primary Action Buttons */}
          <div className="flex flex-wrap items-center gap-3 pt-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-3 rounded-control bg-accent-violet text-white text-xs sm:text-sm font-semibold hover:opacity-95 transition-all flex items-center gap-2.5 shadow-card hover:shadow-violet-glow"
            >
              <span>Launch Investigation Workspace</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => navigate('/network')}
              className="px-5 py-3 rounded-control bg-surface border border-subtle text-xs sm:text-sm font-semibold text-primary hover:bg-surface-secondary transition-colors flex items-center gap-2"
            >
              <GitFork className="w-4 h-4 text-accent-violet" />
              <span>Explore Network Canvas</span>
            </button>

            <button
              onClick={() => navigate('/entities')}
              className="px-4 py-3 rounded-control text-xs sm:text-sm text-secondary hover:text-primary transition-colors flex items-center gap-1.5"
            >
              <Search className="w-3.5 h-3.5" />
              <span>Suspect Registry</span>
            </button>
          </div>
        </div>
      </section>

      {/* 2. Active Operation Showcase Widget */}
      <section className="rounded-card border border-subtle bg-surface p-6 sm:p-8 shadow-card space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-subtle">
          <div className="flex items-center gap-3">
            <CrimeIntelligenceSeal className="w-10 h-10 shrink-0" />
            <div>
              <span className="text-[10px] font-bold uppercase tracking-widest text-accent-violet block">
                ACTIVE CASE FILE // PRIORITY ZERO
              </span>
              <h2 className="font-display font-bold text-xl sm:text-2xl text-primary">
                Operation Cerberus // Hawala-Logistics Nexus
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded bg-accent-coral/10 text-accent-coral border border-accent-coral/25 font-mono text-[11px] font-bold">
              3 Syndicate Cells Isolated
            </span>
            <button
              onClick={() => navigate('/network')}
              className="px-3.5 py-1.5 rounded-control bg-surface-secondary border border-subtle text-xs text-primary hover:border-accent-violet/40 transition-colors flex items-center gap-1.5 font-medium"
            >
              <span>Inspect in Canvas</span>
              <ExternalLink className="w-3 h-3 text-secondary" />
            </button>
          </div>
        </div>

        {/* Case Narrative & Multi-Hop Path Highlight */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-card bg-surface-secondary/70 border border-subtle space-y-2">
            <div className="flex items-center justify-between text-[11px] font-mono text-secondary">
              <span>LEAD SUSPECT</span>
              <span className="text-accent-coral font-bold">RISK 92</span>
            </div>
            <div className="font-display font-bold text-base text-primary">
              Tariq Sheikh (P006)
            </div>
            <p className="text-[11px] text-secondary leading-relaxed">
              High betweenness broker identified connecting overseas wire conduits to domestic transport logistics.
            </p>
          </div>

          <div className="p-4 rounded-card bg-surface-secondary/70 border border-subtle space-y-2">
            <div className="flex items-center justify-between text-[11px] font-mono text-secondary">
              <span>INTERMEDIARY ENTITY</span>
              <span className="text-accent-cyan font-bold">E001</span>
            </div>
            <div className="font-display font-bold text-base text-primary">
              Metro Distribution Syndicate
            </div>
            <p className="text-[11px] text-secondary leading-relaxed">
              Front distribution hub routing contraband freight and burner telephone exchanges.
            </p>
          </div>

          <div className="p-4 rounded-card bg-surface-secondary/70 border border-subtle space-y-2">
            <div className="flex items-center justify-between text-[11px] font-mono text-secondary">
              <span>TARGET RECIPIENT</span>
              <span className="text-accent-amber font-bold">RISK 88</span>
            </div>
            <div className="font-display font-bold text-base text-primary">
              Imran Batra (P001)
            </div>
            <p className="text-[11px] text-secondary leading-relaxed">
              Key operational node coordinating cross-border logistics deliveries and Hawala payoffs.
            </p>
          </div>
        </div>

        {/* Verbatim Court Citation Snippet */}
        <div className="p-4 rounded-card bg-surface-secondary/40 border border-subtle border-l-2 border-l-accent-violet flex items-start gap-3">
          <FileText className="w-4 h-4 text-accent-violet shrink-0 mt-0.5" />
          <div className="space-y-1 text-xs">
            <span className="font-mono text-[10px] font-bold text-secondary uppercase tracking-wider block">
              PRIMARY EVIDENCE RECORD // FIR-001 EXCERPT
            </span>
            <p className="font-serif italic text-primary/90 leading-relaxed text-xs">
              "Surveillance logs and telecommunication records confirm Tariq Sheikh directed Rs 45,00,000 through Metro Distribution to Imran Batra for contraband logistics clearance."
            </p>
          </div>
        </div>
      </section>

      {/* 3. Three-Pillar Core Engine Architecture */}
      <section className="space-y-6">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-widest text-accent-violet block mb-1">
            CORE ALGORITHMIC CAPABILITIES
          </span>
          <h2 className="font-display font-bold text-2xl sm:text-3xl text-primary tracking-tight">
            How VERITAS Deconstructs Criminal Networks
          </h2>
          <p className="text-xs sm:text-sm text-secondary mt-1 max-w-2xl leading-relaxed">
            Built from the ground up for strict judicial admissibility, explainable graph traversal, and zero hallucination.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="p-6 rounded-card bg-surface border border-subtle shadow-card interactive-card space-y-4">
            <div className="w-12 h-12 rounded-control bg-accent-violet/10 border border-accent-violet/25 flex items-center justify-center text-accent-violet">
              <Users className="w-6 h-6" />
            </div>
            <h3 className="font-display font-bold text-lg text-primary">
              AI Entity Resolution & Alias Merging
            </h3>
            <p className="text-xs text-secondary leading-relaxed">
              Automatically links burner aliases, shared phone IMEI/IMSI devices, shell company directorships, and offshore bank accounts into a unified actor dossier with Jaro-Winkler confidence scoring.
            </p>
            <div className="pt-2 border-t border-subtle/70 text-[11px] font-mono text-accent-violet">
              Accuracy: 99.4% cross-match
            </div>
          </div>

          {/* Card 2 */}
          <div className="p-6 rounded-card bg-surface border border-subtle shadow-card interactive-card space-y-4">
            <div className="w-12 h-12 rounded-control bg-accent-cyan/10 border border-accent-cyan/25 flex items-center justify-center text-accent-cyan">
              <GitFork className="w-6 h-6" />
            </div>
            <h3 className="font-display font-bold text-lg text-primary">
              Multi-Hop Relational Provenance
            </h3>
            <p className="text-xs text-secondary leading-relaxed">
              Traces indirect relationship paths up to 6 hops deep using Dijkstra low-friction routing. Every single hop links directly back to the exact sentence or ledger entry in underlying evidence.
            </p>
            <div className="pt-2 border-t border-subtle/70 text-[11px] font-mono text-accent-cyan">
              Latency: &lt;15ms multi-hop traversal
            </div>
          </div>

          {/* Card 3 */}
          <div className="p-6 rounded-card bg-surface border border-subtle shadow-card interactive-card space-y-4">
            <div className="w-12 h-12 rounded-control bg-[#B28DFF]/10 border border-[#B28DFF]/25 flex items-center justify-center text-[#B28DFF]">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="font-display font-bold text-lg text-primary">
              Louvain Modularity Syndicate Cells
            </h3>
            <p className="text-xs text-secondary leading-relaxed">
              Identifies functional syndicate cells (e.g. Hawala money laundering, courier distribution, enforcement muscle) through community clustering without manual investigator tagging.
            </p>
            <div className="pt-2 border-t border-subtle/70 text-[11px] font-mono text-[#B28DFF]">
              Modularity: Q = 0.814 optimal cut
            </div>
          </div>
        </div>
      </section>

      {/* 4. Specialized Law Enforcement Crime Units */}
      <section className="space-y-6">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-widest text-accent-violet block mb-1">
            CRIME ENFORCEMENT DIVISIONS
          </span>
          <h2 className="font-display font-bold text-2xl sm:text-3xl text-primary tracking-tight">
            Tailored for Specialized Investigative Teams
          </h2>
          <p className="text-xs sm:text-sm text-secondary mt-1 max-w-2xl leading-relaxed">
            Modular intelligence pipelines for financial, telecom, and organized syndicate operations.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Unit 1 */}
          <div className="p-6 rounded-card bg-surface border border-subtle shadow-card interactive-card space-y-4">
            <div className="flex items-center justify-between">
              <FinancialCrimesBadge className="w-12 h-12" />
              <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-surface-secondary text-secondary border border-subtle">
                UNIT-01 // FIN-CRIME
              </span>
            </div>
            <h3 className="font-display font-bold text-base text-primary">
              Financial Crimes & Hawala Division
            </h3>
            <p className="text-xs text-secondary leading-relaxed">
              Unmasks smurfing deposits, cross-border token handoffs, informal ledger balancing, and shell corporate conduits with full FATF/PMLA compliance trails.
            </p>
            <ul className="text-[11px] text-secondary space-y-1.5 pt-2 border-t border-subtle/70">
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-accent-emerald shrink-0" />
                <span>Informal ledger cash-token mapping</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-accent-emerald shrink-0" />
                <span>Smurfing anomaly thresholds</span>
              </li>
            </ul>
          </div>

          {/* Unit 2 */}
          <div className="p-6 rounded-card bg-surface border border-subtle shadow-card interactive-card space-y-4">
            <div className="flex items-center justify-between">
              <DetectiveBadge className="w-10 h-12 text-accent-violet" />
              <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-surface-secondary text-secondary border border-subtle">
                UNIT-02 // INTERDICTION
              </span>
            </div>
            <h3 className="font-display font-bold text-base text-primary">
              Organized Syndicate Interdiction
            </h3>
            <p className="text-xs text-secondary leading-relaxed">
              Isolates cut-vertex brokers and logistics choke points across intermodal transit routes, warehouse waypoints, and handler-courier handoff chains.
            </p>
            <ul className="text-[11px] text-secondary space-y-1.5 pt-2 border-t border-subtle/70">
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-accent-emerald shrink-0" />
                <span>Critical broker bottleneck detection</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-accent-emerald shrink-0" />
                <span>Multi-jurisdictional syndicate mapping</span>
              </li>
            </ul>
          </div>

          {/* Unit 3 */}
          <div className="p-6 rounded-card bg-surface border border-subtle shadow-card interactive-card space-y-4">
            <div className="flex items-center justify-between">
              <TelecomForensicsLogo className="w-12 h-12" />
              <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-surface-secondary text-secondary border border-subtle">
                UNIT-03 // CYBER-TEL
              </span>
            </div>
            <h3 className="font-display font-bold text-base text-primary">
              Telecom CDR & Burner Intercepts
            </h3>
            <p className="text-xs text-secondary leading-relaxed">
              Detects burner phone IMEI-IMSI rotation pacing, cell tower proximity clustering, and coordinated silence windows before major operational deliveries.
            </p>
            <ul className="text-[11px] text-secondary space-y-1.5 pt-2 border-t border-subtle/70">
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-accent-emerald shrink-0" />
                <span>Burner device swap triangulation</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-accent-emerald shrink-0" />
                <span>Call time-frequency co-occurrence</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* 5. Cryptographic Evidence Chain-of-Custody Proof */}
      <section className="p-8 rounded-card border border-subtle bg-surface shadow-card space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-subtle">
          <div className="flex items-center gap-3">
            <EvidenceVaultSeal className="w-12 h-12 shrink-0" />
            <div>
              <span className="text-[10px] font-bold uppercase tracking-widest text-accent-emerald block">
                JUDICIAL ADMISSIBILITY STANDARD
              </span>
              <h3 className="font-display font-bold text-xl text-primary">
                Federal Rule 902(14) Self-Authenticating Digital Records
              </h3>
            </div>
          </div>

          <span className="font-mono text-xs px-2.5 py-1 rounded bg-surface-secondary text-secondary border border-subtle self-start sm:self-auto">
            FIPS 140-3 HSM SIGNED
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-secondary">
          <div className="space-y-3">
            <p className="leading-relaxed">
              Every relationship edge rendered in VERITAS is backed by a deterministic cryptographic audit trail. When subpoenaed records, FIR reports, or wiretaps are ingested, the system generates immutable SHA-256 Merkle proofs verifying no records were altered during graph computation.
            </p>
            <div className="p-3 rounded-control bg-surface-secondary font-mono text-[10px] text-primary/80 space-y-1 border border-subtle">
              <div>MERKLE ROOT: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08</div>
              <div>CUSTODIAN: SPECIAL AGENT M. VANCE // BADGE #8841-K</div>
              <div className="text-accent-emerald">AUDIT STATUS: FULLY VERIFIED & COURT READY</div>
            </div>
          </div>

          <div className="p-4 rounded-card bg-surface-secondary/60 border border-subtle space-y-2.5">
            <span className="font-display font-semibold text-xs text-primary block">
              Ethical AI Principle & Safeguards
            </span>
            <p className="leading-relaxed text-[11px]">
              VERITAS serves exclusively as an investigative decision-support system. Algorithmic scores (betweenness, PageRank, cell clustering) are neutral topological signals, never autonomous determinations of guilt or criminality.
            </p>
            <div className="flex items-center gap-2 pt-1 text-[11px] text-accent-violet font-semibold">
              <Shield className="w-4 h-4" />
              <span>Full human-in-the-loop analyst review mandatory.</span>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Launch Workspace Call to Action */}
      <section className="text-center p-10 sm:p-14 rounded-card border border-subtle bg-gradient-to-b from-surface to-surface-secondary/80 shadow-card space-y-5">
        <div className="flex justify-center">
          <DetectiveBadge className="w-12 h-14 text-accent-violet" />
        </div>
        <h2 className="font-display font-extrabold text-2xl sm:text-4xl text-primary tracking-tight">
          Ready to Deconstruct Network Intelligence?
        </h2>
        <p className="text-xs sm:text-sm text-secondary max-w-xl mx-auto leading-relaxed">
          Access the live investigation workspace, inspect multi-hop suspect connections, and review verified evidentiary dossiers.
        </p>
        <div className="flex justify-center gap-3 pt-2">
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-3 rounded-control bg-accent-violet text-white text-xs sm:text-sm font-semibold hover:opacity-95 transition-all shadow-card hover:shadow-violet-glow flex items-center gap-2"
          >
            <span>Enter Workspace Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => navigate('/network')}
            className="px-5 py-3 rounded-control bg-surface border border-subtle text-xs sm:text-sm font-semibold text-primary hover:bg-surface-secondary transition-colors"
          >
            Open Network Graph
          </button>
        </div>
      </section>
    </div>
  )
}
