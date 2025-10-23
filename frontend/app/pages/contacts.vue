<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <h2 class="text-3xl font-thin text-slate-100">Contacts</h2>
      <button @click="showContactForm = true" 
              class="bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105">
        + Add Contact
      </button>
    </div>

      <!-- Contacts List -->
      <div class="bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-emerald-500/20">
            <thead class="bg-slate-700/50">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Name</th>
                <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Email</th>
                <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Platform</th>
                <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Status</th>
                <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-slate-800/30 divide-y divide-emerald-500/10">
              <tr v-for="contact in contacts" :key="contact.id" class="hover:bg-slate-700/30 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-light text-slate-100">
                  {{ contact.name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                  {{ contact.email }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                  {{ contact.platform_preference }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="contact.is_active ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'"
                        class="inline-flex px-3 py-1 text-xs font-light rounded-full">
                    {{ contact.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-light">
                  <button @click="editContact(contact)" class="text-emerald-400 hover:text-emerald-300 mr-4 transition-colors">Edit</button>
                  <button @click="handleDeleteContact(contact.id)" class="text-red-400 hover:text-red-300 transition-colors">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    <!-- Contact Form Modal -->
    <div v-if="showContactForm" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 w-full max-w-md">
        <h3 class="text-2xl font-thin text-slate-100 mb-6">Add Contact</h3>
        
        <form @submit.prevent="handleSaveContact" class="space-y-4">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Name *</label>
            <input v-model="newContact.name" type="text" required
                   class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>
          
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Email</label>
            <input v-model="newContact.email" type="email"
                   class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>
          
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Codementor Username</label>
            <input v-model="newContact.codementor_username" type="text"
                   class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>
          
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Platform Preference</label>
            <select v-model="newContact.platform_preference"
                    class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
              <option value="email">Email</option>
              <option value="codementor">Codementor</option>
              <option value="both">Both</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Notes</label>
            <textarea v-model="newContact.notes" rows="3"
                      class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"></textarea>
          </div>
          
          <div class="flex space-x-3 pt-4">
            <button type="button" @click="showContactForm = false"
                    class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
              Cancel
            </button>
            <button type="submit"
                    class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
              Save Contact
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Contact Form Modal -->
    <div v-if="showEditContactForm" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 w-full max-w-md">
        <h3 class="text-2xl font-thin text-slate-100 mb-6">Edit Contact</h3>
        
        <form @submit.prevent="handleUpdateContact" class="space-y-4">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Name *</label>
            <input v-model="newContact.name" type="text" required
                   class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>
          
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Email</label>
            <input v-model="newContact.email" type="email"
                   class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>
          
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Codementor Username</label>
            <input v-model="newContact.codementor_username" type="text"
                   class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>
          
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Platform Preference</label>
            <select v-model="newContact.platform_preference"
                    class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
              <option value="email">Email</option>
              <option value="codementor">Codementor</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Notes</label>
            <textarea v-model="newContact.notes" rows="3"
                      class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"></textarea>
          </div>
          
          <div class="flex space-x-3 pt-4">
            <button type="button" @click="showEditContactForm = false"
                    class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
              Cancel
            </button>
            <button type="submit"
                    class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
              Update Contact
            </button>
          </div>
        </form>
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
import { ref } from 'vue'

// Set page title
useHead({
  title: 'Contacts - Followupper'
})

// Use shared API state
const { contacts, createContact, updateContact, deleteContact, loadContacts, showStatusWithProgress } = useApi()

// Local UI state
const statusMessage = ref('Loading...')
const showStatusBar = ref(false)
const statusTimer = ref(null)
const statusProgress = ref(100)
const showContactForm = ref(false)
const showEditContactForm = ref(false)
const editingContact = ref(null)

// Form data
const newContact = ref({
  name: '',
  email: '',
  codementor_username: '',
  platform_preference: 'email',
  notes: ''
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

const handleSaveContact = async () => {
  // Store the contact data before clearing the form
  const contactData = { ...newContact.value }
  
  // Instant UI update
  const tempId = Date.now() // Temporary ID
  const newContactData = {
    id: tempId,
    ...contactData,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
  
  contacts.value.push(newContactData)
  showContactForm.value = false
  newContact.value = { name: '', email: '', codementor_username: '', platform_preference: 'email', notes: '' }
  
  // Background API call
  try {
    const result = await createContact(contactData)
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

const handleUpdateContact = async () => {
  // Store the contact data before clearing the form
  const contactData = { ...newContact.value }
  const contactId = editingContact.value.id
  
  // Instant UI update
  const index = contacts.value.findIndex(c => c.id === contactId)
  if (index !== -1) {
    contacts.value[index] = {
      ...contacts.value[index],
      ...contactData,
      updated_at: new Date().toISOString()
    }
  }
  
  showEditContactForm.value = false
  editingContact.value = null
  newContact.value = { name: '', email: '', codementor_username: '', platform_preference: 'email', notes: '' }
  
  // Background API call
  try {
    await updateContact(contactId, contactData)
    showStatusWithProgressLocal('Contact updated successfully', 5000)
  } catch (error) {
    console.error('Error updating contact:', error)
    // Revert on error
    await loadContacts()
    showStatusWithProgressLocal('Error updating contact', 5000)
  }
}

// Data is loaded at app startup, no need to load here
onMounted(() => {
  // No status message needed
})
</script>
