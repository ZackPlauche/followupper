<template>
  <div>
    <div class="mb-6 sm:mb-8">
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-4">
        <h2 class="text-2xl sm:text-3xl font-thin text-slate-100">Contacts</h2>
        <div class="flex flex-wrap gap-2 sm:gap-3 ml-auto">
          <button @click="showFilters = !showFilters"
            :class="['bg-slate-700/50 border text-slate-300 px-4 py-2.5 rounded-xl font-light hover:border-emerald-500/50 hover:text-emerald-400 transition-all duration-300 text-sm sm:text-base flex items-center justify-center gap-1.5 sm:gap-2 h-10', showFilters ? 'border-emerald-500/50 text-emerald-400' : 'border-emerald-500/30']">
            <Icon name="lucide:sliders-horizontal" class="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" />
            <span class="hidden sm:inline">Filters</span>
            <span v-if="hasActiveFilters"
              class="px-1.5 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-xs">
              {{ activeFilterCount }}
            </span>
          </button>
          <button v-if="selectedContactIds.size > 0" @click="openBulkEditModal"
            class="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2.5 rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105 text-sm sm:text-base h-10 flex items-center justify-center">
            <span class="hidden sm:inline">Bulk Edit</span>
            <span class="sm:hidden">Edit</span>
            <span class="ml-1">({{ selectedContactIds.size }})</span>
          </button>
          <button v-if="selectedContactIds.size > 0" @click="openBulkMessageModal"
            class="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-4 py-2.5 rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105 text-sm sm:text-base h-10 flex items-center justify-center">
            <span class="hidden sm:inline">Bulk Message</span>
            <span class="sm:hidden">Message</span>
            <span class="ml-1">({{ selectedContactIds.size }})</span>
          </button>
          <button v-if="selectedContactIds.size > 0" @click="handleBulkDelete"
            class="bg-gradient-to-r from-red-500 to-orange-500 text-white px-4 py-2.5 rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105 text-sm sm:text-base h-10 flex items-center justify-center">
            <span class="hidden sm:inline">Bulk Delete</span>
            <span class="sm:hidden">Delete</span>
            <span class="ml-1">({{ selectedContactIds.size }})</span>
          </button>
          <button @click="exportContacts"
            class="bg-slate-700/50 border border-emerald-500/30 text-slate-300 px-4 py-2.5 rounded-xl font-light hover:border-emerald-500/50 hover:text-emerald-400 transition-all duration-300 text-sm sm:text-base h-10 flex items-center justify-center gap-1.5 sm:gap-2">
            <Icon name="lucide:upload" class="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" />
            <span class="hidden sm:inline">Export</span>
          </button>
          <button @click="showImportModal = true"
            class="bg-slate-700/50 border border-emerald-500/30 text-slate-300 px-4 py-2.5 rounded-xl font-light hover:border-emerald-500/50 hover:text-emerald-400 transition-all duration-300 text-sm sm:text-base h-10 flex items-center justify-center gap-1.5 sm:gap-2">
            <Icon name="lucide:download" class="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" />
            <span class="hidden sm:inline">Import</span>
          </button>
          <button @click="showContactForm = true"
            class="bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-2.5 rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105 text-sm sm:text-base h-10 flex items-center justify-center">
            <span class="sm:hidden">+</span>
            <span class="hidden sm:inline">+ Add Contact</span>
          </button>
        </div>
      </div>

      <!-- Search Bar (Always Visible) -->
      <div class="mb-4">
        <label class="block text-sm font-light text-slate-300 mb-2">Search</label>
        <input v-model="filterSearch" type="text" placeholder="Search by name..."
          class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-4 py-2.5 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
      </div>

      <!-- Filters Panel (Collapsible) -->
      <ContactFilters :show="showFilters" :filters="filterData" :available-sources="availableSources"
        @update:filters="updateFilters" />
    </div>

    <!-- Contacts List -->
    <div
      class="bg-slate-800/50 backdrop-blur-sm rounded-xl sm:rounded-2xl shadow-2xl border border-emerald-500/20 overflow-hidden">
      <!-- Desktop Table View -->
      <div class="hidden md:block overflow-x-auto">
        <table class="min-w-full divide-y divide-emerald-500/20">
          <thead class="bg-slate-700/50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider w-12">
                <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
              </th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Name</th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Platforms
              </th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Status</th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Last Messaged
              </th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-slate-800/30 divide-y divide-emerald-500/10">
            <tr v-for="contact in filteredContacts" :key="contact.id" class="hover:bg-slate-700/30 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <input type="checkbox" :checked="selectedContactIds.has(contact.id)"
                  @change="toggleContactSelection(contact.id)"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-light text-slate-100">
                <div class="flex items-center gap-2">
                  <button @click="toggleFavorite(contact)" class="transition group"
                    :class="contact.is_favorite ? '' : 'opacity-30 hover:opacity-100'">
                    <Icon :name="contact.is_favorite ? 'mdi:star' : 'mdi:star-outline'"
                      class="w-4 h-4 text-yellow-400 group-hover:text-yellow-300" />
                  </button>
                  <button @click="openContactProfile(contact)"
                    class="hover:text-emerald-400 transition-colors cursor-pointer">
                    {{ contact.name }}
                  </button>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-3">
                  <div class="flex items-center gap-1.5" :class="contact.email ? '' : 'opacity-40'">
                    <Icon name="lucide:mail" class="w-4 h-4"
                      :class="contact.email ? 'text-slate-300' : 'text-slate-500'" />
                  </div>
                  <div class="flex items-center gap-1.5" :class="contact.codementor_username ? '' : 'opacity-40'">
                    <Icon name="simple-icons:codementor" class="w-4 h-4"
                      :class="contact.codementor_username ? 'text-slate-300' : 'text-slate-500'" />
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="contact.is_active ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'"
                  class="inline-flex px-3 py-1 text-xs font-light rounded-full">
                  {{ contact.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-light text-slate-300">
                {{ formatLastMessaged(contact.last_messaged) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-light">
                <button @click="openQuickSendModal(contact)"
                  class="text-blue-400 hover:text-blue-300 mr-4 transition-colors">Send</button>
                <button @click="editContact(contact)"
                  class="text-emerald-400 hover:text-emerald-300 mr-4 transition-colors">Edit</button>
                <button @click="handleDeleteContact(contact.id)"
                  class="text-red-400 hover:text-red-300 transition-colors">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Card View -->
      <div class="md:hidden">
        <!-- Select All Header -->
        <div class="bg-slate-700/50 p-4 mb-2 rounded-t-xl">
          <div class="flex items-center gap-2">
            <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll"
              class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
            <span class="text-sm font-light text-emerald-400">Select All</span>
          </div>
        </div>
        <div class="divide-y divide-emerald-500/10">
          <div v-for="contact in filteredContacts" :key="contact.id" class="p-4 hover:bg-slate-700/30 transition-colors">
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-2 flex-1">
              <input type="checkbox" :checked="selectedContactIds.has(contact.id)"
                @change="toggleContactSelection(contact.id)"
                class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500 mt-1" />
              <button @click="toggleFavorite(contact)" class="transition group"
                :class="contact.is_favorite ? '' : 'opacity-30 hover:opacity-100'">
                <Icon :name="contact.is_favorite ? 'mdi:star' : 'mdi:star-outline'"
                  class="w-4 h-4 text-yellow-400 group-hover:text-yellow-300" />
              </button>
              <button @click="openContactProfile(contact)"
                class="text-slate-100 hover:text-emerald-400 transition-colors cursor-pointer font-medium">
                {{ contact.name }}
              </button>
            </div>
            <span
              :class="contact.is_active ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'"
              class="inline-flex px-2 py-1 text-xs font-light rounded-full">
              {{ contact.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="flex items-center gap-3 mb-3">
            <div :class="contact.email ? '' : 'opacity-40'">
              <Icon name="lucide:mail" class="w-4 h-4" :class="contact.email ? 'text-slate-300' : 'text-slate-500'" />
            </div>
            <div :class="contact.codementor_username ? '' : 'opacity-40'">
              <Icon name="simple-icons:codementor" class="w-4 h-4"
                :class="contact.codementor_username ? 'text-slate-300' : 'text-slate-500'" />
            </div>
          </div>
          <div class="text-xs text-slate-400 mb-3">
            Last messaged: {{ formatLastMessaged(contact.last_messaged) }}
          </div>
          <div class="flex gap-3">
            <button @click="openQuickSendModal(contact)"
              class="flex-1 text-center px-3 py-2 bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30 transition-colors text-sm">
              Send
            </button>
            <button @click="editContact(contact)"
              class="flex-1 text-center px-3 py-2 bg-emerald-500/20 text-emerald-400 rounded-lg hover:bg-emerald-500/30 transition-colors text-sm">
              Edit
            </button>
            <button @click="handleDeleteContact(contact.id)"
              class="flex-1 text-center px-3 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors text-sm">
              Delete
            </button>
          </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contact Form Modal -->
    <ContactFormModal :show="showContactForm" :available-platforms="availablePlatforms" @close="showContactForm = false"
      @save="handleSaveContact" />

    <!-- Edit Contact Form Modal -->
    <ContactFormModal :show="showEditContactForm" :contact="editingContact" :available-platforms="availablePlatforms"
      @close="showEditContactForm = false; editingContact = null" @save="handleUpdateContact" />

    <!-- Quick Send Modal -->
    <QuickSendModal
      :show="showQuickSendModal"
      :contact="selectedContact"
      :templates="activeTemplates"
      :available-platforms="quickSendAvailablePlatforms"
      :default-footer="settings?.user?.footer || ''"
      @close="closeQuickSendModal"
      @send="handleQuickSend"
      @send-chain="handleQuickSendChain"
    />

    <!-- Status Bar -->
    <StatusBar :show="showStatusBar" :message="statusMessage" :progress="statusProgress" />

    <!-- Bulk Edit Modal -->
    <BulkEditModal
      :show="showBulkEditModal"
      :contact-count="selectedContactIds.size"
      :data="bulkEditData"
      @close="closeBulkEditModal"
      @save="handleBulkEdit"
    />

    <!-- Bulk Message Modal -->
    <BulkMessageModal
      :show="showBulkMessageModal"
      :contact-count="selectedContactIds.size"
      :message="bulkMessage"
      :templates="activeTemplates"
      @close="closeBulkMessageModal"
      @send="handleBulkSend"
      @template-change="applyBulkTemplate"
    />

    <!-- Contact Profile Modal -->
    <ContactProfile v-if="showContactProfileModal && selectedContact" :contact="selectedContact"
      :upcoming-messages="upcomingMessages" :is-modal="true" @close="closeContactProfileModal"
      @update="handleContactUpdate" @send-message="handleSendMessage" />

    <!-- Import Modal -->
    <div v-if="showImportModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
      <div
        class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full h-full sm:h-auto sm:max-w-md flex flex-col">
        <div class="p-6 border-b border-slate-700/50 flex justify-between items-center">
          <h3 class="text-2xl font-thin text-slate-100">Import Contacts</h3>
          <button @click="showImportModal = false" class="text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="lucide:x" class="w-6 h-6" />
          </button>
        </div>
        <div class="p-6">
          <div class="mb-4 flex items-center gap-2">
            <label class="text-sm text-slate-300 font-light">Select CSV File</label>
            <button @click="showImportInstructions = !showImportInstructions"
              class="text-slate-400 hover:text-emerald-400 transition-colors">
              <Icon name="lucide:info" class="w-4 h-4" />
            </button>
          </div>
          <div v-if="showImportInstructions" class="mb-4 p-4 bg-slate-700/30 rounded-xl border border-slate-600/50">
            <p class="text-sm text-slate-300 mb-2 font-light">CSV Format Instructions:</p>
            <ul class="text-xs text-slate-400 space-y-1 list-disc list-inside font-light">
              <li><strong class="text-slate-300">Required:</strong> Name</li>
              <li><strong class="text-slate-300">Optional:</strong> Preferred Name, Email, Codementor Username, Gender,
                Timezone, Notes, Is Active, Platform Preference</li>
              <li>First row must be headers: <code
                  class="text-emerald-400">Name, Email, Codementor Username, Preferred Name, Gender, Timezone, Notes, Is Active, Platform Preference</code>
              </li>
              <li>Platform Preference: comma-separated list (e.g., <code
                  class="text-emerald-400">email, codementor</code>)</li>
              <li>Is Active: <code class="text-emerald-400">true</code> or <code class="text-emerald-400">false</code>
                (defaults to true)</li>
            </ul>
          </div>
          <input type="file" accept=".csv" @change="handleFileSelect"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 mb-4">
          <div v-if="importStatus" class="mb-4 p-4 rounded-xl text-sm"
            :class="importStatus.includes('Error') ? 'bg-red-500/20 text-red-300' : 'bg-emerald-500/20 text-emerald-300'">
            {{ importStatus }}
          </div>
          <div class="flex space-x-3">
            <button @click="showImportModal = false"
              class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
              Cancel
            </button>
            <button @click="handleImport" :disabled="!importFile"
              class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
              Import
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Set page title
useHead({
  title: 'Contacts - Followupper'
})

// Use shared API state
const { contacts, campaigns, templates, createContact, updateContact, deleteContact, loadContacts, sendEmail, sendMessage, showStatusWithProgress, settings } = useApi()
const { apiCall, apiFetch } = useApiFetch()

// Available platforms for new contact (based on what they've entered)
const availablePlatforms = computed(() => {
  const platforms = []
  if (newContact.value.email) platforms.push('email')
  if (newContact.value.codementor_username) platforms.push('codementor')
  return platforms
})

// Local UI state
const statusMessage = ref('Loading...')
const showStatusBar = ref(false)
const statusTimer = ref(null)
const statusProgress = ref(100)
const showContactForm = ref(false)
const showEditContactForm = ref(false)
const editingContact = ref(null)
const showQuickSendModal = ref(false)
const selectedContact = ref(null)
const showContactProfileModal = ref(false)
const upcomingMessages = ref([])
const selectedContactIds = ref(new Set())
const showImportModal = ref(false)
const importFile = ref(null)
const importStatus = ref('')
const showImportInstructions = ref(false)
const showBulkMessageModal = ref(false)
const showBulkEditModal = ref(false)
const bulkMessage = ref({
  platforms: [],
  usePreferredPlatforms: false,
  subject: '',
  body: ''
})
const bulkSelectedTemplate = ref('')
const bulkEditData = ref({
  platform_preference: [],
  timezone: '',
  is_active: null,
  source: '',
  is_favorite: null,
  gender: ''
})

// Filter visibility
const showFilters = ref(false)

// Filters
const filterSearch = ref('')
const filterPlatform = ref([])
const filterStatus = ref('')
const filterSource = ref([])
const filterFavorite = ref('')
const filterLastMessaged = ref('')

const filterData = computed({
  get: () => ({
    search: filterSearch.value,
    platform: filterPlatform.value,
    status: filterStatus.value,
    source: filterSource.value,
    favorite: filterFavorite.value,
    lastMessaged: filterLastMessaged.value
  }),
  set: (value) => {
    filterSearch.value = value.search
    filterPlatform.value = value.platform
    filterStatus.value = value.status
    filterSource.value = value.source
    filterFavorite.value = value.favorite
    filterLastMessaged.value = value.lastMessaged
  }
})

const updateFilters = (newFilters) => {
  filterSearch.value = newFilters.search
  filterPlatform.value = newFilters.platform
  filterStatus.value = newFilters.status
  filterSource.value = newFilters.source
  filterFavorite.value = newFilters.favorite
  filterLastMessaged.value = newFilters.lastMessaged
}

// Form data
const newContact = ref({
  name: '',
  preferred_name: '',
  gender: '',
  email: '',
  codementor_username: '',
  platform_preference: [],
  timezone: 'UTC',
  notes: '',
  source: '',
  is_favorite: false
})

const quickSendMessage = ref({
  platforms: [],
  subject: '',
  body: '',
  send_date: '',
  send_time: '',
  schedule: false,
  timezone: 'my'
})
const quickSendIsChainMode = ref(false)
const quickSendMessageChain = ref([])
const quickSendChainSubject = ref('')
const quickSendChainFooter = ref('')
const quickSendSelectedTemplate = ref('')
const quickSendChainSettings = ref({
  platforms: [],
  sendFirstImmediately: false,
  timingType: 'interval',
  startDate: '',
  startTime: '09:00',
  timezone: 'my'
})

const activeTemplates = computed(() => {
  return templates.value.filter(t => t.is_active)
})

const applyQuickSendTemplate = () => {
  if (!quickSendSelectedTemplate.value) return
  const template = templates.value.find(t => t.id === parseInt(quickSendSelectedTemplate.value))
  if (template) {
    if (template.subject) {
      quickSendMessage.value.subject = template.subject
    }
    if (template.body) {
      quickSendMessage.value.body = template.body
      // For email, append footer: template footer if exists, otherwise user settings footer
      if (quickSendMessage.value.platforms.includes('email')) {
        const footerToUse = template.footer || settings.value?.user?.footer || ''
        if (footerToUse) {
          quickSendMessage.value.body = quickSendMessage.value.body + '\n\n' + footerToUse
        }
      }
    }
  }
}

const applyBulkTemplate = (templateId) => {
  if (!templateId) return
  const template = templates.value.find(t => t.id === parseInt(templateId))
  if (template) {
    if (template.subject) {
      bulkMessage.value.subject = template.subject
    }
    if (template.body) {
      bulkMessage.value.body = template.body
    }
  }
}

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


const editContact = (contact) => {
  editingContact.value = contact
  newContact.value = { ...contact }
  showEditContactForm.value = true
}

const handleDeleteContact = async (contactId) => {
  // Instant UI update
  contacts.value = contacts.value.filter(c => c.id !== contactId)

  // Background API call
  try {
    await deleteContact(contactId)
    showStatusWithProgressLocal('Contact deleted successfully', 5000)
  } catch (error) {
    console.error('Error deleting contact:', error)
    // Revert on error
    await loadContacts()
    showStatusWithProgressLocal('Error deleting contact', 5000)
  }
}

const handleSaveContact = async (contactData) => {
  // Store the contact data before clearing the form
  const data = contactData || { ...newContact.value }

  // Instant UI update
  const tempId = Date.now() // Temporary ID
  const newContactData = {
    id: tempId,
    ...data,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }

  contacts.value.push(newContactData)
  showContactForm.value = false
  newContact.value = { name: '', preferred_name: '', gender: '', email: '', codementor_username: '', platform_preference: [], timezone: 'UTC', notes: '', source: '', is_favorite: false }

  // Background API call
  try {
    const result = await createContact(data)
    // Update with real ID
    const index = contacts.value.findIndex(c => c.id === tempId)
    if (index !== -1) {
      contacts.value[index].id = result.id
    }
    showStatusWithProgressLocal('Contact created successfully', 5000)
  } catch (error) {
    console.error('Error saving contact:', error)
    // Revert on error
    contacts.value = contacts.value.filter(c => c.id !== tempId)
    showStatusWithProgressLocal('Error creating contact', 5000)
  }
}

const handleUpdateContact = async (contactData) => {
  // Store the contact data before clearing the form
  const data = contactData || { ...newContact.value }
  const contactId = editingContact.value.id

  // Instant UI update
  const index = contacts.value.findIndex(c => c.id === contactId)
  if (index !== -1) {
    contacts.value[index] = {
      ...contacts.value[index],
      ...data,
      updated_at: new Date().toISOString()
    }
  }

  showEditContactForm.value = false
  editingContact.value = null
  newContact.value = { name: '', email: '', codementor_username: '', platform_preference: [], notes: '', source: '', is_favorite: false }

  // Background API call
  try {
    await updateContact(contactId, data)
    showStatusWithProgressLocal('Contact updated successfully', 5000)
  } catch (error) {
    console.error('Error updating contact:', error)
    // Revert on error
    await loadContacts()
    showStatusWithProgressLocal('Error updating contact', 5000)
  }
}

const getTodayDate = () => {
  return new Date().toISOString().split('T')[0]
}

const getCurrentTime = () => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

const quickSendAvailablePlatforms = computed(() => {
  if (!selectedContact.value) return []
  const platforms = []
  if (selectedContact.value.email) platforms.push('email')
  if (selectedContact.value.codementor_username) platforms.push('codementor')
  return platforms
})

const getDefaultPlatforms = (contact) => {
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

const openQuickSendModal = (contact) => {
  selectedContact.value = contact
  const defaultPlatforms = getDefaultPlatforms(contact)
  quickSendMessage.value = {
    platforms: defaultPlatforms.length > 0 ? defaultPlatforms : (contact.email ? ['email'] : []),
    subject: '',
    body: '',
    send_date: getTodayDate(),
    send_time: getCurrentTime(),
    schedule: false,
    timezone: 'my'
  }
  quickSendIsChainMode.value = false
  loadQuickSendMessageChain()
  showQuickSendModal.value = true
}

const loadQuickSendMessageChain = () => {
  quickSendMessageChain.value = []
  quickSendChainSubject.value = ''
  quickSendChainFooter.value = settings.value?.user?.footer || ''
  const defaultPlatforms = selectedContact.value ? getDefaultPlatforms(selectedContact.value) : []
  quickSendChainSettings.value = {
    platforms: defaultPlatforms.length > 0 ? defaultPlatforms : (selectedContact.value?.email ? ['email'] : []),
    sendFirstImmediately: false,
    timingType: 'interval',
    startDate: getTodayDate(),
    startTime: getCurrentTime(),
    timezone: 'my'
  }
}

const addQuickSendMessageToChain = () => {
  const newMessage = {
    body: '',
    send_date: getTodayDate(),
    send_time: getCurrentTime(),
    timezone: 'my',
    frequency_days: 1
  }
  quickSendMessageChain.value.push(newMessage)
}

const removeQuickSendMessageFromChain = (index) => {
  quickSendMessageChain.value.splice(index, 1)
}

const clearQuickSendMessageChain = () => {
  quickSendMessageChain.value = []
}

const handleQuickSendChainModeToggle = () => {
  quickSendIsChainMode.value = true
  loadQuickSendMessageChain()
  addQuickSendMessageToChain()
}

const closeQuickSendModal = () => {
  showQuickSendModal.value = false
  selectedContact.value = null
  quickSendIsChainMode.value = false
  quickSendSelectedTemplate.value = ''
  quickSendMessage.value = {
    platforms: [],
    subject: '',
    body: '',
    send_date: '',
    send_time: '',
    schedule: false,
    timezone: 'my'
  }
  loadQuickSendMessageChain()
}

const handleQuickSend = async (messageData) => {
  const msg = messageData || quickSendMessage.value
  if (!msg.body.trim()) {
    alert('Please fill in the message body')
    return
  }

  if (!msg.platforms || msg.platforms.length === 0) {
    alert('Please select at least one platform')
    return
  }


  try {
    // If sending now (not scheduled), send immediately
    if (!msg.schedule) {
      await sendMessage(selectedContact.value.id, {
        platforms: msg.platforms,
        subject: msg.subject || '',
        body: msg.body
      })

      showStatusWithProgressLocal('Message sent successfully!', 5000)
      closeQuickSendModal()
    } else {
      // If scheduled, create a Message object via API
      const userTimezoneValue = settings.value?.user?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
      const timezoneToUse = msg.timezone === 'my'
        ? userTimezoneValue
        : (selectedContact.value.timezone || 'UTC')

      await apiCall('/messages/', {
        method: 'POST',
        body: JSON.stringify({
          contact: selectedContact.value.id,
          subject: msg.subject || '',
          body: msg.body,
          platforms: msg.platforms,
          status: 'pending',
          send_date: msg.send_date || null,
          send_time: msg.send_time || getCurrentTime(),
          timezone: timezoneToUse,
          frequency_days: 0
        })
      })

      showStatusWithProgressLocal('Message scheduled successfully!', 5000)
      closeQuickSendModal()
    }
  } catch (error) {
    console.error('Error sending/scheduling message:', error)
    alert('Error sending message: ' + (error.message || 'Unknown error'))
  }
}

const handleQuickSendChain = async (chainData) => {
  const data = chainData || {
    subject: quickSendChainSubject.value,
    footer: quickSendChainFooter.value,
    settings: quickSendChainSettings.value,
    messages: quickSendMessageChain.value
  }

  // Validate platforms
  if (!data.settings.platforms || data.settings.platforms.length === 0) {
    alert('Please select at least one platform')
    return
  }


  // Validate that all messages have body
  if (data.messages.some(msg => !msg.body.trim())) {
    alert('Please fill in the message body for all messages')
    return
  }

  // Validate specific date/time mode
  if (data.settings.timingType === 'specific') {
    if (data.messages.some(msg => !msg.send_date || !msg.send_time)) {
      alert('Please fill in send date and time for all messages in specific mode')
      return
    }
  }

  // Validate interval mode
  if (data.settings.timingType === 'interval') {
    if (!data.settings.startDate || !data.settings.startTime) {
      if (!data.settings.sendFirstImmediately) {
        alert('Please set a start date and time for interval chains')
        return
      }
    }
  }

  try {
    const userTimezoneValue = settings.value?.user?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'

    // Determine chain timezone for interval mode
    const chainTimezoneToUse = data.settings.timingType === 'interval'
      ? (data.settings.timezone === 'my'
        ? userTimezoneValue
        : (selectedContact.value.timezone || 'UTC'))
      : null

    // Determine chain start date/time for interval mode
    let chainStartDate = null
    let chainStartTime = null
    if (data.settings.timingType === 'interval') {
      if (data.settings.startDate && data.settings.startTime) {
        chainStartDate = data.settings.startDate
        chainStartTime = data.settings.startTime
      } else if (data.settings.sendFirstImmediately) {
        chainStartDate = new Date().toISOString().split('T')[0]
        chainStartTime = new Date().toTimeString().slice(0, 5)
      } else {
        chainStartDate = data.settings.startDate || new Date().toISOString().split('T')[0]
        chainStartTime = data.settings.startTime || '09:00'
      }
    }

    // Create MessageSequence first
    const sequence = await apiCall('/message-sequences/', {
      method: 'POST',
      body: JSON.stringify({
        contact: selectedContact.value.id,
        timing_type: data.settings.timingType,
        chain_start_date: chainStartDate,
        chain_start_time: chainStartTime,
        chain_timezone: chainTimezoneToUse
      })
    })

    // Create Message objects for each message in the chain
    const messagePromises = data.messages.map(async (msg, index) => {
      // Combine body and footer
      let messageBody = msg.body || ''
      if (data.footer && data.footer.trim()) {
        messageBody += '\n\n' + data.footer.trim()
      }

      // Determine timezone to use
      const timezoneToUse = (msg.timezone || 'my') === 'my'
        ? userTimezoneValue
        : (selectedContact.value.timezone || 'UTC')

      const messageData = {
        contact: selectedContact.value.id,
        sequence: sequence.id,
        order: index,
        subject: data.settings.platforms.includes('email') ? data.subject : '',
        body: messageBody,
        platforms: data.settings.platforms,
        status: 'pending'
      }

      if (data.settings.timingType === 'interval') {
        messageData.frequency_days = msg.frequency_days || (index === 0 ? 0 : 1)
      } else {
        // Specific mode
        messageData.send_date = msg.send_date || null
        messageData.send_time = msg.send_time || getCurrentTime()
        messageData.timezone = timezoneToUse
        messageData.frequency_days = 0
      }

      const createdMessage = await apiCall('/messages/', {
        method: 'POST',
        body: JSON.stringify(messageData)
      })

      // If this is the first message and sendFirstImmediately is true, send it now
      if (index === 0 && data.settings.timingType === 'interval' && data.settings.sendFirstImmediately) {
        try {
          const sendResult = await apiCall(`/messages/${createdMessage.id}/send-now/`, {
            method: 'POST'
          })
          createdMessage.email_message_id = sendResult.email_message_id
          createdMessage.status = sendResult.status
        } catch (error) {
          console.error('Error sending first message immediately:', error)
        }
      }

      return createdMessage
    })

    await Promise.all(messagePromises)

    showStatusWithProgressLocal('Message sequence created successfully!', 5000)
    closeQuickSendModal()
  } catch (error) {
    console.error('Error saving message chain:', error)
    alert('Error saving message chain: ' + (error.message || 'Unknown error'))
  }
}

const openContactProfile = async (contact) => {
  selectedContact.value = contact
  await loadContactAssignments(contact.id)
  showContactProfileModal.value = true
}

const loadContactAssignments = async (contactId) => {
  try {
    const allAssignments = []

    // Load assignments from all campaigns
    for (const campaign of campaigns.value) {
      try {
        const assignments = await apiCall(`/campaigns/${campaign.id}/assignments/`)
        const contactAssigns = assignments
          .filter(a => a.contact === contactId && a.next_send_date && a.status === 'active')
          .map(a => ({
            ...a,
            campaign_name: campaign.name,
            campaign_description: campaign.description,
            campaign_type: campaign.campaign_type
          }))
        allAssignments.push(...contactAssigns)
      } catch (error) {
        console.error(`Error loading assignments for campaign ${campaign.id}:`, error)
      }
    }

    upcomingMessages.value = allAssignments.sort((a, b) => new Date(a.next_send_date) - new Date(b.next_send_date))
  } catch (error) {
    console.error('Error loading contact assignments:', error)
    upcomingMessages.value = []
  }
}

const closeContactProfileModal = () => {
  showContactProfileModal.value = false
  selectedContact.value = null
}

const handleContactUpdate = (updatedContact) => {
  // Update local state
  const contactIndex = contacts.value.findIndex(c => c.id === updatedContact.id)
  if (contactIndex !== -1) {
    Object.assign(contacts.value[contactIndex], updatedContact)
  }
  if (selectedContact.value && selectedContact.value.id === updatedContact.id) {
    Object.assign(selectedContact.value, updatedContact)
  }
  showStatusWithProgressLocal('Contact updated successfully', 3000)
}

const handleSendMessage = (messageData) => {
  showStatusWithProgressLocal('Message sent successfully', 3000)
}

// Multi-select functionality
const toggleContactSelection = (contactId) => {
  if (selectedContactIds.value.has(contactId)) {
    selectedContactIds.value.delete(contactId)
  } else {
    selectedContactIds.value.add(contactId)
  }
}

const toggleSelectAll = (event) => {
  if (event.target.checked) {
    filteredContacts.value.forEach(contact => {
      selectedContactIds.value.add(contact.id)
    })
  } else {
    selectedContactIds.value.clear()
  }
}

const isAllSelected = computed(() => {
  return filteredContacts.value.length > 0 && filteredContacts.value.every(contact => selectedContactIds.value.has(contact.id))
})

// Available sources for filter dropdown (dynamically populated from contacts)
const availableSources = computed(() => {
  const sources = new Set()
  contacts.value.forEach(contact => {
    sources.add(contact.source || '')
  })
  return Array.from(sources).sort()
})

// Check if any filters are active
const hasActiveFilters = computed(() => {
  return filterSearch.value.trim() !== '' ||
    (filterPlatform.value && filterPlatform.value.length > 0) ||
    filterStatus.value !== '' ||
    (filterSource.value && filterSource.value.length > 0) ||
    filterFavorite.value !== '' ||
    filterLastMessaged.value !== ''
})

// Count active filters
const activeFilterCount = computed(() => {
  let count = 0
  if (filterSearch.value.trim() !== '') count++
  if (filterPlatform.value && filterPlatform.value.length > 0) count++
  if (filterStatus.value !== '') count++
  if (filterSource.value && filterSource.value.length > 0) count++
  if (filterFavorite.value !== '') count++
  if (filterLastMessaged.value !== '') count++
  return count
})

// Filtered contacts - optimized single-pass filtering
const filteredContacts = computed(() => {
  const contactsList = contacts.value
  if (!contactsList || contactsList.length === 0) return []

  // Pre-compute filter conditions to avoid repeated checks
  const hasSearch = filterSearch.value.trim()
  const searchLower = hasSearch ? filterSearch.value.toLowerCase() : ''
  const hasPlatformFilter = filterPlatform.value && filterPlatform.value.length > 0
  const hasStatusFilter = filterStatus.value !== ''
  const hasSourceFilter = filterSource.value && filterSource.value.length > 0
  const hasFavoriteFilter = filterFavorite.value === 'true'
  const hasLastMessagedFilter = filterLastMessaged.value !== ''
  
  // Pre-compute date for last messaged filter (only once per filter run)
  let now = null
  if (hasLastMessagedFilter) {
    now = new Date()
  }

  // Single pass through all contacts
  const filtered = contactsList.filter(contact => {
    // Search filter
    if (hasSearch) {
      const name = contact.name?.toLowerCase() || ''
      if (!name.includes(searchLower)) return false
    }

    // Platform filter
    if (hasPlatformFilter) {
      const hasEmail = filterPlatform.value.includes('email') && contact.email
      const hasCodementor = filterPlatform.value.includes('codementor') && contact.codementor_username
      if (!hasEmail && !hasCodementor) return false
    }

    // Status filter
    if (hasStatusFilter) {
      if (filterStatus.value === 'active' && !contact.is_active) return false
      if (filterStatus.value === 'inactive' && contact.is_active) return false
    }

    // Source filter
    if (hasSourceFilter) {
      const matchesSource = filterSource.value.some(selectedSource => {
        if (selectedSource === '__empty__') {
          return !contact.source || contact.source === ''
        }
        return contact.source === selectedSource
      })
      if (!matchesSource) return false
    }

    // Favorite filter
    if (hasFavoriteFilter && !contact.is_favorite) {
      return false
    }

    // Last Messaged filter
    if (hasLastMessagedFilter) {
      const filterValue = filterLastMessaged.value
      
      // Handle "never" case (contact has never been messaged)
      if (!contact.last_messaged) {
        if (filterValue === 'never') {
          return true // Show contacts who have never been messaged
        }
        // For "not contacted in X" filters, never-messaged contacts should be included
        if (filterValue.startsWith('not_')) {
          return true
        }
        return false
      }
      
      // Contact has been messaged, calculate days since
      const lastMessagedDate = new Date(contact.last_messaged)
      const daysSince = Math.floor((now - lastMessagedDate) / (1000 * 60 * 60 * 24))

      switch (filterValue) {
        // Regular filters (contacted within X time)
        case 'never':
          return false // Already handled above
        case 'today':
          if (daysSince !== 0) return false
          break
        case 'last_7_days':
          if (daysSince > 7) return false
          break
        case 'last_30_days':
          if (daysSince > 30) return false
          break
        case 'last_90_days':
          if (daysSince > 90) return false
          break
        case 'over_90_days':
          if (daysSince <= 90) return false
          break
        
        // Reverse filters (NOT contacted in X time)
        case 'not_7_days':
          if (daysSince <= 7) return false // Exclude if contacted within 7 days
          break
        case 'not_30_days':
          if (daysSince <= 30) return false // Exclude if contacted within 30 days
          break
        case 'not_90_days':
          if (daysSince <= 90) return false // Exclude if contacted within 90 days
          break
        case 'not_6_months':
          if (daysSince <= 180) return false // Exclude if contacted within 6 months (~180 days)
          break
        case 'not_1_year':
          if (daysSince <= 365) return false // Exclude if contacted within 1 year
          break
      }
    }

    return true
  })

  // Sort case-insensitively by name
  return filtered.sort((a, b) => {
    const nameA = (a.name || '').toLowerCase()
    const nameB = (b.name || '').toLowerCase()
    return nameA.localeCompare(nameB)
  })
})

// Toggle favorite
const toggleFavorite = async (contact) => {
  const newFavoriteValue = !contact.is_favorite
  // Instant UI update
  contact.is_favorite = newFavoriteValue

  // Background API call
  try {
    await updateContact(contact.id, { is_favorite: newFavoriteValue })
  } catch (error) {
    console.error('Error updating favorite:', error)
    // Revert on error
    contact.is_favorite = !newFavoriteValue
    await loadContacts()
  }
}

const selectedContacts = computed(() => {
  return contacts.value.filter(contact => selectedContactIds.value.has(contact.id))
})

const canSendBulkMessage = computed(() => {
  if (!bulkMessage.value.body.trim()) return false
  if (!bulkMessage.value.usePreferredPlatforms && bulkMessage.value.platforms.length === 0) return false
  return selectedContacts.value.length > 0
})

// Template variable replacement
const getPreviewText = (text, contact) => {
  if (!text) return ''

  // Extract first and last name from full name
  const nameParts = (contact.name || '').split(' ')
  const firstName = contact.preferred_name || nameParts[0] || ''
  const lastName = nameParts.slice(1).join(' ') || ''
  const preferredName = contact.preferred_name || firstName
  const gender = contact.gender || ''

  let result = text

  // Handle gender-based conditionals first (e.g., {if_male:text}{if_female:text})
  if (gender === 'male') {
    result = result.replace(/\{if_male:([^}]+)\}/g, '$1')
    result = result.replace(/\{if_female:([^}]+)\}/g, '')
  } else if (gender === 'female') {
    result = result.replace(/\{if_female:([^}]+)\}/g, '$1')
    result = result.replace(/\{if_male:([^}]+)\}/g, '')
  } else {
    // If gender not specified, remove both blocks
    result = result.replace(/\{if_male:([^}]+)\}/g, '')
    result = result.replace(/\{if_female:([^}]+)\}/g, '')
  }

  // Handle frequency conditionals (remove all for non-campaign messages)
  const frequencyConditionals = [
    'if_frequency_daily', 'if_frequency_week', 'if_frequency_month',
    'if_frequency_quarter', 'if_frequency_year', 'if_frequency_custom'
  ]
  frequencyConditionals.forEach(conditional => {
    result = result.replace(new RegExp(`\\{${conditional}:([^}]+)\\}`, 'g'), '')
  })

  // Handle seasonal conditionals (seasons: spring, summer, fall, winter)
  const now = new Date()
  const month = now.getMonth() + 1 // 1-12
  const day = now.getDate()
  
  // Determine season
  let season = null
  if ((month === 3 && day >= 20) || [4, 5].includes(month) || (month === 6 && day < 21)) {
    season = 'spring'
  } else if ((month === 6 && day >= 21) || [7, 8].includes(month) || (month === 9 && day < 23)) {
    season = 'summer'
  } else if ((month === 9 && day >= 23) || [10, 11].includes(month) || (month === 12 && day < 21)) {
    season = 'fall'
  } else { // December 21 - March 19
    season = 'winter'
  }
  
  const seasonConditionals = ['if_spring', 'if_summer', 'if_fall', 'if_winter']
  seasonConditionals.forEach(seasonConditional => {
    const seasonName = seasonConditional.replace('if_', '')
    const pattern = new RegExp(`\\{${seasonConditional}:([^}]+)\\}`, 'g')
    if (season === seasonName) {
      result = result.replace(pattern, '$1')
    } else {
      result = result.replace(pattern, '')
    }
  })
  
  // Handle holiday conditionals
  let holiday = null
  if (month === 12) {
    holiday = 'christmas'
  } else if (month === 10) {
    holiday = 'halloween'
  } else if (month === 11 && day >= 20) {
    holiday = 'thanksgiving'
  } else if ((month === 3 && day >= 20) || (month === 4 && day <= 30)) {
    holiday = 'easter'
  } else if (month === 1 && day <= 7) {
    holiday = 'newyear'
  }

  // Process holiday conditionals (new naming: if_X, also support old if_season_X)
  const holidayConditionals = ['if_christmas', 'if_halloween', 'if_thanksgiving', 'if_easter', 'if_newyear']
  const oldHolidayConditionals = ['if_season_christmas', 'if_season_halloween', 'if_season_thanksgiving', 'if_season_easter', 'if_season_newyear']
  
  ;[...holidayConditionals, ...oldHolidayConditionals].forEach(holidayConditional => {
    const holidayName = holidayConditional.startsWith('if_season_') 
      ? holidayConditional.replace('if_season_', '')
      : holidayConditional.replace('if_', '')
    const escaped = holidayConditional.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const pattern = new RegExp(`\\{${escaped}:([^}]+)\\}`, 'g')
    if (holiday === holidayName) {
      result = result.replace(pattern, '$1')
    } else {
      result = result.replace(pattern, '')
    }
  })
  
  // Process generic if_holiday conditional
  if (holiday) {
    result = result.replace(/\{if_holiday:([^}]+)\}/g, '$1')
  } else {
    result = result.replace(/\{if_holiday:([^}]+)\}/g, '')
  }

  // Replace simplified syntax first (e.g., {first_name}, {name})
  result = result.replace(/\{name\}/g, contact.name || '')
  result = result.replace(/\{first_name\}/g, firstName)
  result = result.replace(/\{preferred_name\}/g, preferredName)
  result = result.replace(/\{last_name\}/g, lastName)
  result = result.replace(/\{gender\}/g, gender)
  result = result.replace(/\{email\}/g, contact.email || '')
  result = result.replace(/\{codementor_username\}/g, contact.codementor_username || '')
  result = result.replace(/\{frequency\}/g, '') // No frequency context
  result = result.replace(/\{frequency_days\}/g, '')
  result = result.replace(/\{season\}/g, season ? season.charAt(0).toUpperCase() + season.slice(1) : '')
  result = result.replace(/\{holiday\}/g, holiday ? holiday.charAt(0).toUpperCase() + holiday.slice(1) : '')
  
  // Add date variables (last_month, last_year, day, month) - reuse existing 'now' variable
  const lastMonthDate = new Date(now.getFullYear(), now.getMonth() - 1, 1)
  const lastMonthName = lastMonthDate.toLocaleString('default', { month: 'long' }) // Full month name (e.g., "January")
  const currentMonthName = now.toLocaleString('default', { month: 'long' }) // Current month name (e.g., "February")
  const lastYear = String(now.getFullYear() - 1)
  const dayName = now.toLocaleString('default', { weekday: 'long' }) // Full day name (e.g., "Monday")
  result = result.replace(/\{last_month\}/g, lastMonthName)
  result = result.replace(/\{last_year\}/g, lastYear)
  result = result.replace(/\{day\}/g, dayName)
  result = result.replace(/\{month\}/g, currentMonthName)

  // Replace old contact variables (for backwards compatibility)
  result = result.replace(/\{contact\.name\}/g, contact.name || '')
  result = result.replace(/\{contact\.first_name\}/g, firstName)
  result = result.replace(/\{contact\.preferred_name\}/g, preferredName)
  result = result.replace(/\{contact\.last_name\}/g, lastName)
  result = result.replace(/\{contact\.gender\}/g, gender)
  result = result.replace(/\{contact\.email\}/g, contact.email || '')
  result = result.replace(/\{contact\.codementor_username\}/g, contact.codementor_username || '')

  // Replace old user variables (for backwards compatibility)
  result = result.replace(/\{user\.name\}/g, contact.name || '')
  result = result.replace(/\{user\.first_name\}/g, firstName)
  result = result.replace(/\{user\.preferred_name\}/g, preferredName)
  result = result.replace(/\{user\.last_name\}/g, lastName)
  result = result.replace(/\{user\.gender\}/g, gender)
  result = result.replace(/\{user\.email\}/g, contact.email || '')
  result = result.replace(/\{user\.codementor_username\}/g, contact.codementor_username || '')

  return result
}

