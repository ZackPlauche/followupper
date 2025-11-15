<template>
  <div id="automation"
    class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 scroll-mt-6">
    <div class="flex items-center mb-6">
      <div
        class="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mr-4">
        <Icon name="lucide:zap" class="w-6 h-6 text-white" />
      </div>
      <div>
        <h3 class="text-2xl font-thin text-slate-100">Automation Settings</h3>
        <p class="text-slate-400 font-light">Configure how and when follow-ups are sent</p>
      </div>
    </div>

    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h4 class="text-lg font-light text-slate-100">Enable Background Scheduler</h4>
          <p class="text-sm text-slate-400">Run the background service that checks for and sends scheduled
            follow-ups</p>
        </div>
        <label class="relative inline-flex items-center cursor-pointer">
          <input v-model="localConfig.enabled" type="checkbox" class="sr-only peer">
          <div
            class="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500">
          </div>
        </label>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Check Interval (minutes)</label>
          <input v-model.number="localConfig.check_interval" type="number" min="1" max="1440"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
        </div>

        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Max Retries</label>
          <input v-model.number="localConfig.max_retries" type="number" min="1" max="10"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
        </div>
      </div>

      <div>
        <label class="block text-sm font-light text-slate-300 mb-2">Default Timezone</label>
        <select v-model="localConfig.timezone"
          class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
          <option value="UTC">UTC</option>
          <option value="America/New_York">Eastern Time</option>
          <option value="America/Chicago">Central Time</option>
          <option value="America/Denver">Mountain Time</option>
          <option value="America/Los_Angeles">Pacific Time</option>
          <option value="Europe/London">London</option>
          <option value="Europe/Paris">Paris</option>
          <option value="Asia/Tokyo">Tokyo</option>
        </select>
      </div>
    </div>

    <div class="flex justify-end mt-6">
      <button @click="handleSave" class="px-6 py-3 rounded-xl font-light transition-all duration-300"
        :class="hasChanges ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:shadow-lg' : 'bg-gradient-to-r from-emerald-500/30 to-cyan-500/30 text-emerald-200'"
        :disabled="!hasChanges">
        Save Automation Settings
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  config: {
    type: Object,
    required: true
  },
  hasChanges: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save', 'update:config'])

const localConfig = computed({
  get: () => props.config,
  set: (value) => emit('update:config', value)
})

const handleSave = () => {
  emit('save', { ...localConfig.value })
}
</script>

