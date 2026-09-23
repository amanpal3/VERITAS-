// VERITAS - Analytics API Calls
import client from './client'

export const getCentrality = (metric) => client.get('/analytics/centrality', { params: { metric } })
export const getCommunities = () => client.get('/communities')
export const getShortestPath = (source, target) => client.get('/paths/shortest', { params: { source, target } })
