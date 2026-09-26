// VERITAS - Cytoscape Visual Stylesheet
// Calm, editorial styling adhering to the master design prompt.

export const getCytoscapeStyles = (theme = 'light') => {
  const isDark = theme === 'dark'

  const textPrimary = isDark ? '#F1F2F6' : '#16181B'
  const textSecondary = isDark ? '#99A0B4' : '#747770'
  const edgeDefault = isDark ? '#2A3344' : '#D8D9D4'
  const edgeHighlight = isDark ? '#9B93FF' : '#635BFF'
  const pathEdge = isDark ? '#FF9A7B' : '#E85D3F'

  // Entity node palette
  const colors = {
    Person: isDark ? '#9B93FF' : '#635BFF',
    Phone: isDark ? '#72DBEF' : '#0088A8',
    Organization: isDark ? '#B28DFF' : '#7E45E8',
    Vehicle: isDark ? '#F5B041' : '#D48207',
    Location: isDark ? '#79D8AD' : '#1F9E66',
    BankAccount: isDark ? '#64B5F6' : '#1E88E5',
    Event: isDark ? '#FF9A7B' : '#E85D3F',
  }

  return [
    // Base Node Style
    {
      selector: 'node',
      style: {
        'label': 'data(label)',
        'color': textPrimary,
        'font-family': 'Plus Jakarta Sans, Inter, system-ui, sans-serif',
        'font-size': '11px',
        'font-weight': 600,
        'text-valign': 'bottom',
        'text-margin-y': 6,
        'text-background-opacity': isDark ? 0.85 : 0.8,
        'text-background-color': isDark ? '#171D2B' : '#FFFFFF',
        'text-background-padding': '3px 5px',
        'text-background-shape': 'roundrectangle',
        'width': 28,
        'height': 28,
        'background-color': ele => colors[ele.data('type')] || (isDark ? '#9B93FF' : '#635BFF'),
        'border-width': 2,
        'border-color': isDark ? '#171D2B' : '#FFFFFF',
        'transition-property': 'background-color, border-color, border-width, opacity, width, height',
        'transition-duration': '0.2s',
      },
    },

    // Entity Specific Shapes
    {
      selector: 'node[type = "Person"]',
      style: {
        'shape': 'ellipse',
        'width': 32,
        'height': 32,
      },
    },
    {
      selector: 'node[type = "Phone"]',
      style: {
        'shape': 'round-rectangle',
        'width': 26,
        'height': 26,
      },
    },
    {
      selector: 'node[type = "Organization"]',
      style: {
        'shape': 'round-hexagon',
        'width': 30,
        'height': 30,
      },
    },
    {
      selector: 'node[type = "Vehicle"]',
      style: {
        'shape': 'round-tag',
        'width': 28,
        'height': 28,
      },
    },
    {
      selector: 'node[type = "Location"]',
      style: {
        'shape': 'diamond',
        'width': 30,
        'height': 30,
      },
    },
    {
      selector: 'node[type = "BankAccount"]',
      style: {
        'shape': 'round-diamond',
        'width': 28,
        'height': 28,
      },
    },

    // Selected Node State
    {
      selector: 'node:selected, node.selected',
      style: {
        'border-width': 4,
        'border-color': isDark ? '#FFFFFF' : '#16181B',
        'border-opacity': 0.9,
        'width': 36,
        'height': 36,
        'z-index': 999,
      },
    },

    // Base Edge Style
    {
      selector: 'edge',
      style: {
        'width': 1.5,
        'line-color': edgeDefault,
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle',
        'target-arrow-color': edgeDefault,
        'arrow-scale': 0.8,
        'opacity': 0.85,
        'transition-property': 'line-color, target-arrow-color, width, opacity',
        'transition-duration': '0.2s',
      },
    },

    // Edge on Hover or Selected
    {
      selector: 'edge:selected, edge.selected',
      style: {
        'width': 2.8,
        'line-color': edgeHighlight,
        'target-arrow-color': edgeHighlight,
        'label': 'data(type)',
        'font-family': 'Inter, system-ui, sans-serif',
        'font-size': '10px',
        'font-weight': 600,
        'color': textPrimary,
        'text-background-opacity': 0.9,
        'text-background-color': isDark ? '#171D2B' : '#FFFFFF',
        'text-background-padding': '2px 4px',
        'text-background-shape': 'roundrectangle',
        'z-index': 998,
      },
    },

    // Multi-Hop Path Highlight
    {
      selector: 'node.path-highlight',
      style: {
        'border-width': 4,
        'border-color': pathEdge,
        'z-index': 1000,
      },
    },
    {
      selector: 'edge.path-highlight',
      style: {
        'width': 3.2,
        'line-color': pathEdge,
        'target-arrow-color': pathEdge,
        'label': 'data(type)',
        'font-family': 'Inter, system-ui, sans-serif',
        'font-size': '10px',
        'font-weight': 700,
        'color': textPrimary,
        'text-background-opacity': 0.95,
        'text-background-color': isDark ? '#171D2B' : '#FFFFFF',
        'text-background-padding': '3px 6px',
        'z-index': 999,
      },
    },

    // Faded State for Non-Selected / Non-Path Nodes
    {
      selector: '.faded',
      style: {
        'opacity': 0.18,
        'text-opacity': 0.1,
      },
    },
  ]
}
