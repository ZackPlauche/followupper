<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <h2 class="text-3xl font-thin text-slate-100">Message Templates</h2>
      <button @click="showTemplateForm = true" 
              class="bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105">
        + Add Template
      </button>
    </div>

      <!-- Templates List -->
      <div class="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        <div v-for="template in templates" :key="template.id" 
             class="bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 hover:shadow-emerald-500/10 hover:border-emerald-500/40 transition-all duration-300 hover:scale-105">
          <h3 class="text-xl font-light text-slate-100 mb-3">{{ template.name }}</h3>
          <p class="text-sm text-slate-300 mb-6 font-light">{{ template.subject || 'No subject' }}</p>
          <div class="flex justify-between items-center">
            <span :class="template.is_active ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-500/20 text-slate-400 border border-slate-500/30'"
                  class="inline-flex px-3 py-1 text-xs font-light rounded-full">
              {{ template.is_active ? 'Active' : 'Inactive' }}
            </span>
            <div class="flex space-x-3">
              <button @click="previewTemplate(template)" class="text-emerald-400 hover:text-emerald-300 text-sm font-light transition-colors">Preview</button>
              <button @click="editTemplate(template)" class="text-emerald-400 hover:text-emerald-300 text-sm font-light transition-colors">Edit</button>
              <button @click="handleDeleteTemplate(template.id)" class="text-red-400 hover:text-red-300 text-sm font-light transition-colors">Delete</button>
            </div>
          </div>
        </div>
      </div>

    <!-- Template Form Modal -->
    <div v-if="showTemplateForm" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="flex gap-6 w-full max-w-6xl mx-8">
        <!-- Form Panel -->
        <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 flex-1">
          <h3 class="text-2xl font-thin text-slate-100 mb-6">Add Template</h3>
          
          <form @submit.prevent="handleSaveTemplate" class="space-y-4">
            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">Template Name *</label>
              <input v-model="newTemplate.name" type="text" required
                     class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>
            
            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">Subject</label>
              <input v-model="newTemplate.subject" type="text"
                     class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                     placeholder="Hi {user.first_name}! 👋">
            </div>
            
            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">Message Body *</label>
              <textarea v-model="newTemplate.body" rows="8" required
                        class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                        placeholder="Hi {user.first_name}! 👋&#10;&#10;Thanks for your interest! 💼&#10;&#10;Your email: {user.email} 📧&#10;Notes: {user.notes}&#10;&#10;Best regards! ✨&#10;Your Team 🚀"></textarea>
            </div>
            
            <div class="flex items-center space-x-4">
              <label class="flex items-center space-x-2">
                <input v-model="newTemplate.is_active" type="checkbox"
                       class="w-4 h-4 text-emerald-500 bg-slate-700/50 border-emerald-500/30 rounded focus:ring-emerald-400">
                <span class="text-sm font-light text-slate-300">Active</span>
              </label>
            </div>
            
            <div class="flex space-x-3 pt-4">
              <button type="button" @click="showTemplateForm = false"
                      class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
                Cancel
              </button>
              <button type="submit"
                      class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
                Save Template
              </button>
            </div>
          </form>
        </div>
        
        <!-- Preview Card -->
        <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 w-96">
          <h4 class="text-lg font-thin text-slate-100 mb-6">Live Preview</h4>
          
          <!-- Subject Preview -->
          <div class="mb-4">
            <label class="block text-sm font-light text-emerald-400 mb-2">Subject</label>
            <div class="bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100">
              {{ previewTemplateSubject }}
            </div>
          </div>
          
          <!-- Body Preview -->
          <div class="mb-4">
            <label class="block text-sm font-light text-emerald-400 mb-2">Message Body</label>
            <div class="bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 min-h-[200px] whitespace-pre-wrap">
              {{ previewTemplateBody }}
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

    <!-- Edit Template Form Modal -->
    <div v-if="showEditTemplateForm" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="flex gap-6 w-full max-w-6xl mx-8">
        <!-- Form Panel -->
        <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 flex-1">
          <h3 class="text-2xl font-thin text-slate-100 mb-6">Edit Template</h3>
          
          <form @submit.prevent="handleUpdateTemplate" class="space-y-4">
            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">Template Name *</label>
              <input v-model="newTemplate.name" type="text" required
                     class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>
            
            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">Subject</label>
              <input v-model="newTemplate.subject" type="text"
                     class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                     placeholder="Hi {user.first_name}! 👋">
            </div>
            
            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">Message Body *</label>
              <textarea v-model="newTemplate.body" rows="8" required
                        class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                        placeholder="Hi {user.first_name}! 👋&#10;&#10;Thanks for your interest! 💼&#10;&#10;Your email: {user.email} 📧&#10;Notes: {user.notes}&#10;&#10;Best regards! ✨&#10;Your Team 🚀"></textarea>
            </div>
            
            <div class="flex items-center space-x-4">
              <label class="flex items-center space-x-2">
                <input v-model="newTemplate.is_active" type="checkbox"
                       class="w-4 h-4 text-emerald-500 bg-slate-700/50 border-emerald-500/30 rounded focus:ring-emerald-400">
                <span class="text-sm font-light text-slate-300">Active</span>
              </label>
            </div>
            
            <div class="flex space-x-3 pt-4">
              <button type="button" @click="showEditTemplateForm = false"
                      class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
                Cancel
              </button>
              <button type="submit"
                      class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
                Update Template
              </button>
            </div>
          </form>
        </div>
        
        <!-- Preview Card -->
        <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 w-96">
          <h4 class="text-lg font-thin text-slate-100 mb-6">Live Preview</h4>
          
          <!-- Subject Preview -->
          <div class="mb-4">
            <label class="block text-sm font-light text-emerald-400 mb-2">Subject</label>
            <div class="bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100">
              {{ previewTemplateSubject }}
            </div>
          </div>
          
          <!-- Body Preview -->
          <div class="mb-4">
            <label class="block text-sm font-light text-emerald-400 mb-2">Message Body</label>
            <div class="bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 min-h-[200px] whitespace-pre-wrap">
              {{ previewTemplateBody }}
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

    <!-- Preview Modal -->
    <div v-if="showPreviewModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 w-full max-w-4xl mx-8">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-thin text-slate-100">Template Preview</h3>
          <button @click="showPreviewModal = false" 
                  class="text-slate-400 hover:text-slate-200 transition-colors text-2xl">
            ×
          </button>
        </div>
        
        <div class="space-y-6">
          <!-- Subject Preview -->
          <div>
            <label class="block text-sm font-light text-emerald-400 mb-3">Subject</label>
            <div class="bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100">
              {{ previewData.subject }}
            </div>
          </div>
          
          <!-- Body Preview -->
          <div>
            <label class="block text-sm font-light text-emerald-400 mb-3">Message Body</label>
            <div class="bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 min-h-[300px] whitespace-pre-wrap">
              {{ previewData.body }}
            </div>
          </div>
          
          <!-- Sample Contact Info -->
          <div class="bg-slate-800/30 border border-emerald-500/20 rounded-xl p-4">
            <h4 class="text-sm font-light text-emerald-400 mb-2">Preview Data</h4>
            <div class="text-xs text-slate-300 space-y-1">
              <div><strong>Name:</strong> John Doe</div>
              <div><strong>Email:</strong> john@example.com</div>
              <div><strong>Notes:</strong> Great client! Very responsive 📧</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Status Bar -->
    <div v-if="showStatusBar" class="fixed bottom-6 right-6 bg-slate-800/90 backdrop-blur-sm rounded-xl shadow-2xl border border-emerald-500/20 overflow-hidden transition-all duration-300">
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
  title: 'Templates - Followupper'
})

