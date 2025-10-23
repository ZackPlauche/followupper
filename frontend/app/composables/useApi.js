// Global state management for API data
export const useApi = () => {
  // Global reactive state using Nuxt's useState
  const contacts = useState('contacts', () => [])
  const templates = useState('templates', () => [])
  const schedule = useState('schedule', () => [])
  const isLoading = useState('isLoading', () => false)
  const error = useState('error', () => null)

  // API base URL
  const API_BASE = 'http://localhost:5000/api'

  // Status message helper
  const showStatus = (message, duration = 5000) => {
    // This will be handled by individual pages
    console.log('Status:', message)
  }

  // Enhanced status helper with progress bar
  const showStatusWithProgress = (message, duration = 5000) => {
    // This will be handled by individual pages
    console.log('Status with progress:', message)
  }

  // Generic API call with retry logic
  const apiCall = async (endpoint, options = {}, retries = 3) => {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
          headers: {
            'Content-Type': 'application/json',
            ...options.headers
          },
          ...options
        })
        
        if (response.ok) {
          return await response.json()
        }
        
        if (i === retries - 1) {
          throw new Error(`API Error: ${response.status}`)
        }
      } catch (error) {
        console.error(`API call failed (attempt ${i + 1}):`, error)
        if (i === retries - 1) {
          throw error
        }
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
    }
  }

  // Load contacts
  const loadContacts = async () => {
    isLoading.value = true
    try {
      const data = await apiCall('/contacts')
      contacts.value = data
      return data
    } catch (error) {
      console.error('Error loading contacts:', error)
      error.value = error.message
      return []
    } finally {
      isLoading.value = false
    }
  }

  // Load templates
  const loadTemplates = async () => {
    isLoading.value = true
    try {
      const data = await apiCall('/templates')
      templates.value = data
      return data
    } catch (error) {
      console.error('Error loading templates:', error)
      error.value = error.message
      return []
    } finally {
      isLoading.value = false
    }
  }

  // Load schedule
  const loadSchedule = async () => {
    isLoading.value = true
    try {
      const data = await apiCall('/schedule')
      schedule.value = data
      return data
    } catch (error) {
      console.error('Error loading schedule:', error)
      error.value = error.message
      return []
    } finally {
      isLoading.value = false
    }
  }

  // Create contact
  const createContact = async (contactData) => {
    try {
      const result = await apiCall('/contacts', {
        method: 'POST',
        body: JSON.stringify(contactData)
      })
      
      return result
    } catch (error) {
      console.error('Error creating contact:', error)
      throw error
    }
  }

  // Update contact
  const updateContact = async (contactId, contactData) => {
    try {
      await apiCall(`/contacts/${contactId}`, {
        method: 'PUT',
        body: JSON.stringify(contactData)
      })
      
      // Update local state
      const index = contacts.value.findIndex(c => c.id === contactId)
      if (index !== -1) {
        contacts.value[index] = { ...contacts.value[index], ...contactData, updated_at: new Date().toISOString() }
      }
    } catch (error) {
      console.error('Error updating contact:', error)
      throw error
    }
  }

  // Delete contact
  const deleteContact = async (contactId) => {
    try {
      await apiCall(`/contacts/${contactId}`, { method: 'DELETE' })
      
    } catch (error) {
      console.error('Error deleting contact:', error)
      throw error
    }
  }

  // Create template
  const createTemplate = async (templateData) => {
    try {
      const result = await apiCall('/templates', {
        method: 'POST',
        body: JSON.stringify(templateData)
      })
      
      return result
    } catch (error) {
      console.error('Error creating template:', error)
      throw error
    }
  }

  // Update template
  const updateTemplate = async (templateId, templateData) => {
    try {
      await apiCall(`/templates/${templateId}`, {
        method: 'PUT',
        body: JSON.stringify(templateData)
      })
      
    } catch (error) {
      console.error('Error updating template:', error)
      throw error
    }
  }

  // Delete template
  const deleteTemplate = async (templateId) => {
    try {
      await apiCall(`/templates/${templateId}`, { method: 'DELETE' })
      
    } catch (error) {
      console.error('Error deleting template:', error)
      throw error
    }
  }

  // Initialize all data on app startup
  const initializeApp = async () => {
    console.log('🚀 Initializing Followupper app...')
    isLoading.value = true
    
    try {
      await Promise.all([
        loadContacts(),
        loadTemplates(),
        loadSchedule()
      ])
      console.log('✅ App initialized successfully')
    } catch (error) {
      console.error('❌ Error initializing app:', error)
      error.value = error.message
    } finally {
      isLoading.value = false
    }
  }

  // Force refresh all data
  const refreshAll = async () => {
    contacts.value = []
    templates.value = []
    schedule.value = []
    
    await Promise.all([
      loadContacts(),
      loadTemplates(),
      loadSchedule()
    ])
  }

  return {
    // State
    contacts,
    templates,
    schedule,
    isLoading,
    error,
    
    // Methods
    initializeApp,
    loadContacts,
    loadTemplates,
    loadSchedule,
    createContact,
    updateContact,
    deleteContact,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    refreshAll,
    showStatus,
    showStatusWithProgress
  }
}
