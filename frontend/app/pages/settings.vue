<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-4xl font-thin gradient-title mb-4">
        Settings
      </h1>
      <p class="text-slate-300 font-light">Configure your platform integrations and automation settings</p>
    </div>

    <!-- Main Content with Side Navigation -->
    <div class="flex gap-8">
      <!-- Side Navigation (Desktop Only) -->
      <aside class="hidden lg:block w-64 flex-shrink-0">
        <div class="sticky top-6 border-r border-slate-600/30 pr-6">
          <nav>
            <ul class="space-y-1">
              <li>
                <a @click="scrollToSection('user-settings')"
                  :class="activeSection === 'user-settings' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50' : 'text-slate-300 hover:bg-slate-700/50 hover:text-slate-100 border-transparent'"
                  class="flex items-center space-x-3 px-3 py-2 rounded-lg border transition-colors cursor-pointer">
                  <Icon name="lucide:user" class="w-4 h-4" />
                  <span class="text-sm font-light">User</span>
                </a>
              </li>
              <li>
                <a @click="scrollToSection('integrations')"
                  :class="activeSection === 'integrations' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50' : 'text-slate-300 hover:bg-slate-700/50 hover:text-slate-100 border-transparent'"
                  class="flex items-center space-x-3 px-3 py-2 rounded-lg border transition-colors cursor-pointer">
                  <Icon name="lucide:plug" class="w-4 h-4" />
                  <span class="text-sm font-light">Integrations</span>
                </a>
              </li>
              <li>
                <a @click="scrollToSection('automation')"
                  :class="activeSection === 'automation' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50' : 'text-slate-300 hover:bg-slate-700/50 hover:text-slate-100 border-transparent'"
                  class="flex items-center space-x-3 px-3 py-2 rounded-lg border transition-colors cursor-pointer">
                  <Icon name="lucide:zap" class="w-4 h-4" />
                  <span class="text-sm font-light">Automation</span>
                </a>
              </li>
            </ul>
          </nav>
        </div>
      </aside>

      <!-- Main Content -->
      <div class="flex-1 space-y-8">

        <!-- User Settings -->
        <UserSettingsSection
          :config="userConfig"
          :password-change="passwordChange"
          :password-error="passwordError"
          :password-success="passwordSuccess"
          :has-changes="hasUserChanges"
          @save="saveUserSettings"
          @change-password="handleChangePassword"
          @update:config="userConfig = $event"
          @update:passwordChange="passwordChange = $event"
        />

        <!-- Integrations Section -->
        <IntegrationsSection
          :gmail-config="gmailConfig"
          :codementor-config="codementorConfig"
          :user-config="userConfig"
          :has-gmail-changes="hasGmailChanges"
          :has-codementor-changes="hasCodementorChanges"
          :importing-codementor="importingCodementor"
          @save-gmail="saveGmailSettings"
          @save-codementor="saveCodementorSettings"
          @test-gmail="testGmailConnection"
          @test-codementor="testCodementorConnection"
          @import-codementor-contacts="importCodementorContacts"
          @update:gmailConfig="gmailConfig = $event"
          @update:codementorConfig="codementorConfig = $event"
          @update:userConfig="userConfig = $event"
        />

        <!-- Automation Settings -->
        <AutomationSection
          :config="automationConfig"
          :has-changes="hasAutomationChanges"
          @save="saveAutomationSettings"
          @update:config="automationConfig = $event"
        />

        <!-- Interest Submissions Section (Superuser Only) -->
        <div v-if="isSuperuser" id="interest-submissions"
          class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 scroll-mt-6">
          <div class="flex items-center mb-6">
            <div
              class="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mr-4">
              <Icon name="lucide:users" class="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 class="text-2xl font-thin text-slate-100">Interest Submissions</h3>
              <p class="text-slate-400 font-light">Manage interest form submissions</p>
            </div>
          </div>

          <div v-if="loadingSubmissions" class="text-center py-8">
            <Icon name="lucide:loader-2" class="w-8 h-8 text-emerald-400 animate-spin mx-auto" />
            <p class="text-slate-400 mt-4">Loading submissions...</p>
          </div>

          <div v-else-if="interestSubmissions.length === 0" class="text-center py-8">
            <p class="text-slate-400">No interest submissions yet.</p>
          </div>

          <div v-else class="space-y-4">
            <div v-for="submission in interestSubmissions" :key="submission.id"
              class="bg-slate-700/50 rounded-xl p-6 border border-slate-600/30">
              <div class="flex justify-between items-start mb-4">
                <div>
                  <h4 class="text-lg font-light text-slate-100">{{ submission.name }}</h4>
                  <p class="text-sm text-slate-400">{{ submission.email }}</p>
                  <p class="text-xs text-slate-500 mt-1">{{ formatDate(submission.created_at) }}</p>
                </div>
                <select v-model="submission.status" @change="updateSubmissionStatus(submission)"
                  class="bg-slate-600 border border-emerald-500/30 rounded-lg px-3 py-1 text-sm text-slate-100">
                  <option value="pending">Pending</option>
                  <option value="contacted">Contacted</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>

              <div v-if="submission.message" class="mb-4">
                <p class="text-sm text-slate-300 font-light whitespace-pre-wrap">{{ submission.message }}</p>
              </div>

              <div>
                <label class="block text-xs font-light text-slate-400 mb-2">Internal Notes</label>
                <textarea v-model="submission.notes" @blur="updateSubmissionNotes(submission)"
                  class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-sm text-slate-100 resize-none"
                  rows="2" placeholder="Add internal notes..."></textarea>
              </div>
            </div>
          </div>
        </div>

        <!-- Save Settings -->
        <div class="flex justify-center">
          <button @click="saveSettings"
            class="px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-xl font-light hover:shadow-lg transition-all duration-300 text-lg">
            Save All Settings
          </button>
        </div>
      </div>
    </div>

    <!-- Status Bar -->
    <div v-if="showStatusBar"
      class="fixed bottom-6 right-6 bg-slate-800/90 backdrop-blur-sm rounded-xl shadow-2xl border border-emerald-500/20 overflow-hidden transition-all duration-300">
      <div class="px-6 py-3 text-sm text-slate-300 font-light">
        <div class="flex items-center space-x-3">
          <div class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
          <span>{{ statusMessage }}</span>
        </div>
        <div class="w-full bg-slate-600/50 rounded-full h-1 mt-2">
          <div class="bg-gradient-to-r from-emerald-400 to-cyan-400 h-1 rounded-full transition-all duration-100"
            :style="{ width: statusProgress + '%' }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useApi } from '../composables/useApi'

