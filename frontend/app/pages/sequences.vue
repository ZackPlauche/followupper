<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-4xl font-thin gradient-title mb-2">
          Sequences
        </h1>
        <p class="text-slate-300 font-light">Create and manage follow-up sequences for automated campaigns</p>
      </div>
      <button @click="showCreateSequenceForm = true"
              class="px-6 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105">
        <Icon name="lucide:plus" class="w-5 h-5 inline mr-2" />
        Create Sequence
      </button>
    </div>

    <!-- Sequences Grid -->
    <div v-if="sequences.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="sequence in sequences" :key="sequence.id" 
           class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-6 hover:border-emerald-400/40 transition-all duration-300">
        
        <!-- Sequence Header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <h3 class="text-xl font-light text-slate-100 mb-1">{{ sequence.name }}</h3>
            <p class="text-sm text-slate-400 font-light">{{ sequence.description || 'No description' }}</p>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 rounded-full" :class="sequence.is_active ? 'bg-emerald-400' : 'bg-slate-500'"></div>
            <span class="text-xs text-slate-400">{{ sequence.is_active ? 'Active' : 'Inactive' }}</span>
          </div>
        </div>

        <!-- Sequence Details -->
        <div class="space-y-3 mb-4">
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-400">Platform:</span>
            <span class="text-slate-200 font-medium capitalize">{{ sequence.platform }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-400">Steps:</span>
            <span class="text-slate-200 font-medium">{{ sequence.step_count }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-400">Duration:</span>
            <span class="text-slate-200 font-medium">{{ sequence.total_duration_days }} days</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center justify-between pt-4 border-t border-slate-700/50">
          <div class="flex space-x-2">
            <button @click="editSequence(sequence)"
                    class="px-3 py-2 bg-slate-600/50 text-slate-300 rounded-lg text-sm font-light hover:bg-slate-600/70 transition-colors">
              <Icon name="lucide:edit" class="w-4 h-4 inline mr-1" />
              Edit
            </button>
            <button @click="viewSequenceSteps(sequence)"
                    class="px-3 py-2 bg-blue-600/50 text-blue-300 rounded-lg text-sm font-light hover:bg-blue-600/70 transition-colors">
              <Icon name="lucide:list" class="w-4 h-4 inline mr-1" />
              Steps
            </button>
          </div>
          <button @click="handleDeleteSequence(sequence.id)"
                  class="px-3 py-2 bg-red-600/50 text-red-300 rounded-lg text-sm font-light hover:bg-red-600/70 transition-colors">
            <Icon name="lucide:trash-2" class="w-4 h-4 inline mr-1" />
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <Icon name="lucide:workflow" class="w-16 h-16 text-slate-500 mx-auto mb-4" />
      <h3 class="text-xl font-light text-slate-300 mb-2">No sequences yet</h3>
      <p class="text-slate-400 font-light mb-6">Create your first follow-up sequence to get started</p>
      <button @click="showCreateSequenceForm = true"
              class="px-6 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-xl font-light hover:shadow-lg transition-all duration-300">
        <Icon name="lucide:plus" class="w-5 h-5 inline mr-2" />
        Create Your First Sequence
      </button>
    </div>

    <!-- Create/Edit Sequence Modal -->
    <div v-if="showCreateSequenceForm" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-slate-800/95 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <!-- Modal Header -->
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-thin text-slate-100">
              {{ editingSequence ? 'Edit Sequence' : 'Create Sequence' }}
            </h2>
            <button @click="closeSequenceForm" class="text-slate-400 hover:text-slate-200 transition-colors">
              <Icon name="lucide:x" class="w-6 h-6" />
            </button>
          </div>

          <!-- Sequence Form -->
          <form @submit.prevent="handleSaveSequence" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-light text-slate-300 mb-2">Sequence Name</label>
                <input v-model="newSequence.name" type="text" placeholder="e.g., New Client Onboarding"
                       class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
              </div>
              
              <div>
                <label class="block text-sm font-light text-slate-300 mb-2">Platform</label>
                <select v-model="newSequence.platform"
                        class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
                  <option value="email">Email</option>
                  <option value="codementor">Codementor</option>
                  <option value="both">Both</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">Description</label>
              <textarea v-model="newSequence.description" rows="3" placeholder="Describe what this sequence is for..."
                        class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"></textarea>
            </div>

            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <input v-model="newSequence.is_active" type="checkbox" id="is_active"
                       class="form-checkbox h-5 w-5 text-emerald-500 rounded border-slate-600 bg-slate-700/50 focus:ring-emerald-400">
                <label for="is_active" class="text-sm font-light text-slate-300">Active sequence</label>
              </div>
            </div>

            <!-- Form Actions -->
            <div class="flex items-center justify-end space-x-3 pt-6 border-t border-slate-700/50">
              <button type="button" @click="closeSequenceForm"
                      class="px-6 py-3 bg-slate-600/50 text-slate-300 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
                Cancel
              </button>
              <button type="submit"
                      class="px-6 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-xl font-light hover:shadow-lg transition-all duration-300">
                {{ editingSequence ? 'Update Sequence' : 'Create Sequence' }}
              </button>
            </div>
          </form>
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
      <div class="h-1 bg-emerald-500 transition-all duration-500 ease-out" :style="{ width: statusProgress + '%' }"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '../composables/useApi'

useHead({
  title: 'Sequences - Followupper'
})

const { sequences, createSequence, updateSequence, deleteSequence, loadSequences } = useApi()

// Local UI state
const showCreateSequenceForm = ref(false)
const editingSequence = ref(null)
const newSequence = ref({
  name: '',
  description: '',
  platform: 'email',
  is_active: true
})

// Status bar state
const statusMessage = ref('')
const showStatusBar = ref(false)
const statusTimer = ref(null)
const statusProgress = ref(100)

const showStatusWithProgressLocal = (message, duration = 5000) => {
  statusMessage.value = message
  showStatusBar.value = true
  statusProgress.value = 100
  
  if (statusTimer.value) {
    clearTimeout(statusTimer.value)
  }
  
  const progressInterval = setInterval(() => {
    statusProgress.value -= (100 / (duration / 50))
    if (statusProgress.value <= 0) {
      clearInterval(progressInterval)
    }
  }, 50)
  
  statusTimer.value = setTimeout(() => {
    showStatusBar.value = false
    statusTimer.value = null
    clearInterval(progressInterval)
  }, duration)
}

// Form handlers
const closeSequenceForm = () => {
  showCreateSequenceForm.value = false
  editingSequence.value = null
  newSequence.value = {
    name: '',
    description: '',
    platform: 'email',
    is_active: true
  }
}

const editSequence = (sequence) => {
  editingSequence.value = sequence
  newSequence.value = {
    name: sequence.name,
    description: sequence.description,
    platform: sequence.platform,
    is_active: sequence.is_active
  }
  showCreateSequenceForm.value = true
}

const handleSaveSequence = async () => {
  try {
    if (editingSequence.value) {
      // Update existing sequence
      await updateSequence(editingSequence.value.id, newSequence.value)
      showStatusWithProgressLocal('Sequence updated successfully!', 3000)
    } else {
      // Create new sequence
      await createSequence(newSequence.value)
      showStatusWithProgressLocal('Sequence created successfully!', 3000)
    }
    
    // Refresh sequences list
    await loadSequences()
    closeSequenceForm()
  } catch (error) {
    console.error('Error saving sequence:', error)
    showStatusWithProgressLocal('Error saving sequence', 3000)
  }
}

const handleDeleteSequence = async (sequenceId) => {
  if (!confirm('Are you sure you want to delete this sequence? This action cannot be undone.')) {
    return
  }
  
  try {
    await deleteSequence(sequenceId)
    showStatusWithProgressLocal('Sequence deleted successfully!', 3000)
    
    // Refresh sequences list
    await loadSequences()
  } catch (error) {
    console.error('Error deleting sequence:', error)
    showStatusWithProgressLocal('Error deleting sequence', 3000)
  }
}

const viewSequenceSteps = (sequence) => {
  // TODO: Implement sequence steps view
  console.log('View steps for sequence:', sequence)
}

onMounted(() => {
  // Sequences are already loaded by initializeApp in app.vue
})
</script>