// Bulk messaging
const openBulkMessageModal = () => {
  // Determine available platforms from selected contacts
  const hasEmail = selectedContacts.value.some(c => c.email)
  const hasCodementor = selectedContacts.value.some(c => c.codementor_username)

  bulkMessage.value = {
    platforms: [
      ...(hasEmail ? ['email'] : []),
      ...(hasCodementor ? ['codementor'] : [])
    ],
    usePreferredPlatforms: true,
    subject: '',
    body: ''
  }
  showBulkMessageModal.value = true
}

const closeBulkMessageModal = () => {
  showBulkMessageModal.value = false
  bulkMessage.value = {
    platforms: [],
    usePreferredPlatforms: false,
    subject: '',
    body: ''
  }
  bulkSelectedTemplate.value = ''
}

const openBulkEditModal = () => {
  // Reset bulk edit data
  bulkEditData.value = {
    platform_preference: [],
    timezone: '',
    is_active: null,
    source: '',
    is_favorite: null,
    gender: ''
  }
  showBulkEditModal.value = true
}

const closeBulkEditModal = () => {
  showBulkEditModal.value = false
  bulkEditData.value = {
    platform_preference: [],
    timezone: '',
    is_active: null,
    source: '',
    is_favorite: null,
    gender: ''
  }
}

