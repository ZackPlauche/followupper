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

    <HeroSection />
    <FeaturesSection />
    <CTASection />
    <FooterSection />
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
