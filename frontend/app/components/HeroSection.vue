<template>
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
      <div
        class="absolute bottom-20 right-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000">
      </div>
    </div>
  </section>
</template>

