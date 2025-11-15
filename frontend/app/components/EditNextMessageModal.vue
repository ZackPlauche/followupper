<template>
  <div v-if="show"
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
    <div
      class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 p-4 sm:p-8 w-full h-full sm:h-auto sm:max-w-2xl sm:max-h-[90vh] overflow-y-auto flex flex-col">
      <div class="flex justify-between items-center mb-4 sm:mb-6 flex-shrink-0">
        <h3 class="text-xl sm:text-2xl font-thin text-slate-100">Edit Next Message for {{ campaign?.name }}</h3>
        <button @click="$emit('close')" class="sm:hidden text-slate-400 hover:text-slate-200 transition-colors">
          <Icon name="lucide:x" class="w-6 h-6" />
        </button>
      </div>

      <div class="flex-1 overflow-y-auto min-h-0">
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Next Message Override *</label>
            <textarea v-model="localMessage" rows="10" required
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"></textarea>
            <p class="mt-2 text-xs text-slate-400 font-light">This message will be sent to all contacts in this campaign
              for their next scheduled send.</p>
          </div>

          <div class="flex flex-col sm:flex-row gap-3 pt-4 flex-shrink-0">
            <button type="button" @click="$emit('close')"
              class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
              Cancel
            </button>
            <button type="submit"
              class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
              Save Next Message
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
  message: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'save'])

const localMessage = ref(props.message)

watch(() => props.message, (newMessage) => {
  localMessage.value = newMessage
})

const handleSubmit = () => {
  emit('save', localMessage.value)
}
</script>

