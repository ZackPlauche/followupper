<template>
  <div
    class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-5xl font-thin gradient-title mb-4">followupper</h1>
        <p class="text-slate-400 font-light">Express your interest</p>
      </div>

      <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Name</label>
            <input v-model="interestForm.name" type="text" required
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="Your name">
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Email</label>
            <input v-model="interestForm.email" type="email" required
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
              placeholder="you@example.com">
          </div>

          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Message (Optional)</label>
            <textarea v-model="interestForm.message" rows="4"
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
              placeholder="Tell us about your needs..."></textarea>
          </div>

          <div v-if="error" class="bg-red-500/20 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">
            {{ error }}
          </div>

          <div v-if="success"
            class="bg-emerald-500/20 border border-emerald-500/30 rounded-xl p-4 text-emerald-300 text-sm">
            {{ success }}
          </div>

          <button type="submit" :disabled="isLoading"
            class="w-full bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
            {{ isLoading ? 'Submitting...' : 'Submit Interest' }}
          </button>

          <div class="text-center">
            <p class="text-sm text-slate-400 font-light">
              Already have access?
              <NuxtLink to="/login" class="text-emerald-400 hover:text-emerald-300 transition-colors">
                Sign in
              </NuxtLink>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
useHead({
  title: 'Express Interest - Followupper'
})

const { apiCall } = useApiFetch()

const interestForm = ref({
  name: '',
  email: '',
  message: ''
})
const isLoading = ref(false)
const error = ref('')
const success = ref('')

const handleSubmit = async () => {
  isLoading.value = true
  error.value = ''
  success.value = ''

  try {
    const data = await apiCall('/auth/submit-interest/', {
      method: 'POST',
      body: JSON.stringify({
        name: interestForm.value.name,
        email: interestForm.value.email,
        message: interestForm.value.message
      })
    }, 3, false) // Don't require auth for interest submission

    // Redirect to thank you page
    await navigateTo(`/thank-you?name=${encodeURIComponent(interestForm.value.name)}`)
  } catch (err) {
    error.value = 'An error occurred. Please try again.'
    console.error('Interest form error:', err)
  } finally {
    isLoading.value = false
  }
}
</script>
