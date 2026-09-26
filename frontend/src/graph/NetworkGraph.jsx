import React, { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'
import cola from 'cytoscape-cola'
import fcose from 'cytoscape-fcose'
import { getCytoscapeStyles } from './graphStyles'
import { highlightPath, resetGraphHighlight, layoutPresets } from './graphUtils'
import { useTheme } from '../context/ThemeContext'

// Register layout plugins safely once
try {
  cytoscape.use(cola)
  cytoscape.use(fcose)
} catch (e) {
  // Already registered or fallback available
}

export default function NetworkGraph({
  graphData,
  onSelectNode,
  onSelectEdge,
  selectedNodeId,
  selectedEdgeId,
  activePath,
  onInitCy,
}) {
  const containerRef = useRef(null)
  const cyRef = useRef(null)
  const activeLayoutRef = useRef(null)
  const { theme } = useTheme()

  // Initialize or re-hydrate Cytoscape
  useEffect(() => {
    if (!containerRef.current || !graphData) return

    const elements = [
      ...(graphData.nodes || []),
      ...(graphData.edges || []),
    ]

    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: getCytoscapeStyles(theme),
      layout: { name: 'preset' },
      minZoom: 0.2,
      maxZoom: 3.5,
      wheelSensitivity: 0.25,
      boxSelectionEnabled: false,
    })

    cyRef.current = cy
    if (onInitCy) onInitCy(cy)

    // Run cose layout safely
    try {
      const layout = cy.layout(layoutPresets.cose)
      activeLayoutRef.current = layout
      layout.run()
    } catch (e) {
      console.warn('Initial layout warning:', e)
    }

    // Node Tap Event
    cy.on('tap', 'node', evt => {
      const node = evt.target
      cy.elements().removeClass('selected')
      node.addClass('selected')
      if (onSelectNode) onSelectNode(node.data())
    })

    // Edge Tap Event
    cy.on('tap', 'edge', evt => {
      const edge = evt.target
      cy.elements().removeClass('selected')
      edge.addClass('selected')
      if (onSelectEdge) onSelectEdge(edge.data())
    })

    // Background Tap Event (Clear selection)
    cy.on('tap', evt => {
      if (evt.target === cy) {
        cy.elements().removeClass('selected')
        if (onSelectNode) onSelectNode(null)
        if (onSelectEdge) onSelectEdge(null)
      }
    })

    return () => {
      try {
        if (activeLayoutRef.current) {
          activeLayoutRef.current.stop()
          activeLayoutRef.current = null
        }
      } catch (err) {}

      try {
        cy.stop()
        cy.removeAllListeners()
        cy.destroy()
      } catch (err) {
        // cleanup
      }
      cyRef.current = null
      if (onInitCy) onInitCy(null)
    }
  }, [graphData])

  // Update styles on theme switch
  useEffect(() => {
    if (cyRef.current && typeof cyRef.current.destroyed === 'function' && !cyRef.current.destroyed()) {
      try {
        cyRef.current.style(getCytoscapeStyles(theme))
      } catch (e) {}
    }
  }, [theme])

  // React to activePath changes
  useEffect(() => {
    if (!cyRef.current || (typeof cyRef.current.destroyed === 'function' && cyRef.current.destroyed())) return
    try {
      if (activePath && activePath.nodes && activePath.nodes.length > 0) {
        highlightPath(cyRef.current, activePath.nodes, activePath.edges)
      } else {
        resetGraphHighlight(cyRef.current)
      }
    } catch (e) {}
  }, [activePath])

  // React to selectedNodeId change from external components
  useEffect(() => {
    if (!cyRef.current || (typeof cyRef.current.destroyed === 'function' && cyRef.current.destroyed())) return
    try {
      if (selectedNodeId) {
        const target = cyRef.current.$id(selectedNodeId)
        if (target.length > 0) {
          cyRef.current.elements().removeClass('selected')
          target.addClass('selected')
        }
      }
    } catch (e) {}
  }, [selectedNodeId])

  return (
    <div className="w-full h-full relative cytoscape-canvas-container select-none">
      <div ref={containerRef} className="w-full h-full" />
    </div>
  )
}
