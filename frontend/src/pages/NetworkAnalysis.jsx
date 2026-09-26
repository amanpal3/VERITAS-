import React, { useEffect, useState } from 'react'
import {
  Search,
  Filter,
  GitFork,
  Maximize2,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  SlidersHorizontal,
  X,
} from 'lucide-react'
import { getGraphData, getEgoNetwork } from '../api/graphApi'
import { getEntityById } from '../api/entityApi'
import NetworkGraph from '../graph/NetworkGraph'
import EntityInspector from '../components/evidence/EntityInspector'
import RelationshipInspector from '../components/evidence/RelationshipInspector'
import GraphFilters from '../components/filters/GraphFilters'
import PathFinderModal from '../components/common/PathFinderModal'
import { useToast } from '../context/ToastContext'
import { DetectiveBadge } from '../components/common/DetectiveLogos'

export default function NetworkAnalysis() {
  const [graphData, setGraphData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [cyInstance, setCyInstance] = useState(null)

  // Selection states
  const [selectedEntity, setSelectedEntity] = useState(null)
  const [selectedEdge, setSelectedEdge] = useState(null)

  // Modals & Panels
  const [isFilterOpen, setIsFilterOpen] = useState(false)
  const [isPathFinderOpen, setIsPathFinderOpen] = useState(false)
  const [activePath, setActivePath] = useState(null)

  // Filter params
  const [selectedTypes, setSelectedTypes] = useState([
    'Person',
    'Phone',
    'Organization',
    'Vehicle',
    'Location',
    'BankAccount',
  ])
  const [minRisk, setMinRisk] = useState(0)
  const [minWeight, setMinWeight] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')

  const { addToast } = useToast()

  // Load graph with filters
  const loadGraph = () => {
    setIsLoading(true)
    getGraphData({
      min_risk: minRisk,
      min_weight: minWeight,
    })
      .then(res => {
        let filtered = res.data
        if (selectedTypes.length < 6) {
          const typeSet = new Set(selectedTypes.map(t => t.toLowerCase()))
          const nodes = res.data.nodes.filter(n =>
            typeSet.has((n.data.type || '').toLowerCase())
          )
          const validNodeIds = new Set(nodes.map(n => n.data.id))
          const edges = res.data.edges.filter(
            e => validNodeIds.has(e.data.source) && validNodeIds.has(e.data.target)
          )
          filtered = { ...res.data, nodes, edges }
        }
        setGraphData(filtered)
        setIsLoading(false)
      })
      .catch(err => {
        console.error('Failed to load graph:', err)
        setIsLoading(false)
        addToast('Failed to connect to graph service', 'error')
      })
  }

  useEffect(() => {
    loadGraph()
  }, [minRisk, minWeight, selectedTypes])

  // Handle node selection
  const handleSelectNode = async nodeData => {
    if (!nodeData) {
      setSelectedEntity(null)
      return
    }
    setSelectedEdge(null)
    try {
      const res = await getEntityById(nodeData.id)
      setSelectedEntity(res.data.entity)
    } catch (e) {
      setSelectedEntity(nodeData)
    }
  }

  // Handle edge selection
  const handleSelectEdge = edgeData => {
    if (!edgeData) {
      setSelectedEdge(null)
      return
    }
    setSelectedEntity(null)
    setSelectedEdge(edgeData)
  }

  // Ego network exploration
  const handleExploreEgo = async entityId => {
    try {
      const res = await getEgoNetwork(entityId, 1)
      setGraphData({
        metadata: { total_nodes: res.data.nodes.length, total_edges: res.data.edges.length },
        nodes: res.data.nodes,
        edges: res.data.edges,
      })
      addToast(`Ego neighborhood centered on ${entityId}`, 'info')
    } catch (e) {
      addToast('Failed to load ego network', 'error')
    }
  }

  const handleToggleType = type => {
    setSelectedTypes(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    )
  }

  const handleResetFilters = () => {
    setSelectedTypes(['Person', 'Phone', 'Organization', 'Vehicle', 'Location', 'BankAccount'])
    setMinRisk(0)
    setMinWeight(0)
    addToast('Filters reset', 'info')
  }

  // Search node focus
  const handleSearchSubmit = e => {
    e.preventDefault()
    if (!searchQuery.trim() || !cyInstance) return

    const q = searchQuery.toLowerCase().trim()
    const target = cyInstance.nodes().filter(ele => {
      const name = (ele.data('name') || ele.data('label') || '').toLowerCase()
      const id = (ele.data('id') || '').toLowerCase()
      return name.includes(q) || id.includes(q)
    })

    if (target.length > 0) {
      const first = target[0]
      cyInstance.animate({
        center: { eles: first },
        zoom: 1.5,
        duration: 350,
      })
      first.trigger('tap')
      addToast(`Focused on ${first.data('label') || first.data('id')}`, 'success')
    } else {
      addToast(`No entity found matching "${searchQuery}"`, 'error')
    }
  }

  // Extract entities list for PathFinder select inputs
  const allEntitiesList = (graphData?.nodes || []).map(n => ({
    id: n.data.id,
    name: n.data.label || n.data.name || n.data.id,
  }))

  return (
    <div className="h-[calc(100vh-5.5rem)] flex flex-col relative rounded-card overflow-hidden border border-subtle bg-surface shadow-card">
      {/* Top Floating Toolbar */}
      <div className="p-3 border-b border-subtle bg-surface-secondary/50 flex flex-wrap items-center justify-between gap-3 z-20">
        <div className="flex items-center gap-2.5">
          <div className="p-1 rounded-control bg-accent-violet/10 border border-accent-violet/25 shadow-xs shrink-0 hidden sm:flex items-center" title="Bureau of Criminal Intelligence">
            <DetectiveBadge className="w-5 h-6 text-accent-violet" />
          </div>
          {/* Search Input with Forensic Indicator */}
          <form onSubmit={handleSearchSubmit} className="relative w-64 sm:w-80">
          <Search className="w-3.5 h-3.5 text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search entity, phone, organization..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full text-xs pl-9 pr-14 py-2 rounded-control bg-surface border border-subtle text-primary placeholder:text-secondary focus:outline-none focus:border-accent-violet transition-colors font-medium"
          />
          <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[9px] font-mono font-medium px-1.5 py-0.5 rounded bg-surface-secondary border border-subtle text-secondary pointer-events-none select-none">
            ↵ JUMP
          </kbd>
        </form>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {/* Path Finder Trigger */}
          <button
            onClick={() => setIsPathFinderOpen(true)}
            className={`px-3 py-1.5 rounded-control text-xs font-medium border flex items-center gap-1.5 transition-all shadow-xs ${
              activePath
                ? 'bg-accent-coral/10 border-accent-coral/30 text-accent-coral font-semibold'
                : 'bg-surface border-subtle text-secondary hover:text-primary hover:border-subtle/80'
            }`}
          >
            <GitFork className="w-3.5 h-3.5" />
            <span>Trace Connection</span>
            {activePath && (
              <span
                onClick={e => {
                  e.stopPropagation()
                  setActivePath(null)
                }}
                className="ml-1 hover:text-primary p-0.5 rounded-full hover:bg-accent-coral/20"
                title="Clear path"
              >
                <X className="w-3 h-3" />
              </span>
            )}
          </button>

          {/* Filter Popover Trigger */}
          <button
            onClick={() => setIsFilterOpen(!isFilterOpen)}
            className={`px-3 py-1.5 rounded-control text-xs font-medium border flex items-center gap-1.5 transition-all shadow-xs ${
              selectedTypes.length < 6 || minRisk > 0
                ? 'bg-accent-violet/10 border-accent-violet/30 text-accent-violet font-semibold'
                : 'bg-surface border-subtle text-secondary hover:text-primary hover:border-subtle/80'
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
            <span>Filter Graph</span>
            {(selectedTypes.length < 6 || minRisk > 0) && (
              <span className="w-1.5 h-1.5 rounded-full bg-accent-violet animate-pulse" />
            )}
          </button>

          {/* Canvas Actions */}
          <div className="hidden sm:flex items-center gap-1 border-l border-subtle pl-2">
            <button
              onClick={() => cyInstance?.fit(40)}
              title="Fit Graph to View"
              className="p-1.5 rounded-control bg-surface border border-subtle text-secondary hover:text-primary hover:border-subtle/80 transition-colors shadow-xs"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => cyInstance?.zoom(cyInstance.zoom() * 1.2)}
              title="Zoom In (+20%)"
              className="p-1.5 rounded-control bg-surface border border-subtle text-secondary hover:text-primary hover:border-subtle/80 transition-colors shadow-xs"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => cyInstance?.zoom(cyInstance.zoom() * 0.8)}
              title="Zoom Out (-20%)"
              className="p-1.5 rounded-control bg-surface border border-subtle text-secondary hover:text-primary hover:border-subtle/80 transition-colors shadow-xs"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={loadGraph}
              title="Reset Layout & Re-center"
              className="p-1.5 rounded-control bg-surface border border-subtle text-secondary hover:text-primary hover:border-subtle/80 transition-colors shadow-xs"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Workspace Area (Graph + Inspectors) */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Interactive Cytoscape Canvas */}
        <div className="flex-1 h-full relative">
          {/* Active Connection Path Telemetry Banner */}
          {activePath && (
            <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 px-4 py-2 rounded-card bg-surface/95 backdrop-blur-md border border-accent-coral/30 shadow-card flex items-center gap-3 animate-in fade-in slide-in-from-top-2 duration-200 select-none">
              <span className="w-2 h-2 rounded-full bg-accent-coral animate-ping" />
              <div className="flex items-center gap-1.5 text-xs font-semibold text-primary">
                <span>Path Discovery:</span>
                <span className="font-mono text-accent-coral px-1.5 py-0.5 rounded bg-accent-coral/10">
                  {activePath.nodes[0]}
                </span>
                <span className="text-secondary text-[10px]">➔</span>
                <span className="font-mono text-accent-coral px-1.5 py-0.5 rounded bg-accent-coral/10">
                  {activePath.nodes[activePath.nodes.length - 1]}
                </span>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-secondary border border-subtle text-secondary">
                {activePath.length} Hops
              </span>
              <button
                type="button"
                onClick={() => {
                  if (cyInstance && activePath.nodes) {
                    const eles = cyInstance.nodes().filter(n => activePath.nodes.includes(n.id()))
                    cyInstance.fit(eles, 80)
                  }
                }}
                className="text-[11px] text-accent-violet hover:underline font-semibold"
              >
                Center Path
              </button>
              <button
                type="button"
                onClick={() => setActivePath(null)}
                className="text-secondary hover:text-primary p-1 rounded-full hover:bg-surface-secondary transition-colors"
                title="Clear Path Highlight"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {isLoading ? (
            <div className="w-full h-full flex flex-col items-center justify-center gap-3 text-xs text-secondary">
              <span className="w-7 h-7 border-2 border-accent-violet border-t-transparent rounded-full animate-spin" />
              <span className="font-medium tracking-wide">Hydrating graph nodes and relationships...</span>
            </div>
          ) : (
            <NetworkGraph
              graphData={graphData}
              selectedNodeId={selectedEntity?.id}
              selectedEdgeId={selectedEdge?.id}
              activePath={activePath}
              onSelectNode={handleSelectNode}
              onSelectEdge={handleSelectEdge}
              onInitCy={cy => setCyInstance(cy)}
            />
          )}

          {/* Quick Legend Overlay in bottom left */}
          <div className="absolute bottom-4 left-4 p-3 rounded-card bg-surface/95 backdrop-blur-md border border-subtle shadow-card text-[10px] text-secondary flex flex-col gap-2 select-none z-10">
            <div className="flex items-center justify-between gap-4 border-b border-subtle/60 pb-1.5 text-[9px] font-mono font-semibold tracking-wider uppercase text-secondary/80">
              <span>LEGEND // CLASSIFICATION</span>
              <span>6 TYPES</span>
            </div>
            <div className="flex items-center gap-3.5">
              <span className="flex items-center gap-1.5 cursor-pointer hover:text-primary" onClick={() => handleToggleType('Person')}>
                <span className="w-2 h-2 rounded-full bg-accent-violet shadow-xs" />
                Person
              </span>
              <span className="flex items-center gap-1.5 cursor-pointer hover:text-primary" onClick={() => handleToggleType('Phone')}>
                <span className="w-2 h-2 rounded-full bg-accent-cyan shadow-xs" />
                Phone
              </span>
              <span className="flex items-center gap-1.5 cursor-pointer hover:text-primary" onClick={() => handleToggleType('Organization')}>
                <span className="w-2 h-2 rounded-full bg-[#B28DFF] shadow-xs" />
                Org
              </span>
              <span className="flex items-center gap-1.5 cursor-pointer hover:text-primary" onClick={() => handleToggleType('Vehicle')}>
                <span className="w-2 h-2 rounded-full bg-accent-amber shadow-xs" />
                Vehicle
              </span>
              <span className="flex items-center gap-1.5 cursor-pointer hover:text-primary" onClick={() => handleToggleType('Location')}>
                <span className="w-2 h-2 rounded-full bg-accent-emerald shadow-xs" />
                Location
              </span>
              <span className="flex items-center gap-1.5 cursor-pointer hover:text-primary" onClick={() => handleToggleType('BankAccount')}>
                <span className="w-2 h-2 rounded-full bg-accent-blue shadow-xs" />
                Account
              </span>
            </div>
          </div>
        </div>

        {/* Right-Side Entity Inspector */}
        {selectedEntity && (
          <EntityInspector
            entity={selectedEntity}
            onClose={() => setSelectedEntity(null)}
            onSelectEntity={id => handleSelectNode({ id })}
            onExploreConnections={handleExploreEgo}
          />
        )}

        {/* Right-Side Relationship Inspector */}
        {selectedEdge && (
          <RelationshipInspector
            edge={selectedEdge}
            onClose={() => setSelectedEdge(null)}
            onSelectEntity={id => handleSelectNode({ id })}
          />
        )}
      </div>

      {/* Floating Filter Popover */}
      <GraphFilters
        isOpen={isFilterOpen}
        onClose={() => setIsFilterOpen(false)}
        selectedTypes={selectedTypes}
        onToggleType={handleToggleType}
        minRisk={minRisk}
        onChangeMinRisk={setMinRisk}
        minWeight={minWeight}
        onChangeMinWeight={setMinWeight}
        onResetFilters={handleResetFilters}
      />

      {/* Path Finder Modal */}
      <PathFinderModal
        isOpen={isPathFinderOpen}
        onClose={() => setIsPathFinderOpen(false)}
        entities={allEntitiesList}
        onPathFound={path => {
          setActivePath(path)
          setIsPathFinderOpen(false)
        }}
        onClearPath={() => setActivePath(null)}
      />
    </div>
  )
}