// Set page title
useHead({
  title: 'Settings - Followupper'
})

const { settings, loadSettings } = useApi()
const { apiCall, apiFetch, API_BASE } = useApiFetch()
const isSuperuser = ref(false)
const interestSubmissions = ref([])
const loadingSubmissions = ref(false)
const importingCodementor = ref(false)

// Use global settings state
const gmailConfig = ref({ ...settings.value.gmail })
const codementorConfig = ref({ ...settings.value.codementor })
const automationConfig = ref({ ...settings.value.automation })
const userConfig = ref({
  timezone: settings.value.user?.timezone || 'UTC',
  footer: settings.value.user?.footer || '',
  codementor_max_concurrent: settings.value.user?.codementor_max_concurrent || 1,
  codementor_send_interval: settings.value.user?.codementor_send_interval || 5
})

// Track original values for change detection
const originalGmail = ref({ ...settings.value.gmail })
const originalCodementor = ref({ ...settings.value.codementor })
const originalAutomation = ref({ ...settings.value.automation })
const originalUser = ref({
  timezone: settings.value.user?.timezone || 'UTC',
  footer: settings.value.user?.footer || '',
  codementor_max_concurrent: settings.value.user?.codementor_max_concurrent || 1,
  codementor_send_interval: settings.value.user?.codementor_send_interval || 5
})
const passwordChange = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const passwordError = ref('')
const passwordSuccess = ref('')

// Watch for changes in global settings
watch(settings, (newSettings) => {
  gmailConfig.value = { ...newSettings.gmail }
  codementorConfig.value = { ...newSettings.codementor }
  automationConfig.value = { ...newSettings.automation }
  userConfig.value = {
    timezone: newSettings.user?.timezone || 'UTC',
    footer: newSettings.user?.footer || '',
    codementor_max_concurrent: newSettings.user?.codementor_max_concurrent || 1,
    codementor_send_interval: newSettings.user?.codementor_send_interval || 5
  }

  // Update original values when settings are loaded
  originalGmail.value = { ...newSettings.gmail }
  originalCodementor.value = { ...newSettings.codementor }
  originalAutomation.value = { ...newSettings.automation }
  originalUser.value = {
    timezone: newSettings.user?.timezone || 'UTC',
    footer: newSettings.user?.footer || '',
    codementor_max_concurrent: newSettings.user?.codementor_max_concurrent || 1,
    codementor_send_interval: newSettings.user?.codementor_send_interval || 5
  }
}, { deep: true })

