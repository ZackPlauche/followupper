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
              Initializing data...
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
import { useRoute } from 'vue-router'
import { watch } from 'vue'

const { initializeApp } = useApi()
const route = useRoute()
const isInitializing = ref(false)
const showContent = ref(true)
const hasInitialized = ref(false)

// Public routes that don't need data initialization
const publicRoutes = ['/', '/login', '/interest', '/reset-password', '/thank-you']

const initializeIfNeeded = async (path) => {
  // Only initialize data if we're on a protected route and haven't initialized yet
  if (!publicRoutes.includes(path) && !hasInitialized.value) {
    isInitializing.value = true
    showContent.value = false
    
    // Add a small delay to ensure API is ready
    await new Promise(resolve => setTimeout(resolve, 500))
    
    try {
      await initializeApp()
      hasInitialized.value = true
    } catch (error) {
      console.error('Error initializing app:', error)
    } finally {
      // First hide loading screen
      isInitializing.value = false
      
      // Then show content after loading screen has faded out
      await new Promise(resolve => setTimeout(resolve, 300))
      showContent.value = true
    }
  } else if (publicRoutes.includes(path)) {
    // On public routes, just show content
    showContent.value = true
  }
}

onMounted(async () => {
  await initializeIfNeeded(route.path)
})

// Watch for route changes and initialize if needed
watch(() => route.path, async (newPath, oldPath) => {
  // Initialize if moving from public to protected route
  if (publicRoutes.includes(oldPath) && !publicRoutes.includes(newPath)) {
    hasInitialized.value = false // Reset flag to allow re-initialization
    await initializeIfNeeded(newPath)
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