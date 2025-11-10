<template>
  <div class="relative" ref="containerRef">
    <label v-if="label" :class="labelClass">{{ label }}</label>
    <div class="relative">
      <div class="flex flex-wrap gap-2 p-2 bg-slate-600/50 border border-emerald-500/30 rounded-lg min-h-[2.5rem]">
        <div v-for="platform in modelValue" :key="platform"
             class="flex items-center gap-1 px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded-md text-xs">
          <span>{{ platform === 'email' ? 'Email' : 'Codementor' }}</span>
          <button @click.stop="removePlatform(platform)"
                  class="hover:text-red-400 transition-colors">
            <Icon name="lucide:x" class="w-3 h-3" />
          </button>
        </div>
        <input 
          ref="inputRef"
          v-model="searchQuery"
          @keydown.enter.prevent="handleEnter"
          @keydown.escape="showDropdown = false"
          @focus="showDropdown = true"
          @input="showDropdown = true"
          @click.stop="showDropdown = true"
          type="text"
          :placeholder="placeholder"
          class="flex-1 min-w-[120px] bg-transparent border-none outline-none text-slate-100 text-xs placeholder-slate-400 cursor-text"
        />
        <Icon name="lucide:chevron-down" 
              class="w-4 h-4 text-slate-400 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none !text-slate-400"
              :class="{'rotate-180': showDropdown}" />
      </div>
      <div v-if="showDropdown && availablePlatformsFiltered.length > 0" 
           class="absolute z-50 w-full mt-1 bg-slate-700 border border-slate-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
        <button 
          v-for="platform in filteredPlatforms" 
          :key="platform"
          @click.stop="addPlatform(platform)"
          class="w-full text-left px-3 py-2 text-sm text-slate-100 hover:bg-slate-600 transition-colors">
          {{ platform === 'email' ? 'Email' : 'Codementor' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  availablePlatforms: {
    type: Array,
    required: true
  },
  label: {
    type: String,
    default: 'Platforms'
  },
  labelClass: {
    type: String,
    default: 'block text-xs font-light text-slate-300 mb-2'
  }
})

const emit = defineEmits(['update:modelValue'])

const containerRef = ref(null)
const inputRef = ref(null)
const searchQuery = ref('')
const showDropdown = ref(false)

const availablePlatformsFiltered = computed(() => {
  return props.availablePlatforms.filter(p => !props.modelValue.includes(p))
})

const filteredPlatforms = computed(() => {
  const query = searchQuery.value.toLowerCase()
  if (!query) return availablePlatformsFiltered.value
  return availablePlatformsFiltered.value.filter(p => {
    const name = p === 'email' ? 'email' : 'codementor'
    return name.includes(query)
  })
})

const placeholder = computed(() => {
  if (props.modelValue.length === 0) return 'Click to select platforms...'
  if (availablePlatformsFiltered.value.length === 0) return 'All platforms added'
  return 'Type to search...'
})

const addPlatform = (platform) => {
  if (!props.modelValue.includes(platform)) {
    const updated = [...props.modelValue, platform]
    emit('update:modelValue', updated)
    // Check if there are more platforms available after adding this one
    const remainingAvailable = props.availablePlatforms.filter(p => !updated.includes(p))
    // Only close dropdown if there are no more available platforms
    if (remainingAvailable.length === 0) {
      showDropdown.value = false
    }
    // Otherwise, keep it open (don't close it) - no need to refocus
  }
  searchQuery.value = ''
}

const removePlatform = (platform) => {
  const updated = props.modelValue.filter(p => p !== platform)
  emit('update:modelValue', updated)
}

const handleEnter = () => {
  if (searchQuery.value.trim() && filteredPlatforms.value.length > 0) {
    addPlatform(filteredPlatforms.value[0])
  }
}

// Close dropdown when clicking outside
let clickOutsideHandler = null

onMounted(() => {
  clickOutsideHandler = (e) => {
    setTimeout(() => {
      // Check if click is on a label (should close dropdown)
      if (e.target.tagName === 'LABEL') {
        showDropdown.value = false
        return
      }
      
      // Check if click is outside the input area
      if (containerRef.value) {
        const input = inputRef.value
        if (input && !input.contains(e.target) && !containerRef.value.querySelector('.absolute')?.contains(e.target)) {
          showDropdown.value = false
        }
      }
    }, 0)
  }
  document.addEventListener('click', clickOutsideHandler)
})

onUnmounted(() => {
  if (clickOutsideHandler) {
    document.removeEventListener('click', clickOutsideHandler)
  }
})
</script>

