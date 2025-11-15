<template>
  <div v-if="show"
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
    <div
      class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full h-full sm:h-auto sm:max-w-2xl sm:max-h-[90vh] flex flex-col overflow-hidden">
      <!-- Header -->
      <div class="flex justify-between items-center p-4 sm:p-6 border-b border-slate-700/50 flex-shrink-0">
        <h3 class="text-xl sm:text-2xl font-thin text-slate-100">Bulk Edit ({{ contactCount }} contacts)</h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-200 transition-colors">
          <Icon name="lucide:x" class="w-6 h-6" />
        </button>
      </div>

      <!-- Scrollable Content -->
      <div class="flex-1 overflow-y-auto p-4 sm:p-6">
        <div class="space-y-4">
          <p class="text-sm text-slate-400 mb-4">Edit fields for all selected contacts. Leave fields empty to keep
            existing values.</p>

          <!-- Platform Preference -->
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Platform Preference</label>
            <div class="flex gap-4">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="localData.platform_preference" value="email"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                <span class="text-slate-300 text-sm">Email</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="localData.platform_preference" value="codementor"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                <span class="text-slate-300 text-sm">Codementor</span>
              </label>
            </div>
            <p class="text-xs text-slate-500 mt-1">Leave unchecked to keep existing preferences</p>
          </div>

          <!-- Timezone -->
          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Timezone</label>
            <select v-model="localData.timezone"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
              <option value="">Keep existing</option>
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

          <!-- Status -->
          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Status</label>
            <select v-model="localData.is_active"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
              <option :value="null">Keep existing</option>
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
          </div>

          <!-- Source -->
          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Source</label>
            <input v-model="localData.source" type="text"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="Leave empty to keep existing">
          </div>

          <!-- Favorite -->
          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Favorite</label>
            <select v-model="localData.is_favorite"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
              <option :value="null">Keep existing</option>
              <option :value="true">Mark as favorite</option>
              <option :value="false">Remove favorite</option>
            </select>
          </div>

          <!-- Gender -->
          <div>
            <label class="block text-sm font-light text-slate-300 mb-1">Gender</label>
            <div class="flex items-center bg-slate-700/50 rounded-lg p-1 border border-slate-500/30 w-fit">
              <button type="button" @click="localData.gender = ''"
                :class="localData.gender === '' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                Not specified
              </button>
              <button type="button" @click="localData.gender = 'male'"
                :class="localData.gender === 'male' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                Male
              </button>
              <button type="button" @click="localData.gender = 'female'"
                :class="localData.gender === 'female' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                Female
              </button>
            </div>
            <p class="text-xs text-slate-500 mt-1">Click "Not specified" to keep existing</p>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex flex-col sm:flex-row gap-3 p-4 sm:p-6 border-t border-slate-700/50 flex-shrink-0">
        <button @click="$emit('close')"
          class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
          Cancel
        </button>
        <button @click="handleSave"
          class="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
          Update {{ contactCount }} Contact{{ contactCount !== 1 ? 's' : '' }}
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
  data: {
    type: Object,
    default: () => ({
      platform_preference: [],
      timezone: '',
      is_active: null,
      source: '',
      is_favorite: null,
      gender: ''
    })
  }
})

const emit = defineEmits(['close', 'save'])

const localData = ref({ ...props.data })

watch(() => props.data, (newData) => {
  localData.value = { ...newData }
}, { deep: true })

const handleSave = () => {
  emit('save', { ...localData.value })
}
</script>