const handleBulkEdit = async (editData) => {
  if (selectedContactIds.value.size === 0) return

  // Prepare update data - only include fields that have values
  const updateData = {
    contact_ids: Array.from(selectedContactIds.value)
  }

  // Only include fields that are set
  if (editData.platform_preference.length > 0) {
    updateData.platform_preference = editData.platform_preference
  }
  if (editData.timezone) {
    updateData.timezone = editData.timezone
  }
  if (editData.is_active !== null) {
    updateData.is_active = editData.is_active
  }
  if (editData.source) {
    updateData.source = editData.source
  }
  if (editData.is_favorite !== null) {
    updateData.is_favorite = editData.is_favorite
  }
  if (editData.gender !== '') {
    updateData.gender = editData.gender
  }

  // Remove contact_ids if no other fields to update
  if (Object.keys(updateData).length === 1) {
    showStatusWithProgressLocal('Please select at least one field to update', 3000)
    return
  }

  try {
    showStatusWithProgressLocal(`Updating ${selectedContactIds.value.size} contacts...`, 5000)

    const result = await apiCall('/contacts/bulk-update/', {
      method: 'POST',
      body: JSON.stringify(updateData)
    })

    showStatusWithProgressLocal(`Successfully updated ${result.updated_count} contact(s)`, 5000)

    // Reload contacts and clear selection
    await loadContacts()
    selectedContactIds.value.clear()
    closeBulkEditModal()
  } catch (error) {
    console.error('Error updating contacts:', error)
    showStatusWithProgressLocal(`Error updating contacts: ${error.message || 'Unknown error'}`, 5000)
  }
}

