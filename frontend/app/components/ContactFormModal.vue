<template>
  <div v-if="show" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
    <div
      class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full h-full sm:h-auto sm:max-w-md sm:max-h-[90vh] flex flex-col">
      <div class="p-4 sm:p-6 border-b border-slate-700/50 flex-shrink-0 flex justify-between items-center">
        <h3 class="text-xl sm:text-2xl font-thin text-slate-100">{{ isEdit ? 'Edit Contact' : 'Add Contact' }}</h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-200 transition-colors">
          <Icon name="lucide:x" class="w-6 h-6" />
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-4 sm:p-6">
        <form @submit.prevent="handleSubmit" class="space-y-3">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Name *</label>
            <input v-model="formData.name" type="text" required
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Preferred Name</label>
            <input v-model="formData.preferred_name" type="text"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="Leave blank to use first name">
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Gender</label>
            <div
              class="flex items-center bg-slate-700/50 rounded-lg p-1 border border-slate-500/30 w-fit flex-wrap gap-1">
              <button type="button" @click="formData.gender = ''"
                :class="formData.gender === '' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="px-2 sm:px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                Not specified
              </button>
              <button type="button" @click="formData.gender = 'male'"
                :class="formData.gender === 'male' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="px-2 sm:px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                Male
              </button>
              <button type="button" @click="formData.gender = 'female'"
                :class="formData.gender === 'female' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="px-2 sm:px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                Female
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Email</label>
            <input v-model="formData.email" type="email"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Codementor Username</label>
            <input v-model="formData.codementor_username" type="text"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>

          <div>
            <PlatformMultiSelect v-model="formData.platform_preference" :available-platforms="availablePlatforms"
              label="Platform Preference" />
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Timezone</label>
            <select v-model="formData.timezone"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
              <option value="UTC">UTC</option>
              <option value="America/New_York">Eastern Time (ET)</option>
              <option value="America/Chicago">Central Time (CT)</option>
              <option value="America/Denver">Mountain Time (MT)</option>
              <option value="America/Los_Angeles">Pacific Time (PT)</option>
              <option value="Europe/London">London (GMT)</option>
              <option value="Europe/Paris">Paris (CET)</option>
              <option value="Asia/Tokyo">Tokyo (JST)</option>
              <option value="Asia/Shanghai">Shanghai (CST)</option>
              <option value="Australia/Sydney">Sydney (AEST)</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Notes</label>
            <textarea v-model="formData.notes" rows="3"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"></textarea>
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Source</label>
            <input v-model="formData.source" type="text"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="e.g., manual, codementor, csv">
          </div>
        </form>
      </div>

      <div
        class="p-4 sm:p-6 border-t border-slate-700/50 flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 flex-shrink-0">
        <button type="button" @click="$emit('close')"
          class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-2 rounded-lg text-sm font-light hover:bg-slate-600/70 transition-colors">
          Cancel
        </button>
        <button @click="handleSubmit"
          class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-2 rounded-lg text-sm font-light hover:shadow-lg transition-all duration-300">
          {{ isEdit ? 'Update Contact' : 'Save Contact' }}
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
  availablePlatforms: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'save'])

const isEdit = computed(() => !!props.contact)

const formData = ref({
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

watch(() => props.contact, (newContact) => {
  if (newContact) {
    formData.value = { ...newContact }
  } else {
    formData.value = {
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
    }
  }
}, { immediate: true })

watch(() => props.show, (newShow) => {
  if (!newShow) {
    // Reset form when modal closes
    if (!props.contact) {
      formData.value = {
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
      }
    }
  }
})

const handleSubmit = () => {
  emit('save', { ...formData.value })
}
</script>
