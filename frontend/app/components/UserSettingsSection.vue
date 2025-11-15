<template>
  <div id="user-settings"
    class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 scroll-mt-6">
    <div class="flex items-center mb-6">
      <div
        class="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center mr-4">
        <Icon name="lucide:user" class="w-6 h-6 text-white" />
      </div>
      <div>
        <h3 class="text-2xl font-thin text-slate-100">User Settings</h3>
        <p class="text-slate-400 font-light">Configure your personal preferences</p>
      </div>
    </div>

    <div class="space-y-6">
      <div>
        <label class="block text-sm font-light text-slate-300 mb-2">Your Timezone</label>
        <select v-model="localConfig.timezone"
          class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
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
        <p class="mt-2 text-xs text-slate-400 font-light">This timezone will be used when you select "Mine" in
          message scheduling</p>
      </div>

      <div>
        <label class="block text-sm font-light text-slate-300 mb-2">Default Footer/Signature</label>
        <textarea v-model="localConfig.footer" rows="4"
          class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
          placeholder="Message footer"></textarea>
        <p class="mt-2 text-xs text-slate-400 font-light">This footer will be used as the default for message
          chains. You can override it per chain.</p>
      </div>
    </div>

    <!-- Password Change Section -->
    <div class="mt-8 pt-8 border-t border-slate-600/30">
      <h4 class="text-lg font-light text-slate-200 mb-4">Change Password</h4>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Current Password</label>
          <input v-model="localPasswordChange.currentPassword" type="password"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
            placeholder="Enter current password">
        </div>
        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">New Password</label>
          <input v-model="localPasswordChange.newPassword" type="password"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
            placeholder="Enter new password">
        </div>
        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Confirm New Password</label>
          <input v-model="localPasswordChange.confirmPassword" type="password"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
            placeholder="Confirm new password">
        </div>
        <div v-if="passwordError" class="text-red-400 text-sm">{{ passwordError }}</div>
        <div v-if="passwordSuccess" class="text-emerald-400 text-sm">{{ passwordSuccess }}</div>
        <button @click="handlePasswordChange"
          :disabled="!localPasswordChange.currentPassword || !localPasswordChange.newPassword || !localPasswordChange.confirmPassword"
          class="px-6 py-3 rounded-xl font-light transition-all duration-300"
          :class="localPasswordChange.currentPassword && localPasswordChange.newPassword && localPasswordChange.confirmPassword
            ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:shadow-lg'
            : 'bg-gradient-to-r from-emerald-500/30 to-cyan-500/30 text-emerald-200 cursor-not-allowed'">
          Change Password
        </button>
      </div>
    </div>

    <div class="flex justify-end mt-6">
      <button @click="handleSave" class="px-6 py-3 rounded-xl font-light transition-all duration-300"
        :class="hasChanges ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:shadow-lg' : 'bg-gradient-to-r from-emerald-500/30 to-cyan-500/30 text-emerald-200'"
        :disabled="!hasChanges">
        Save User Settings
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
  passwordChange: {
    type: Object,
    default: () => ({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
  },
  passwordError: {
    type: String,
    default: ''
  },
  passwordSuccess: {
    type: String,
    default: ''
  },
  hasChanges: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save', 'change-password', 'update:config', 'update:passwordChange'])

const localConfig = computed({
  get: () => props.config,
  set: (value) => emit('update:config', value)
})

const localPasswordChange = computed({
  get: () => props.passwordChange,
  set: (value) => emit('update:passwordChange', value)
})

const handleSave = () => {
  emit('save', { ...localConfig.value })
}

const handlePasswordChange = () => {
  emit('change-password', { ...localPasswordChange.value })
}
</script>

