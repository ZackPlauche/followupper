// Global state management for API data
export const useApi = () => {
  // Use the API fetch composable
  const { apiCallWithRetry } = useApiFetch()

  // Global reactive state using Nuxt's useState
  const contacts = useState('contacts', () => [])
  const templates = useState('templates', () => [])
  const schedule = useState('schedule', () => [])
  const campaigns = useState('campaigns', () => [])
  const settings = useState('settings', () => ({
    gmail: { email: '', app_password: '' },
    codementor: { access_token: '', refresh_token: '' },
    automation: { enabled: false, check_interval: 15, max_retries: 3, timezone: 'UTC' },
    user: { timezone: 'UTC', footer: '', codementor_max_concurrent: 1, codementor_send_interval: 5 }
  }))
  const isLoading = useState('isLoading', () => false)
  const error = useState('error', () => null)

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

  // Generic API call with retry logic (wrapper for backward compatibility)
  const apiCall = async (endpoint, options = {}, retries = 3) => {
    return await apiCallWithRetry(endpoint, options, retries, true)
  }

  // Load contacts
  const loadContacts = async () => {
    isLoading.value = true
    try {
      const data = await apiCall('/contacts/')
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
      const data = await apiCall('/templates/')
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
      const data = await apiCall('/schedule/')
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


  // Load settings
  const loadSettings = async () => {
    isLoading.value = true
    try {
      const data = await apiCall('/settings/')
      settings.value = data
      return data
    } catch (error) {
      console.error('Error loading settings:', error)
      error.value = error.message
      return settings.value // Return current settings on error
    } finally {
      isLoading.value = false
    }
  }

  // Create contact
  const createContact = async (contactData) => {
    try {
      const result = await apiCall('/contacts/', {
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
      await apiCall(`/contacts/${contactId}/`, {
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
      await apiCall(`/contacts/${contactId}/`, { method: 'DELETE' })
      
    } catch (error) {
      console.error('Error deleting contact:', error)
      throw error
    }
  }

  // Create template
  const createTemplate = async (templateData) => {
    try {
      const result = await apiCall('/templates/', {
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
      await apiCall(`/templates/${templateId}/`, {
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
      await apiCall(`/templates/${templateId}/`, { method: 'DELETE' })
      
    } catch (error) {
      console.error('Error deleting template:', error)
      throw error
    }
  }


  // Load campaigns
  const loadCampaigns = async () => {
    isLoading.value = true
    try {
      const data = await apiCall('/campaigns/')
      campaigns.value = data
      return data
    } catch (error) {
      console.error('Error loading campaigns:', error)
      error.value = error.message
      return []
    } finally {
      isLoading.value = false
    }
  }

  // Create campaign
  const createCampaign = async (campaignData) => {
    try {
      const result = await apiCall('/campaigns/', {
        method: 'POST',
        body: JSON.stringify(campaignData)
      })
      return result
    } catch (error) {
      console.error('Error creating campaign:', error)
      throw error
    }
  }

  // Update campaign
  const updateCampaign = async (id, campaignData) => {
    try {
      const result = await apiCall(`/campaigns/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(campaignData)
      })
      // Update the campaign in the local state
      const index = campaigns.value.findIndex(c => c.id === id)
      if (index !== -1) {
        campaigns.value[index] = result
      }
      return result
    } catch (error) {
      console.error('Error updating campaign:', error)
      throw error
    }
  }

  // Delete campaign
  const deleteCampaign = async (id) => {
    try {
      await apiCall(`/campaigns/${id}/`, { method: 'DELETE' })
    } catch (error) {
      console.error('Error deleting campaign:', error)
      throw error
    }
  }

  // Send email (legacy - kept for backward compatibility)
  const sendEmail = async (emailData) => {
    try {
      const result = await apiCall('/settings/send-email/', {
        method: 'POST',
        body: JSON.stringify(emailData)
      })
      return result
    } catch (error) {
      console.error('Error sending email:', error)
      throw error
    }
  }

  // Send message via multiple platforms
  const sendMessage = async (contactId, messageData) => {
    try {
      const result = await apiCall('/settings/send-message/', {
        method: 'POST',
        body: JSON.stringify({
          contact_id: contactId,
          ...messageData
        })
      })
      return result
    } catch (error) {
      console.error('Error sending message:', error)
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
        loadSchedule(),
        loadCampaigns(),
        loadSettings()
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
    campaigns.value = []
    settings.value = {
      gmail: { email: '', app_password: '' },
      codementor: { access_token: '', refresh_token: '' },
      automation: { enabled: false, check_interval: 15, max_retries: 3, timezone: 'UTC' },
      user: { timezone: 'UTC', footer: '', codementor_max_concurrent: 1, codementor_send_interval: 5 }
    }
    
    await Promise.all([
      loadContacts(),
      loadTemplates(),
      loadSchedule(),
      loadCampaigns(),
      loadSettings()
    ])
  }

  return {
    // State
    contacts,
    templates,
    schedule,
    campaigns,
    settings,
    isLoading,
    error,
    
    // Methods
    initializeApp,
    loadContacts,
    loadTemplates,
    loadSchedule,
    loadCampaigns,
    loadSettings,
    createContact,
    updateContact,
    deleteContact,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    createCampaign,
    updateCampaign,
    deleteCampaign,
    sendEmail,
    sendMessage,
    refreshAll,
    showStatus,
    showStatusWithProgress
  }
}