// Use shared API state
const { templates, createTemplate, updateTemplate, deleteTemplate, loadTemplates, showStatusWithProgress } = useApi()

// Local UI state
const statusMessage = ref('Loading...')
const showStatusBar = ref(false)
const statusTimer = ref(null)
const statusProgress = ref(100)
const showTemplateForm = ref(false)
const showEditTemplateForm = ref(false)
const editingTemplate = ref(null)
const showPreviewModal = ref(false)
const previewData = ref({ subject: '', body: '' })

// Form data
const newTemplate = ref({
  name: '',
  subject: '',
  body: '',
  is_active: true
})


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

// Computed properties
const previewTemplateBody = computed(() => {
  if (!newTemplate.value.body) return 'Start typing your template...'
  
  // Sample contact data for preview
  const sampleContact = {
    name: 'John Doe',
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    notes: 'Great client! Very responsive 📧'
  }
  
  // Replace template variables with sample data
  let preview = newTemplate.value.body
  
  // Replace user variables
  preview = preview.replace(/\{user\.name\}/g, sampleContact.name)
  preview = preview.replace(/\{user\.first_name\}/g, sampleContact.first_name)
  preview = preview.replace(/\{user\.last_name\}/g, sampleContact.last_name)
  preview = preview.replace(/\{user\.email\}/g, sampleContact.email)
  preview = preview.replace(/\{user\.notes\}/g, sampleContact.notes)
  
  // Replace contact variables (same as user for now)
  preview = preview.replace(/\{contact\.name\}/g, sampleContact.name)
  preview = preview.replace(/\{contact\.first_name\}/g, sampleContact.first_name)
  preview = preview.replace(/\{contact\.last_name\}/g, sampleContact.last_name)
  preview = preview.replace(/\{contact\.email\}/g, sampleContact.email)
  preview = preview.replace(/\{contact\.notes\}/g, sampleContact.notes)
  
  return preview
})

