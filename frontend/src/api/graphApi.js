// VERITAS - Graph API Calls
import client from './client'

export const getGraphData = (params) => client.get('/graph', { params })
export const getEgoNetwork = (entityId, hops = 1) => client.get(`/graph/ego/${entityId}`, { params: { hops } })
export const getHealth = () => client.get('/health')
