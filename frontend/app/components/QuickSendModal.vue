<template>
  <div v-if="show"
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
    <div
      class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full h-full sm:h-auto sm:max-w-md sm:max-h-[90vh] flex flex-col">
      <div class="p-6 border-b border-slate-700/50 flex items-center justify-between">
        <h3 class="text-2xl font-thin text-slate-100">Send Message to {{ contact?.name }}</h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-200 transition-colors">
          <Icon name="material-symbols:close" class="w-6 h-6" />
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-6">
        <div class="space-y-3">
          <!-- Mode Toggle -->
          <div class="flex items-center justify-between mb-4">
            <h4 class="text-lg font-light text-slate-100">{{ isChainMode ? 'Send Message Chain' : 'Send Message' }}</h4>
            <div class="flex items-center bg-slate-700/50 rounded-lg p-1 border border-slate-500/30">
              <button type="button" @click="isChainMode = false"
                :class="!isChainMode ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="flex items-center px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                <Icon name="fa:send" class="w-4 h-4" />
              </button>
              <button type="button" @click="handleChainModeToggle"
                :class="isChainMode ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="flex items-center space-x-2 px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                <Icon name="mage:link" class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Single Message Mode -->
          <div v-if="!isChainMode" class="space-y-3">
            <!-- Template Selection -->
            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Template (optional)</label>
              <select v-model="selectedTemplate" @change="applyTemplate"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
                <option value="">None</option>
                <option v-for="template in templates" :key="template.id" :value="template.id">{{ template.name }}</option>
              </select>
            </div>

            <!-- Subject (only for email) -->
            <div v-if="message.platforms.includes('email')">
              <label class="block text-sm font-light text-slate-300 mb-1">Subject *</label>
              <input v-model="message.subject" type="text" required
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                placeholder="Message subject">
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Message *</label>
              <textarea v-model="message.body" rows="5" required
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                placeholder="Enter your message here..."></textarea>
            </div>

            <!-- Platform Selection -->
            <PlatformMultiSelect v-model="message.platforms"
              :available-platforms="availablePlatforms" label="Platforms"
              label-class="block text-sm font-light text-slate-300 mb-1" />

            <div v-if="message.schedule" class="space-y-3">
              <div class="flex items-end gap-3">
                <div class="flex-1">
                  <label class="block text-xs font-light text-slate-300 mb-1">Send Date</label>
                  <input v-model="message.send_date" type="date"
                    class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                </div>
                <div class="flex-1">
                  <label class="block text-xs font-light text-slate-300 mb-1">Send Time</label>
                  <input v-model="message.send_time" type="time"
                    class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                </div>
                <div>
                  <label class="block text-xs font-light text-slate-300 mb-1">Timezone</label>
                  <div class="flex items-center bg-slate-600/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                    <button type="button" @click="message.timezone = 'my'"
                      :class="message.timezone === 'my' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                      class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                      Mine
                    </button>
                    <button type="button" @click="message.timezone = 'user'"
                      :class="message.timezone === 'user' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                      class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                      Contact
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Chain Mode -->
          <div v-else class="space-y-4">
            <!-- Global Chain Settings -->
            <!-- Subject (only for email) -->
            <div v-if="chainSettings.platforms.includes('email')">
              <label class="block text-sm font-light text-slate-300 mb-1">Subject (applies to all messages) *</label>
              <input v-model="chainSubject" type="text" required
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors"
                placeholder="Message subject">
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Footer/Signature (applies to all messages)</label>
              <textarea v-model="chainFooter" rows="3"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                placeholder="Message footer"></textarea>
            </div>

            <!-- Platform Selection -->
            <PlatformMultiSelect v-model="chainSettings.platforms"
              :available-platforms="availablePlatforms" label="Platforms"
              label-class="block text-sm font-light text-slate-300 mb-1" />

            <!-- Chain Timing Settings -->
            <div class="space-y-3">
              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Timing Type</label>
                <div class="flex items-center bg-slate-700/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                  <button type="button" @click="chainSettings.timingType = 'interval'"
                    :class="chainSettings.timingType === 'interval' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                    class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                    Interval
                  </button>
                  <button type="button" @click="chainSettings.timingType = 'specific'"
                    :class="chainSettings.timingType === 'specific' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                    class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                    Specific
                  </button>
                </div>
              </div>

              <div v-if="chainSettings.timingType === 'interval'" class="space-y-2">
                <div class="flex items-center space-x-2">
                  <input type="checkbox" v-model="chainSettings.sendFirstImmediately"
                    id="quick-send-first-immediately"
                    class="w-4 h-4 rounded border-emerald-500/30 bg-slate-600/50 text-emerald-500 focus:ring-emerald-500 focus:ring-2">
                  <label for="quick-send-first-immediately" class="text-xs text-slate-300 cursor-pointer">Send first
                    message immediately</label>
                </div>

                <div class="space-y-2">
                  <div class="flex items-end gap-2">
                    <div class="flex-1">
                      <label class="block text-xs font-light text-slate-300 mb-1">Start Date</label>
                      <input v-model="chainSettings.startDate" type="date"
                        class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                    </div>
                    <div class="flex-1">
                      <label class="block text-xs font-light text-slate-300 mb-1">Start Time</label>
                      <input v-model="chainSettings.startTime" type="time"
                        class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                    </div>
                    <div>
                      <label class="block text-xs font-light text-slate-300 mb-1">Timezone</label>
                      <div class="flex items-center bg-slate-600/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                        <button type="button" @click="chainSettings.timezone = 'my'"
                          :class="chainSettings.timezone === 'my' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                          class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                          Mine
                        </button>
                        <button type="button" @click="chainSettings.timezone = 'user'"
                          :class="chainSettings.timezone === 'user' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                          class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                          Contact
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-for="(msg, index) in messageChain" :key="index"
              class="bg-slate-600/30 rounded-lg p-4 border border-slate-500/20">
              <div class="flex items-start justify-between mb-3">
                <h5 class="text-sm font-medium text-slate-200">Message {{ index + 1 }}</h5>
                <button type="button" @click="removeMessageFromChain(index)"
                  class="text-slate-400 hover:text-red-400 transition-colors">
                  <Icon name="lucide:trash-2" class="w-4 h-4" />
                </button>
              </div>

              <div class="space-y-3">
                <div>
                  <label class="block text-xs font-light text-slate-300 mb-1">Message *</label>
                  <textarea v-model="msg.body" rows="4" required
                    class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                    placeholder="Enter your message here..."></textarea>
                </div>

                <!-- Interval Mode -->
                <div v-if="chainSettings.timingType === 'interval' && index > 0">
                  <label class="block text-xs font-light text-slate-300 mb-1">
                    Days after previous message
                  </label>
                  <input v-model.number="msg.frequency_days" type="number" min="0" step="1"
                    class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors"
                    placeholder="0 = send immediately after previous">
                </div>

                <!-- Specific Date/Time Mode -->
                <div v-else-if="chainSettings.timingType === 'specific'" class="space-y-2">
                  <div class="flex items-end gap-2">
                    <div class="flex-1">
                      <label class="block text-xs font-light text-slate-300 mb-1">Send Date</label>
                      <input v-model="msg.send_date" type="date"
                        class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                    </div>
                    <div class="flex-1">
                      <label class="block text-xs font-light text-slate-300 mb-1">Send Time</label>
                      <input v-model="msg.send_time" type="time"
                        class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                    </div>
                    <div>
                      <label class="block text-xs font-light text-slate-300 mb-1">Timezone</label>
                      <div class="flex items-center bg-slate-600/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                        <button type="button" @click="msg.timezone = 'my'"
                          :class="msg.timezone === 'my' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                          class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                          Mine
                        </button>
                        <button type="button" @click="msg.timezone = 'user'"
                          :class="msg.timezone === 'user' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                          class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                          Contact
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <button type="button" @click="addMessageToChain"
              class="w-full py-2 border-2 border-dashed border-emerald-500/30 rounded-lg text-emerald-300 hover:border-emerald-500/50 hover:bg-emerald-500/10 transition-colors flex items-center justify-center">
              <Icon name="lucide:plus" class="w-4 h-4 mr-2" />
              Add Another Message
            </button>
          </div>
        </div>
      </div>

      <div class="p-6 border-t border-slate-700/50 flex space-x-3">
        <button type="button" @click="$emit('close')"
          class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-2 rounded-lg text-sm font-light hover:bg-slate-600/70 transition-colors">
          Cancel
        </button>
        <button @click="handleSend"
          class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-2 rounded-lg text-sm font-light hover:shadow-lg transition-all duration-300">
          {{ message.schedule ? 'Schedule' : 'Send' }}
        </button>
        <button @click="message.schedule = !message.schedule"
          class="px-3 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg text-sm font-light hover:shadow-lg transition-all duration-300">
          <Icon name="material-symbols:schedule-send" class="w-4 h-4" />
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
  contact: {
    type: Object,
    default: null
  },
  templates: {
    type: Array,
    default: () => []
  },
  availablePlatforms: {
    type: Array,
    default: () => []
  },
  defaultFooter: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'send', 'send-chain'])

