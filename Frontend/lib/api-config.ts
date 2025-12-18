// Configuration de l'URL du backend FastAPI
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Helper pour construire les URLs
export const getApiUrl = (endpoint: string) => {
  return `${API_BASE_URL}${endpoint}`
}