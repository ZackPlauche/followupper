/**
 * Composable for making authenticated API calls
 * Handles CSRF tokens, credentials, and error handling
 */
export const useApiFetch = () => {
  const config = useRuntimeConfig()
  const API_BASE = config.public.apiBase || 'http://localhost:8001/api'

  // Store CSRF token in memory (since we can't reliably read cross-domain cookies)
  let csrfTokenCache = null

  /**
   * Get CSRF token from cache or cookies
   */
  const getCsrfToken = () => {
    // First try cache
    if (csrfTokenCache) {
      return csrfTokenCache
    }
    
    // Then try cookies (works for same-domain)
    const name = 'csrftoken'
    const cookies = document.cookie.split(';')
    for (let cookie of cookies) {
      const [key, value] = cookie.trim().split('=')
      if (key === name) {
        const token = decodeURIComponent(value)
        csrfTokenCache = token
        return token
      }
    }
    return null
  }
  
  /**
   * Set CSRF token in cache
   */
  const setCsrfToken = (token) => {
    csrfTokenCache = token
  }

  /**
   * Ensure CSRF token is available by fetching it if needed
   * Note: This should only be called for authenticated requests
   */
  const ensureCsrfToken = async () => {
    let token = getCsrfToken()
    if (!token) {
      // Try to get CSRF token from a simple GET request to any endpoint
      // The backend should set the CSRF cookie on any request
      try {
        // Use a simple endpoint that doesn't require auth to get CSRF token
        // Try health endpoint first, fallback to any public endpoint
        try {
          await fetch(`${API_BASE}/health/`, {
            method: 'GET',
            credentials: 'include'
          })
        } catch (e) {
          // If health doesn't exist, try a simple GET to contacts (will fail but sets CSRF cookie)
          await fetch(`${API_BASE}/contacts/`, {
            method: 'GET',
            credentials: 'include'
          })
        }
        token = getCsrfToken()
      } catch (e) {
        // If all else fails, the token might already be set from a previous request
        console.warn('Could not fetch CSRF token:', e)
      }
    }
    return token
  }

  /**
   * Generic API fetch with authentication and CSRF handling
   * @param {string} endpoint - API endpoint (e.g., '/contacts/')
   * @param {object} options - Fetch options (method, body, headers, etc.)
   * @param {boolean} requireAuth - Whether to include CSRF token (default: true)
   * @returns {Promise<Response>}
   */
  const apiFetch = async (endpoint, options = {}, requireAuth = true) => {
    const headers = {
      ...options.headers
    }

    // Only set Content-Type if not FormData (FormData sets its own Content-Type with boundary)
    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json'
    }

    // Determine if this is a state-changing request that needs CSRF protection
    const method = (options.method || 'GET').toUpperCase()
    const isStateChanging = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)
    const isAuthEndpoint = endpoint.includes('/auth/login/') || endpoint.includes('/auth/register/')
    
    // Add CSRF token for:
    // 1. State-changing requests (POST, PUT, DELETE, etc.) - ALWAYS need CSRF
    // 2. Authenticated requests (unless it's login/register which don't need it initially)
    if (isStateChanging || (requireAuth && !isAuthEndpoint)) {
      // Try to get CSRF token, and fetch it if needed
      let csrfToken = getCsrfToken()
      if (!csrfToken) {
        // For state-changing requests, we MUST have a CSRF token
        // Try to get it by making a GET request first
        try {
          await fetch(`${API_BASE}/health/`, {
            method: 'GET',
            credentials: 'include'
          })
          csrfToken = getCsrfToken()
        } catch (e) {
          console.warn('Could not fetch CSRF token:', e)
        }
      }
      
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken
      } else if (isStateChanging) {
        // For state-changing requests, we MUST have CSRF token
        console.error('CSRF token not available for state-changing request:', method, endpoint)
      }
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
      credentials: 'include' // Always include cookies for session auth
    })

    // Extract CSRF token from response headers (for cross-domain)
    const csrfTokenFromHeader = response.headers.get('X-CSRFToken')
    if (csrfTokenFromHeader) {
      setCsrfToken(csrfTokenFromHeader)
    }

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

    return await response.json()
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
    apiCallWithRetry,
    getCsrfToken,
    setCsrfToken,
    ensureCsrfToken
  }
}