const isChainMode = ref(false)
const selectedTemplate = ref('')
const message = ref({
  platforms: [],
  subject: '',
  body: '',
  send_date: '',
  send_time: '',
  schedule: false,
  timezone: 'my'
})
const chainSubject = ref('')
const chainFooter = ref('')
const chainSettings = ref({
  platforms: [],
  sendFirstImmediately: false,
  timingType: 'interval',
  startDate: '',
  startTime: '',
  timezone: 'my'
})
const messageChain = ref([])

watch(() => props.show, (newVal) => {
  if (newVal && props.contact) {
    initializeModal()
  }
})

const getTodayDate = () => {
  return new Date().toISOString().split('T')[0]
}

const getCurrentTime = () => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

const getDefaultPlatforms = (contact) => {
  if (!contact) return []
  let preference = contact.platform_preference
  if (!preference) {
    preference = contact.email ? ['email'] : []
  } else if (typeof preference === 'string') {
    if (preference === 'both') {
      preference = ['email', 'codementor']
    } else {
      preference = [preference]
    }
  }
  if (!Array.isArray(preference)) {
    preference = []
  }
  return preference.filter(p => {
    if (p === 'email') return !!contact.email
    if (p === 'codementor') return !!contact.codementor_username
    return false
  })
}

const initializeModal = () => {
  const defaultPlatforms = getDefaultPlatforms(props.contact)
  message.value = {
    platforms: defaultPlatforms.length > 0 ? defaultPlatforms : (props.contact.email ? ['email'] : []),
    subject: '',
    body: '',
    send_date: getTodayDate(),
    send_time: getCurrentTime(),
    schedule: false,
    timezone: 'my'
  }
  isChainMode.value = false
  selectedTemplate.value = ''
  loadMessageChain()
}

