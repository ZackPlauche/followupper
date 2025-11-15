<template>
  <div v-if="show"
    class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-0 sm:p-4">
    <div
      class="bg-slate-800 rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full h-full sm:h-auto sm:max-w-4xl sm:max-h-[90vh] overflow-y-auto p-4 sm:p-8 space-y-4 sm:space-y-6">
      <div class="flex justify-between items-center mb-4 sm:mb-6">
        <h2 class="text-2xl sm:text-3xl font-thin gradient-title">
          {{ isEdit ? 'Edit Campaign' : 'Create New Campaign' }}
        </h2>
        <button @click="$emit('close')" class="sm:hidden text-slate-400 hover:text-slate-200 transition-colors">
          <Icon name="lucide:x" class="w-6 h-6" />
        </button>
      </div>

      <div>
        <label class="block text-sm font-light text-slate-300 mb-2">Campaign Name</label>
        <input v-model="localCampaign.name" type="text" placeholder="e.g., Weekly Check-ins"
          class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
      </div>

      <div>
        <label class="block text-sm font-light text-slate-300 mb-2">Description (Optional)</label>
        <textarea v-model="localCampaign.description" placeholder="Describe what this campaign is for..."
          class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors h-24 resize-none"></textarea>
      </div>

      <div>
        <label class="block text-sm font-light text-slate-300 mb-2">Campaign Type</label>
        <select v-model="localCampaign.campaign_type"
          class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
          <option value="recurring">Recurring</option>
          <option value="sequence">Sequence</option>
        </select>
      </div>

      <div v-if="localCampaign.campaign_type === 'recurring'">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Frequency</label>
            <select v-model="localCampaign.frequency_type" @change="handleFrequencyChange"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
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
            <label class="block text-sm font-light text-slate-300 mb-2">Send On</label>
            <select v-model="localCampaign.send_day"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
              <option value="1">1st of the month</option>
              <option value="15">15th of the month</option>
              <option value="last">Last day of the month</option>
            </select>
          </div>

          <div v-if="localCampaign.frequency_type === 'yearly'">
            <label class="block text-sm font-light text-slate-300 mb-2">Send On</label>
            <input v-model="yearlyDateInput" type="date" @input="handleYearlyDateChange"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
            <p class="text-xs text-slate-400 mt-1">Select a specific date (month and day) to send each year</p>
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Send Time</label>
            <input v-model="localCampaign.send_time" type="time"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
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

      <div v-if="localCampaign.campaign_type === 'recurring'">
        <label class="block text-sm font-light text-slate-300 mb-2">Message Template</label>
        <textarea v-model="localCampaign.message_template" placeholder="Hey {first_name}! Just checking in..."
          class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors h-32 resize-none"></textarea>
        <div class="text-xs text-slate-400 mt-2">
          <p>Available variables: <code class="bg-slate-700/50 px-2 py-1 rounded">{first_name}</code>, <code
              class="bg-slate-700/50 px-2 py-1 rounded">{name}</code>, <code
              class="bg-slate-700/50 px-2 py-1 rounded">{email}</code></p>
        </div>
      </div>

      <div v-if="localCampaign.campaign_type === 'sequence'">
        <label class="block text-sm font-light text-slate-300 mb-2">Sequence Steps</label>
        <div class="space-y-4">
          <div v-for="(step, index) in localCampaign.steps" :key="index"
            class="bg-slate-700/30 rounded-xl p-4 space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="text-sm font-medium text-slate-300">Step {{ index + 1 }}</h4>
              <button @click="removeStep(index)"
                class="px-3 py-1 bg-red-600/50 text-red-300 rounded-lg hover:bg-red-600/70 transition-colors text-sm">
                <Icon name="lucide:trash-2" class="w-4 h-4" />
              </button>
            </div>

            <div>
              <label class="block text-xs text-slate-400 mb-1">Subject</label>
              <input v-model="step.subject" type="text" placeholder="Step subject (optional)"
                class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>

            <textarea v-model="step.message" :placeholder="`Step ${index + 1} message...`"
              class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors h-24 resize-none"></textarea>

            <div class="flex items-center space-x-3">
              <div class="flex-1">
                <label class="block text-xs text-slate-400 mb-1">Delay (Days)</label>
                <input v-model.number="step.delay_days" type="number" min="0" placeholder="0"
                  class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
              </div>
              <div class="text-xs text-slate-400 pt-6">
                <p>Variables: <code class="bg-slate-700/50 px-2 py-1 rounded">{first_name}</code>, <code
                    class="bg-slate-700/50 px-2 py-1 rounded">{name}</code>, <code
                    class="bg-slate-700/50 px-2 py-1 rounded">{email}</code></p>
              </div>
            </div>
          </div>

          <button @click="addStep"
            class="w-full px-4 py-3 bg-slate-600/50 text-slate-300 rounded-xl hover:bg-slate-600/70 transition-colors border-2 border-dashed border-slate-600">
            <Icon name="lucide:plus" class="w-5 h-5 inline mr-2" />
            Add Step
          </button>
        </div>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Status</label>
          <select v-model="localCampaign.is_active"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
            <option :value="true">Active</option>
            <option :value="false">Inactive</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">When someone is added to this campaign:</label>
          <div class="space-y-2">
            <label class="flex items-center space-x-3">
              <input v-model="localCampaign.start_immediately" type="radio" value="immediate" name="start_behavior"
                class="form-radio h-4 w-4 text-emerald-500 border-slate-600 bg-slate-700/50 focus:ring-emerald-400">
              <span class="text-sm text-slate-300">Send first message immediately</span>
            </label>
            <label class="flex items-center space-x-3">
              <input v-model="localCampaign.start_immediately" type="radio" value="scheduled" name="start_behavior"
                class="form-radio h-4 w-4 text-emerald-500 border-slate-600 bg-slate-700/50 focus:ring-emerald-400">
              <span class="text-sm text-slate-300">Wait until next scheduled time</span>
            </label>
          </div>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row sm:justify-end gap-3 sm:gap-4 mt-6">
        <button @click="$emit('close')"
          class="flex-1 sm:flex-initial px-6 py-3 bg-slate-600/50 text-slate-300 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
          Cancel
        </button>
        <button @click="handleSave"
          class="flex-1 sm:flex-initial px-6 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-xl font-light hover:shadow-lg transition-all duration-300"
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

const localCampaign = ref({ ...props.campaign })
const yearlyDateInput = ref('')

watch(() => props.campaign, (newCampaign) => {
  localCampaign.value = { ...newCampaign }
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
}, { deep: true })

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
</script>

