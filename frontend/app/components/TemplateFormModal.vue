<template>
  <div v-if="show"
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
    <div class="flex flex-col lg:flex-row gap-0 w-full h-full sm:h-auto sm:max-w-6xl sm:max-h-[90vh] overflow-y-auto lg:overflow-hidden p-0">
      <!-- Form Panel -->
      <div
        class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 flex-1 flex flex-col lg:overflow-hidden">
        <!-- Header -->
        <div class="p-4 sm:p-6 border-b border-slate-700/50 flex-shrink-0 flex justify-between items-center">
          <h3 class="text-xl sm:text-2xl font-thin text-slate-100">{{ isEdit ? 'Edit Template' : 'Add Template' }}</h3>
          <button @click="$emit('close')" class="text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="lucide:x" class="w-6 h-6" />
          </button>
        </div>

        <!-- Form Content -->
        <div class="p-4 sm:p-6 lg:flex-1 lg:overflow-y-auto lg:min-h-0">
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">Template Name *</label>
              <input v-model="localTemplate.name" type="text" required
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">
                Subject
                <span class="text-xs text-slate-500 ml-2">Variables: {name}, {first_name}, {preferred_name},
                  {last_name}, {email}, {gender}. Conditionals: {if_male:text}{if_female:text}</span>
              </label>
              <input v-model="localTemplate.subject" type="text"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                placeholder="Hi {first_name}! 👋">
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">
                Message Body *
                <span class="text-xs text-slate-500 ml-2">Variables: {name}, {first_name}, {preferred_name},
                  {last_name}, {email}, {codementor_username}, {gender}. Conditionals:
                  {if_male:text}{if_female:text}</span>
              </label>
              <textarea v-model="localTemplate.body" rows="8" required
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                placeholder="Hi {first_name}! 👋&#10;&#10;Thanks for your interest! 💼&#10;&#10;Your email: {email} 📧&#10;Notes: {notes}&#10;&#10;Best regards! ✨&#10;Your Team 🚀"></textarea>
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">
                Footer/Signature (Email only)
                <span class="text-xs text-slate-500 ml-2">Variables: {name}, {first_name}, {preferred_name},
                  {last_name}, {email}, {gender}. Conditionals: {if_male:text}{if_female:text}</span>
              </label>
              <textarea v-model="localTemplate.footer" rows="3"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                placeholder="Best regards,&#10;Your Name"></textarea>
            </div>

            <div class="flex items-center space-x-4">
              <label class="flex items-center space-x-2">
                <input v-model="localTemplate.is_active" type="checkbox"
                  class="w-4 h-4 text-emerald-500 bg-slate-700/50 border-emerald-500/30 rounded focus:ring-emerald-400">
                <span class="text-sm font-light text-slate-300">Active</span>
              </label>
            </div>

            <div class="flex flex-col sm:flex-row gap-3 pt-4">
              <button type="button" @click="$emit('close')"
                class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
                Cancel
              </button>
              <button type="submit"
                class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
                {{ isEdit ? 'Update Template' : 'Save Template' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Preview Card -->
      <div
        class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full lg:w-96 flex flex-col lg:overflow-hidden flex-shrink-0">
        <div class="p-4 sm:p-6 border-b border-slate-700/50 flex-shrink-0 flex justify-between items-center">
          <h4 class="text-base sm:text-lg font-thin text-slate-100">Live Preview</h4>
          <button @click="$emit('close')" class="lg:hidden text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="lucide:x" class="w-5 h-5" />
          </button>
        </div>
        <div class="p-4 sm:p-6 lg:flex-1 lg:overflow-y-auto lg:min-h-0">
          <!-- Subject Preview -->
          <div class="mb-4">
            <label class="block text-sm font-light text-emerald-400 mb-2">Subject</label>
            <div class="bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100">
              {{ previewSubject }}
            </div>
          </div>

          <!-- Body Preview -->
          <div class="mb-4">
            <label class="block text-sm font-light text-emerald-400 mb-2">Message Body</label>
            <div
              class="bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 min-h-[200px] whitespace-pre-wrap overflow-y-auto">
              {{ previewBody }}
            </div>
          </div>

          <!-- Sample Contact Info -->
          <div class="bg-slate-800/30 border border-emerald-500/20 rounded-xl p-3">
            <h5 class="text-sm font-light text-emerald-400 mb-2">Preview Data</h5>
            <div class="text-xs text-slate-300 space-y-1">
              <div><strong>Name:</strong> John Doe</div>
              <div><strong>Email:</strong> john@example.com</div>
              <div><strong>Notes:</strong> Great client! Very responsive 📧</div>
            </div>
          </div>
        </div>
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

const previewSubject = computed(() => {
  if (!localTemplate.value.subject) return ''
  return localTemplate.value.subject
    .replace(/\{name\}/g, 'John Doe')
    .replace(/\{first_name\}/g, 'John')
    .replace(/\{preferred_name\}/g, 'Johnny')
    .replace(/\{last_name\}/g, 'Doe')
    .replace(/\{email\}/g, 'john@example.com')
    .replace(/\{gender\}/g, 'male')
})

const previewBody = computed(() => {
  if (!localTemplate.value.body) return ''
  let result = localTemplate.value.body
  result = result.replace(/\{if_male:([^}]+)\}/g, '$1')
  result = result.replace(/\{if_female:([^}]+)\}/g, '')
  result = result.replace(/\{name\}/g, 'John Doe')
  result = result.replace(/\{first_name\}/g, 'John')
  result = result.replace(/\{preferred_name\}/g, 'Johnny')
  result = result.replace(/\{last_name\}/g, 'Doe')
  result = result.replace(/\{email\}/g, 'john@example.com')
  result = result.replace(/\{codementor_username\}/g, 'johndoe')
  result = result.replace(/\{gender\}/g, 'male')
  return result
})

const handleSubmit = () => {
  emit('save', { ...localTemplate.value })
}
</script>

