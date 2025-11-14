// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/icon', '@nuxt/fonts', '@nuxt/image', '@nuxtjs/tailwindcss'],
  icon: {
    mode: 'svg',
  },
  css: ['~/assets/css/tailwind.css'],
  devServer: {
    port: 4000
  },
  tailwindcss: {
    exposeConfig: true,
    cssPath: '~/assets/css/tailwind.css',
    configPath: 'tailwind.config.js',
    viewer: true,
  },
  // For static site generation on Netlify
  nitro: {
    prerender: {
      crawlLinks: true
    }
  },
  runtimeConfig: {
    // Private keys (only available on server-side)
    // Public keys (exposed to client-side)
    public: {
      apiBase: import.meta.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8001/api'
    }
  }
})