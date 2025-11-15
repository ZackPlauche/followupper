<template>
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
            App created by <a href="https://www.zackplauche.com" target="_blank" rel="noopener noreferrer"
              class="text-emerald-400 hover:text-emerald-300 transition-colors">Zack Plauché</a>
          </span>
        </div>
      </div>
    </div>
  </footer>
</template>

