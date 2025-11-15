<template>
  <header v-if="isAuthenticated" class="bg-slate-900/50 backdrop-blur-sm border-b border-emerald-500/20">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center py-4 sm:py-6">
        <NuxtLink to="/contacts" class="text-2xl sm:text-3xl lg:text-4xl font-thin gradient-title">
          followupper
        </NuxtLink>

        <!-- Desktop Navigation -->
        <nav class="hidden md:flex space-x-2 items-center">
          <NuxtLink to="/contacts"
            class="px-4 lg:px-6 py-2 lg:py-3 rounded-xl font-light transition-all duration-300 hover:scale-105 text-sm lg:text-base"
            :class="$route.path === '/contacts' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400'">
            Contacts
          </NuxtLink>
          <NuxtLink to="/templates"
            class="px-4 lg:px-6 py-2 lg:py-3 rounded-xl font-light transition-all duration-300 hover:scale-105 text-sm lg:text-base"
            :class="$route.path === '/templates' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400'">
            Templates
          </NuxtLink>
          <NuxtLink to="/campaigns"
            class="px-4 lg:px-6 py-2 lg:py-3 rounded-xl font-light transition-all duration-300 hover:scale-105 text-sm lg:text-base"
            :class="$route.path === '/campaigns' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400'">
            Campaigns
          </NuxtLink>
          <NuxtLink to="/settings"
            class="px-4 lg:px-6 py-2 lg:py-3 rounded-xl font-light transition-all duration-300 hover:scale-105 text-sm lg:text-base"
            :class="$route.path === '/settings' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400'">
            Settings
          </NuxtLink>
          <button @click="handleLogout"
            class="px-4 lg:px-6 py-2 lg:py-3 rounded-xl font-light transition-all duration-300 hover:scale-105 text-slate-300 hover:text-red-400 text-sm lg:text-base">
            Logout
          </button>
        </nav>

        <!-- Mobile Menu Button -->
        <button @click="mobileMenuOpen = !mobileMenuOpen"
          class="md:hidden p-2 text-slate-300 hover:text-emerald-400 transition-colors">
          <Icon :name="mobileMenuOpen ? 'lucide:x' : 'lucide:menu'" class="w-6 h-6" />
        </button>
      </div>

      <!-- Mobile Navigation -->
      <Transition name="mobile-menu">
        <nav v-if="mobileMenuOpen" class="md:hidden pb-4 space-y-2">
          <NuxtLink to="/contacts" @click="mobileMenuOpen = false"
            class="block px-4 py-3 rounded-xl font-light transition-all duration-300 text-sm"
            :class="$route.path === '/contacts' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400 hover:bg-slate-800/50'">
            Contacts
          </NuxtLink>
          <NuxtLink to="/templates" @click="mobileMenuOpen = false"
            class="block px-4 py-3 rounded-xl font-light transition-all duration-300 text-sm"
            :class="$route.path === '/templates' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400 hover:bg-slate-800/50'">
            Templates
          </NuxtLink>
          <NuxtLink to="/campaigns" @click="mobileMenuOpen = false"
            class="block px-4 py-3 rounded-xl font-light transition-all duration-300 text-sm"
            :class="$route.path === '/campaigns' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400 hover:bg-slate-800/50'">
            Campaigns
          </NuxtLink>
          <NuxtLink to="/settings" @click="mobileMenuOpen = false"
            class="block px-4 py-3 rounded-xl font-light transition-all duration-300 text-sm"
            :class="$route.path === '/settings' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400 hover:bg-slate-800/50'">
            Settings
          </NuxtLink>
          <button @click="handleLogout"
            class="block w-full text-left px-4 py-3 rounded-xl font-light transition-all duration-300 text-slate-300 hover:text-red-400 hover:bg-slate-800/50 text-sm">
            Logout
          </button>
        </nav>
      </Transition>
    </div>
  </header>
</template>

<script setup>
const router = useRouter()
const route = useRoute()
const { apiFetch } = useApiFetch()
const isAuthenticated = ref(false)
const mobileMenuOpen = ref(false)

// Public routes that don't require authentication
const publicRoutes = ['/', '/login', '/interest', '/reset-password', '/thank-you']

const checkAuth = async () => {
  try {
    const response = await apiFetch('/auth/current-user/', {
      method: 'GET'
    }, false) // Don't require auth for this call

    if (response.ok) {
      isAuthenticated.value = true
      // If on public route, redirect to dashboard
      if (publicRoutes.includes(route.path)) {
        await router.push('/contacts')
      }
    } else {
      isAuthenticated.value = false
      // If on protected route, redirect to login
      if (!publicRoutes.includes(route.path)) {
        await router.push('/login')
      }
    }
  } catch (error) {
    isAuthenticated.value = false
    if (!publicRoutes.includes(route.path)) {
      await router.push('/login')
    }
  }
}

const handleLogout = async () => {
  try {
    // Call logout endpoint
    await apiFetch('/auth/logout/', {
      method: 'POST'
    })
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    // Always clear authentication state
    isAuthenticated.value = false

    // Clear any local storage or session storage
    if (typeof localStorage !== 'undefined') {
      localStorage.clear()
    }
    if (typeof sessionStorage !== 'undefined') {
      sessionStorage.clear()
    }

    // Navigate to login without full page reload
    await router.push('/login')
  }
}

onMounted(() => {
  checkAuth()
})

// Watch for route changes
watch(() => route.path, () => {
  checkAuth()
  mobileMenuOpen.value = false // Close mobile menu on route change
})
</script>

<style scoped>
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: all 0.3s ease;
}

.mobile-menu-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
