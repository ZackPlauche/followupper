/**
 * Composable for making authenticated API calls
 * Handles CSRF tokens, credentials, and error handling
 */
export const useApiFetch = () => {
  const config = useRuntimeConfig()
  const API_BASE = config.public.apiBase || 'http://localhost:8001/api'


  /**
   * Generic API fetch with authentication
   * @param {string} endpoint - API endpoint (e.g., '/contacts/')
   * @param {object} options - Fetch options (method, body, headers, etc.)
   * @param {boolean} requireAuth - Whether auth is required (for future use, not currently enforced)
   * @returns {Promise<Response>}
   */
  const apiFetch = async (endpoint, options = {}, requireAuth = true) => {
    const headers = {
      ...options.headers
    }

    // Only set Content-Type if not FormData (FormData sets its own Content-Type with boundary)
    // For FormData, we must NOT set Content-Type - let the browser set it with the boundary
    if (options.body instanceof FormData) {
      // Explicitly remove Content-Type if it was set, so browser can set it with boundary
      delete headers['Content-Type']
      delete headers['content-type']
    } else {
      // For JSON, set Content-Type if not already set
      if (!headers['Content-Type'] && !headers['content-type']) {
        headers['Content-Type'] = 'application/json'
      }
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
      credentials: 'include' // Always include cookies for session auth
    })

    return response
  }

  /**
   * API fetch that automatically parses JSON response
   * @param {string} endpoint - API endpoint
   * @param {object} options - Fetch options
   * @param {boolean} requireAuth - Whether to include CSRF token
   * @returns {Promise<object>} Parsed JSON response
   */
  const apiCall = async (endpoint, options = {}, requireAuth = true) => {
    const response = await apiFetch(endpoint, options, requireAuth)
    
    if (!response.ok) {
      // Try to extract error message from response body
      let errorMessage = `API Error: ${response.status}`
      try {
        const errorData = await response.json()
        if (errorData.error) {
          errorMessage = errorData.error
        } else if (errorData.message) {
          errorMessage = errorData.message
        }
      } catch (e) {
        // If response is not JSON, use status code
      }
      const error = new Error(errorMessage)
      error.status = response.status
      error.response = response
      throw error
    }

    // Handle 204 No Content responses (no body to parse)
    if (response.status === 204) {
      return null
    }

    // Check if response has content before parsing
    const contentType = response.headers.get('content-type')
    const contentLength = response.headers.get('content-length')
    
    // If no content-type or content-length is 0, return null
    if (!contentType || (contentLength && parseInt(contentLength) === 0)) {
      return null
    }

    // Try to parse JSON response
    try {
      const text = await response.text()
      if (!text || text.trim() === '') {
        return null
      }
      return JSON.parse(text)
    } catch (e) {
      // If parsing fails, return null for empty responses
      return null
    }
  }

  /**
   * API fetch with retry logic
   * @param {string} endpoint - API endpoint
   * @param {object} options - Fetch options
   * @param {number} retries - Number of retry attempts (default: 3)
   * @param {boolean} requireAuth - Whether to include CSRF token
   * @returns {Promise<object>} Parsed JSON response
   */
  const apiCallWithRetry = async (endpoint, options = {}, retries = 3, requireAuth = true) => {
    for (let i = 0; i < retries; i++) {
      try {
        return await apiCall(endpoint, options, requireAuth)
      } catch (error) {
        console.error(`API call failed (attempt ${i + 1}/${retries}):`, error)
        if (i === retries - 1) {
          throw error
        }
        // Wait before retrying (exponential backoff)
        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)))
      }
    }
  }

  return {
    API_BASE,
    apiFetch,
    apiCall,
    apiCallWithRetry
  }
}