// Change detection functions
const hasGmailChanges = computed(() => {
  return gmailConfig.value.email !== originalGmail.value.email ||
    gmailConfig.value.app_password !== originalGmail.value.app_password ||
    gmailConfig.value.name !== originalGmail.value.name
})

const hasCodementorChanges = computed(() => {
  return codementorConfig.value.access_token !== originalCodementor.value.access_token ||
    codementorConfig.value.refresh_token !== originalCodementor.value.refresh_token ||
    userConfig.value.codementor_max_concurrent !== originalUser.value.codementor_max_concurrent ||
    userConfig.value.codementor_send_interval !== originalUser.value.codementor_send_interval
})

const hasAutomationChanges = computed(() => {
  return automationConfig.value.enabled !== originalAutomation.value.enabled ||
    automationConfig.value.check_interval !== originalAutomation.value.check_interval ||
    automationConfig.value.max_retries !== originalAutomation.value.max_retries ||
    automationConfig.value.timezone !== originalAutomation.value.timezone
})

const hasUserChanges = computed(() => {
  return userConfig.value.timezone !== originalUser.value.timezone ||
    userConfig.value.footer !== originalUser.value.footer
})

// Side navigation
const activeSection = ref('user-settings')

const scrollToSection = (sectionId) => {
  if (sectionId === 'user-settings') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
    activeSection.value = sectionId
  } else {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      activeSection.value = sectionId
    }
  }
}

// Track active section on scroll
const handleScroll = () => {
  const scrollPosition = window.scrollY + 200 // Offset for better detection

  // If near the top, set to user-settings
  if (scrollPosition < 300) {
    activeSection.value = 'user-settings'
    return
  }

  const sections = ['integrations', 'automation']
  if (isSuperuser.value) {
    sections.push('interest-submissions')
  }
  for (const section of sections) {
    const element = document.getElementById(section)
    if (element) {
      const offsetTop = element.offsetTop
      const offsetBottom = offsetTop + element.offsetHeight

      if (scrollPosition >= offsetTop && scrollPosition < offsetBottom) {
        activeSection.value = section
        break
      }
    }
  }
}

// Status bar
const statusMessage = ref('')
const showStatusBar = ref(false)
const statusProgress = ref(100)
const statusTimer = ref(null)

// Status helper
const showStatusWithProgress = (message, duration = 5000) => {
  statusMessage.value = message
  showStatusBar.value = true
  statusProgress.value = 100

  // Clear existing timer
  if (statusTimer.value) {
    clearTimeout(statusTimer.value)
  }

  // Animate progress bar
  const progressInterval = setInterval(() => {
    statusProgress.value -= 2 // 100% / 50 intervals = 2% per interval
    if (statusProgress.value <= 0) {
      clearInterval(progressInterval)
    }
  }, duration / 50) // 50 intervals over the duration

  // Set new timer
  statusTimer.value = setTimeout(() => {
    showStatusBar.value = false
    statusTimer.value = null
    clearInterval(progressInterval)
  }, duration)
}

// Using apiCall from useApiFetch composable (already imported above)

// Test connections
const testGmailConnection = async () => {
  try {
    showStatusWithProgress('Testing Gmail connection...', 3000)
    const result = await apiCall('/settings/test/gmail/', {
      method: 'POST',
      body: JSON.stringify(gmailConfig.value)
    })
    showStatusWithProgress('Gmail connection successful!', 5000)
  } catch (error) {
    console.error('Gmail connection test failed:', error)
    // Error message is already extracted by apiCall
    const errorMessage = error.message || 'Gmail connection failed'
    showStatusWithProgress(errorMessage, 5000)
  }
}

const testCodementorConnection = async () => {
  try {
    showStatusWithProgress('Testing Codementor connection...', 3000)
    await apiCall('/settings/test/codementor/', {
      method: 'POST',
      body: JSON.stringify(codementorConfig.value)
    })
    showStatusWithProgress('Codementor connection successful!', 3000)
  } catch (error) {
    console.error('Codementor connection test failed:', error)
    showStatusWithProgress('Codementor connection failed', 3000)
  }
}

const importCodementorContacts = async () => {
  if (!codementorConfig.value.access_token || !codementorConfig.value.refresh_token) {
    showStatusWithProgress('Please configure Codementor credentials first', 3000)
    return
  }

  importingCodementor.value = true
  try {
    showStatusWithProgress('Importing contacts from Codementor...', 10000)
    const data = await apiCall('/settings/import/codementor/', {
      method: 'POST'
    })

    const message = `Import completed: ${data.created} created, ${data.updated} updated${data.errors.length > 0 ? `. ${data.errors.length} errors` : ''}`
    showStatusWithProgress(message, 5000)

    // Reload contacts if available
    const { loadContacts } = useApi()
    try {
      await loadContacts()
    } catch (e) {
      console.warn('Could not reload contacts:', e)
    }
  } catch (error) {
    console.error('Codementor import failed:', error)
    showStatusWithProgress(`Import failed: ${error.message || 'Unknown error'}`, 5000)
  } finally {
    importingCodementor.value = false
  }
}