const previewTemplateSubject = computed(() => {
  if (!newTemplate.value.subject) return 'Start typing your subject...'
  
  // Sample contact data for preview
  const sampleContact = {
    name: 'John Doe',
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    notes: 'Great client! Very responsive 📧'
  }
  
  // Replace template variables with sample data
  let preview = newTemplate.value.subject
  
  // Replace user variables
  preview = preview.replace(/\{user\.name\}/g, sampleContact.name)
  preview = preview.replace(/\{user\.first_name\}/g, sampleContact.first_name)
  preview = preview.replace(/\{user\.last_name\}/g, sampleContact.last_name)
  preview = preview.replace(/\{user\.email\}/g, sampleContact.email)
  preview = preview.replace(/\{user\.notes\}/g, sampleContact.notes)
  
  // Replace contact variables (same as user for now)
  preview = preview.replace(/\{contact\.name\}/g, sampleContact.name)
  preview = preview.replace(/\{contact\.first_name\}/g, sampleContact.first_name)
  preview = preview.replace(/\{contact\.last_name\}/g, sampleContact.last_name)
  preview = preview.replace(/\{contact\.email\}/g, sampleContact.email)
  preview = preview.replace(/\{contact\.notes\}/g, sampleContact.notes)
  
  return preview
})


const editTemplate = (template) => {
  editingTemplate.value = template
  newTemplate.value = {
    name: template.name,
    subject: template.subject,
    body: template.body,
    is_active: template.is_active
  }
  showEditTemplateForm.value = true
}

const previewTemplate = (template) => {
  // Use sample data for preview - no API call needed
  const sampleContact = {
    name: 'John Doe',
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    notes: 'Great client! Very responsive 📧'
  }
  
  // Replace template variables with sample data
  let previewSubject = template.subject || ''
  let previewBody = template.body || ''
  
  // Replace user variables
  previewSubject = previewSubject.replace(/\{user\.name\}/g, sampleContact.name)
  previewSubject = previewSubject.replace(/\{user\.first_name\}/g, sampleContact.first_name)
  previewSubject = previewSubject.replace(/\{user\.last_name\}/g, sampleContact.last_name)
  previewSubject = previewSubject.replace(/\{user\.email\}/g, sampleContact.email)
  previewSubject = previewSubject.replace(/\{user\.notes\}/g, sampleContact.notes)
  
  previewBody = previewBody.replace(/\{user\.name\}/g, sampleContact.name)
  previewBody = previewBody.replace(/\{user\.first_name\}/g, sampleContact.first_name)
  previewBody = previewBody.replace(/\{user\.last_name\}/g, sampleContact.last_name)
  previewBody = previewBody.replace(/\{user\.email\}/g, sampleContact.email)
  previewBody = previewBody.replace(/\{user\.notes\}/g, sampleContact.notes)
  
  // Set preview data and show modal
  previewData.value = {
    subject: previewSubject,
    body: previewBody
  }
  showPreviewModal.value = true
}

const handleDeleteTemplate = async (templateId) => {
  // Instant UI update
  templates.value = templates.value.filter(t => t.id !== templateId)
  
  // Background API call
  try {
    await deleteTemplate(templateId)
    showStatusWithProgressLocal('Template deleted successfully', 5000)
  } catch (error) {
    console.error('Error deleting template:', error)
    // Revert on error
    await loadTemplates()
    showStatusWithProgressLocal('Error deleting template', 5000)
  }
}

const handleSaveTemplate = async () => {
  // Store the template data before clearing the form
  const templateData = { ...newTemplate.value }
  
  // Instant UI update
  const tempId = Date.now() // Temporary ID
  const newTemplateData = {
    id: tempId,
    ...templateData,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
  
  templates.value.push(newTemplateData)
  showTemplateForm.value = false
  newTemplate.value = { name: '', subject: '', body: '', is_active: true }
  
  // Background API call
  try {
    const result = await createTemplate(templateData)
    // Update with real ID
    const index = templates.value.findIndex(t => t.id === tempId)
    if (index !== -1) {
      templates.value[index].id = result.id
    }
    showStatusWithProgressLocal('Template created successfully', 5000)
  } catch (error) {
    console.error('Error saving template:', error)
    // Revert on error
    templates.value = templates.value.filter(t => t.id !== tempId)
    showStatusWithProgressLocal('Error creating template', 5000)
  }
}

const handleUpdateTemplate = async () => {
  // Store the template data before clearing the form
  const templateData = { ...newTemplate.value }
  const templateId = editingTemplate.value.id
  
  // Instant UI update
  const index = templates.value.findIndex(t => t.id === templateId)
  if (index !== -1) {
    templates.value[index] = {
      ...templates.value[index],
      ...templateData,
      updated_at: new Date().toISOString()
    }
  }
  
  showEditTemplateForm.value = false
  editingTemplate.value = null
  newTemplate.value = { name: '', subject: '', body: '', is_active: true }
  
  // Background API call
  try {
    await updateTemplate(templateId, templateData)
    showStatusWithProgressLocal('Template updated successfully', 5000)
  } catch (error) {
    console.error('Error updating template:', error)
    // Revert on error
    await loadTemplates()
    showStatusWithProgressLocal('Error updating template', 5000)
  }
}




// Data is loaded at app startup, no need to load here
onMounted(() => {
  // No status message needed
})
</script>