const handleBulkDelete = async () => {
  if (selectedContactIds.value.size === 0) return

  if (!confirm(`Are you sure you want to delete ${selectedContactIds.value.size} contact(s)? This action cannot be undone.`)) {
    return
  }

  try {
    showStatusWithProgressLocal(`Deleting ${selectedContactIds.value.size} contacts...`, 5000)

    const result = await apiCall('/contacts/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({
        contact_ids: Array.from(selectedContactIds.value)
      })
    })

    showStatusWithProgressLocal(`Successfully deleted ${result.deleted_count} contact(s)`, 5000)

    // Remove deleted contacts from local state immediately
    const deletedIds = new Set(selectedContactIds.value)
    contacts.value = contacts.value.filter(c => !deletedIds.has(c.id))
    selectedContactIds.value.clear()

    // Reload to ensure sync
    await loadContacts()
  } catch (error) {
    console.error('Error deleting contacts:', error)
    showStatusWithProgressLocal(`Error deleting contacts: ${error.message || 'Unknown error'}`, 5000)
    // Reload on error to ensure sync
    await loadContacts()
  }
}

const handleBulkSend = async (messageData) => {
  if (!confirm(`Send this message to ${selectedContactIds.value.size} contact(s)?`)) {
    return
  }

  try {
    // Prepare message body with template variables (use first contact for preview)
    // The backend will handle per-contact template replacement
    let body = messageData.body
    let subject = messageData.subject || ''

    // Append footer if email is being used
    if (messageData.platforms.includes('email') || messageData.usePreferredPlatforms) {
      let footerToUse = ''
      if (bulkSelectedTemplate.value) {
        const template = templates.value.find(t => t.id === parseInt(bulkSelectedTemplate.value))
        if (template && template.footer) {
          footerToUse = template.footer
        }
      }
      if (!footerToUse) {
        footerToUse = settings.value?.user?.footer || ''
      }
      if (footerToUse) {
        body = body + '\n\n' + footerToUse
      }
    }

    // Send ONE bulk request to backend - it handles everything
    await apiCall('/contacts/bulk-send/', {
      method: 'POST',
      body: JSON.stringify({
        contact_ids: Array.from(selectedContactIds.value),
        platforms: messageData.platforms,
        subject: subject,
        body: body,
        use_preferred_platforms: messageData.usePreferredPlatforms
      })
    })

    showStatusWithProgressLocal(
      `Bulk send initiated for ${selectedContactIds.value.size} contact(s). Processing in background.`,
      5000
    )

    // Close modal and clear selection immediately
    showBulkMessageModal.value = false
    selectedContactIds.value.clear()

    // Reload contacts after a short delay to see updates
    setTimeout(async () => {
      await loadContacts()
    }, 2000)
  } catch (error) {
    console.error('Bulk send error:', error)
    showStatusWithProgressLocal(`Bulk send failed: ${error.message || 'Unknown error'}`, 5000)
  }
}