// Save individual settings
const saveGmailSettings = async () => {
  try {
    showStatusWithProgress('Saving Gmail settings...', 3000)
    await apiCall('/settings/gmail/', {
      method: 'POST',
      body: JSON.stringify(gmailConfig.value)
    })

    // Reload settings from server to get the latest data
    await loadSettings()

    // Update original values from reloaded settings
    originalGmail.value = { ...settings.value.gmail }

    showStatusWithProgress('Gmail settings saved!', 3000)
  } catch (error) {
    console.error('Error saving Gmail settings:', error)
    showStatusWithProgress('Error saving Gmail settings', 3000)
  }
}

const saveCodementorSettings = async () => {
  try {
    showStatusWithProgress('Saving Codementor settings...', 3000)

    // Save Codementor credentials
    await apiCall('/settings/codementor/', {
      method: 'POST',
      body: JSON.stringify(codementorConfig.value)
    })

    // Save Codementor rate limiting (stored in user settings)
    await apiCall('/settings/user/', {
      method: 'POST',
      body: JSON.stringify({
        codementor_max_concurrent: userConfig.value.codementor_max_concurrent,
        codementor_send_interval: userConfig.value.codementor_send_interval
      })
    })

    // Reload settings from server to get the latest data
    await loadSettings()

    // Update original values from reloaded settings
    originalCodementor.value = { ...settings.value.codementor }
    originalUser.value.codementor_max_concurrent = settings.value.user?.codementor_max_concurrent || 1
    originalUser.value.codementor_send_interval = settings.value.user?.codementor_send_interval || 5

    showStatusWithProgress('Codementor settings saved!', 3000)
  } catch (error) {
    console.error('Error saving Codementor settings:', error)
    showStatusWithProgress('Error saving Codementor settings', 3000)
  }
}

const saveAutomationSettings = async () => {
  try {
    showStatusWithProgress('Saving automation settings...', 3000)
    await apiCall('/settings/automation/', {
      method: 'POST',
      body: JSON.stringify(automationConfig.value)
    })

    // Update original values after successful save
    originalAutomation.value = { ...automationConfig.value }

    showStatusWithProgress('Automation settings saved!', 3000)
  } catch (error) {
    console.error('Error saving automation settings:', error)
    showStatusWithProgress('Error saving automation settings', 3000)
  }
}

const saveUserSettings = async () => {
  try {
    showStatusWithProgress('Saving user settings...', 3000)
    await apiCall('/settings/user/', {
      method: 'POST',
      body: JSON.stringify(userConfig.value)
    })

    // Reload settings from server to get the latest data
    await loadSettings()

    // Update original values from reloaded settings
    originalUser.value = {
      timezone: settings.value.user?.timezone || 'UTC',
      footer: settings.value.user?.footer || '',
      codementor_max_concurrent: settings.value.user?.codementor_max_concurrent || 1,
      codementor_send_interval: settings.value.user?.codementor_send_interval || 5
    }

    showStatusWithProgress('User settings saved!', 3000)
  } catch (error) {
    console.error('Error saving user settings:', error)
    showStatusWithProgress('Error saving user settings', 3000)
  }
}


// Handle password change
const handleChangePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''

  // Validate passwords match
  if (passwordChange.value.newPassword !== passwordChange.value.confirmPassword) {
    passwordError.value = 'New passwords do not match'
    return
  }

  // Validate password length
  if (passwordChange.value.newPassword.length < 8) {
    passwordError.value = 'New password must be at least 8 characters'
    return
  }

  try {
    const response = await apiFetch('/auth/change-password/', {
      method: 'POST',
      body: JSON.stringify({
        old_password: passwordChange.value.currentPassword,
        new_password: passwordChange.value.newPassword
      })
    })

    if (response.ok) {
      const data = await response.json()
      passwordSuccess.value = 'Password changed successfully!'
      passwordError.value = ''
      // Clear form
      passwordChange.value = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
      // Clear success message after 3 seconds
      setTimeout(() => {
        passwordSuccess.value = ''
      }, 3000)
    } else {
      passwordError.value = data.error || 'Failed to change password'
      passwordSuccess.value = ''
    }
  } catch (error) {
    console.error('Error changing password:', error)
    passwordError.value = 'An error occurred. Please try again.'
    passwordSuccess.value = ''
  }
}

