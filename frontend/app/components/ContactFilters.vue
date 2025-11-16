<template>
  <Transition name="filters">
    <div v-show="show"
      class="bg-slate-800/50 backdrop-blur-sm rounded-xl sm:rounded-2xl shadow-xl border border-emerald-500/20 mb-4 overflow-hidden">
      <div class="p-4 sm:p-6">
        <!-- Filter Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
          <!-- Platform Filter -->
          <div class="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30">
            <label class="block text-xs font-light text-emerald-400 mb-2 uppercase tracking-wider">Platform</label>
            <div class="space-y-2">
              <label class="flex items-center gap-2 cursor-pointer group">
                <input type="checkbox" v-model="localFilters.platform" value="email"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                <span class="text-slate-300 text-xs group-hover:text-slate-100 transition-colors">Email</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer group">
                <input type="checkbox" v-model="localFilters.platform" value="codementor"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                <span class="text-slate-300 text-xs group-hover:text-slate-100 transition-colors">Codementor</span>
              </label>
            </div>
          </div>

          <!-- Status Filter -->
          <div class="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30">
            <label class="block text-xs font-light text-emerald-400 mb-2 uppercase tracking-wider">Status</label>
            <select v-model="localFilters.status"
              class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          <!-- Source Filter -->
          <div class="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30">
            <label class="block text-xs font-light text-emerald-400 mb-2 uppercase tracking-wider">Source</label>
            <div class="space-y-2 max-h-32 overflow-y-auto pr-1">
              <label v-for="source in availableSources" :key="source || '__empty__'"
                class="flex items-center gap-2 cursor-pointer group">
                <input type="checkbox" v-model="localFilters.source" :value="source === '' ? '__empty__' : source"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                <span class="text-slate-300 text-xs group-hover:text-slate-100 transition-colors">{{ source || '(empty)'
                  }}</span>
              </label>
            </div>
          </div>

          <!-- Favorite Filter -->
          <div class="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30">
            <label class="block text-xs font-light text-emerald-400 mb-2 uppercase tracking-wider">Favorite</label>
            <select v-model="localFilters.favorite"
              class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
              <option value="">All</option>
              <option value="true">Favorites Only</option>
            </select>
          </div>

          <!-- Last Messaged Filter -->
          <div class="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30">
            <label class="block text-xs font-light text-emerald-400 mb-2 uppercase tracking-wider">Last Messaged</label>
            <select v-model="localFilters.lastMessaged"
              class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
              <option value="">All</option>
              <optgroup label="Contacted">
                <option value="never">Never</option>
                <option value="today">Today</option>
                <option value="last_7_days">Last 7 days</option>
                <option value="last_30_days">Last 30 days</option>
                <option value="last_90_days">Last 90 days</option>
                <option value="over_90_days">Over 90 days ago</option>
              </optgroup>
              <optgroup label="Not Contacted In">
                <option value="not_7_days">Not in last 7 days</option>
                <option value="not_30_days">Not in last 30 days</option>
                <option value="not_90_days">Not in last 90 days</option>
                <option value="not_6_months">Not in last 6 months</option>
                <option value="not_1_year">Not in last year</option>
              </optgroup>
            </select>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  filters: {
    type: Object,
    required: true
  },
  availableSources: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:filters'])

// Create a reactive copy of filters that we can modify
const localFilters = ref({
  search: props.filters?.search || '',
  platform: props.filters?.platform || [],
  status: props.filters?.status || '',
  source: props.filters?.source || [],
  favorite: props.filters?.favorite || '',
  lastMessaged: props.filters?.lastMessaged || ''
})

let isUpdatingFromProps = false

// Watch for prop changes and update local filters
watch(() => props.filters, (newFilters) => {
  if (newFilters && !isUpdatingFromProps) {
    isUpdatingFromProps = true
    localFilters.value = {
      search: newFilters.search || '',
      platform: newFilters.platform || [],
      status: newFilters.status || '',
      source: newFilters.source || [],
      favorite: newFilters.favorite || '',
      lastMessaged: newFilters.lastMessaged || ''
    }
    nextTick(() => {
      isUpdatingFromProps = false
    })
  }
}, { deep: true, immediate: true })

// Watch local filters and emit updates with debouncing for search
let debounceTimer = null
watch(localFilters, (newFilters) => {
  if (!isUpdatingFromProps) {
    // Debounce search input to avoid excessive filtering
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    
    // For search, debounce by 300ms; for others, emit immediately
    const isSearchChange = newFilters.search !== (props.filters?.search || '')
    const delay = isSearchChange ? 300 : 0
    
    debounceTimer = setTimeout(() => {
      emit('update:filters', { ...newFilters })
    }, delay)
  }
}, { deep: true })
</script>

<style scoped>
.filters-enter-active,
.filters-leave-active {
  transition: all 0.3s ease;
}

.filters-enter-from,
.filters-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
