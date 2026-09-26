import React, { useEffect, useState } from 'react'
import {
  BarChart2,
  TrendingUp,
  Share2,
  Users,
  Layers,
  Activity,
  ShieldCheck,
  ChevronRight,
} from 'lucide-react'
import { getCentrality, getCommunities } from '../api/analyticsApi'
import { getGraphData } from '../api/graphApi'
import CentralityChart from '../charts/CentralityChart'
import CommunityChart from '../charts/CommunityChart'
import { CrimeIntelligenceSeal } from '../components/common/DetectiveLogos'

export default function Analytics() {
  const [metric, setMetric] = useState('betweenness')
  const [centralityData, setCentralityData] = useState([])
  const [communities, setCommunities] = useState([])
  const [graphMeta, setGraphMeta] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    setIsLoading(true)
    Promise.all([
      getCentrality(metric),
      getCommunities(),
      getGraphData(),
    ])
      .then(([centRes, commRes, graphRes]) => {
        setCentralityData(centRes.data.rankings || [])
        setCommunities(commRes.data.communities || [])
        setGraphMeta(graphRes.data.metadata || {})
        setIsLoading(false)
      })
      .catch(err => {
        console.error('Failed to load analytics:', err)
        setIsLoading(false)
      })
  }, [metric])

  return (
    <div className="space-y-8 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="flex items-start gap-4 border-b border-subtle/80 pb-6">
        <CrimeIntelligenceSeal className="w-12 h-12 shrink-0 hidden sm:block shadow-xs" />
        <div>
          <span className="text-[10px] font-bold uppercase tracking-widest text-accent-violet block mb-1 font-mono">
            GRAPH TOPOLOGY & SYNDICATE STRUCTURE // LOUVAIN MODULARITY
          </span>
          <h1 className="font-display font-bold text-2xl sm:text-3xl text-primary tracking-tight">
            Network Analytics & Structure
          </h1>
          <p className="text-xs sm:text-sm text-secondary mt-1 max-w-2xl leading-relaxed">
            Measure network density, betweenness gatekeepers, and Louvain modularity communities without losing evidentiary context.
          </p>
        </div>
      </div>

      {/* Structural Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-card bg-surface border border-subtle shadow-card interactive-card">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-[10px] font-semibold uppercase tracking-widest text-secondary/90">Network Density</span>
            <Activity className="w-4 h-4 text-accent-violet" />
          </div>
          <div className="font-display text-2xl sm:text-3xl font-bold text-primary tabular-nums">
            0.081
          </div>
          <div className="text-[11px] text-secondary mt-1 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-violet/60" />
            <span>Sparse multi-layer graph</span>
          </div>
        </div>

        <div className="p-5 rounded-card bg-surface border border-subtle shadow-card interactive-card">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-[10px] font-semibold uppercase tracking-widest text-secondary/90">Components</span>
            <Share2 className="w-4 h-4 text-accent-cyan" />
          </div>
          <div className="font-display text-2xl sm:text-3xl font-bold text-primary tabular-nums">
            1 Major
          </div>
          <div className="text-[11px] text-secondary mt-1 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan/60" />
            <span>Giant connected component</span>
          </div>
        </div>

        <div className="p-5 rounded-card bg-surface border border-subtle shadow-card interactive-card">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-[10px] font-semibold uppercase tracking-widest text-secondary/90">Average Degree</span>
            <TrendingUp className="w-4 h-4 text-accent-emerald" />
          </div>
          <div className="font-display text-2xl sm:text-3xl font-bold text-primary tabular-nums">
            2.28
          </div>
          <div className="text-[11px] text-secondary mt-1 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald/60" />
            <span>Edges per entity</span>
          </div>
        </div>

        <div className="p-5 rounded-card bg-surface border border-subtle shadow-card interactive-card">
          <div className="flex items-center justify-between text-secondary mb-2">
            <span className="text-[10px] font-semibold uppercase tracking-widest text-secondary/90">Detected Cells</span>
            <Layers className="w-4 h-4 text-[#B28DFF]" />
          </div>
          <div className="font-display text-2xl sm:text-3xl font-bold text-primary tabular-nums">
            0{communities.length || 3}
          </div>
          <div className="text-[11px] text-secondary mt-1 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#B28DFF]/60" />
            <span>Louvain modularity clusters</span>
          </div>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Centrality Chart Card */}
        <div className="p-6 rounded-card bg-surface border border-subtle shadow-card space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-subtle">
            <div>
              <h2 className="font-display font-bold text-base text-primary">
                Entity Centrality Rankings
              </h2>
              <p className="text-xs text-secondary mt-0.5">
                Key influencers and gatekeepers identified by structural position.
              </p>
            </div>

            {/* Metric Switcher */}
            <div className="flex items-center gap-1 p-0.5 rounded-control bg-surface-secondary border border-subtle text-xs">
              {['betweenness', 'pagerank', 'degree'].map(m => (
                <button
                  key={m}
                  onClick={() => setMetric(m)}
                  className={`px-2.5 py-1 rounded text-[11px] capitalize font-medium transition-colors ${
                    metric === m
                      ? 'bg-surface text-primary shadow-xs font-semibold'
                      : 'text-secondary hover:text-primary'
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          <CentralityChart data={centralityData} metric={metric} />

          <p className="text-[11px] text-secondary border-t border-subtle/60 pt-3 leading-normal">
            Betweenness centrality highlights gatekeepers (e.g. Tariq Sheikh) who bridge disparate cells.
            High centrality signifies analytical structural importance, not legal guilt.
          </p>
        </div>

        {/* Communities Chart Card */}
        <div className="p-6 rounded-card bg-surface border border-subtle shadow-card space-y-4">
          <div className="pb-3 border-b border-subtle">
            <h2 className="font-display font-bold text-base text-primary">
              Community Cluster Distribution
            </h2>
            <p className="text-xs text-secondary mt-0.5">
              Partitioning of nodes into functional syndicates using Louvain Modularity.
            </p>
          </div>

          <CommunityChart communities={communities} />

          <p className="text-[11px] text-secondary border-t border-subtle/60 pt-3 leading-normal">
            Cluster labels are derived from entity roles (e.g. Hawala vs. Transport Courier) rather than subjective labeling.
          </p>
        </div>
      </div>

      {/* Community Detail Cards */}
      <div className="rounded-card bg-surface border border-subtle shadow-soft p-6 space-y-4">
        <h3 className="font-display font-bold text-base text-primary">
          Detected Syndicate Cells
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {communities.map(comm => (
            <div
              key={comm.community_id}
              className="p-5 rounded-card bg-surface-secondary/70 border border-subtle space-y-3.5 interactive-card"
            >
              <div className="flex items-center justify-between pb-2 border-b border-subtle/70">
                <span className="font-display font-bold text-base text-primary">
                  Cell 0{comm.community_id}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface border border-subtle text-accent-violet font-semibold">
                  {comm.size} Members
                </span>
              </div>

              <span className="text-xs font-semibold text-primary block leading-tight font-display">
                {comm.label}
              </span>

              <div>
                <span className="text-[10px] text-secondary uppercase font-semibold tracking-wider block mb-1.5">
                  Member Key Entities
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {comm.members.slice(0, 6).map((m, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded bg-surface border border-subtle/70 text-[10px] font-mono text-secondary hover:text-primary transition-colors"
                    >
                      {m}
                    </span>
                  ))}
                  {comm.members.length > 6 && (
                    <span className="text-[10px] text-secondary font-mono self-center px-1">
                      +{comm.members.length - 6} more
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
