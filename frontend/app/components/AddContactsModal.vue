<template>
  <div v-if="show"
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
    <div
      class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 p-4 sm:p-8 w-full h-full sm:h-auto sm:max-w-2xl sm:max-h-[90vh] overflow-y-auto flex flex-col">
      <div class="flex justify-between items-center mb-4 sm:mb-6 flex-shrink-0">
        <h3 class="text-xl sm:text-2xl font-thin text-slate-100">Add Contacts to {{ campaign?.name }}</h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-200 transition-colors">
          <Icon name="lucide:x" class="w-6 h-6" />
        </button>
      </div>

      <div class="flex-1 overflow-y-auto min-h-0">
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Select Contacts *</label>
            <div class="mb-3">
              <input v-model="searchQuery" type="text" placeholder="Search contacts..."
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>
            <div class="bg-slate-700/30 rounded-xl border border-emerald-500/30 p-3 max-h-96 overflow-y-auto">
              <div v-if="filteredContacts.length === 0"
                class="text-slate-400 text-xs text-center py-3">
                <div v-if="availableContacts.length === 0">
                  <div v-if="allContacts.length === 0">No active contacts available</div>
                  <div v-else>All active contacts are already assigned to this campaign</div>
                </div>
                <div v-else>No contacts match your search</div>
              </div>
              <div v-else class="space-y-1">
                <label v-for="contact in filteredContacts" :key="contact.id"
                  class="flex items-center space-x-2 p-1.5 rounded hover:bg-slate-600/30 cursor-pointer transition-colors">
                  <input type="checkbox" :value="contact.id" v-model="localSelectedIds"
                    class="w-4 h-4 text-emerald-500 bg-slate-600 border-slate-500 rounded focus:ring-emerald-400 focus:ring-2">
                  <div class="flex-1 min-w-0">
                    <div class="text-slate-100 text-sm font-medium truncate">{{ contact.name }}</div>
                    <div class="text-slate-400 text-xs truncate">
                      {{ contact.email || contact.codementor_username || 'No contact info' }}
                    </div>
                  </div>
                </label>
              </div>
            </div>
            <p v-if="localSelectedIds.length > 0" class="text-xs text-slate-400 mt-2">
              {{ localSelectedIds.length }} contact{{ localSelectedIds.length !== 1 ? 's' : '' }} selected
            </p>
          </div>

          <div class="flex flex-col sm:flex-row gap-3 pt-4 flex-shrink-0">
            <button type="button" @click="$emit('close')"
              class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
              Cancel
            </button>
            <button type="submit" :disabled="localSelectedIds.length === 0"
              class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
              Add Contacts
            </button>
          </div>
        </form>
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
    default: null
  },
  availableContacts: {
    type: Array,
    default: () => []
  },
  allContacts: {
    type: Array,
    default: () => []
  },
  selectedContactIds: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'save'])

const localSelectedIds = ref([...props.selectedContactIds])
const searchQuery = ref('')

watch(() => props.selectedContactIds, (newIds) => {
  localSelectedIds.value = [...newIds]
})

const filteredContacts = computed(() => {
  if (!searchQuery.value.trim()) {
    return props.availableContacts
  }
  const query = searchQuery.value.toLowerCase().trim()
  return props.availableContacts.filter(contact => {
    const name = (contact.name || '').toLowerCase()
    const email = (contact.email || '').toLowerCase()
    const codementor = (contact.codementor_username || '').toLowerCase()
    return name.includes(query) || email.includes(query) || codementor.includes(query)
  })
})

const handleSubmit = () => {
  emit('save', [...localSelectedIds.value])
}
</script>

