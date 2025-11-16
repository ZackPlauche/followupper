<template>
  <div class="bg-slate-800/30 border border-emerald-500/20 rounded-xl p-3" :class="mbClass">
    <h5 class="text-xs font-medium text-emerald-400 mb-2">Available Variables & Conditionals</h5>
    <div class="text-xs text-slate-300 space-y-2">
      <div><strong>Variables:</strong> {name}, {first_name}, {preferred_name}, {last_name}, {email}, {codementor_username}, {gender}, <span v-if="showFrequency">{frequency}, </span>{season}, {holiday}, {last_month}, {last_year}, {month}, {day}</div>
      <div><strong>Gender:</strong> {if_male:text}, {if_female:text}</div>
      <div v-if="showFrequency"><strong>Frequency:</strong> {if_frequency_daily:text}, {if_frequency_week:text}, {if_frequency_month:text}, {if_frequency_quarter:text}, {if_frequency_year:text}</div>
      <div><strong>Seasonal:</strong> {if_spring:text}, {if_summer:text}, {if_fall:text}, {if_winter:text}</div>
      <div><strong>Holiday:</strong> {if_holiday:text}, {if_christmas:text}, {if_halloween:text}, {if_thanksgiving:text}, {if_easter:text}, {if_newyear:text}</div>
      <div class="text-xs text-slate-400 mt-2 italic">Note: Conditionals can be nested, e.g., {if_holiday: Happy {holiday}!}</div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  showFrequency: {
    type: Boolean,
    default: true
  },
  mbClass: {
    type: String,
    default: 'mb-4'
  }
})
</script>

