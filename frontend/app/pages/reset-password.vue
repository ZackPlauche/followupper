<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-5xl font-thin gradient-title mb-4">followupper</h1>
        <p class="text-slate-400 font-light">Reset your password</p>
      </div>

      <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8">
        <form @submit.prevent="handleReset" class="space-y-6">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">New Password</label>
            <input v-model="password" type="password" required minlength="8"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="••••••••">
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Confirm Password</label>
            <input v-model="confirmPassword" type="password" required minlength="8"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="••••••••">
          </div>

          <div v-if="error" class="bg-red-500/20 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">
            {{ error }}
          </div>

          <div v-if="success" class="bg-emerald-500/20 border border-emerald-500/30 rounded-xl p-4 text-emerald-300 text-sm">
            {{ success }}
          </div>

          <button type="submit" :disabled="isLoading || !password || password !== confirmPassword"
            class="w-full bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
            {{ isLoading ? 'Resetting...' : 'Reset Password' }}
          </button>

          <div class="text-center">
            <NuxtLink to="/login" class="text-sm text-emerald-400 hover:text-emerald-300 font-light transition-colors">
              Back to login
            </NuxtLink>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

useHead({
  title: 'Reset Password - Followupper'
})

const route = useRoute()
const { apiCall } = useApiFetch()

const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const error = ref('')
const success = ref('')

const token = computed(() => route.query.token)

const handleReset = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  if (!token.value) {
    error.value = 'Invalid reset token'
    return
  }

  isLoading.value = true
  error.value = ''
  success.value = ''
  
  try {
    const data = await apiCall('/auth/password-reset/', {
      method: 'POST',
      body: JSON.stringify({
        token: token.value,
        new_password: password.value
      })
    }, 3, false) // Don't require auth for password reset
    
    success.value = data.message || 'Password reset successful! Redirecting to login...'
    setTimeout(() => {
      navigateTo('/login')
    }, 2000)
  } catch (err) {
    error.value = err.message || 'Password reset failed'
    console.error('Password reset error:', err)
  } finally {
    isLoading.value = false
  }
}
</script>

