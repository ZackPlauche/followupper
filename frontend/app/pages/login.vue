<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <NuxtLink to="/" class="block mb-4">
          <h1 class="text-5xl font-thin gradient-title mb-4 hover:opacity-80 transition-opacity cursor-pointer">followupper</h1>
        </NuxtLink>
        <p class="text-slate-400 font-light">Sign in to your account</p>
      </div>

      <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8">
        <!-- Login Form -->
        <form v-if="!requires2FA && !showPasswordReset" @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Email</label>
            <input v-model="loginForm.email" type="email" required
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="you@example.com">
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Password</label>
            <input v-model="loginForm.password" type="password" required
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="••••••••">
          </div>

          <div class="flex items-center justify-between">
            <label class="flex items-center space-x-2">
              <input v-model="loginForm.remember" type="checkbox"
                class="w-4 h-4 text-emerald-500 bg-slate-700/50 border-emerald-500/30 rounded focus:ring-emerald-400">
              <span class="text-sm font-light text-slate-300">Remember me</span>
            </label>
            <button type="button" @click="showPasswordReset = true"
              class="text-sm text-emerald-400 hover:text-emerald-300 font-light transition-colors">
              Forgot password?
            </button>
          </div>

          <div v-if="loginError" class="bg-red-500/20 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">
            {{ loginError }}
          </div>

          <button type="submit" :disabled="isLoading"
            class="w-full bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
            {{ isLoading ? 'Signing in...' : 'Sign In' }}
          </button>

          <div class="text-center space-y-2">
            <p class="text-sm text-slate-400 font-light">
              Need access?
              <NuxtLink to="/interest" class="text-emerald-400 hover:text-emerald-300 transition-colors">
                Express interest
              </NuxtLink>
            </p>
            <p class="text-sm text-slate-400 font-light">
              <NuxtLink to="/" class="text-slate-500 hover:text-slate-300 transition-colors">
                ← Back to home
              </NuxtLink>
            </p>
          </div>
        </form>

        <!-- 2FA Form -->
        <form v-if="requires2FA" @submit.prevent="handle2FALogin" class="space-y-6">
          <div class="text-center mb-6">
            <h2 class="text-2xl font-thin text-slate-100 mb-2">Two-Factor Authentication</h2>
            <p class="text-sm text-slate-400 font-light">Enter the code from your authenticator app</p>
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">2FA Code</label>
            <input v-model="twoFactorCode" type="text" required maxlength="6" pattern="[0-9]{6}"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors text-center text-2xl tracking-widest"
              placeholder="000000">
          </div>

          <div v-if="loginError" class="bg-red-500/20 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">
            {{ loginError }}
          </div>

          <button type="submit" :disabled="isLoading"
            class="w-full bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
            {{ isLoading ? 'Verifying...' : 'Verify' }}
          </button>

          <button type="button" @click="requires2FA = false; loginError = ''"
            class="w-full text-slate-400 hover:text-slate-300 text-sm font-light transition-colors">
            Back to login
          </button>
        </form>

        <!-- Password Reset Form -->
        <form v-if="showPasswordReset" @submit.prevent="handlePasswordReset" class="space-y-6">
          <div class="text-center mb-6">
            <h2 class="text-2xl font-thin text-slate-100 mb-2">Reset Password</h2>
            <p class="text-sm text-slate-400 font-light">Enter your email to receive a reset link</p>
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Email</label>
            <input v-model="resetEmail" type="email" required
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="you@example.com">
          </div>

          <div v-if="resetMessage" class="bg-emerald-500/20 border border-emerald-500/30 rounded-xl p-4 text-emerald-300 text-sm">
            {{ resetMessage }}
          </div>

          <div v-if="resetError" class="bg-red-500/20 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">
            {{ resetError }}
          </div>

          <button type="submit" :disabled="isLoading"
            class="w-full bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
            {{ isLoading ? 'Sending...' : 'Send Reset Link' }}
          </button>

          <button type="button" @click="showPasswordReset = false; resetError = ''; resetMessage = ''"
            class="w-full text-slate-400 hover:text-slate-300 text-sm font-light transition-colors">
            Back to login
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

useHead({
  title: 'Login - Followupper'
})

const { apiCall } = useApiFetch()

const loginForm = ref({
  email: '',
  password: '',
  remember: false
})
const twoFactorCode = ref('')
const requires2FA = ref(false)
const showPasswordReset = ref(false)
const resetEmail = ref('')
const isLoading = ref(false)
const loginError = ref('')
const resetError = ref('')
const resetMessage = ref('')

const handleLogin = async () => {
  isLoading.value = true
  loginError.value = ''
  
  try {
    const data = await apiCall('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({
        email: loginForm.value.email,
        password: loginForm.value.password
      })
    }, 3, false) // Don't require auth for login
    
    // Check if 2FA is required
    if (data.requires_2fa) {
      requires2FA.value = true
    } else {
      // Login successful - wait a moment for cookies to be set
      // Then verify authentication before initializing
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // Verify we're authenticated by checking current user
      const { apiFetch } = useApiFetch()
      const authCheck = await apiFetch('/auth/current-user/', {
        method: 'GET'
      }, false)
      
      if (authCheck.ok) {
        // Now initialize data
        const { initializeApp } = useApi()
        try {
          await initializeApp()
        } catch (error) {
          console.error('Error initializing app after login:', error)
          // Continue with redirect even if initialization fails
        }
        // Redirect to dashboard
        await navigateTo('/contacts')
      } else {
        // Authentication didn't work - show error
        loginError.value = 'Login successful but session not established. Please try again.'
        console.error('Auth check failed after login:', await authCheck.text())
      }
    }
  } catch (error) {
    loginError.value = error.message || 'Login failed'
    console.error('Login error:', error)
  } finally {
    isLoading.value = false
  }
}

const handle2FALogin = async () => {
  isLoading.value = true
  loginError.value = ''
  
  try {
    const data = await apiCall('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({
        email: loginForm.value.email,
        password: loginForm.value.password,
        two_factor_token: twoFactorCode.value
      })
    }, 3, false) // Don't require auth for login
    
    // Login successful - wait a moment for cookies to be set
    // Then verify authentication before initializing
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Verify we're authenticated by checking current user
    const { apiFetch } = useApiFetch()
    const authCheck = await apiFetch('/auth/current-user/', {
      method: 'GET'
    }, false)
    
    if (authCheck.ok) {
      // Now initialize data
      const { initializeApp } = useApi()
      try {
        await initializeApp()
      } catch (error) {
        console.error('Error initializing app after 2FA login:', error)
        // Continue with redirect even if initialization fails
      }
      // Redirect to dashboard
      await navigateTo('/contacts')
    } else {
      // Authentication didn't work - show error
      loginError.value = 'Login successful but session not established. Please try again.'
      console.error('Auth check failed after 2FA login:', await authCheck.text())
    }
  } catch (error) {
    loginError.value = error.message || 'Invalid 2FA code'
    console.error('2FA login error:', error)
  } finally {
    isLoading.value = false
  }
}

const handlePasswordReset = async () => {
  isLoading.value = true
  resetError.value = ''
  resetMessage.value = ''
  
  try {
    const data = await apiCall('/auth/password-reset/request/', {
      method: 'POST',
      body: JSON.stringify({ email: resetEmail.value })
    }, 3, false) // Don't require auth for password reset
    
    resetMessage.value = data.message || 'If the email exists, a password reset link has been sent.'
  } catch (error) {
    resetError.value = error.message || 'Failed to send reset email'
    console.error('Password reset error:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

