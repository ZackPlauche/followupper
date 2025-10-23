<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <h2 class="text-3xl font-thin text-slate-100">Scheduled Follow-ups</h2>
      <button @click="refreshSchedule"
        class="bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105">
        🔄 Refresh
      </button>
    </div>

    <!-- Schedule List -->
    <div class="bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-emerald-500/20">
          <thead class="bg-slate-700/50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Contact</th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Template</th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Scheduled
                Date</th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody class="bg-slate-800/30 divide-y divide-emerald-500/10">
            <tr v-for="followup in schedule" :key="followup.id" class="hover:bg-slate-700/30 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-light text-slate-100">
                Contact #{{ followup.contact_id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                Template #{{ followup.template_id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                {{ formatDate(followup.scheduled_date) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(followup.status)"
                  class="inline-flex px-3 py-1 text-xs font-light rounded-full">
                  {{ followup.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
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
      </div>
      <!-- Progress Bar -->
      <div class="h-1 bg-slate-700/50">
        <div class="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all duration-100 ease-linear"
          :style="{ width: statusProgress + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<script setup>

// Set page title
useHead({
  title: 'Schedule - Followupper'
})

// Use shared API state
const { schedule, showStatusWithProgress } = useApi()

// Local UI state
const statusMessage = ref('Loading...')
const showStatusBar = ref(false)
const statusTimer = ref(null)
const statusProgress = ref(100)

// Enhanced status helper with progress bar
const showStatusWithProgressLocal = (message, duration = 5000) => {
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

// Methods
const loadSchedule = async (retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(`${API_BASE}/schedule`)
      if (response.ok) {
        schedule.value = await response.json()
        showStatus(`Loaded ${schedule.value.length} scheduled follow-ups`)
        return
      }
    } catch (error) {
      console.error(`Error loading schedule (attempt ${i + 1}):`, error)
      if (i === retries - 1) {
        showStatus('Error loading schedule - API not responding')
      } else {
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
    }
  }
}

const refreshSchedule = () => {
  showStatusWithProgressLocal(`Refreshed ${schedule.value.length} scheduled follow-ups`, 2000)
}

const formatDate = (dateString) => {
  if (!dateString) return 'Not scheduled'
  return new Date(dateString).toLocaleDateString()
}

const getStatusClass = (status) => {
  switch (status) {
    case 'pending': return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
    case 'sent': return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
    case 'failed': return 'bg-red-500/20 text-red-400 border border-red-500/30'
    default: return 'bg-slate-500/20 text-slate-400 border border-slate-500/30'
  }
}

// Data is loaded at app startup, no need to load here
onMounted(() => {
  // No status message needed
})
</script>