const loadMessageChain = () => {
  messageChain.value = []
  chainSubject.value = ''
  chainFooter.value = props.defaultFooter || ''
  const defaultPlatforms = getDefaultPlatforms(props.contact)
  chainSettings.value = {
    platforms: defaultPlatforms.length > 0 ? defaultPlatforms : (props.contact?.email ? ['email'] : []),
    sendFirstImmediately: false,
    timingType: 'interval',
    startDate: getTodayDate(),
    startTime: getCurrentTime(),
    timezone: 'my'
  }
}

const handleChainModeToggle = () => {
  isChainMode.value = true
  loadMessageChain()
  addMessageToChain()
}

const addMessageToChain = () => {
  const newMessage = {
    body: '',
    send_date: getTodayDate(),
    send_time: getCurrentTime(),
    timezone: 'my',
    frequency_days: 1
  }
  messageChain.value.push(newMessage)
}

const removeMessageFromChain = (index) => {
  messageChain.value.splice(index, 1)
}

const applyTemplate = () => {
  if (!selectedTemplate.value) return
  const template = props.templates.find(t => t.id === parseInt(selectedTemplate.value))
  if (template) {
    if (template.subject) {
      message.value.subject = template.subject
    }
    if (template.body) {
      message.value.body = template.body
      if (message.value.platforms.includes('email')) {
        const footerToUse = template.footer || props.defaultFooter || ''
        if (footerToUse) {
          message.value.body = message.value.body + '\n\n' + footerToUse
        }
      }
    }
  }
}

const handleSend = () => {
  if (isChainMode.value) {
    emit('send-chain', {
      subject: chainSubject.value,
      footer: chainFooter.value,
      settings: { ...chainSettings.value },
      messages: [...messageChain.value]
    })
  } else {
    emit('send', { ...message.value })
  }
}
</script>