const formatLastMessaged = (dateString) => {
  if (!dateString) return 'Never'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return 'Never'
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (e) {
    console.error('Error formatting last messaged date:', e)
    return 'Never'
  }
}

const exportContacts = async () => {
  try {
    const response = await apiFetch('/contacts/export/', {
      method: 'GET'
    })

    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'contacts_export.csv'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      showStatusWithProgressLocal('Contacts exported successfully', 3000)
    } else {
      showStatusWithProgressLocal('Export failed', 3000)
    }
  } catch (error) {
    console.error('Export error:', error)
    showStatusWithProgressLocal('Export failed', 3000)
  }
}

const handleFileSelect = (event) => {
  importFile.value = event.target.files[0]
  importStatus.value = ''
}

const handleImport = async () => {
  if (!importFile.value) return

  try {
    const formData = new FormData()
    formData.append('file', importFile.value)

    const data = await apiCall('/contacts/import/', {
      method: 'POST',
      body: formData,
      headers: {} // Let fetch set Content-Type for FormData
    })

    importStatus.value = `Import completed: ${data.created} created, ${data.updated} updated${data.errors.length > 0 ? `. Errors: ${data.errors.join(', ')}` : ''}`
    await loadContacts()
    setTimeout(() => {
      showImportModal.value = false
      importFile.value = null
      importStatus.value = ''
    }, 3000)
  } catch (error) {
    console.error('Import error:', error)
    importStatus.value = `Error: ${error.message || 'Import failed'}`
  }
}

// Data is loaded at app startup, no need to load here
onMounted(() => {
  // No status message needed
})
</script>
