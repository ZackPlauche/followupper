<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-4xl font-thin gradient-title mb-4">
        Settings
      </h1>
      <p class="text-slate-300 font-light">Configure your platform integrations and automation settings</p>
    </div>

    <!-- Gmail Configuration -->
    <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8">
      <div class="flex items-center mb-6">
        <div class="w-12 h-12 bg-gradient-to-r from-red-500 to-pink-500 rounded-xl flex items-center justify-center mr-4">
          <Icon name="lucide:mail" class="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 class="text-2xl font-thin text-slate-100">Gmail Integration</h3>
          <p class="text-slate-400 font-light">Configure your Gmail account for automated email sending</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Gmail Address</label>
          <input v-model="gmailConfig.email" type="email" placeholder="your-email@gmail.com"
                 class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
        </div>
        
        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">App Password</label>
          <input v-model="gmailConfig.app_password" type="password" placeholder="16-character app password"
                 class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
        </div>
      </div>

      <div class="flex items-center justify-between mt-6">
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 rounded-full" :class="gmailConfig.email && gmailConfig.app_password ? 'bg-emerald-400' : 'bg-slate-500'"></div>
          <span class="text-sm text-slate-300 font-light">
            {{ gmailConfig.email && gmailConfig.app_password ? 'Configured' : 'Not configured' }}
          </span>
        </div>
        <div class="flex space-x-3">
          <button @click="testGmailConnection" 
                  class="px-4 py-2 bg-blue-600/50 text-blue-300 rounded-lg font-light hover:bg-blue-600/70 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="!gmailConfig.email || !gmailConfig.app_password">
            Test
          </button>
          <button @click="saveGmailSettings" 
                  class="px-4 py-2 rounded-lg font-light transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  :class="hasGmailChanges ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:shadow-lg' : 'bg-gradient-to-r from-emerald-500/30 to-cyan-500/30 text-emerald-200'"
                  :disabled="!gmailConfig.email || !hasGmailChanges">
            Save
          </button>
        </div>
      </div>
    </div>

    <!-- Codementor Configuration -->
    <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8">
      <div class="flex items-center mb-6">
        <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center mr-4">
          <Icon name="lucide:code" class="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 class="text-2xl font-thin text-slate-100">Codementor Integration</h3>
          <p class="text-slate-400 font-light">Configure your Codementor account credentials</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Access Token</label>
          <input v-model="codementorConfig.access_token" type="password" placeholder="Your Codementor access token"
                 class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
        </div>
        
        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Refresh Token</label>
          <input v-model="codementorConfig.refresh_token" type="password" placeholder="Your Codementor refresh token"
                 class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
        </div>
      </div>

      <div class="mt-4 p-4 bg-slate-700/30 rounded-xl border border-slate-600/30">
        <div class="flex items-start space-x-3">
          <Icon name="lucide:info" class="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
          <div class="text-sm text-slate-300">
            <p class="font-medium text-blue-400 mb-1">Token Authentication</p>
            <p>Get these tokens from your Codementor cookies in your browser. The system will automatically refresh the access token when needed.</p>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between mt-6">
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 rounded-full" :class="codementorConfig.access_token && codementorConfig.refresh_token ? 'bg-emerald-400' : 'bg-slate-500'"></div>
          <span class="text-sm text-slate-300 font-light">
            {{ codementorConfig.access_token && codementorConfig.refresh_token ? 'Configured' : 'Not configured' }}
          </span>
        </div>
        <div class="flex space-x-3">
          <button @click="testCodementorConnection" 
                  class="px-4 py-2 bg-blue-600/50 text-blue-300 rounded-lg font-light hover:bg-blue-600/70 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="!codementorConfig.access_token || !codementorConfig.refresh_token">
            Test
          </button>
          <button @click="saveCodementorSettings" 
                  class="px-4 py-2 rounded-lg font-light transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  :class="hasCodementorChanges ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:shadow-lg' : 'bg-gradient-to-r from-emerald-500/30 to-cyan-500/30 text-emerald-200'"
                  :disabled="!codementorConfig.access_token || !hasCodementorChanges">
            Save
          </button>
        </div>
      </div>
    </div>

    <!-- Automation Settings -->
    <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8">
      <div class="flex items-center mb-6">
        <div class="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mr-4">
          <Icon name="lucide:zap" class="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 class="text-2xl font-thin text-slate-100">Automation Settings</h3>
          <p class="text-slate-400 font-light">Configure how and when follow-ups are sent</p>
        </div>
      </div>

      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-lg font-light text-slate-100">Enable Background Scheduler</h4>
            <p class="text-sm text-slate-400">Run the background service that checks for and sends scheduled follow-ups</p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input v-model="automationConfig.enabled" type="checkbox" class="sr-only peer">
            <div class="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
          </label>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Check Interval (minutes)</label>
            <input v-model="automationConfig.check_interval" type="number" min="1" max="1440"
                   class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>
          
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Max Retries</label>
            <input v-model="automationConfig.max_retries" type="number" min="1" max="10"
                   class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>
        </div>

        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Default Timezone</label>
          <select v-model="automationConfig.timezone"
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
            <option value="UTC">UTC</option>
            <option value="America/New_York">Eastern Time</option>
            <option value="America/Chicago">Central Time</option>
            <option value="America/Denver">Mountain Time</option>
            <option value="America/Los_Angeles">Pacific Time</option>
            <option value="Europe/London">London</option>
            <option value="Europe/Paris">Paris</option>
            <option value="Asia/Tokyo">Tokyo</option>
          </select>
        </div>
      </div>

      <div class="flex justify-end mt-6">
        <button @click="saveAutomationSettings" 
                class="px-6 py-3 rounded-xl font-light transition-all duration-300"
                :class="hasAutomationChanges ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:shadow-lg' : 'bg-gradient-to-r from-emerald-500/30 to-cyan-500/30 text-emerald-200'"
                :disabled="!hasAutomationChanges">
          Save Automation Settings
        </button>
      </div>
    </div>

    <!-- Save Settings -->
    <div class="flex justify-center">
      <button @click="saveSettings" 
              class="px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-xl font-light hover:shadow-lg transition-all duration-300 text-lg">
        Save All Settings
      </button>
    </div>

    <!-- Status Bar -->
    <div v-if="showStatusBar" class="fixed bottom-6 right-6 bg-slate-800/90 backdrop-blur-sm rounded-xl shadow-2xl border border-emerald-500/20 overflow-hidden transition-all duration-300">
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
import { ref, onMounted, watch, computed } from 'vue'
import { useApi } from '../composables/useApi'

