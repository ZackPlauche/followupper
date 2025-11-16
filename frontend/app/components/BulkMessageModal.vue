<template>
  <div v-if="show"
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
    <div
      class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full h-full sm:h-auto sm:max-w-6xl sm:max-h-[90vh] flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="flex justify-between items-center p-4 sm:p-6 border-b border-slate-700/50 flex-shrink-0">
        <h3 class="text-xl sm:text-2xl font-thin text-slate-100">Bulk Message ({{ contactCount }} contacts)</h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-200 transition-colors">
          <Icon name="lucide:x" class="w-6 h-6" />
        </button>
      </div>

      <!-- Scrollable Content -->
      <div class="flex-1 flex flex-col sm:flex-row gap-4 sm:gap-6 overflow-y-auto p-4 sm:p-6 min-h-0">
        <!-- Left: Message Composition -->
        <div class="flex-1 space-y-4">
          <!-- Variable Hints Info Block -->
          <VariableHints :show-frequency="false" mb-class="" />

          <div>
            <label class="block text-xs font-light text-slate-300 mb-1">
              Platforms *
              <span class="text-xs text-slate-500 ml-2">(Available for selected contacts)</span>
            </label>
            <div class="space-y-3">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="localMessage.usePreferredPlatforms"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                <span class="text-slate-300 text-sm">Use each contact's preferred platforms</span>
              </label>
              <div v-if="!localMessage.usePreferredPlatforms" class="flex gap-4">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" v-model="localMessage.platforms" value="email"
                    class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                  <span class="text-slate-300 text-sm">Email</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" v-model="localMessage.platforms" value="codementor"
                    class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                  <span class="text-slate-300 text-sm">Codementor</span>
                </label>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-xs font-light text-slate-300 mb-1">Template (optional)</label>
            <select v-model="selectedTemplate" @change="handleTemplateChange"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
              <option value="">None</option>
              <option v-for="template in templates" :key="template.id" :value="template.id">{{ template.name }}
              </option>
            </select>
          </div>

          <div v-if="localMessage.usePreferredPlatforms || localMessage.platforms.includes('email')">
            <label class="block text-xs font-light text-slate-300 mb-1">Subject *</label>
            <input v-model="localMessage.subject" type="text" required
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="Hello {first_name}!" />
          </div>

          <div>
            <label class="block text-xs font-light text-slate-300 mb-1">Message Body *</label>
            <textarea v-model="localMessage.body" rows="8" required
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
              placeholder="Hi {first_name}, ..."></textarea>
          </div>
        </div>

        <!-- Right: Preview Section -->
        <div class="w-full sm:w-96 border-t sm:border-t-0 sm:border-l border-slate-700/50 pt-4 sm:pl-6 sm:pt-0 flex-shrink-0">
          <h4 class="text-lg font-light text-slate-100 mb-4">Preview</h4>

          <!-- Message Preview -->
          <div class="bg-slate-700/30 rounded-lg p-4 border border-slate-600/30 mb-4">
            <div v-if="localMessage.subject" class="text-xs text-slate-400 mb-2">
              <strong>Subject:</strong> {{ previewText(localMessage.subject) }}
            </div>
            <div v-if="localMessage.body.trim()" class="text-sm text-slate-300 whitespace-pre-wrap">
              {{ previewText(localMessage.body) }}
            </div>
            <div v-else class="text-sm text-slate-500 italic">
              (No message body yet)
            </div>
          </div>

          <!-- User Data Section -->
          <div class="bg-slate-800/30 border border-emerald-500/20 rounded-xl p-3">
            <h5 class="text-sm font-light text-emerald-400 mb-2">Preview Data</h5>
            <div class="text-xs text-slate-300 space-y-1">
              <div><strong>Name:</strong> John Doe</div>
              <div><strong>Preferred Name:</strong> Johnny</div>
              <div><strong>Gender:</strong> Male</div>
              <div><strong>Email:</strong> john.doe@example.com</div>
              <div><strong>Codementor:</strong> johndoe</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex space-x-3 p-4 sm:p-6 border-t border-slate-700/50 flex-shrink-0">
        <button @click="handleSend" :disabled="!canSend"
          class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
          Send to {{ contactCount }} Contact{{ contactCount !== 1 ? 's' : '' }}
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
  contactCount: {
    type: Number,
    required: true
  },
  message: {
    type: Object,
    default: () => ({
      platforms: [],
      usePreferredPlatforms: false,
      subject: '',
      body: ''
    })
  },
  templates: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'send', 'template-change'])

const localMessage = ref({ ...props.message })
const selectedTemplate = ref('')

watch(() => props.message, (newMessage) => {
  localMessage.value = { ...newMessage }
}, { deep: true })

const canSend = computed(() => {
  if (!localMessage.value.body.trim()) return false
  if (!localMessage.value.usePreferredPlatforms && localMessage.value.platforms.length === 0) return false
  if ((localMessage.value.usePreferredPlatforms || localMessage.value.platforms.includes('email')) && !localMessage.value.subject.trim()) return false
  return true
})

const { replaceTemplateVariables } = useTemplateVariables()

const previewText = (text) => {
  if (!text) return ''
  return replaceTemplateVariables(text, {
    useSampleData: true,
    frequencyType: null,
    frequency: '',
    frequencyDays: ''
  })
}

const handleTemplateChange = () => {
  if (selectedTemplate.value) {
    const template = props.templates.find(t => t.id === parseInt(selectedTemplate.value))
    if (template) {
      if (template.subject) {
        localMessage.value.subject = template.subject
      }
      if (template.body) {
        localMessage.value.body = template.body
      }
    }
  }
  emit('template-change', selectedTemplate.value)
}

const handleSend = () => {
  if (canSend.value) {
    emit('send', { ...localMessage.value })
  }
}
</script>

