<template>
  <div
    class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div
          class="w-20 h-20 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6">
          <Icon name="lucide:check" class="w-12 h-12 text-white" />
        </div>
        <h1 class="text-5xl font-thin gradient-title mb-4">Thank You!</h1>
        <p class="text-slate-400 font-light text-lg">
          <span v-if="name">Hi {{ name }},</span>
          <span v-else>Hi there,</span>
        </p>
      </div>

      <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 text-center">
        <p class="text-slate-300 font-light mb-6 text-lg">
          Your interest has been sent successfully! We'll review your submission and get back to you soon.
        </p>

        <div class="space-y-4">
          <NuxtLink to="/login"
            class="block w-full bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105">
            Sign In
          </NuxtLink>

          <NuxtLink to="/"
            class="block w-full text-slate-400 hover:text-slate-300 text-sm font-light transition-colors">
            ← Back to home
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

useHead({
  title: 'Thank You - Followupper'
})

const route = useRoute()
const name = route.query.name || null
</script>
