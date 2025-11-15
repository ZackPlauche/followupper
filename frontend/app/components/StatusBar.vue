<template>
  <Transition name="status-bar">
    <div v-if="show"
      class="fixed bottom-4 sm:bottom-6 right-4 sm:right-6 left-4 sm:left-auto bg-slate-800/90 backdrop-blur-sm rounded-xl shadow-2xl border border-emerald-500/20 overflow-hidden transition-all duration-300 z-[60] max-w-sm">
      <div class="px-4 sm:px-6 py-3 text-sm text-slate-300 font-light">
        <div class="flex items-center space-x-3">
          <div class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse flex-shrink-0"></div>
          <span class="break-words">{{ message }}</span>
        </div>
      </div>
      <!-- Progress Bar -->
      <div class="h-1 bg-slate-700/50">
        <div class="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all duration-100 ease-linear"
          :style="{ width: progress + '%' }"></div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  show: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: ''
  },
  progress: {
    type: Number,
    default: 100
  }
})
</script>

<style scoped>
.status-bar-enter-active,
.status-bar-leave-active {
  transition: all 0.3s ease;
}

.status-bar-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.status-bar-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
