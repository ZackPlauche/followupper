<template>
  <div>
    <NuxtLayout>
      <!-- Loading Screen -->
      <Transition name="loading" appear>
        <div v-if="isInitializing" class="flex items-center justify-center pt-10">
          <div class="text-center">
            <div class="mb-2">
              <Icon name="lucide:loader-2" class="w-12 h-12 text-emerald-400 animate-spin mx-auto" />
            </div>
            <h2 class="text-4xl font-thin text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400 leading-loose">
              Initializing app...
            </h2>
          </div>
        </div>
      </Transition>

      <!-- Main Content -->
      <Transition name="content" appear>
        <div v-if="showContent">
          <NuxtPage />
        </div>
      </Transition>
    </NuxtLayout>
  </div>
</template>

<script setup>
const { initializeApp } = useApi()
const isInitializing = ref(true)
const showContent = ref(false)

onMounted(async () => {
  // Add a small delay to ensure API is ready
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  try {
    await initializeApp()
  } catch (error) {
    console.error('Error initializing app:', error)
  } finally {
    // First hide loading screen
    isInitializing.value = false
    
    // Then show content after loading screen has faded out
    await new Promise(resolve => setTimeout(resolve, 600))
    showContent.value = true
  }
})
</script>

<style scoped>
/* Loading screen transitions */
.loading-enter-active,
.loading-leave-active {
  transition: all 0.6s ease;
}

.loading-enter-from {
  opacity: 0;
}

.loading-leave-to {
  opacity: 0;
}

/* Content transitions */
.content-enter-active,
.content-leave-active {
  transition: all 0.8s ease;
}

.content-enter-from {
  opacity: 0;
}

.content-leave-to {
  opacity: 0;
}
</style>