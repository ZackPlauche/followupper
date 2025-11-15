<template>
  <div id="integrations" class="space-y-8 scroll-mt-6">
    <!-- Gmail Configuration -->
    <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8">
      <div class="flex items-center mb-6">
        <div
          class="w-12 h-12 bg-gradient-to-r from-red-500 to-pink-500 rounded-xl flex items-center justify-center mr-4">
          <Icon name="lucide:mail" class="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 class="text-2xl font-thin text-slate-100">Gmail Integration</h3>
          <p class="text-slate-400 font-light">Configure your Gmail account for automated email sending</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Gmail Address</label>
          <input v-model="localGmailConfig.email" type="email" placeholder="your-email@gmail.com"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
        </div>

        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">App Password</label>
          <input v-model="localGmailConfig.app_password" type="password" placeholder="16-character app password"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-light text-slate-300 mb-2">Display Name (Optional)</label>
          <input v-model="localGmailConfig.name" type="text" placeholder="Your Name"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
          <p class="mt-2 text-xs text-slate-400 font-light">This name will appear as the sender in emails (e.g.,
            "Your Name &lt;your-email@gmail.com&gt;")</p>
        </div>
      </div>

      <div class="flex items-center justify-between mt-6">
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 rounded-full"
            :class="localGmailConfig.email && localGmailConfig.app_password ? 'bg-emerald-400' : 'bg-slate-500'"></div>
          <span class="text-sm text-slate-300 font-light">
            {{ localGmailConfig.email && localGmailConfig.app_password ? 'Configured' : 'Not configured' }}
          </span>
        </div>
        <div class="flex space-x-3">
          <button @click="$emit('test-gmail')"
            class="px-4 py-2 bg-blue-600/50 text-blue-300 rounded-lg font-light hover:bg-blue-600/70 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!localGmailConfig.email || !localGmailConfig.app_password">
            Test
          </button>
          <button @click="handleSaveGmail"
            class="px-4 py-2 rounded-lg font-light transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            :class="hasGmailChanges ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:shadow-lg' : 'bg-gradient-to-r from-emerald-500/30 to-cyan-500/30 text-emerald-200'"
            :disabled="!localGmailConfig.email || !hasGmailChanges">
            Save
          </button>
        </div>
      </div>
    </div>

    <!-- Codementor Configuration -->
    <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8">
      <div class="flex items-center mb-6">
        <div
          class="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center mr-4">
          <Icon name="lucide:code" class="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 class="text-2xl font-thin text-slate-100">Codementor Integration</h3>
          <p class="text-slate-400 font-light">Configure your Codementor account credentials</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Access Token</label>
          <input v-model="localCodementorConfig.access_token" type="password"
            placeholder="Your Codementor access token"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
        </div>

        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Refresh Token</label>
          <input v-model="localCodementorConfig.refresh_token" type="password"
            placeholder="Your Codementor refresh token"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
        </div>
      </div>

      <div class="mt-4 p-4 bg-slate-700/30 rounded-xl border border-slate-600/30">
        <div class="flex items-start space-x-3">
          <Icon name="lucide:info" class="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
          <div class="text-sm text-slate-300">
            <p class="font-medium text-blue-400 mb-1">Token Authentication</p>
            <p>Get these tokens from your Codementor cookies in your browser. The system will automatically
              refresh the access token when needed.</p>
          </div>
        </div>
      </div>

      <!-- Codementor Rate Limiting -->
      <div class="mt-6 pt-6 border-t border-slate-600/30">
        <h4 class="text-lg font-light text-slate-200 mb-4">Rate Limiting</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Max Concurrent Messages</label>
            <input v-model.number="localUserConfig.codementor_max_concurrent" type="number" min="1"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="1">
            <p class="mt-2 text-xs text-slate-400 font-light">Maximum number of Codementor messages that can be
              sent at the same time</p>
          </div>
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Send Interval (seconds)</label>
            <input v-model.number="localUserConfig.codementor_send_interval" type="number" min="1"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="5">
            <p class="mt-2 text-xs text-slate-400 font-light">Interval in seconds between sending Codementor
              messages</p>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between mt-6">
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 rounded-full"
            :class="localCodementorConfig.access_token && localCodementorConfig.refresh_token ? 'bg-emerald-400' : 'bg-slate-500'">
          </div>
          <span class="text-sm text-slate-300 font-light">
            {{ localCodementorConfig.access_token && localCodementorConfig.refresh_token ? 'Configured' : 'Not configured'
            }}
          </span>
        </div>
        <div class="flex space-x-3">
          <button @click="$emit('import-codementor-contacts')"
            class="px-4 py-2 bg-purple-600/50 text-purple-300 rounded-lg font-light hover:bg-purple-600/70 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!localCodementorConfig.access_token || !localCodementorConfig.refresh_token || importingCodementor">
            <Icon name="lucide:download" class="w-4 h-4 inline mr-1" />
            {{ importingCodementor ? 'Importing...' : 'Import Contacts' }}
          </button>
          <button @click="$emit('test-codementor')"
            class="px-4 py-2 bg-blue-600/50 text-blue-300 rounded-lg font-light hover:bg-blue-600/70 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!localCodementorConfig.access_token || !localCodementorConfig.refresh_token">
            Test
          </button>
          <button @click="handleSaveCodementor"
            class="px-4 py-2 rounded-lg font-light transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            :class="hasCodementorChanges ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:shadow-lg' : 'bg-gradient-to-r from-emerald-500/30 to-cyan-500/30 text-emerald-200'"
            :disabled="!localCodementorConfig.access_token || !hasCodementorChanges">
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  gmailConfig: {
    type: Object,
    required: true
  },
  codementorConfig: {
    type: Object,
    required: true
  },
  userConfig: {
    type: Object,
    required: true
  },
  hasGmailChanges: {
    type: Boolean,
    default: false
  },
  hasCodementorChanges: {
    type: Boolean,
    default: false
  },
  importingCodementor: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save-gmail', 'save-codementor', 'test-gmail', 'test-codementor', 'import-codementor-contacts', 'update:gmailConfig', 'update:codementorConfig', 'update:userConfig'])

const localGmailConfig = computed({
  get: () => props.gmailConfig,
  set: (value) => emit('update:gmailConfig', value)
})

const localCodementorConfig = computed({
  get: () => props.codementorConfig,
  set: (value) => emit('update:codementorConfig', value)
})

const localUserConfig = computed({
  get: () => props.userConfig,
  set: (value) => emit('update:userConfig', value)
})

const handleSaveGmail = () => {
  emit('save-gmail', { ...localGmailConfig.value })
}

const handleSaveCodementor = () => {
  emit('save-codementor', { ...localCodementorConfig.value, userConfig: { ...localUserConfig.value } })
}
</script>