// Set page title
useHead({
  title: 'Settings - Followupper'
})

const { settings, loadSettings } = useApi()

// Use global settings state
const gmailConfig = ref({ ...settings.value.gmail })
const codementorConfig = ref({ ...settings.value.codementor })
const automationConfig = ref({ ...settings.value.automation })

// Track original values for change detection
const originalGmail = ref({ ...settings.value.gmail })
const originalCodementor = ref({ ...settings.value.codementor })
const originalAutomation = ref({ ...settings.value.automation })

// Watch for changes in global settings
watch(settings, (newSettings) => {
  gmailConfig.value = { ...newSettings.gmail }
  codementorConfig.value = { ...newSettings.codementor }
  automationConfig.value = { ...newSettings.automation }
  
  // Update original values when settings are loaded
  originalGmail.value = { ...newSettings.gmail }
  originalCodementor.value = { ...newSettings.codementor }
  originalAutomation.value = { ...newSettings.automation }
}, { deep: true })

// Change detection functions
const hasGmailChanges = computed(() => {
  return gmailConfig.value.email !== originalGmail.value.email || 
         gmailConfig.value.app_password !== originalGmail.value.app_password
})

const hasCodementorChanges = computed(() => {
  return codementorConfig.value.access_token !== originalCodementor.value.access_token || 
         codementorConfig.value.refresh_token !== originalCodementor.value.refresh_token
})

const hasAutomationChanges = computed(() => {
  return automationConfig.value.enabled !== originalAutomation.value.enabled ||
         automationConfig.value.check_interval !== originalAutomation.value.check_interval ||
         automationConfig.value.max_retries !== originalAutomation.value.max_retries ||
         automationConfig.value.timezone !== originalAutomation.value.timezone
})

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

