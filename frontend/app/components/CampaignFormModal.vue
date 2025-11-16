<template>
  <div v-if="show"
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
    <div
      class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full h-full sm:h-auto sm:max-w-6xl sm:max-h-[90vh] flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="flex justify-between items-center p-4 sm:p-6 border-b border-slate-700/50 flex-shrink-0">
        <h2 class="text-xl sm:text-2xl font-thin text-slate-100">
          {{ isEdit ? 'Edit Campaign' : 'Create New Campaign' }}
        </h2>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-200 transition-colors">
          <Icon name="lucide:x" class="w-6 h-6" />
        </button>
      </div>

      <!-- Scrollable Content -->
      <div class="flex-1 flex flex-col sm:flex-row gap-4 sm:gap-6 overflow-y-auto p-4 sm:p-6 min-h-0">
        <!-- Left: Form -->
        <div class="flex-1 space-y-4">
          <div>
            <label class="block text-xs font-light text-slate-300 mb-1">Campaign Name</label>
            <input v-model="localCampaign.name" type="text" placeholder="e.g., Weekly Check-ins"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>

          <div>
            <label class="block text-xs font-light text-slate-300 mb-1">Description (Optional)</label>
            <textarea v-model="localCampaign.description" placeholder="Describe what this campaign is for..."
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors h-24 resize-none"></textarea>
          </div>

          <div>
            <label class="block text-xs font-light text-slate-300 mb-1">Campaign Type</label>
            <select v-model="localCampaign.campaign_type"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
              <option value="recurring">Recurring</option>
              <option value="sequence">Sequence</option>
            </select>
          </div>

          <div v-if="localCampaign.campaign_type === 'recurring'">
            <div class="space-y-4">
              <div>
                <label class="block text-xs font-light text-slate-300 mb-1">Frequency</label>
                <select v-model="localCampaign.frequency_type" @change="handleFrequencyChange"
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="yearly">Yearly</option>
              <option value="custom">Custom (Days)</option>
            </select>
          </div>

          <div v-if="localCampaign.frequency_type === 'custom'">
            <label class="block text-sm font-light text-slate-300 mb-2">Custom Frequency (Days)</label>
            <input v-model.number="localCampaign.default_frequency_days" type="number" min="1" max="365"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>

          <div v-if="localCampaign.frequency_type === 'weekly'">
            <label class="block text-sm font-light text-slate-300 mb-2">Send On</label>
            <select v-model="localCampaign.send_day"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
              <option value="0">Monday</option>
              <option value="1">Tuesday</option>
              <option value="2">Wednesday</option>
              <option value="3">Thursday</option>
              <option value="4">Friday</option>
              <option value="5">Saturday</option>
              <option value="6">Sunday</option>
            </select>
          </div>

              <div v-if="localCampaign.frequency_type === 'monthly' || localCampaign.frequency_type === 'quarterly'">
                <label class="block text-xs font-light text-slate-300 mb-1">Send On</label>
                <select v-model="localCampaign.send_day"
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                  <option value="1">1st of the month</option>
                  <option value="15">15th of the month</option>
                  <option value="last">Last day of the month</option>
                </select>
              </div>

              <div v-if="localCampaign.frequency_type === 'yearly'">
                <label class="block text-xs font-light text-slate-300 mb-1">Send On</label>
                <input v-model="yearlyDateInput" type="date" @input="handleYearlyDateChange"
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                <p class="text-xs text-slate-400 mt-1">Select a specific date (month and day) to send each year</p>
              </div>

              <div>
                <label class="block text-xs font-light text-slate-300 mb-1">Send Time</label>
                <input v-model="localCampaign.send_time" type="time"
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
              </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Timezone</label>
            <div class="flex items-center bg-slate-700/50 rounded-lg p-1 border border-slate-500/30 w-fit">
              <button type="button" @click="localCampaign.timezone = 'contact'"
                :class="localCampaign.timezone === 'contact' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                Contact
              </button>
              <button type="button" @click="localCampaign.timezone = 'UTC'"
                :class="localCampaign.timezone === 'UTC' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                UTC
              </button>
              <button type="button" @click="localCampaign.timezone = 'America/New_York'"
                :class="localCampaign.timezone === 'America/New_York' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                ET
              </button>
              <button type="button" @click="localCampaign.timezone = 'America/Chicago'"
                :class="localCampaign.timezone === 'America/Chicago' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                CT
              </button>
              <button type="button" @click="localCampaign.timezone = 'America/Denver'"
                :class="localCampaign.timezone === 'America/Denver' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                MT
              </button>
              <button type="button" @click="localCampaign.timezone = 'America/Los_Angeles'"
                :class="localCampaign.timezone === 'America/Los_Angeles' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                PT
              </button>
            </div>
            <p class="text-xs text-slate-400 mt-1">Select "Contact" to send at the specified time in each contact's
              local timezone</p>
          </div>
        </div>
      </div>

          <!-- Variable Hints Info Block -->
          <VariableHints v-if="localCampaign.campaign_type === 'recurring' || localCampaign.campaign_type === 'sequence'" :show-frequency="true" />

          <div v-if="localCampaign.campaign_type === 'recurring'">
            <div>
              <label class="block text-xs font-light text-slate-300 mb-1">Subject Template (Optional)</label>
              <input v-model="localCampaign.subject_template" type="text"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                placeholder="e.g., Follow-up: {name}">
              <p class="text-xs text-slate-400 mt-1">Supports template variables like {name}, {first_name}, etc.</p>
            </div>

            <div>
              <label class="block text-xs font-light text-slate-300 mb-1">Message Template *</label>
              <textarea v-model="localCampaign.message_template" rows="8" required
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                placeholder="Hi {first_name},&#10;&#10;This is your {frequency} check-in message.&#10;&#10;Hope you're doing well!&#10;&#10;Best regards"></textarea>
            </div>
          </div>

          <div v-if="localCampaign.campaign_type === 'sequence'">
            <label class="block text-xs font-light text-slate-300 mb-1">Sequence Steps</label>
            <div class="space-y-4">
              <div v-for="(step, index) in localCampaign.steps" :key="index"
                class="bg-slate-700/30 rounded-lg p-3 space-y-3">
                <div class="flex items-center justify-between">
                  <h4 class="text-xs font-medium text-slate-300">Step {{ index + 1 }}</h4>
                  <button @click="removeStep(index)"
                    class="px-2 py-1 bg-red-600/50 text-red-300 rounded text-xs hover:bg-red-600/70 transition-colors">
                    <Icon name="lucide:trash-2" class="w-4 h-4" />
                  </button>
                </div>

                <div>
                  <label class="block text-xs text-slate-400 mb-1">Subject</label>
                  <input v-model="step.subject" type="text" placeholder="Step subject (optional)"
                    class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
                </div>

            <div>
              <label class="block text-xs font-light text-slate-300 mb-1">Message *</label>
              <textarea v-model="step.message" rows="6" required
                class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                placeholder="Hi {first_name},&#10;&#10;This is step {{ index + 1 }} of the sequence.&#10;&#10;Hope you're doing well!"></textarea>
            </div>

                <div class="flex items-center space-x-3">
                  <div class="flex-1">
                    <label class="block text-xs text-slate-400 mb-1">Delay (Days)</label>
                    <input v-model.number="step.delay_days" type="number" min="0" placeholder="0"
                      class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
                  </div>
                </div>
              </div>

              <button @click="addStep"
                class="w-full px-4 py-2 bg-slate-600/50 text-slate-300 rounded-lg hover:bg-slate-600/70 transition-colors border-2 border-dashed border-slate-600 text-sm">
                <Icon name="lucide:plus" class="w-4 h-4 inline mr-2" />
                Add Step
              </button>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-xs font-light text-slate-300 mb-1">Status</label>
              <select v-model="localCampaign.is_active"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                <option :value="true">Active</option>
                <option :value="false">Inactive</option>
              </select>
            </div>

            <div class="pb-4">
              <label class="block text-xs font-light text-slate-300 mb-1">When someone is added to this campaign:</label>
              <div class="space-y-2">
                <label class="flex items-center space-x-3">
                  <input v-model="localCampaign.start_immediately" type="radio" value="immediate" name="start_behavior"
                    class="form-radio h-4 w-4 text-emerald-500 border-slate-600 bg-slate-700/50 focus:ring-emerald-400">
                  <span class="text-xs text-slate-300">Send first message immediately</span>
                </label>
                <label class="flex items-center space-x-3">
                  <input v-model="localCampaign.start_immediately" type="radio" value="scheduled" name="start_behavior"
                    class="form-radio h-4 w-4 text-emerald-500 border-slate-600 bg-slate-700/50 focus:ring-emerald-400">
                  <span class="text-xs text-slate-300">Wait until next scheduled time</span>
                </label>
              </div>
            </div>
          </div>

        </div>

        <!-- Right: Preview Section -->
        <div v-if="localCampaign.campaign_type === 'recurring' || (localCampaign.campaign_type === 'sequence' && localCampaign.steps && localCampaign.steps.length > 0)"
          class="w-full sm:w-96 border-t sm:border-t-0 sm:border-l border-slate-700/50 pt-4 sm:pl-6 sm:pt-0 flex-shrink-0 sm:sticky sm:top-0 sm:self-start">
          <h4 class="text-lg font-light text-slate-100 mb-4">Preview</h4>

          <!-- Recurring Campaign Preview -->
          <div v-if="localCampaign.campaign_type === 'recurring'">
            <!-- Subject Preview -->
            <div v-if="localCampaign.subject_template" class="bg-slate-700/30 rounded-lg p-4 border border-slate-600/30 mb-4">
              <div class="text-xs text-slate-400 mb-1">
                <strong>Subject:</strong>
              </div>
              <div class="text-sm text-slate-300">
                {{ previewSubject }}
              </div>
            </div>

            <!-- Message Preview -->
            <div class="bg-slate-700/30 rounded-lg p-4 border border-slate-600/30 mb-4">
              <div v-if="localCampaign.message_template" class="text-sm text-slate-300 whitespace-pre-wrap">
                {{ previewMessage }}
              </div>
              <div v-else class="text-sm text-slate-500 italic">
                (No message template yet)
              </div>
            </div>

            <!-- User Data Section -->
            <div class="bg-slate-800/30 border border-emerald-500/20 rounded-xl p-3">
              <h5 class="text-sm font-light text-emerald-400 mb-2">Preview Data</h5>
              <div class="text-xs text-slate-300 space-y-1">
                <div><strong>Name:</strong> John Doe</div>
                <div><strong>Preferred Name:</strong> Johnny</div>
                <div><strong>Gender:</strong> Male</div>
                <div><strong>Email:</strong> john@example.com</div>
                <div><strong>Codementor:</strong> johndoe</div>
                <div><strong>Frequency:</strong> {{ formatFrequencyPreview() }}</div>
              </div>
            </div>
          </div>

          <!-- Sequence Campaign Preview -->
          <div v-if="localCampaign.campaign_type === 'sequence'">
            <div v-for="(step, index) in localCampaign.steps" :key="index" class="mb-4">
              <div class="bg-slate-700/30 rounded-lg p-4 border border-slate-600/30 mb-4">
                <div v-if="step.subject" class="text-xs text-slate-400 mb-2">
                  <strong>Subject:</strong> {{ previewStepText(step.subject, index) }}
                </div>
                <div v-if="step.message.trim()" class="text-sm text-slate-300 whitespace-pre-wrap">
                  {{ previewStepText(step.message, index) }}
                </div>
                <div v-else class="text-sm text-slate-500 italic">
                  (No message yet)
                </div>
              </div>
            </div>
            <div class="bg-slate-800/30 border border-emerald-500/20 rounded-xl p-3">
              <h5 class="text-sm font-light text-emerald-400 mb-2">Preview Data</h5>
              <div class="text-xs text-slate-300 space-y-1">
                <div><strong>Name:</strong> John Doe</div>
                <div><strong>Preferred Name:</strong> Johnny</div>
                <div><strong>Gender:</strong> Male</div>
                <div><strong>Email:</strong> john@example.com</div>
                <div><strong>Codementor:</strong> johndoe</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex space-x-3 p-4 sm:p-6 border-t border-slate-700/50 flex-shrink-0">
        <button @click="$emit('close')"
          class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
          Cancel
        </button>
        <button @click="handleSave"
          class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300"
          :disabled="!localCampaign.name || !localCampaign.campaign_type">
          {{ isEdit ? 'Update Campaign' : 'Create Campaign' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  campaign: {
    type: Object,
    default: () => ({
      name: '',
      description: '',
      campaign_type: 'recurring',
      is_active: true,
      frequency_type: 'weekly',
      default_frequency_days: 7,
      send_day: '1',
      send_time: '09:00',
      timezone: 'contact',
      message_template: '',
      subject_template: '',
      steps: [],
      start_immediately: 'scheduled'
    })
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'save'])

const localCampaign = ref({ 
  name: '',
  description: '',
  campaign_type: 'recurring',
  is_active: true,
  frequency_type: 'weekly',
  default_frequency_days: 7,
  send_day: '1',
  send_time: '09:00',
  timezone: 'contact',
  message_template: '',
  subject_template: '',
  steps: [],
  start_immediately: 'scheduled',
  ...props.campaign 
})
const yearlyDateInput = ref('')

watch(() => props.campaign, (newCampaign) => {
  if (newCampaign) {
    localCampaign.value = {
      name: '',
      description: '',
      campaign_type: 'recurring',
      is_active: true,
      frequency_type: 'weekly',
      default_frequency_days: 7,
      send_day: '1',
      send_time: '09:00',
      timezone: 'contact',
      message_template: '',
      subject_template: '',
      steps: [],
      start_immediately: 'scheduled',
      ...newCampaign
    }
    if (!localCampaign.value.steps) {
      localCampaign.value.steps = []
    }
    if (newCampaign.frequency_type === 'yearly' && newCampaign.send_day && newCampaign.send_day !== '1' && newCampaign.send_day !== '15' && newCampaign.send_day !== 'last') {
      const parts = newCampaign.send_day.split('-')
      if (parts.length === 2) {
        const year = new Date().getFullYear()
        yearlyDateInput.value = `${year}-${parts[0]}-${parts[1]}`
      }
    } else {
      yearlyDateInput.value = ''
    }
  }
}, { deep: true, immediate: true })

const handleFrequencyChange = () => {
  if (localCampaign.value.frequency_type === 'daily') {
    localCampaign.value.default_frequency_days = 1
  } else if (localCampaign.value.frequency_type === 'weekly') {
    localCampaign.value.default_frequency_days = 7
  } else if (localCampaign.value.frequency_type === 'monthly') {
    localCampaign.value.default_frequency_days = 30
  } else if (localCampaign.value.frequency_type === 'quarterly') {
    localCampaign.value.default_frequency_days = 90
  } else if (localCampaign.value.frequency_type === 'yearly') {
    localCampaign.value.default_frequency_days = 365
  }
}

const handleYearlyDateChange = () => {
  if (yearlyDateInput.value) {
    const date = new Date(yearlyDateInput.value)
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    localCampaign.value.send_day = `${month}-${day}`
  }
}

const addStep = () => {
  if (!localCampaign.value.steps) {
    localCampaign.value.steps = []
  }
  localCampaign.value.steps.push({
    subject: '',
    message: '',
    delay_days: 0
  })
}

const removeStep = (index) => {
  localCampaign.value.steps.splice(index, 1)
}

const handleSave = () => {
  emit('save', { ...localCampaign.value })
}

const formatFrequencyPreview = () => {
  const freqType = localCampaign.value.frequency_type || 'weekly'
  const sendTime = localCampaign.value.send_time || '09:00'
  switch (freqType) {
    case 'daily':
      return `Daily at ${sendTime}`
    case 'weekly':
      const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
      const dayIndex = parseInt(localCampaign.value.send_day || '0')
      if (!isNaN(dayIndex) && dayIndex >= 0 && dayIndex <= 6) {
        return `Weekly on ${dayNames[dayIndex]}s at ${sendTime}`
      }
      return `Weekly at ${sendTime}`
    case 'monthly':
      if (localCampaign.value.send_day === 'last') {
        return `Monthly on the last day at ${sendTime}`
      } else if (localCampaign.value.send_day) {
        const day = parseInt(localCampaign.value.send_day)
        if (!isNaN(day)) {
          const suffix = day >= 11 && day <= 13 ? 'th' : day % 10 === 1 ? 'st' : day % 10 === 2 ? 'nd' : day % 10 === 3 ? 'rd' : 'th'
          return `Monthly on the ${day}${suffix} at ${sendTime}`
        }
      }
      return `Monthly at ${sendTime}`
    case 'quarterly':
      if (localCampaign.value.send_day === 'last') {
        return `Quarterly on the last day at ${sendTime}`
      } else if (localCampaign.value.send_day) {
        const day = parseInt(localCampaign.value.send_day)
        if (!isNaN(day)) {
          const suffix = day >= 11 && day <= 13 ? 'th' : day % 10 === 1 ? 'st' : day % 10 === 2 ? 'nd' : day % 10 === 3 ? 'rd' : 'th'
          return `Quarterly on the ${day}${suffix} at ${sendTime}`
        }
      }
      return `Quarterly at ${sendTime}`
    case 'yearly':
      if (localCampaign.value.send_day && localCampaign.value.send_day.includes('-')) {
        const parts = localCampaign.value.send_day.split('-')
        if (parts.length === 2) {
          const month = parseInt(parts[0])
          const day = parseInt(parts[1])
          const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
          const monthName = monthNames[month - 1] || month
          return `Yearly on ${monthName} ${day} at ${sendTime}`
        }
      }
      return `Yearly at ${sendTime}`
    default:
      return `${localCampaign.value.default_frequency_days || 7} days`
  }
}

const previewSubject = computed(() => {
  if (!localCampaign.value.subject_template) return ''
  return previewStepText(localCampaign.value.subject_template, 0)
})

const previewMessage = computed(() => {
  if (!localCampaign.value.message_template) return ''
  return previewStepText(localCampaign.value.message_template, 0)
})

const { replaceTemplateVariables } = useTemplateVariables()

const previewStepText = (text, stepIndex) => {
  if (!text) return ''
  const freqType = localCampaign.value.frequency_type || 'weekly'
  // Frequency word will be determined by the composable based on frequencyType
  return replaceTemplateVariables(text, {
    useSampleData: true,
    frequencyType: freqType,
    frequency: '', // Not used anymore - composable determines from frequencyType
    frequencyDays: String(localCampaign.value.default_frequency_days || 7)
  })
}
</script>