// Save all settings at once
const saveSettings = async () => {
  try {
    showStatusWithProgress('Saving all settings...', 5000)

    // Save all settings in parallel
    const promises = []

    // Only save Gmail if email is provided
    if (gmailConfig.value.email) {
      promises.push(
        apiCall('/settings/gmail/', {
          method: 'POST',
          body: JSON.stringify(gmailConfig.value)
        })
      )
    }

    // Only save Codementor if access_token is provided
    if (codementorConfig.value.access_token) {
      promises.push(
        apiCall('/settings/codementor/', {
          method: 'POST',
          body: JSON.stringify(codementorConfig.value)
        })
      )
    }

    // Always save automation settings
    promises.push(
      apiCall('/settings/automation/', {
        method: 'POST',
        body: JSON.stringify(automationConfig.value)
      })
    )

    // Always save user settings
    promises.push(
      apiCall('/settings/user/', {
        method: 'POST',
        body: JSON.stringify(userConfig.value)
      })
    )

    // Wait for all saves to complete
    await Promise.all(promises)

    // Reload settings from server to get the latest data
    await loadSettings()

    // Update original values from reloaded settings
    originalGmail.value = { ...settings.value.gmail }
    originalCodementor.value = { ...settings.value.codementor }
    originalAutomation.value = { ...settings.value.automation }
    originalUser.value = {
      timezone: settings.value.user?.timezone || 'UTC',
      footer: settings.value.user?.footer || '',
      codementor_max_concurrent: settings.value.user?.codementor_max_concurrent || 1,
      codementor_send_interval: settings.value.user?.codementor_send_interval || 5
    }

    showStatusWithProgress('All settings saved successfully!', 3000)
  } catch (error) {
    console.error('Error saving settings:', error)
    showStatusWithProgress('Error saving settings', 3000)
  }
}

onMounted(() => {
  // Ensure we sync with global state on mount
  if (settings.value && settings.value.gmail) {
    gmailConfig.value = { ...settings.value.gmail }
    originalGmail.value = { ...settings.value.gmail }
  }
  if (settings.value && settings.value.codementor) {
    codementorConfig.value = { ...settings.value.codementor }
    originalCodementor.value = { ...settings.value.codementor }
  }
  if (settings.value && settings.value.automation) {
    automationConfig.value = { ...settings.value.automation }
    originalAutomation.value = { ...settings.value.automation }
  }
  if (settings.value && settings.value.user) {
    userConfig.value = {
      timezone: settings.value.user.timezone || 'UTC',
      footer: settings.value.user.footer || '',
      codementor_max_concurrent: settings.value.user.codementor_max_concurrent || 1,
      codementor_send_interval: settings.value.user.codementor_send_interval || 5
    }
    originalUser.value = {
      timezone: settings.value.user.timezone || 'UTC',
      footer: settings.value.user.footer || '',
      codementor_max_concurrent: settings.value.user.codementor_max_concurrent || 1,
      codementor_send_interval: settings.value.user.codementor_send_interval || 5
    }
  }

  // Check if user is superuser and load submissions
  checkSuperuser()

  // Set up scroll tracking for side navigation
  window.addEventListener('scroll', handleScroll)
  handleScroll() // Initial check
})

const checkSuperuser = async () => {
  try {
    const response = await fetch(`${API_BASE}/auth/current-user/`, {
      credentials: 'include'
    })
    if (response.ok) {
      const data = await response.json()
      isSuperuser.value = data.is_superuser || false
      if (isSuperuser.value) {
        loadInterestSubmissions()
      }
    }
  } catch (error) {
    console.error('Error checking superuser status:', error)
  }
}

const loadInterestSubmissions = async () => {
  loadingSubmissions.value = true
  try {
    const data = await apiCall('/interest-submissions/')
    interestSubmissions.value = data
  } catch (error) {
    console.error('Error loading interest submissions:', error)
  } finally {
    loadingSubmissions.value = false
  }
}

const updateSubmissionStatus = async (submission) => {
  try {
    await apiCall(`/interest-submissions/${submission.id}/`, {
      method: 'PATCH',
      body: JSON.stringify({ status: submission.status })
    })
  } catch (error) {
    console.error('Error updating submission status:', error)
  }
}

const updateSubmissionNotes = async (submission) => {
  try {
    await apiCall(`/interest-submissions/${submission.id}/`, {
      method: 'PATCH',
      body: JSON.stringify({ notes: submission.notes })
    })
  } catch (error) {
    console.error('Error updating submission notes:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (e) {
    return dateString
  }
}

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>
