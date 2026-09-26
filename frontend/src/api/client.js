// VERITAS - Axios API Client
// Standardized client with baseURL resolution and error interceptors.
import axios from 'axios'

/**
 * Resolves the API base URL with full tolerance for:
 * 1. Root domain: "https://backend.onrender.com" -> appends "/api/v1"
 * 2. Versioned domain: "https://backend.onrender.com/api/v1" -> preserves "/api/v1"
 * 3. Local dev fallback: undefined / "" -> defaults to "/api/v1" (handled by Vite proxy)
 */
function resolveBaseUrl() {
  const raw = (
    import.meta.env.VITE_API_URL ||
    import.meta.env.VITE_API_BASE_URL ||
    '/api/v1'
  ).trim().replace(/\/+$/, '')

  if (!raw || raw === '/api/v1' || raw.endsWith('/api/v1')) {
    return raw || '/api/v1'
  }

  // If a full domain without /api/v1 is supplied (e.g. Render RENDER_EXTERNAL_URL), append /api/v1
  if (raw.startsWith('http://') || raw.startsWith('https://')) {
    return `${raw}/api/v1`
  }

  return raw
}

export const API_BASE_URL = resolveBaseUrl()

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

// Global response error interceptor for graceful error telemetry
client.interceptors.response.use(
  response => response,
  error => {
    const status = error.response ? error.response.status : null
    const url = error.config ? error.config.url : ''
    console.warn(`[API] ${error.config?.method?.toUpperCase() || 'REQUEST'} ${url} failed [${status || 'NETWORK_ERROR'}]: ${error.message}`)
    return Promise.reject(error)
  }
)

export default client
