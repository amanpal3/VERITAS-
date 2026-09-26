import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Users,
  Network,
  Share2,
  FileText,
  ArrowRight,
  TrendingUp,
  AlertTriangle,
  Radio,
  ChevronRight,
  Maximize2,
  ShieldCheck,
  Building2,
  Sparkles,
} from 'lucide-react'
import { getGraphData } from '../api/graphApi'
import NetworkGraph from '../graph/NetworkGraph'
import { DetectiveBadge, CrimeIntelligenceSeal, EvidenceVaultSeal } from '../components/common/DetectiveLogos'

export default function Dashboard() {
  const [graphData, setGraphData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [cyInstance, setCyInstance] = useState(null)

  useEffect(() => {
    getGraphData()
      .then(res => {
        setGraphData(res.data)
        setIsLoading(false)
      })
      .catch(err => {
        console.error('Failed to load dashboard graph:', err)
        setIsLoading(false)
      })
  }, [])

  const reviewSignals = [
    {
      id: 1,
      title: 'Cross-Community Bridge: Tariq Sheikh connects Logistics and Hawala cells',
      description: 'Graph centrality metrics identify critical broker bridging shipping channels to covert banking transactions.',
      source: 'FIR_002_Hawala_Raid',
      time: '12 Sep 2026',
      confidence: '95%',
      type: 'BRIDGE',
      icon: TrendingUp,
      color: 'text-accent-violet',
      bgColor: 'bg-accent-violet/10 border-accent-violet/20',
    },
    {
      id: 2,
      title: 'High Transaction Volume: ACC-ASTRA-7701 transferred INR 8,500,000 to Hawala Broker',
      description: 'Structuring pattern detected: Multiple transactions below regulatory review thresholds over 48 hours.',
      source: 'BANK_LEDGER_TX1048',
      time: '11 Sep 2026',
      confidence: '100%',
      type: 'FINANCIAL',
      icon: AlertTriangle,
      color: 'text-accent-coral',
      bgColor: 'bg-accent-coral/10 border-accent-coral/20',
    },
    {
      id: 3,
      title: 'Burner Cluster Identified: Mobile device cluster PH004 active across 24 late calls',
      description: 'Co-location telemetry with Vehicle DL-1M-4412 during transit window between 02:00 and 04:30 AM.',
      source: 'CDR_TELECOM_1001',
      time: '10 Sep 2026',
      confidence: '100%',
      type: 'TELECOM',
      icon: Radio,
      color: 'text-accent-cyan',
      bgColor: 'bg-accent-cyan/10 border-accent-cyan/20',
    },
    {
      id: 4,
      title: 'Vehicular Logistics: Truck DL-1M-4412 associated with safehouse transport corridor',
      description: 'Border checkpoint surveillance matches truck operator Arjun Verma to logistics coordinator handler.',
      source: 'FIR_001_Smuggling_Bust',
      time: '09 Sep 2026',
      confidence: '92%',
      type: 'LOGISTICS',
      icon: ShieldCheck,
      color: 'text-accent-amber',
      bgColor: 'bg-accent-amber/10 border-accent-amber/20',
    },
  ]

  const totalNodes = graphData?.nodes?.length || 29
  const totalEdges = graphData?.edges?.length || 33
  const communitiesCount = graphData?.metadata?.communities_detected || 3

  return (
    <div className="space-y-8 max-w-7xl mx-auto py-2 animate-in fade-in duration-300">
      {/* Header Content */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-subtle/80 pb-6">
        <div className="flex items-start gap-4">
          <DetectiveBadge className="w-12 h-14 text-accent-violet shrink-0 hidden sm:block shadow-xs" />
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-violet" />
              <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-accent-violet">
                CRIMINAL INTELLIGENCE OVERVIEW // CASE #4092-B
              </span>
            </div>
            <h1 className="font-display font-extrabold text-2xl sm:text-3xl lg:text-4xl text-primary tracking-tight">
              See the connections hidden in the data.
            </h1>
            <p className="text-xs sm:text-sm text-secondary mt-1 max-w-2xl leading-relaxed">
              Explore entities, relationships and evidence across connected investigation records.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden lg:block text-right">
            <span className="text-[10px] font-mono text-secondary uppercase block">INTELLIGENCE GRAPH</span>
            <span className="text-xs font-mono text-accent-emerald font-semibold flex items-center gap-1.5 justify-end">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald animate-pulse" />
              Synced & Ready
            </span>
          </div>
          <Link
            to="/network"
            className="py-2.5 px-4 rounded-control bg-primary text-canvas text-xs font-semibold hover:opacity-90 transition-all flex items-center gap-2 shadow-card active:scale-97"
          >
            <span>Open Explorer</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Entities */}
        <div className="interactive-card p-5 rounded-card bg-surface border border-subtle shadow-card">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-[10px] font-mono font-semibold uppercase tracking-wider">ENTITIES</span>
            <span className="p-1 rounded bg-accent-violet/10 text-accent-violet">
              <Users className="w-3.5 h-3.5" />
            </span>
          </div>
          <div className="font-display text-2xl sm:text-3xl font-extrabold text-primary">
            {totalNodes}
          </div>
          <div className="flex items-center justify-between text-[11px] text-secondary mt-2 pt-2 border-t border-subtle/50">
            <span>6 Entity Classes</span>
            <span className="font-mono text-[10px] text-accent-emerald font-medium">+4 resolved</span>
          </div>
        </div>

        {/* Card 2: Relationships */}
        <div className="interactive-card p-5 rounded-card bg-surface border border-subtle shadow-card">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-[10px] font-mono font-semibold uppercase tracking-wider">RELATIONSHIPS</span>
            <span className="p-1 rounded bg-accent-cyan/10 text-accent-cyan">
              <Share2 className="w-3.5 h-3.5" />
            </span>
          </div>
          <div className="font-display text-2xl sm:text-3xl font-extrabold text-primary">
            {totalEdges}
          </div>
          <div className="flex items-center justify-between text-[11px] text-secondary mt-2 pt-2 border-t border-subtle/50">
            <span>Directed Multigraph</span>
            <span className="font-mono text-[10px] text-secondary">0.082 density</span>
          </div>
        </div>

        {/* Card 3: Detected Cells */}
        <div className="interactive-card p-5 rounded-card bg-surface border border-subtle shadow-card">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-[10px] font-mono font-semibold uppercase tracking-wider">DETECTED CELLS</span>
            <span className="p-1 rounded bg-[#B28DFF]/10 text-[#B28DFF]">
              <Network className="w-3.5 h-3.5" />
            </span>
          </div>
          <div className="font-display text-2xl sm:text-3xl font-extrabold text-primary">
            0{communitiesCount}
          </div>
          <div className="flex items-center justify-between text-[11px] text-secondary mt-2 pt-2 border-t border-subtle/50">
            <span>Louvain Modularity</span>
            <span className="font-mono text-[10px] text-accent-violet">0.74 Q</span>
          </div>
        </div>

        {/* Card 4: Source Records */}
        <div className="interactive-card p-5 rounded-card bg-surface border border-subtle shadow-card">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-[10px] font-mono font-semibold uppercase tracking-wider">SOURCE RECORDS</span>
            <span className="p-1 rounded bg-accent-emerald/10 text-accent-emerald">
              <FileText className="w-3.5 h-3.5" />
            </span>
          </div>
          <div className="font-display text-2xl sm:text-3xl font-extrabold text-primary">
            128
          </div>
          <div className="flex items-center justify-between text-[11px] text-secondary mt-2 pt-2 border-t border-subtle/50">
            <span>FIRs, CDRs, Ledgers</span>
            <span className="font-mono text-[10px] text-accent-emerald">100% Verified</span>
          </div>
        </div>
      </div>

      {/* Hero Relationship Map Card */}
      <div className="rounded-card bg-surface border border-subtle shadow-card overflow-hidden">
        {/* Card Header */}
        <div className="p-5 border-b border-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-secondary/30">
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-accent-violet">
                TOPOLOGY CANVAS
              </span>
              <span className="text-[10px] font-mono px-2 py-0.2 rounded-full bg-surface border border-subtle text-secondary">
                FORCE-DIRECTED STABILIZED
              </span>
            </div>
            <h2 className="font-display font-bold text-base text-primary">
              Global Knowledge Network
            </h2>
            <p className="text-xs text-secondary mt-0.5">
              Interactive relationship canvas displaying verified actor connections, burner communication lines, and Hawala transfers.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => cyInstance?.fit(40)}
              className="px-3 py-1.5 rounded-control bg-surface border border-subtle text-xs text-secondary hover:text-primary transition-all flex items-center gap-1.5 active:scale-95 shadow-soft"
            >
              <Maximize2 className="w-3 h-3" />
              <span>Fit View</span>
            </button>
            <Link
              to="/network"
              className="px-3.5 py-1.5 rounded-control bg-primary text-canvas text-xs font-semibold hover:opacity-90 transition-all active:scale-95 shadow-soft"
            >
              Full Workspace
            </Link>
          </div>
        </div>

        {/* Canvas Area */}
        <div className="h-[460px] w-full relative">
          {isLoading ? (
            <div className="w-full h-full flex flex-col items-center justify-center gap-2 text-xs text-secondary">
              <span className="w-6 h-6 border-2 border-accent-violet border-t-transparent rounded-full animate-spin" />
              <span className="font-mono text-[11px]">Synthesizing relationship network...</span>
            </div>
          ) : (
            <NetworkGraph
              graphData={graphData}
              onInitCy={cy => setCyInstance(cy)}
            />
          )}
        </div>
      </div>

      {/* Review Signals Section */}
      <div className="rounded-card bg-surface border border-subtle shadow-card p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-subtle">
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <span className="w-2 h-2 rounded-full bg-accent-coral" />
              <h3 className="font-display font-bold text-base text-primary">
                Explainable Forensic Signals & Review
              </h3>
            </div>
            <p className="text-xs text-secondary">
              Statistically salient relationship behaviors flagged for analytical audit.
            </p>
          </div>
          <span className="text-[10px] font-mono font-semibold px-2.5 py-1 rounded-full bg-surface-secondary border border-subtle text-secondary">
            4 ACTIVE SIGNALS
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {reviewSignals.map(sig => {
            const Icon = sig.icon
            return (
              <div
                key={sig.id}
                className="interactive-card p-4 rounded-card bg-surface border border-subtle flex flex-col justify-between hover:bg-surface-secondary/30 transition-all cursor-pointer group"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className={`p-1.5 rounded-control border flex items-center justify-center ${sig.bgColor} ${sig.color}`}>
                      <Icon className="w-3.5 h-3.5" />
                    </span>
                    <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-accent-emerald/10 border border-accent-emerald/20 text-accent-emerald">
                      {sig.confidence} Confidence
                    </span>
                  </div>
                  <h4 className="font-semibold text-xs text-primary leading-tight group-hover:text-accent-violet transition-colors">
                    {sig.title}
                  </h4>
                  <p className="text-[11px] text-secondary mt-1.5 leading-relaxed">
                    {sig.description}
                  </p>
                </div>

                <div className="flex items-center justify-between text-[10px] font-mono text-secondary pt-3 mt-3 border-t border-subtle/60">
                  <span className="px-1.5 py-0.5 rounded bg-surface-secondary border border-subtle/50 text-secondary">
                    {sig.source}
                  </span>
                  <span className="flex items-center gap-1 group-hover:text-primary transition-colors">
                    <span>Inspect Pathway</span>
                    <ChevronRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
