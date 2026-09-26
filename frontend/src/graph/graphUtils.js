// VERITAS - Cytoscape Utility Helpers

export const layoutPresets = {
  fcose: {
    name: 'fcose',
    quality: 'proof',
    randomize: false,
    animate: true,
    animationDuration: 400,
    fit: true,
    padding: 40,
    nodeDimensionsIncludeLabels: true,
    uniformNodeDimensions: false,
    packComponents: true,
    nodeRepulsion: node => 4500,
    idealEdgeLength: edge => 100,
    edgeElasticity: edge => 0.45,
    gravity: 0.25,
  },
  cola: {
    name: 'cola',
    animate: true,
    refresh: 1,
    maxSimulationTime: 2000,
    ungrabifyWhileSimulating: false,
    fit: true,
    padding: 30,
    nodeSpacing: 45,
  },
  cose: {
    name: 'cose',
    animate: false,
    fit: true,
    padding: 40,
    nodeRepulsion: 8000,
    idealEdgeLength: 80,
  },
}

export function highlightPath(cy, nodeIds = [], edgeIds = []) {
  if (!cy || (typeof cy.destroyed === 'function' && cy.destroyed())) return

  try {
    cy.batch(() => {
      // Fade everything
      cy.elements().addClass('faded').removeClass('path-highlight')

      // Unfade and highlight path nodes
      nodeIds.forEach(id => {
        const node = cy.$id(id)
        if (node.length > 0) {
          node.removeClass('faded').addClass('path-highlight')
        }
      })

      // Unfade and highlight path edges
      edgeIds.forEach(id => {
        const edge = cy.$id(id)
        if (edge.length > 0) {
          edge.removeClass('faded').addClass('path-highlight')
        }
      })
    })
  } catch (e) {
    // Cy instance may be tearing down
  }
}

export function resetGraphHighlight(cy) {
  if (!cy || (typeof cy.destroyed === 'function' && cy.destroyed())) return
  try {
    cy.batch(() => {
      cy.elements().removeClass('faded').removeClass('path-highlight')
    })
  } catch (e) {
    // Cy instance may be tearing down
  }
}

export function focusNode(cy, nodeId) {
  if (!cy || (typeof cy.destroyed === 'function' && cy.destroyed()) || !nodeId) return
  try {
    const node = cy.$id(nodeId)
    if (node.length > 0) {
      cy.animate({
        center: { eles: node },
        zoom: 1.4,
        duration: 350,
      })
    }
  } catch (e) {
    // Cy instance may be tearing down
  }
}
