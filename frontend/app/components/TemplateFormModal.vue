<template>
  <div v-if="show"
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
    <div
      class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full h-full sm:h-auto sm:max-w-6xl sm:max-h-[90vh] flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="flex justify-between items-center p-4 sm:p-6 border-b border-slate-700/50 flex-shrink-0">
        <h3 class="text-xl sm:text-2xl font-thin text-slate-100">{{ isEdit ? 'Edit Template' : 'Add Template' }}</h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-200 transition-colors">
          <Icon name="lucide:x" class="w-6 h-6" />
        </button>
      </div>

      <!-- Scrollable Content -->
      <div class="flex-1 flex flex-col sm:flex-row gap-4 sm:gap-6 overflow-y-auto p-4 sm:p-6 min-h-0">
        <!-- Left: Form -->
        <div class="flex-1 space-y-4">
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <!-- Variable Hints Info Block -->
            <VariableHints :show-frequency="true" />

            <div>
              <label class="block text-xs font-light text-slate-300 mb-1">Template Name *</label>
              <input v-model="localTemplate.name" type="text" required
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>

            <div>
              <label class="block text-xs font-light text-slate-300 mb-1">Subject</label>
              <input v-model="localTemplate.subject" type="text"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                placeholder="Hello {first_name}!">
            </div>

            <div>
              <label class="block text-xs font-light text-slate-300 mb-1">Message Body *</label>
              <textarea v-model="localTemplate.body" rows="8" required
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                placeholder="Hi {first_name},&#10;&#10;Thanks for your interest!&#10;&#10;Your email: {email}&#10;&#10;Best regards!"></textarea>
            </div>

            <div>
              <label class="block text-xs font-light text-slate-300 mb-1">Footer/Signature (Email only)</label>
              <textarea v-model="localTemplate.footer" rows="3"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                placeholder="Best regards,&#10;Your Name"></textarea>
            </div>

            <div class="flex items-center space-x-4 pb-4">
              <label class="flex items-center space-x-2">
                <input v-model="localTemplate.is_active" type="checkbox"
                  class="w-4 h-4 text-emerald-500 bg-slate-700/50 border-emerald-500/30 rounded focus:ring-emerald-400">
                <span class="text-sm font-light text-slate-300">Active</span>
              </label>
            </div>

          </form>
        </div>

        <!-- Right: Preview Section -->
        <div class="w-full sm:w-96 border-t sm:border-t-0 sm:border-l border-slate-700/50 pt-4 sm:pl-6 sm:pt-0 flex-shrink-0">
          <h4 class="text-lg font-light text-slate-100 mb-4">Preview</h4>

          <!-- Message Preview -->
          <div class="bg-slate-700/30 rounded-lg p-4 border border-slate-600/30 mb-4">
            <div v-if="localTemplate.subject" class="text-xs text-slate-400 mb-2">
              <strong>Subject:</strong> {{ previewSubject }}
            </div>
            <div v-if="localTemplate.body.trim()" class="text-sm text-slate-300 whitespace-pre-wrap">
              {{ previewBody }}
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
        <button type="button" @click="$emit('close')"
          class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
          Cancel
        </button>
        <button @click="handleSubmit"
          class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
          {{ isEdit ? 'Update Template' : 'Save Template' }}
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
  template: {
    type: Object,
    default: () => ({
      name: '',
      subject: '',
      body: '',
      footer: '',
      is_active: true
    })
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'save'])

const localTemplate = ref({ ...props.template })

watch(() => props.template, (newTemplate) => {
  localTemplate.value = { ...newTemplate }
}, { deep: true })

const { replaceTemplateVariables } = useTemplateVariables()

const previewSubject = computed(() => {
  if (!localTemplate.value.subject) return ''
  return replaceTemplateVariables(localTemplate.value.subject, {
    useSampleData: true,
    frequencyType: null,
    frequency: '',
    frequencyDays: ''
  })
})

const previewBody = computed(() => {
  if (!localTemplate.value.body) return ''
  return replaceTemplateVariables(localTemplate.value.body, {
    useSampleData: true,
    frequencyType: 'weekly',
    frequency: 'Weekly',
    frequencyDays: '7'
  })
})

const handleSubmit = () => {
  if (!localTemplate.value.name || !localTemplate.value.body) return
  emit('save', { ...localTemplate.value })
}
</script>

