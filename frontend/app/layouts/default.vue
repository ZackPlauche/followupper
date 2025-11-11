<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900">
    <!-- Header -->
    <header v-if="isAuthenticated" class="bg-slate-900/50 backdrop-blur-sm border-b border-emerald-500/20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <NuxtLink to="/contacts" class="text-4xl font-thin gradient-title">
            followupper
          </NuxtLink>
          <nav class="flex space-x-2 items-center">
            <NuxtLink to="/contacts" 
                      class="px-6 py-3 rounded-xl font-light transition-all duration-300 hover:scale-105"
                      :class="$route.path === '/contacts' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400'">
              Contacts
            </NuxtLink>
            <NuxtLink to="/templates" 
                      class="px-6 py-3 rounded-xl font-light transition-all duration-300 hover:scale-105"
                      :class="$route.path === '/templates' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400'">
              Templates
            </NuxtLink>
            <NuxtLink to="/campaigns" 
                      class="px-6 py-3 rounded-xl font-light transition-all duration-300 hover:scale-105"
                      :class="$route.path === '/campaigns' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400'">
              Campaigns
            </NuxtLink>
            <NuxtLink to="/settings" 
                      class="px-6 py-3 rounded-xl font-light transition-all duration-300 hover:scale-105"
                      :class="$route.path === '/settings' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400'">
              Settings
            </NuxtLink>
            <button @click="handleLogout"
                    class="px-6 py-3 rounded-xl font-light transition-all duration-300 hover:scale-105 text-slate-300 hover:text-red-400">
              Logout
            </button>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main :class="isAuthenticated ? 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8' : ''">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const { apiFetch, API_BASE } = useApiFetch()
const isAuthenticated = ref(false)

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
})
</script>
