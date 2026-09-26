// VERITAS - Axios API Client
// Configured Axios instance with baseURL and error interceptors.
import axios from 'axios'

// Prefer VITE_API_URL, fallback to VITE_API_BASE_URL, default to local Vite dev proxy '/api/v1'
const rawApiUrl = (
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  '/api/v1'
).trim().replace(/\/+$/, '')

// If raw domain without /api/v1 is supplied (e.g. https://veritas-backend.onrender.com), append /api/v1
const baseURL =
  rawApiUrl.endsWith('/api/v1') || rawApiUrl === '/api/v1'
    ? rawApiUrl
    : rawApiUrl.startsWith('http')
    ? `${rawApiUrl}/api/v1`
    : rawApiUrl

const client = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default client
