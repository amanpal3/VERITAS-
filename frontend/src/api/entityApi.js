// VERITAS - Entity API Calls
import client from './client'

export const getEntities = (params) => client.get('/entities', { params })
export const getEntityById = (id) => client.get(`/entities/${id}`)
