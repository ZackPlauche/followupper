<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900">
    <!-- Header -->
    <header class="bg-slate-900/50 backdrop-blur-sm border-b border-emerald-500/20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <NuxtLink to="/" class="text-4xl font-thin gradient-title">
            followupper
          </NuxtLink>
              <nav class="flex space-x-2">
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
                <NuxtLink to="/sequences" 
                          class="px-6 py-3 rounded-xl font-light transition-all duration-300 hover:scale-105"
                          :class="$route.path === '/sequences' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400'">
                  Sequences
                </NuxtLink>
                <NuxtLink to="/schedule" 
                          class="px-6 py-3 rounded-xl font-light transition-all duration-300 hover:scale-105"
                          :class="$route.path === '/schedule' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400'">
                  Schedule
                </NuxtLink>
                <NuxtLink to="/settings" 
                          class="px-6 py-3 rounded-xl font-light transition-all duration-300 hover:scale-105"
                          :class="$route.path === '/settings' ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg' : 'text-slate-300 hover:text-emerald-400'">
                  Settings
                </NuxtLink>
              </nav>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <slot />
    </main>
  </div>
</template>

<script setup>
// Layout for all pages
</script>
