// VERITAS - Axios API Client
// Configured Axios instance with baseURL and error interceptors.
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export default client
