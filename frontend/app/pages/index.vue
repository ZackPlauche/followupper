<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900">
    <!-- Home Page Navbar -->
    <header class="bg-slate-900/50 backdrop-blur-sm border-b border-emerald-500/20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <NuxtLink to="/" class="text-4xl font-thin gradient-title hover:opacity-80 transition-opacity">
            followupper
          </NuxtLink>
          <nav class="flex space-x-4 items-center">
            <NuxtLink to="/interest" 
                      class="px-6 py-3 rounded-xl font-light transition-all duration-300 hover:scale-105 text-slate-300 hover:text-emerald-400">
              Get Started
            </NuxtLink>
            <NuxtLink to="/login" 
                      class="px-6 py-3 rounded-xl font-light transition-all duration-300 hover:scale-105 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:shadow-lg">
              Sign In
            </NuxtLink>
          </nav>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="relative overflow-hidden">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
        <div class="text-center">
          <h1 class="text-6xl md:text-7xl font-thin gradient-title mb-6 animate-fade-in">
            followupper
          </h1>
          <p class="text-2xl md:text-3xl text-slate-300 font-light mb-8 max-w-3xl mx-auto">
            Never lose a client again. Automate your follow-ups and grow your business effortlessly.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <NuxtLink to="/interest"
              class="px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-xl font-light text-lg hover:shadow-2xl transition-all duration-300 hover:scale-105">
              Get Started
            </NuxtLink>
            <NuxtLink to="/login"
              class="px-8 py-4 bg-slate-800/50 backdrop-blur-sm border border-emerald-500/30 text-slate-300 rounded-xl font-light text-lg hover:border-emerald-500/50 transition-all duration-300">
              Sign In
            </NuxtLink>
          </div>
        </div>
      </div>
      
      <!-- Animated Background Elements -->
      <div class="absolute top-0 left-0 w-full h-full pointer-events-none">
        <div class="absolute top-20 left-10 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div class="absolute bottom-20 right-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-20 relative">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-4xl md:text-5xl font-thin gradient-title mb-4">
            Everything you need to stay connected
          </h2>
          <p class="text-xl text-slate-400 font-light max-w-2xl mx-auto">
            Powerful features designed to help you maintain relationships and grow your business
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <!-- Feature 1 -->
          <div class="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-emerald-500/20 hover:border-emerald-500/40 transition-all duration-300 hover:scale-105">
            <div class="w-16 h-16 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl flex items-center justify-center mb-6">
              <Icon name="lucide:users" class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-2xl font-thin text-slate-100 mb-3">Smart Contact Management</h3>
            <p class="text-slate-400 font-light">
              Organize all your contacts in one place. Track communication history, preferences, and never miss an important detail.
            </p>
          </div>

          <!-- Feature 2 -->
          <div class="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-emerald-500/20 hover:border-emerald-500/40 transition-all duration-300 hover:scale-105">
            <div class="w-16 h-16 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl flex items-center justify-center mb-6">
              <Icon name="lucide:message-square" class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-2xl font-thin text-slate-100 mb-3">Automated Follow-ups</h3>
            <p class="text-slate-400 font-light">
              Set up message sequences that send automatically. Schedule follow-ups, reminders, and keep your pipeline moving.
            </p>
          </div>

          <!-- Feature 3 -->
          <div class="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-emerald-500/20 hover:border-emerald-500/40 transition-all duration-300 hover:scale-105">
            <div class="w-16 h-16 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl flex items-center justify-center mb-6">
              <Icon name="lucide:mail" class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-2xl font-thin text-slate-100 mb-3">Multi-Platform Support</h3>
            <p class="text-slate-400 font-light">
              Send messages via Email and Codementor. Choose the right platform for each contact automatically.
            </p>
          </div>

          <!-- Feature 4 -->
          <div class="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-emerald-500/20 hover:border-emerald-500/40 transition-all duration-300 hover:scale-105">
            <div class="w-16 h-16 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl flex items-center justify-center mb-6">
              <Icon name="lucide:file-text" class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-2xl font-thin text-slate-100 mb-3">Message Templates</h3>
            <p class="text-slate-400 font-light">
              Create reusable templates with dynamic variables. Personalize messages at scale while maintaining authenticity.
            </p>
          </div>

          <!-- Feature 5 -->
          <div class="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-emerald-500/20 hover:border-emerald-500/40 transition-all duration-300 hover:scale-105">
            <div class="w-16 h-16 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl flex items-center justify-center mb-6">
              <Icon name="lucide:calendar" class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-2xl font-thin text-slate-100 mb-3">Campaign Management</h3>
            <p class="text-slate-400 font-light">
              Run targeted campaigns with multiple steps. Schedule messages, track engagement, and optimize your outreach.
            </p>
          </div>

          <!-- Feature 6 -->
          <div class="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-emerald-500/20 hover:border-emerald-500/40 transition-all duration-300 hover:scale-105">
            <div class="w-16 h-16 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl flex items-center justify-center mb-6">
              <Icon name="lucide:shield-check" class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-2xl font-thin text-slate-100 mb-3">Secure & Reliable</h3>
            <p class="text-slate-400 font-light">
              Your data is protected with industry-standard security. Two-factor authentication and encrypted connections.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-20 relative">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div class="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-12 border border-emerald-500/20">
          <h2 class="text-4xl md:text-5xl font-thin gradient-title mb-6">
            Ready to transform your follow-up process?
          </h2>
          <p class="text-xl text-slate-300 font-light mb-8">
            Join thousands of professionals who never lose a client again.
          </p>
          <NuxtLink to="/interest"
            class="inline-block px-8 py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-xl font-light text-lg hover:shadow-2xl transition-all duration-300 hover:scale-105">
            Get Started
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-emerald-500/20 py-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="text-slate-400 font-light mb-4 md:mb-0">
            © {{ new Date().getFullYear() }} followupper. All rights reserved.
          </div>
          <div class="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-6">
            <NuxtLink to="/login" class="text-slate-400 hover:text-emerald-400 font-light transition-colors">
              Sign In
            </NuxtLink>
            <span class="text-slate-500 text-sm">
              App created by <a href="https://www.zackplauche.com" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:text-emerald-300 transition-colors">Zack Plauché</a>
            </span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
useHead({
  title: 'Followupper - Never Lose a Client Again',
  meta: [
    { name: 'description', content: 'Automate your follow-ups and grow your business effortlessly with Followupper.' }
  ]
})
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 1s ease-out;
}

.delay-1000 {
  animation-delay: 1s;
}
</style>