// API base URL
const API_BASE = 'http://localhost:5000/api'

// Generic API call with retry logic
const apiCall = async (endpoint, options = {}, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options
      })
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `API Error: ${response.status}`)
      }
      return await response.json()
    } catch (err) {
      console.error(`API call to ${endpoint} failed (attempt ${i + 1}/${retries}):`, err)
      if (i === retries - 1) {
        throw err
      }
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
  }
}

// Test connections
const testGmailConnection = async () => {
  try {
    showStatusWithProgress('Testing Gmail connection...', 3000)
    await apiCall('/settings/test/gmail', {
      method: 'POST',
      body: JSON.stringify(gmailConfig.value)
    })
    showStatusWithProgress('Gmail connection successful!', 3000)
  } catch (error) {
    console.error('Gmail connection test failed:', error)
    showStatusWithProgress('Gmail connection failed', 3000)
  }
}

const testCodementorConnection = async () => {
  try {
    showStatusWithProgress('Testing Codementor connection...', 3000)
    await apiCall('/settings/test/codementor', {
      method: 'POST',
      body: JSON.stringify(codementorConfig.value)
    })
    showStatusWithProgress('Codementor connection successful!', 3000)
  } catch (error) {
    console.error('Codementor connection test failed:', error)
    showStatusWithProgress('Codementor connection failed', 3000)
  }
}

// Save individual settings
const saveGmailSettings = async () => {
  try {
    showStatusWithProgress('Saving Gmail settings...', 3000)
    await apiCall('/settings/gmail', {
      method: 'POST',
      body: JSON.stringify(gmailConfig.value)
    })
    
    // Update original values after successful save
    originalGmail.value = { ...gmailConfig.value }
    
    showStatusWithProgress('Gmail settings saved!', 3000)
  } catch (error) {
    console.error('Error saving Gmail settings:', error)
    showStatusWithProgress('Error saving Gmail settings', 3000)
  }
}

const saveCodementorSettings = async () => {
  try {
    showStatusWithProgress('Saving Codementor settings...', 3000)
    await apiCall('/settings/codementor', {
      method: 'POST',
      body: JSON.stringify(codementorConfig.value)
    })
    
    // Update original values after successful save
    originalCodementor.value = { ...codementorConfig.value }
    
    showStatusWithProgress('Codementor settings saved!', 3000)
  } catch (error) {
    console.error('Error saving Codementor settings:', error)
    showStatusWithProgress('Error saving Codementor settings', 3000)
  }
}

const saveAutomationSettings = async () => {
  try {
    showStatusWithProgress('Saving automation settings...', 3000)
    await apiCall('/settings/automation', {
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

// Save all settings at once
const saveSettings = async () => {
  try {
    showStatusWithProgress('Saving all settings...', 5000)
    
    // Save all settings in parallel
    const promises = []
    
    // Only save Gmail if email is provided
    if (gmailConfig.value.email) {
      promises.push(
        apiCall('/settings/gmail', {
          method: 'POST',
          body: JSON.stringify(gmailConfig.value)
        })
      )
    }
    
    // Only save Codementor if access_token is provided
    if (codementorConfig.value.access_token) {
      promises.push(
        apiCall('/settings/codementor', {
          method: 'POST',
          body: JSON.stringify(codementorConfig.value)
        })
      )
    }
    
    // Always save automation settings
    promises.push(
      apiCall('/settings/automation', {
        method: 'POST',
        body: JSON.stringify(automationConfig.value)
      })
    )
    
    // Wait for all saves to complete
    await Promise.all(promises)
    
    // Update original values after successful save
    originalGmail.value = { ...gmailConfig.value }
    originalCodementor.value = { ...codementorConfig.value }
    originalAutomation.value = { ...automationConfig.value }
    
    showStatusWithProgress('All settings saved successfully!', 3000)
  } catch (error) {
    console.error('Error saving settings:', error)
    showStatusWithProgress('Error saving settings', 3000)
  }
}

onMounted(() => {
  // Settings are already loaded by initializeApp in app.vue
  console.log('Settings page mounted - settings already loaded globally')
})
</script>
