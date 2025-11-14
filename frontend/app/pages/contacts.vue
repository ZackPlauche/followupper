<template>
  <div>
    <div class="mb-8">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-3xl font-thin text-slate-100">Contacts</h2>
        <div class="flex gap-3">
          <button @click="showFilters = !showFilters"
            :class="['bg-slate-700/50 border text-slate-300 px-6 py-3 rounded-xl font-light hover:border-emerald-500/50 hover:text-emerald-400 transition-all duration-300', showFilters ? 'border-emerald-500/50 text-emerald-400' : 'border-emerald-500/30']">
            <Icon name="lucide:sliders-horizontal" class="w-5 h-5 inline mr-2" />
            Filters
            <span v-if="hasActiveFilters" class="ml-2 px-1.5 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-xs">
              {{ activeFilterCount }}
            </span>
          </button>
          <button v-if="selectedContactIds.size > 0" @click="openBulkEditModal"
            class="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105">
            Bulk Edit ({{ selectedContactIds.size }})
          </button>
          <button v-if="selectedContactIds.size > 0" @click="openBulkMessageModal"
            class="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105">
            Bulk Message ({{ selectedContactIds.size }})
          </button>
          <button v-if="selectedContactIds.size > 0" @click="handleBulkDelete"
            class="bg-gradient-to-r from-red-500 to-orange-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105">
            Bulk Delete ({{ selectedContactIds.size }})
          </button>
          <button @click="exportContacts"
            class="bg-slate-700/50 border border-emerald-500/30 text-slate-300 px-6 py-3 rounded-xl font-light hover:border-emerald-500/50 hover:text-emerald-400 transition-all duration-300">
            <Icon name="lucide:download" class="w-5 h-5 inline mr-2" />
            Export
          </button>
          <button @click="showImportModal = true"
            class="bg-slate-700/50 border border-emerald-500/30 text-slate-300 px-6 py-3 rounded-xl font-light hover:border-emerald-500/50 hover:text-emerald-400 transition-all duration-300">
            <Icon name="lucide:upload" class="w-5 h-5 inline mr-2" />
            Import
          </button>
          <button @click="showContactForm = true"
            class="bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-6 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105">
            + Add Contact
          </button>
        </div>
      </div>

      <!-- Filters Panel (Collapsible) -->
      <div v-show="showFilters" class="bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-xl border border-emerald-500/20 mb-4 overflow-hidden">
        <div class="p-6">
          <!-- Search Bar - Full Width -->
          <div class="mb-6">
            <label class="block text-sm font-light text-slate-300 mb-2">Search</label>
            <input v-model="filterSearch" type="text" placeholder="Search by name..."
              class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-4 py-2.5 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
          </div>

          <!-- Filter Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <!-- Platform Filter -->
          <div class="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30">
            <label class="block text-xs font-light text-emerald-400 mb-2 uppercase tracking-wider">Platform</label>
            <div class="space-y-2">
              <label class="flex items-center gap-2 cursor-pointer group">
                <input type="checkbox" v-model="filterPlatform" value="email"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                <span class="text-slate-300 text-xs group-hover:text-slate-100 transition-colors">Email</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer group">
                <input type="checkbox" v-model="filterPlatform" value="codementor"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                <span class="text-slate-300 text-xs group-hover:text-slate-100 transition-colors">Codementor</span>
              </label>
            </div>
          </div>

          <!-- Status Filter -->
          <div class="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30">
            <label class="block text-xs font-light text-emerald-400 mb-2 uppercase tracking-wider">Status</label>
            <select v-model="filterStatus"
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
              <label v-for="source in availableSources" :key="source || '__empty__'" class="flex items-center gap-2 cursor-pointer group">
                <input type="checkbox" v-model="filterSource" :value="source === '' ? '__empty__' : source"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                <span class="text-slate-300 text-xs group-hover:text-slate-100 transition-colors">{{ source || '(empty)' }}</span>
              </label>
            </div>
          </div>

          <!-- Favorite Filter -->
          <div class="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30">
            <label class="block text-xs font-light text-emerald-400 mb-2 uppercase tracking-wider">Favorite</label>
            <select v-model="filterFavorite"
              class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
              <option value="">All</option>
              <option value="true">Favorites Only</option>
            </select>
          </div>

          <!-- Last Messaged Filter -->
          <div class="bg-slate-700/30 rounded-lg p-3 border border-slate-600/30">
            <label class="block text-xs font-light text-emerald-400 mb-2 uppercase tracking-wider">Last Messaged</label>
            <select v-model="filterLastMessaged"
              class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
              <option value="">All</option>
              <option value="never">Never</option>
              <option value="today">Today</option>
              <option value="last_7_days">Last 7 days</option>
              <option value="last_30_days">Last 30 days</option>
              <option value="last_90_days">Last 90 days</option>
              <option value="over_90_days">Over 90 days ago</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Contacts List -->
    <div class="bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-emerald-500/20">
          <thead class="bg-slate-700/50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider w-12">
                <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
              </th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Name</th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Platforms
              </th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Status</th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Last Messaged
              </th>
              <th class="px-6 py-4 text-left text-xs font-light text-emerald-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-slate-800/30 divide-y divide-emerald-500/10">
            <tr v-for="contact in filteredContacts" :key="contact.id" class="hover:bg-slate-700/30 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <input type="checkbox" :checked="selectedContactIds.has(contact.id)"
                  @change="toggleContactSelection(contact.id)"
                  class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-light text-slate-100">
                <div class="flex items-center gap-2">
                  <button @click="toggleFavorite(contact)"
                    class="transition group"
                    :class="contact.is_favorite ? '' : 'opacity-30 hover:opacity-100'">
                    <Icon :name="contact.is_favorite ? 'mdi:star' : 'mdi:star-outline'" class="w-4 h-4 text-yellow-400 group-hover:text-yellow-300" />
                  </button>
                  <button @click="openContactProfile(contact)"
                    class="hover:text-emerald-400 transition-colors cursor-pointer">
                    {{ contact.name }}
                  </button>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-3">
                  <div class="flex items-center gap-1.5" :class="contact.email ? '' : 'opacity-40'">
                    <Icon name="lucide:mail" class="w-4 h-4"
                      :class="contact.email ? 'text-slate-300' : 'text-slate-500'" />
                  </div>
                  <div class="flex items-center gap-1.5" :class="contact.codementor_username ? '' : 'opacity-40'">
                    <Icon name="simple-icons:codementor" class="w-4 h-4"
                      :class="contact.codementor_username ? 'text-slate-300' : 'text-slate-500'" />
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="contact.is_active ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'"
                  class="inline-flex px-3 py-1 text-xs font-light rounded-full">
                  {{ contact.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-light text-slate-300">
                {{ formatLastMessaged(contact.last_messaged) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-light">
                <button @click="openQuickSendModal(contact)"
                  class="text-blue-400 hover:text-blue-300 mr-4 transition-colors">Send</button>
                <button @click="editContact(contact)"
                  class="text-emerald-400 hover:text-emerald-300 mr-4 transition-colors">Edit</button>
                <button @click="handleDeleteContact(contact.id)"
                  class="text-red-400 hover:text-red-300 transition-colors">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Contact Form Modal -->
    <div v-if="showContactForm"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div
        class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 w-full max-w-md max-h-[90vh] flex flex-col">
        <div class="p-6 border-b border-slate-700/50">
          <h3 class="text-2xl font-thin text-slate-100">Add Contact</h3>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <form @submit.prevent="handleSaveContact" class="space-y-3">
            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Name *</label>
              <input v-model="newContact.name" type="text" required
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Preferred Name</label>
              <input v-model="newContact.preferred_name" type="text"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                placeholder="Leave blank to use first name">
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Gender</label>
              <div class="flex items-center bg-slate-700/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                <button type="button" @click="newContact.gender = ''"
                  :class="newContact.gender === '' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                  Not specified
                </button>
                <button type="button" @click="newContact.gender = 'male'"
                  :class="newContact.gender === 'male' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                  Male
                </button>
                <button type="button" @click="newContact.gender = 'female'"
                  :class="newContact.gender === 'female' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                  Female
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Email</label>
              <input v-model="newContact.email" type="email"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Codementor Username</label>
              <input v-model="newContact.codementor_username" type="text"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>

            <div>
              <PlatformMultiSelect v-model="newContact.platform_preference" :available-platforms="availablePlatforms"
                label="Platform Preference" />
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Timezone</label>
              <select v-model="newContact.timezone"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time (ET)</option>
                <option value="America/Chicago">Central Time (CT)</option>
                <option value="America/Denver">Mountain Time (MT)</option>
                <option value="America/Los_Angeles">Pacific Time (PT)</option>
                <option value="Europe/London">London (GMT)</option>
                <option value="Europe/Paris">Paris (CET)</option>
                <option value="Asia/Tokyo">Tokyo (JST)</option>
                <option value="Asia/Shanghai">Shanghai (CST)</option>
                <option value="Australia/Sydney">Sydney (AEST)</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Notes</label>
              <textarea v-model="newContact.notes" rows="3"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"></textarea>
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Source</label>
              <input v-model="newContact.source" type="text"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                placeholder="e.g., manual, codementor, csv">
            </div>
          </form>
        </div>

        <div class="p-6 border-t border-slate-700/50 flex space-x-3">
          <button type="button" @click="showContactForm = false"
            class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-2 rounded-lg text-sm font-light hover:bg-slate-600/70 transition-colors">
            Cancel
          </button>
          <button @click="handleSaveContact"
            class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-2 rounded-lg text-sm font-light hover:shadow-lg transition-all duration-300">
            Save Contact
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Contact Form Modal -->
    <div v-if="showEditContactForm"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div
        class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 w-full max-w-md max-h-[90vh] flex flex-col">
        <div class="p-6 border-b border-slate-700/50">
          <h3 class="text-2xl font-thin text-slate-100">Edit Contact</h3>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <form @submit.prevent="handleUpdateContact" class="space-y-3">
            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Name *</label>
              <input v-model="newContact.name" type="text" required
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Preferred Name</label>
              <input v-model="newContact.preferred_name" type="text"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                placeholder="Leave blank to use first name">
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Gender</label>
              <div class="flex items-center bg-slate-700/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                <button type="button" @click="newContact.gender = ''"
                  :class="newContact.gender === '' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                  Not specified
                </button>
                <button type="button" @click="newContact.gender = 'male'"
                  :class="newContact.gender === 'male' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                  Male
                </button>
                <button type="button" @click="newContact.gender = 'female'"
                  :class="newContact.gender === 'female' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                  Female
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Email</label>
              <input v-model="newContact.email" type="email"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Codementor Username</label>
              <input v-model="newContact.codementor_username" type="text"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>

            <div>
              <PlatformMultiSelect v-model="newContact.platform_preference" :available-platforms="availablePlatforms"
                label="Platform Preference" />
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Timezone</label>
              <select v-model="newContact.timezone"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time (ET)</option>
                <option value="America/Chicago">Central Time (CT)</option>
                <option value="America/Denver">Mountain Time (MT)</option>
                <option value="America/Los_Angeles">Pacific Time (PT)</option>
                <option value="Europe/London">London (GMT)</option>
                <option value="Europe/Paris">Paris (CET)</option>
                <option value="Asia/Tokyo">Tokyo (JST)</option>
                <option value="Asia/Shanghai">Shanghai (CST)</option>
                <option value="Australia/Sydney">Sydney (AEST)</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Notes</label>
              <textarea v-model="newContact.notes" rows="3"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"></textarea>
            </div>

            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Source</label>
              <input v-model="newContact.source" type="text"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                placeholder="e.g., manual, codementor, csv">
            </div>
          </form>
        </div>

        <div class="p-6 border-t border-slate-700/50 flex space-x-3">
          <button type="button" @click="showEditContactForm = false"
            class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-2 rounded-lg text-sm font-light hover:bg-slate-600/70 transition-colors">
            Cancel
          </button>
          <button @click="handleUpdateContact"
            class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-2 rounded-lg text-sm font-light hover:shadow-lg transition-all duration-300">
            Update Contact
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Send Modal -->
    <div v-if="showQuickSendModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div
        class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 w-full max-w-md max-h-[90vh] flex flex-col">
        <div class="p-6 border-b border-slate-700/50 flex items-center justify-between">
          <h3 class="text-2xl font-thin text-slate-100">Send Message to {{ selectedContact?.name }}</h3>
          <button @click="closeQuickSendModal" class="text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="material-symbols:close" class="w-6 h-6" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <div class="space-y-3">
            <!-- Mode Toggle -->
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-lg font-light text-slate-100">{{ quickSendIsChainMode ? 'Send Message Chain' : 'Send Message' }}</h4>
              <div class="flex items-center bg-slate-700/50 rounded-lg p-1 border border-slate-500/30">
                <button type="button" @click="quickSendIsChainMode = false"
                  :class="!quickSendIsChainMode ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="flex items-center px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                  <Icon name="fa:send" class="w-4 h-4" />
                </button>
                <button type="button" @click="handleQuickSendChainModeToggle"
                  :class="quickSendIsChainMode ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="flex items-center space-x-2 px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                  <Icon name="mage:link" class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Single Message Mode -->
            <div v-if="!quickSendIsChainMode" class="space-y-3">
              <!-- Template Selection -->
              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Template (optional)</label>
                <select v-model="quickSendSelectedTemplate" @change="applyQuickSendTemplate"
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
                  <option value="">None</option>
                  <option v-for="template in activeTemplates" :key="template.id" :value="template.id">{{ template.name
                    }}</option>
                </select>
              </div>

              <!-- Subject (only for email) -->
              <div v-if="quickSendMessage.platforms.includes('email')">
                <label class="block text-sm font-light text-slate-300 mb-1">Subject *</label>
                <input v-model="quickSendMessage.subject" type="text" required
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                  placeholder="Message subject">
              </div>

              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Message *</label>
                <textarea v-model="quickSendMessage.body" rows="5" required
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                  placeholder="Enter your message here..."></textarea>
              </div>

              <!-- Platform Selection -->
              <PlatformMultiSelect v-model="quickSendMessage.platforms"
                :available-platforms="quickSendAvailablePlatforms" label="Platforms"
                label-class="block text-sm font-light text-slate-300 mb-1" />

              <div v-if="quickSendMessage.schedule" class="space-y-3">
                <div class="flex items-end gap-3">
                  <div class="flex-1">
                    <label class="block text-xs font-light text-slate-300 mb-1">Send Date</label>
                    <input v-model="quickSendMessage.send_date" type="date"
                      class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                  </div>
                  <div class="flex-1">
                    <label class="block text-xs font-light text-slate-300 mb-1">Send Time</label>
                    <input v-model="quickSendMessage.send_time" type="time"
                      class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                  </div>
                  <div>
                    <label class="block text-xs font-light text-slate-300 mb-1">Timezone</label>
                    <div class="flex items-center bg-slate-600/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                      <button type="button" @click="quickSendMessage.timezone = 'my'"
                        :class="quickSendMessage.timezone === 'my' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                        class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                        Mine
                      </button>
                      <button type="button" @click="quickSendMessage.timezone = 'user'"
                        :class="quickSendMessage.timezone === 'user' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                        class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                        Contact
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Chain Mode -->
            <div v-else class="space-y-4">
              <!-- Global Chain Settings -->
              <!-- Subject (only for email) -->
              <div v-if="quickSendChainSettings.platforms.includes('email')">
                <label class="block text-sm font-light text-slate-300 mb-1">Subject (applies to all messages) *</label>
                <input v-model="quickSendChainSubject" type="text" required
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors"
                  placeholder="Message subject">
              </div>

              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Footer/Signature (applies to all
                  messages)</label>
                <textarea v-model="quickSendChainFooter" rows="3"
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                  placeholder="Message footer"></textarea>
              </div>

              <!-- Platform Selection -->
              <PlatformMultiSelect v-model="quickSendChainSettings.platforms"
                :available-platforms="quickSendAvailablePlatforms" label="Platforms"
                label-class="block text-sm font-light text-slate-300 mb-1" />

              <!-- Chain Timing Settings -->
              <div class="space-y-3">
                <div>
                  <label class="block text-sm font-light text-slate-300 mb-1">Timing Type</label>
                  <div class="flex items-center bg-slate-700/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                    <button type="button" @click="quickSendChainSettings.timingType = 'interval'"
                      :class="quickSendChainSettings.timingType === 'interval' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                      class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                      Interval
                    </button>
                    <button type="button" @click="quickSendChainSettings.timingType = 'specific'"
                      :class="quickSendChainSettings.timingType === 'specific' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                      class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                      Specific
                    </button>
                  </div>
                </div>

                <div v-if="quickSendChainSettings.timingType === 'interval'" class="space-y-2">
                  <div class="flex items-center space-x-2">
                    <input type="checkbox" v-model="quickSendChainSettings.sendFirstImmediately"
                      id="quick-send-first-immediately"
                      class="w-4 h-4 rounded border-emerald-500/30 bg-slate-600/50 text-emerald-500 focus:ring-emerald-500 focus:ring-2">
                    <label for="quick-send-first-immediately" class="text-xs text-slate-300 cursor-pointer">Send first
                      message immediately</label>
                  </div>

                  <div class="space-y-2">
                    <div class="flex items-end gap-2">
                      <div class="flex-1">
                        <label class="block text-xs font-light text-slate-300 mb-1">Start Date</label>
                        <input v-model="quickSendChainSettings.startDate" type="date"
                          class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                      </div>
                      <div class="flex-1">
                        <label class="block text-xs font-light text-slate-300 mb-1">Start Time</label>
                        <input v-model="quickSendChainSettings.startTime" type="time"
                          class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                      </div>
                      <div>
                        <label class="block text-xs font-light text-slate-300 mb-1">Timezone</label>
                        <div class="flex items-center bg-slate-600/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                          <button type="button" @click="quickSendChainSettings.timezone = 'my'"
                            :class="quickSendChainSettings.timezone === 'my' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                            class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                            Mine
                          </button>
                          <button type="button" @click="quickSendChainSettings.timezone = 'user'"
                            :class="quickSendChainSettings.timezone === 'user' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                            class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                            Contact
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-for="(message, index) in quickSendMessageChain" :key="index"
                class="bg-slate-600/30 rounded-lg p-4 border border-slate-500/20">
                <div class="flex items-start justify-between mb-3">
                  <h5 class="text-sm font-medium text-slate-200">Message {{ index + 1 }}</h5>
                  <button type="button" @click="removeQuickSendMessageFromChain(index)"
                    class="text-slate-400 hover:text-red-400 transition-colors">
                    <Icon name="lucide:trash-2" class="w-4 h-4" />
                  </button>
                </div>

                <div class="space-y-3">
                  <div>
                    <label class="block text-xs font-light text-slate-300 mb-1">Message *</label>
                    <textarea v-model="message.body" rows="4" required
                      class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                      placeholder="Enter your message here..."></textarea>
                  </div>

                  <!-- Interval Mode -->
                  <div v-if="quickSendChainSettings.timingType === 'interval' && index > 0">
                    <label class="block text-xs font-light text-slate-300 mb-1">
                      Days after previous message
                    </label>
                    <input v-model.number="message.frequency_days" type="number" min="0" step="1"
                      class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors"
                      placeholder="0 = send immediately after previous">
                  </div>

                  <!-- Specific Date/Time Mode -->
                  <div v-else-if="quickSendChainSettings.timingType === 'specific'" class="space-y-2">
                    <div class="flex items-end gap-2">
                      <div class="flex-1">
                        <label class="block text-xs font-light text-slate-300 mb-1">Send Date</label>
                        <input v-model="message.send_date" type="date"
                          class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                      </div>
                      <div class="flex-1">
                        <label class="block text-xs font-light text-slate-300 mb-1">Send Time</label>
                        <input v-model="message.send_time" type="time"
                          class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                      </div>
                      <div>
                        <label class="block text-xs font-light text-slate-300 mb-1">Timezone</label>
                        <div class="flex items-center bg-slate-600/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                          <button type="button" @click="message.timezone = 'my'"
                            :class="message.timezone === 'my' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                            class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                            Mine
                          </button>
                          <button type="button" @click="message.timezone = 'user'"
                            :class="message.timezone === 'user' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                            class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                            Contact
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <button type="button" @click="addQuickSendMessageToChain"
                class="w-full py-2 border-2 border-dashed border-emerald-500/30 rounded-lg text-emerald-300 hover:border-emerald-500/50 hover:bg-emerald-500/10 transition-colors flex items-center justify-center">
                <Icon name="lucide:plus" class="w-4 h-4 mr-2" />
                Add Another Message
              </button>
            </div>
          </div>
        </div>

        <div class="p-6 border-t border-slate-700/50 flex space-x-3">
          <button type="button" @click="closeQuickSendModal"
            class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-2 rounded-lg text-sm font-light hover:bg-slate-600/70 transition-colors">
            Cancel
          </button>
          <button @click="handleQuickSend"
            class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-2 rounded-lg text-sm font-light hover:shadow-lg transition-all duration-300">
            {{ quickSendMessage.schedule ? 'Schedule' : 'Send' }}
          </button>
          <button @click="quickSendMessage.schedule = !quickSendMessage.schedule"
            class="px-3 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg text-sm font-light hover:shadow-lg transition-all duration-300">
            <Icon name="material-symbols:schedule-send" class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Status Bar -->
    <div v-if="showStatusBar"
      class="fixed bottom-6 right-6 bg-slate-800/90 backdrop-blur-sm rounded-xl shadow-2xl border border-emerald-500/20 overflow-hidden transition-all duration-300 z-[60]">
      <div class="px-6 py-3 text-sm text-slate-300 font-light">
        <div class="flex items-center space-x-3">
          <div class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
          <span>{{ statusMessage }}</span>
        </div>
      </div>
      <!-- Progress Bar -->
      <div class="h-1 bg-slate-700/50">
        <div class="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all duration-100 ease-linear"
          :style="{ width: statusProgress + '%' }"></div>
      </div>
    </div>

    <!-- Bulk Edit Modal -->
    <div v-if="showBulkEditModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div
        class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex justify-between items-center p-6 border-b border-slate-700/50 flex-shrink-0">
          <h3 class="text-2xl font-thin text-slate-100">Bulk Edit ({{ selectedContactIds.size }} contacts)</h3>
          <button @click="closeBulkEditModal" class="text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="lucide:x" class="w-6 h-6" />
          </button>
        </div>

        <!-- Scrollable Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <div class="space-y-4">
            <p class="text-sm text-slate-400 mb-4">Edit fields for all selected contacts. Leave fields empty to keep existing values.</p>

            <!-- Platform Preference -->
            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">Platform Preference</label>
              <div class="flex gap-4">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" v-model="bulkEditData.platform_preference" value="email"
                    class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                  <span class="text-slate-300 text-sm">Email</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" v-model="bulkEditData.platform_preference" value="codementor"
                    class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                  <span class="text-slate-300 text-sm">Codementor</span>
                </label>
              </div>
              <p class="text-xs text-slate-500 mt-1">Leave unchecked to keep existing preferences</p>
            </div>

            <!-- Timezone -->
            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Timezone</label>
              <select v-model="bulkEditData.timezone"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
                <option value="">Keep existing</option>
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time (ET)</option>
                <option value="America/Chicago">Central Time (CT)</option>
                <option value="America/Denver">Mountain Time (MT)</option>
                <option value="America/Los_Angeles">Pacific Time (PT)</option>
                <option value="Europe/London">London (GMT)</option>
                <option value="Europe/Paris">Paris (CET)</option>
                <option value="Asia/Tokyo">Tokyo (JST)</option>
                <option value="Asia/Shanghai">Shanghai (CST)</option>
                <option value="Australia/Sydney">Sydney (AEST)</option>
              </select>
            </div>

            <!-- Status -->
            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Status</label>
              <select v-model="bulkEditData.is_active"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
                <option :value="null">Keep existing</option>
                <option :value="true">Active</option>
                <option :value="false">Inactive</option>
              </select>
            </div>

            <!-- Source -->
            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Source</label>
              <input v-model="bulkEditData.source" type="text"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                placeholder="Leave empty to keep existing">
            </div>

            <!-- Favorite -->
            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Favorite</label>
              <select v-model="bulkEditData.is_favorite"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
                <option :value="null">Keep existing</option>
                <option :value="true">Mark as favorite</option>
                <option :value="false">Remove favorite</option>
              </select>
            </div>

            <!-- Gender -->
            <div>
              <label class="block text-sm font-light text-slate-300 mb-1">Gender</label>
              <div class="flex items-center bg-slate-700/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                <button type="button" @click="bulkEditData.gender = ''"
                  :class="bulkEditData.gender === '' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                  Not specified
                </button>
                <button type="button" @click="bulkEditData.gender = 'male'"
                  :class="bulkEditData.gender === 'male' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                  Male
                </button>
                <button type="button" @click="bulkEditData.gender = 'female'"
                  :class="bulkEditData.gender === 'female' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                  Female
                </button>
              </div>
              <p class="text-xs text-slate-500 mt-1">Click "Not specified" to keep existing</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex space-x-3 p-6 border-t border-slate-700/50 flex-shrink-0">
          <button @click="closeBulkEditModal"
            class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
            Cancel
          </button>
          <button @click="handleBulkEdit"
            class="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
            Update {{ selectedContactIds.size }} Contact{{ selectedContactIds.size !== 1 ? 's' : '' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Bulk Message Modal -->
    <div v-if="showBulkMessageModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div
        class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 w-full max-w-6xl max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex justify-between items-center p-6 border-b border-slate-700/50 flex-shrink-0">
          <h3 class="text-2xl font-thin text-slate-100">Bulk Message ({{ selectedContactIds.size }} contacts)</h3>
          <button @click="closeBulkMessageModal" class="text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="lucide:x" class="w-6 h-6" />
          </button>
        </div>

        <!-- Scrollable Content -->
        <div class="flex-1 flex gap-6 overflow-y-auto p-6 min-h-0">
          <!-- Left: Message Composition -->
          <div class="flex-1 space-y-4">
            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">
                Platforms *
                <span class="text-xs text-slate-500 ml-2">(Available for selected contacts)</span>
              </label>
              <div class="space-y-3">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" v-model="bulkMessage.usePreferredPlatforms"
                    class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                  <span class="text-slate-300 text-sm">Use each contact's preferred platforms</span>
                </label>
                <div v-if="!bulkMessage.usePreferredPlatforms" class="flex gap-4">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" v-model="bulkMessage.platforms" value="email"
                      class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                    <span class="text-slate-300 text-sm">Email</span>
                  </label>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" v-model="bulkMessage.platforms" value="codementor"
                      class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                    <span class="text-slate-300 text-sm">Codementor</span>
                  </label>
                </div>
              </div>
            </div>

            <div>
              <label class="block text-xs font-light text-slate-300 mb-1">Template (optional)</label>
              <select v-model="bulkSelectedTemplate" @change="applyBulkTemplate"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
                <option value="">None</option>
                <option v-for="template in activeTemplates" :key="template.id" :value="template.id">{{ template.name }}
                </option>
              </select>
            </div>

            <div v-if="bulkMessage.usePreferredPlatforms || bulkMessage.platforms.includes('email')">
              <label class="block text-xs font-light text-slate-300 mb-1">
                Subject *
                <span class="text-xs text-slate-500 ml-2">Variables: {name}, {first_name}, {preferred_name},
                  {last_name}, {email}, {gender}. Conditionals: {if_male:text}{if_female:text}</span>
              </label>
              <input v-model="bulkMessage.subject" type="text" required
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                placeholder="Hello {first_name}!" />
            </div>

            <div>
              <label class="block text-xs font-light text-slate-300 mb-1">
                Message Body *
                <span class="text-xs text-slate-500 ml-2">Variables: {name}, {first_name}, {preferred_name},
                  {last_name}, {email}, {codementor_username}, {gender}. Conditionals:
                  {if_male:text}{if_female:text}</span>
              </label>
              <textarea v-model="bulkMessage.body" rows="8" required
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                placeholder="Hi {first_name}, ..."></textarea>
            </div>
          </div>

          <!-- Right: Preview Section -->
          <div class="w-96 border-l border-slate-700/50 pl-6 flex-shrink-0">
            <h4 class="text-lg font-light text-slate-100 mb-4">Preview</h4>

            <!-- Message Preview -->
            <div class="bg-slate-700/30 rounded-lg p-4 border border-slate-600/30 mb-4">
              <div v-if="bulkMessage.subject" class="text-xs text-slate-400 mb-2">
                <strong>Subject:</strong> {{ getPreviewText(bulkMessage.subject, {
                  name: 'John Doe', preferred_name:
                    'Johnny', first_name: 'Johnny', last_name: 'Doe', gender: 'male', email: 'john.doe@example.com',
                codementor_username: 'johndoe' }) }}
              </div>
              <div v-if="bulkMessage.body.trim()" class="text-sm text-slate-300 whitespace-pre-wrap">
                {{ getPreviewText(bulkMessage.body, {
                  name: 'John Doe', preferred_name: 'Johnny', first_name: 'Johnny',
                  last_name: 'Doe', gender: 'male', email: 'john.doe@example.com', codementor_username: 'johndoe' }) }}
              </div>
              <div v-else class="text-sm text-slate-500 italic">
                (No message body yet)
              </div>
            </div>

            <!-- User Data Section -->
            <div class="bg-slate-800/30 border border-emerald-500/20 rounded-xl p-3">
              <h5 class="text-sm font-light text-emerald-400 mb-2">Preview Data</h5>
              <div class="text-xs text-slate-300 space-y-1">
                <div><strong>Name:</strong> John Doe</div>
                <div><strong>Preferred Name:</strong> Johnny</div>
                <div><strong>Gender:</strong> Male</div>
                <div><strong>Email:</strong> john.doe@example.com</div>
                <div><strong>Codementor:</strong> johndoe</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex space-x-3 p-6 border-t border-slate-700/50 flex-shrink-0">
          <button @click="handleBulkSend" :disabled="!canSendBulkMessage"
            class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
            Send to {{ selectedContactIds.size }} Contact{{ selectedContactIds.size !== 1 ? 's' : '' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Contact Profile Modal -->
    <ContactProfile v-if="showContactProfileModal && selectedContact" :contact="selectedContact"
      :upcoming-messages="upcomingMessages" :is-modal="true" @close="closeContactProfileModal"
      @update="handleContactUpdate" @send-message="handleSendMessage" />

    <!-- Import Modal -->
    <div v-if="showImportModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 w-full max-w-md">
        <div class="p-6 border-b border-slate-700/50 flex justify-between items-center">
          <h3 class="text-2xl font-thin text-slate-100">Import Contacts</h3>
          <button @click="showImportModal = false" class="text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="lucide:x" class="w-6 h-6" />
          </button>
        </div>
        <div class="p-6">
          <div class="mb-4 flex items-center gap-2">
            <label class="text-sm text-slate-300 font-light">Select CSV File</label>
            <button @click="showImportInstructions = !showImportInstructions"
              class="text-slate-400 hover:text-emerald-400 transition-colors">
              <Icon name="lucide:info" class="w-4 h-4" />
            </button>
          </div>
          <div v-if="showImportInstructions" class="mb-4 p-4 bg-slate-700/30 rounded-xl border border-slate-600/50">
            <p class="text-sm text-slate-300 mb-2 font-light">CSV Format Instructions:</p>
            <ul class="text-xs text-slate-400 space-y-1 list-disc list-inside font-light">
              <li><strong class="text-slate-300">Required:</strong> Name</li>
              <li><strong class="text-slate-300">Optional:</strong> Preferred Name, Email, Codementor Username, Gender,
                Timezone, Notes, Is Active, Platform Preference</li>
              <li>First row must be headers: <code
                  class="text-emerald-400">Name, Email, Codementor Username, Preferred Name, Gender, Timezone, Notes, Is Active, Platform Preference</code>
              </li>
              <li>Platform Preference: comma-separated list (e.g., <code
                  class="text-emerald-400">email, codementor</code>)</li>
              <li>Is Active: <code class="text-emerald-400">true</code> or <code class="text-emerald-400">false</code>
                (defaults to true)</li>
            </ul>
          </div>
          <input type="file" accept=".csv" @change="handleFileSelect"
            class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 mb-4">
          <div v-if="importStatus" class="mb-4 p-4 rounded-xl text-sm"
            :class="importStatus.includes('Error') ? 'bg-red-500/20 text-red-300' : 'bg-emerald-500/20 text-emerald-300'">
            {{ importStatus }}
          </div>
          <div class="flex space-x-3">
            <button @click="showImportModal = false"
              class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
              Cancel
            </button>
            <button @click="handleImport" :disabled="!importFile"
              class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
              Import
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
// Set page title
useHead({
  title: 'Contacts - Followupper'
})

// Use shared API state
const { contacts, campaigns, templates, createContact, updateContact, deleteContact, loadContacts, sendEmail, sendMessage, showStatusWithProgress, settings } = useApi()
const { apiCall, apiFetch } = useApiFetch()

// Available platforms for new contact (based on what they've entered)
const availablePlatforms = computed(() => {
  const platforms = []
  if (newContact.value.email) platforms.push('email')
  if (newContact.value.codementor_username) platforms.push('codementor')
  return platforms
})

// Local UI state
const statusMessage = ref('Loading...')
const showStatusBar = ref(false)
const statusTimer = ref(null)
const statusProgress = ref(100)
const showContactForm = ref(false)
const showEditContactForm = ref(false)
const editingContact = ref(null)
const showQuickSendModal = ref(false)
const selectedContact = ref(null)
const showContactProfileModal = ref(false)
const upcomingMessages = ref([])
const selectedContactIds = ref(new Set())
const showImportModal = ref(false)
const importFile = ref(null)
const importStatus = ref('')
const showImportInstructions = ref(false)
const showBulkMessageModal = ref(false)
const showBulkEditModal = ref(false)
const bulkMessage = ref({
  platforms: [],
  usePreferredPlatforms: false,
  subject: '',
  body: ''
})
const bulkSelectedTemplate = ref('')
const bulkEditData = ref({
  platform_preference: [],
  timezone: '',
  is_active: null,
  source: '',
  is_favorite: null,
  gender: ''
})

// Filter visibility
const showFilters = ref(true)

// Filters
const filterSearch = ref('')
const filterPlatform = ref([])
const filterStatus = ref('')
const filterSource = ref([])
const filterFavorite = ref('')
const filterLastMessaged = ref('')

// Form data
const newContact = ref({
  name: '',
  preferred_name: '',
  gender: '',
  email: '',
  codementor_username: '',
  platform_preference: [],
  timezone: 'UTC',
  notes: '',
  source: '',
  is_favorite: false
})

const quickSendMessage = ref({
  platforms: [],
  subject: '',
  body: '',
  send_date: '',
  send_time: '',
  schedule: false,
  timezone: 'my'
})
const quickSendIsChainMode = ref(false)
const quickSendMessageChain = ref([])
const quickSendChainSubject = ref('')
const quickSendChainFooter = ref('')
const quickSendSelectedTemplate = ref('')
const quickSendChainSettings = ref({
  platforms: [],
  sendFirstImmediately: false,
  timingType: 'interval',
  startDate: '',
  startTime: '09:00',
  timezone: 'my'
})

const activeTemplates = computed(() => {
  return templates.value.filter(t => t.is_active)
})

const applyQuickSendTemplate = () => {
  if (!quickSendSelectedTemplate.value) return
  const template = templates.value.find(t => t.id === parseInt(quickSendSelectedTemplate.value))
  if (template) {
    if (template.subject) {
      quickSendMessage.value.subject = template.subject
    }
    if (template.body) {
      quickSendMessage.value.body = template.body
      // For email, append footer: template footer if exists, otherwise user settings footer
      if (quickSendMessage.value.platforms.includes('email')) {
        const footerToUse = template.footer || settings.value?.user?.footer || ''
        if (footerToUse) {
          quickSendMessage.value.body = quickSendMessage.value.body + '\n\n' + footerToUse
        }
      }
    }
  }
}

const applyBulkTemplate = () => {
  if (!bulkSelectedTemplate.value) return
  const template = templates.value.find(t => t.id === parseInt(bulkSelectedTemplate.value))
  if (template) {
    if (template.subject) {
      bulkMessage.value.subject = template.subject
    }
    if (template.body) {
      bulkMessage.value.body = template.body
    }
  }
}

// Enhanced status helper with progress bar
const showStatusWithProgressLocal = (message, duration = 5000) => {
  statusMessage.value = message
  showStatusBar.value = true
  statusProgress.value = 100

  // Clear existing timer
  if (statusTimer.value) {
    clearTimeout(statusTimer.value)
  }

  // Animate progress bar
  const progressInterval = setInterval(() => {
    statusProgress.value -= 2 // 100% / 50 intervals = 2% per interval
    if (statusProgress.value <= 0) {
      clearInterval(progressInterval)
    }
  }, duration / 50) // 50 intervals over the duration

  // Set new timer
  statusTimer.value = setTimeout(() => {
    showStatusBar.value = false
    statusTimer.value = null
    clearInterval(progressInterval)
  }, duration)
}


const editContact = (contact) => {
  editingContact.value = contact
  newContact.value = { ...contact }
  showEditContactForm.value = true
}

const handleDeleteContact = async (contactId) => {
  // Instant UI update
  contacts.value = contacts.value.filter(c => c.id !== contactId)

  // Background API call
  try {
    await deleteContact(contactId)
    showStatusWithProgressLocal('Contact deleted successfully', 5000)
  } catch (error) {
    console.error('Error deleting contact:', error)
    // Revert on error
    await loadContacts()
    showStatusWithProgressLocal('Error deleting contact', 5000)
  }
}

const handleSaveContact = async () => {
  // Store the contact data before clearing the form
  const contactData = { ...newContact.value }

  // Instant UI update
  const tempId = Date.now() // Temporary ID
  const newContactData = {
    id: tempId,
    ...contactData,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }

  contacts.value.push(newContactData)
  showContactForm.value = false
  newContact.value = { name: '', preferred_name: '', gender: '', email: '', codementor_username: '', platform_preference: [], timezone: 'UTC', notes: '', source: '', is_favorite: false }

  // Background API call
  try {
    const result = await createContact(contactData)
    // Update with real ID
    const index = contacts.value.findIndex(c => c.id === tempId)
    if (index !== -1) {
      contacts.value[index].id = result.id
    }
    showStatusWithProgressLocal('Contact created successfully', 5000)
  } catch (error) {
    console.error('Error saving contact:', error)
    // Revert on error
    contacts.value = contacts.value.filter(c => c.id !== tempId)
    showStatusWithProgressLocal('Error creating contact', 5000)
  }
}

const handleUpdateContact = async () => {
  // Store the contact data before clearing the form
  const contactData = { ...newContact.value }
  const contactId = editingContact.value.id

  // Instant UI update
  const index = contacts.value.findIndex(c => c.id === contactId)
  if (index !== -1) {
    contacts.value[index] = {
      ...contacts.value[index],
      ...contactData,
      updated_at: new Date().toISOString()
    }
  }

  showEditContactForm.value = false
  editingContact.value = null
  newContact.value = { name: '', email: '', codementor_username: '', platform_preference: [], notes: '', source: '', is_favorite: false }

  // Background API call
  try {
    await updateContact(contactId, contactData)
    showStatusWithProgressLocal('Contact updated successfully', 5000)
  } catch (error) {
    console.error('Error updating contact:', error)
    // Revert on error
    await loadContacts()
    showStatusWithProgressLocal('Error updating contact', 5000)
  }
}

const getTodayDate = () => {
  return new Date().toISOString().split('T')[0]
}

const getCurrentTime = () => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

const quickSendAvailablePlatforms = computed(() => {
  if (!selectedContact.value) return []
  const platforms = []
  if (selectedContact.value.email) platforms.push('email')
  if (selectedContact.value.codementor_username) platforms.push('codementor')
  return platforms
})

const getDefaultPlatforms = (contact) => {
  let preference = contact.platform_preference
  if (!preference) {
    preference = contact.email ? ['email'] : []
  } else if (typeof preference === 'string') {
    if (preference === 'both') {
      preference = ['email', 'codementor']
    } else {
      preference = [preference]
    }
  }
  if (!Array.isArray(preference)) {
    preference = []
  }
  return preference.filter(p => {
    if (p === 'email') return !!contact.email
    if (p === 'codementor') return !!contact.codementor_username
    return false
  })
}

const openQuickSendModal = (contact) => {
  selectedContact.value = contact
  const defaultPlatforms = getDefaultPlatforms(contact)
  quickSendMessage.value = {
    platforms: defaultPlatforms.length > 0 ? defaultPlatforms : (contact.email ? ['email'] : []),
    subject: '',
    body: '',
    send_date: getTodayDate(),
    send_time: getCurrentTime(),
    schedule: false,
    timezone: 'my'
  }
  quickSendIsChainMode.value = false
  loadQuickSendMessageChain()
  showQuickSendModal.value = true
}

const loadQuickSendMessageChain = () => {
  quickSendMessageChain.value = []
  quickSendChainSubject.value = ''
  quickSendChainFooter.value = settings.value?.user?.footer || ''
  const defaultPlatforms = selectedContact.value ? getDefaultPlatforms(selectedContact.value) : []
  quickSendChainSettings.value = {
    platforms: defaultPlatforms.length > 0 ? defaultPlatforms : (selectedContact.value?.email ? ['email'] : []),
    sendFirstImmediately: false,
    timingType: 'interval',
    startDate: getTodayDate(),
    startTime: getCurrentTime(),
    timezone: 'my'
  }
}

const addQuickSendMessageToChain = () => {
  const newMessage = {
    body: '',
    send_date: getTodayDate(),
    send_time: getCurrentTime(),
    timezone: 'my',
    frequency_days: 1
  }
  quickSendMessageChain.value.push(newMessage)
}

const removeQuickSendMessageFromChain = (index) => {
  quickSendMessageChain.value.splice(index, 1)
}

const clearQuickSendMessageChain = () => {
  quickSendMessageChain.value = []
}

const handleQuickSendChainModeToggle = () => {
  quickSendIsChainMode.value = true
  loadQuickSendMessageChain()
  addQuickSendMessageToChain()
}

const closeQuickSendModal = () => {
  showQuickSendModal.value = false
  selectedContact.value = null
  quickSendIsChainMode.value = false
  quickSendSelectedTemplate.value = ''
  quickSendMessage.value = {
    platforms: [],
    subject: '',
    body: '',
    send_date: '',
    send_time: '',
    schedule: false,
    timezone: 'my'
  }
  loadQuickSendMessageChain()
}

const handleQuickSend = async () => {
  if (!quickSendMessage.value.body.trim()) {
    alert('Please fill in the message body')
    return
  }

  if (!quickSendMessage.value.platforms || quickSendMessage.value.platforms.length === 0) {
    alert('Please select at least one platform')
    return
  }

  if (quickSendMessage.value.platforms.includes('email') && !quickSendMessage.value.subject.trim()) {
    alert('Subject is required for email messages')
    return
  }

  try {
    // If sending now (not scheduled), send immediately
    if (!quickSendMessage.value.schedule) {
      await sendMessage(selectedContact.value.id, {
        platforms: quickSendMessage.value.platforms,
        subject: quickSendMessage.value.subject || '',
        body: quickSendMessage.value.body
      })

      showStatusWithProgressLocal('Message sent successfully!', 5000)
      closeQuickSendModal()
    } else {
      // If scheduled, create a Message object via API
      const userTimezoneValue = settings.value?.user?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
      const timezoneToUse = quickSendMessage.value.timezone === 'my'
        ? userTimezoneValue
        : (selectedContact.value.timezone || 'UTC')

      await apiCall('/messages/', {
        method: 'POST',
        body: JSON.stringify({
          contact: selectedContact.value.id,
          subject: quickSendMessage.value.subject || '',
          body: quickSendMessage.value.body,
          platforms: quickSendMessage.value.platforms,
          status: 'pending',
          send_date: quickSendMessage.value.send_date || null,
          send_time: quickSendMessage.value.send_time || getCurrentTime(),
          timezone: timezoneToUse,
          frequency_days: 0
        })
      })

      showStatusWithProgressLocal('Message scheduled successfully!', 5000)
      closeQuickSendModal()
    }
  } catch (error) {
    console.error('Error sending/scheduling message:', error)
    alert('Error sending message: ' + (error.message || 'Unknown error'))
  }
}

const handleQuickSendChain = async () => {
  // Validate platforms
  if (!quickSendChainSettings.value.platforms || quickSendChainSettings.value.platforms.length === 0) {
    alert('Please select at least one platform')
    return
  }

  // Validate subject if email is selected
  if (quickSendChainSettings.value.platforms.includes('email') && !quickSendChainSubject.value.trim()) {
    alert('Subject is required when email is selected')
    return
  }

  // Validate that all messages have body
  if (quickSendMessageChain.value.some(msg => !msg.body.trim())) {
    alert('Please fill in the message body for all messages')
    return
  }

  // Validate specific date/time mode
  if (quickSendChainSettings.value.timingType === 'specific') {
    if (quickSendMessageChain.value.some(msg => !msg.send_date || !msg.send_time)) {
      alert('Please fill in send date and time for all messages in specific mode')
      return
    }
  }

  // Validate interval mode
  if (quickSendChainSettings.value.timingType === 'interval') {
    if (!quickSendChainSettings.value.startDate || !quickSendChainSettings.value.startTime) {
      if (!quickSendChainSettings.value.sendFirstImmediately) {
        alert('Please set a start date and time for interval chains')
        return
      }
    }
  }

  try {
    const userTimezoneValue = settings.value?.user?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'

    // Determine chain timezone for interval mode
    const chainTimezoneToUse = quickSendChainSettings.value.timingType === 'interval'
      ? (quickSendChainSettings.value.timezone === 'my'
        ? userTimezoneValue
        : (selectedContact.value.timezone || 'UTC'))
      : null

    // Determine chain start date/time for interval mode
    let chainStartDate = null
    let chainStartTime = null
    if (quickSendChainSettings.value.timingType === 'interval') {
      if (quickSendChainSettings.value.startDate && quickSendChainSettings.value.startTime) {
        chainStartDate = quickSendChainSettings.value.startDate
        chainStartTime = quickSendChainSettings.value.startTime
      } else if (quickSendChainSettings.value.sendFirstImmediately) {
        chainStartDate = new Date().toISOString().split('T')[0]
        chainStartTime = new Date().toTimeString().slice(0, 5)
      } else {
        chainStartDate = quickSendChainSettings.value.startDate || new Date().toISOString().split('T')[0]
        chainStartTime = quickSendChainSettings.value.startTime || '09:00'
      }
    }

    // Create MessageSequence first
    const sequence = await apiCall('/message-sequences/', {
      method: 'POST',
      body: JSON.stringify({
        contact: selectedContact.value.id,
        timing_type: quickSendChainSettings.value.timingType,
        chain_start_date: chainStartDate,
        chain_start_time: chainStartTime,
        chain_timezone: chainTimezoneToUse
      })
    })

    // Create Message objects for each message in the chain
    const messagePromises = quickSendMessageChain.value.map(async (msg, index) => {
      // Combine body and footer
      let messageBody = msg.body || ''
      if (quickSendChainFooter.value && quickSendChainFooter.value.trim()) {
        messageBody += '\n\n' + quickSendChainFooter.value.trim()
      }

      // Determine timezone to use
      const timezoneToUse = (msg.timezone || 'my') === 'my'
        ? userTimezoneValue
        : (selectedContact.value.timezone || 'UTC')

      const messageData = {
        contact: selectedContact.value.id,
        sequence: sequence.id,
        order: index,
        subject: quickSendChainSettings.value.platforms.includes('email') ? quickSendChainSubject.value : '',
        body: messageBody,
        platforms: quickSendChainSettings.value.platforms,
        status: 'pending'
      }

      if (quickSendChainSettings.value.timingType === 'interval') {
        messageData.frequency_days = msg.frequency_days || (index === 0 ? 0 : 1)
      } else {
        // Specific mode
        messageData.send_date = msg.send_date || null
        messageData.send_time = msg.send_time || getCurrentTime()
        messageData.timezone = timezoneToUse
        messageData.frequency_days = 0
      }

      const createdMessage = await apiCall('/messages/', {
        method: 'POST',
        body: JSON.stringify(messageData)
      })

      // If this is the first message and sendFirstImmediately is true, send it now
      if (index === 0 && quickSendChainSettings.value.timingType === 'interval' && quickSendChainSettings.value.sendFirstImmediately) {
        try {
          const sendResult = await apiCall(`/messages/${createdMessage.id}/send-now/`, {
            method: 'POST'
          })
          createdMessage.email_message_id = sendResult.email_message_id
          createdMessage.status = sendResult.status
        } catch (error) {
          console.error('Error sending first message immediately:', error)
        }
      }

      return createdMessage
    })

    await Promise.all(messagePromises)

    showStatusWithProgressLocal('Message sequence created successfully!', 5000)
    closeQuickSendModal()
  } catch (error) {
    console.error('Error saving message chain:', error)
    alert('Error saving message chain: ' + (error.message || 'Unknown error'))
  }
}

const openContactProfile = async (contact) => {
  selectedContact.value = contact
  await loadContactAssignments(contact.id)
  showContactProfileModal.value = true
}

const loadContactAssignments = async (contactId) => {
  try {
    const allAssignments = []

    // Load assignments from all campaigns
    for (const campaign of campaigns.value) {
      try {
        const assignments = await apiCall(`/campaigns/${campaign.id}/assignments/`)
        const contactAssigns = assignments
          .filter(a => a.contact === contactId && a.next_send_date && a.status === 'active')
          .map(a => ({
            ...a,
            campaign_name: campaign.name,
            campaign_description: campaign.description,
            campaign_type: campaign.campaign_type
          }))
        allAssignments.push(...contactAssigns)
      } catch (error) {
        console.error(`Error loading assignments for campaign ${campaign.id}:`, error)
      }
    }

    upcomingMessages.value = allAssignments.sort((a, b) => new Date(a.next_send_date) - new Date(b.next_send_date))
  } catch (error) {
    console.error('Error loading contact assignments:', error)
    upcomingMessages.value = []
  }
}

const closeContactProfileModal = () => {
  showContactProfileModal.value = false
  selectedContact.value = null
}

const handleContactUpdate = (updatedContact) => {
  // Update local state
  const contactIndex = contacts.value.findIndex(c => c.id === updatedContact.id)
  if (contactIndex !== -1) {
    Object.assign(contacts.value[contactIndex], updatedContact)
  }
  if (selectedContact.value && selectedContact.value.id === updatedContact.id) {
    Object.assign(selectedContact.value, updatedContact)
  }
  showStatusWithProgressLocal('Contact updated successfully', 3000)
}

const handleSendMessage = (messageData) => {
  showStatusWithProgressLocal('Message sent successfully', 3000)
}

// Multi-select functionality
const toggleContactSelection = (contactId) => {
  if (selectedContactIds.value.has(contactId)) {
    selectedContactIds.value.delete(contactId)
  } else {
    selectedContactIds.value.add(contactId)
  }
}

const toggleSelectAll = (event) => {
  if (event.target.checked) {
    filteredContacts.value.forEach(contact => {
      selectedContactIds.value.add(contact.id)
    })
  } else {
    selectedContactIds.value.clear()
  }
}

const isAllSelected = computed(() => {
  return filteredContacts.value.length > 0 && filteredContacts.value.every(contact => selectedContactIds.value.has(contact.id))
})

// Available sources for filter dropdown (dynamically populated from contacts)
const availableSources = computed(() => {
  const sources = new Set()
  contacts.value.forEach(contact => {
    sources.add(contact.source || '')
  })
  return Array.from(sources).sort()
})

// Check if any filters are active
const hasActiveFilters = computed(() => {
  return filterSearch.value.trim() !== '' ||
    (filterPlatform.value && filterPlatform.value.length > 0) ||
    filterStatus.value !== '' ||
    (filterSource.value && filterSource.value.length > 0) ||
    filterFavorite.value !== '' ||
    filterLastMessaged.value !== ''
})

// Count active filters
const activeFilterCount = computed(() => {
  let count = 0
  if (filterSearch.value.trim() !== '') count++
  if (filterPlatform.value && filterPlatform.value.length > 0) count++
  if (filterStatus.value !== '') count++
  if (filterSource.value && filterSource.value.length > 0) count++
  if (filterFavorite.value !== '') count++
  if (filterLastMessaged.value !== '') count++
  return count
})

// Filtered contacts
const filteredContacts = computed(() => {
  let result = contacts.value

  // Search filter (reactive, searches name)
  if (filterSearch.value.trim()) {
    const searchLower = filterSearch.value.toLowerCase()
    result = result.filter(contact =>
      contact.name?.toLowerCase().includes(searchLower)
    )
  }

  // Platform filter (multi-select)
  if (filterPlatform.value && filterPlatform.value.length > 0) {
    result = result.filter(contact => {
      const hasEmail = filterPlatform.value.includes('email') && contact.email
      const hasCodementor = filterPlatform.value.includes('codementor') && contact.codementor_username
      return hasEmail || hasCodementor
    })
  }

  // Status filter
  if (filterStatus.value) {
    if (filterStatus.value === 'active') {
      result = result.filter(contact => contact.is_active)
    } else if (filterStatus.value === 'inactive') {
      result = result.filter(contact => !contact.is_active)
    }
  }

  // Source filter (multi-select)
  if (filterSource.value && filterSource.value.length > 0) {
    result = result.filter(contact => {
      return filterSource.value.some(selectedSource => {
        if (selectedSource === '__empty__') {
          return !contact.source || contact.source === ''
        }
        return contact.source === selectedSource
      })
    })
  }

  // Favorite filter
  if (filterFavorite.value === 'true') {
    result = result.filter(contact => contact.is_favorite)
  }

  // Last Messaged filter
  if (filterLastMessaged.value) {
    const now = new Date()
    result = result.filter(contact => {
      if (!contact.last_messaged) {
        return filterLastMessaged.value === 'never'
      }
      
      const lastMessagedDate = new Date(contact.last_messaged)
      const daysSince = Math.floor((now - lastMessagedDate) / (1000 * 60 * 60 * 24))
      
      switch (filterLastMessaged.value) {
        case 'never':
          return false // Already handled above
        case 'today':
          return daysSince === 0
        case 'last_7_days':
          return daysSince <= 7
        case 'last_30_days':
          return daysSince <= 30
        case 'last_90_days':
          return daysSince <= 90
        case 'over_90_days':
          return daysSince > 90
        default:
          return true
      }
    })
  }

  return result
})

// Toggle favorite
const toggleFavorite = async (contact) => {
  const newFavoriteValue = !contact.is_favorite
  // Instant UI update
  contact.is_favorite = newFavoriteValue

  // Background API call
  try {
    await updateContact(contact.id, { is_favorite: newFavoriteValue })
  } catch (error) {
    console.error('Error updating favorite:', error)
    // Revert on error
    contact.is_favorite = !newFavoriteValue
    await loadContacts()
  }
}

const selectedContacts = computed(() => {
  return contacts.value.filter(contact => selectedContactIds.value.has(contact.id))
})

const canSendBulkMessage = computed(() => {
  if (!bulkMessage.value.body.trim()) return false
  if (!bulkMessage.value.usePreferredPlatforms && bulkMessage.value.platforms.length === 0) return false
  if ((bulkMessage.value.usePreferredPlatforms || bulkMessage.value.platforms.includes('email')) && !bulkMessage.value.subject.trim()) return false
  return selectedContacts.value.length > 0
})

// Template variable replacement
const getPreviewText = (text, contact) => {
  if (!text) return ''

  // Extract first and last name from full name
  const nameParts = (contact.name || '').split(' ')
  const firstName = contact.preferred_name || nameParts[0] || ''
  const lastName = nameParts.slice(1).join(' ') || ''
  const preferredName = contact.preferred_name || firstName
  const gender = contact.gender || ''

  let result = text

  // Handle gender-based conditionals first (e.g., {if_male:text}{if_female:text})
  if (gender === 'male') {
    result = result.replace(/\{if_male:([^}]+)\}/g, '$1')
    result = result.replace(/\{if_female:([^}]+)\}/g, '')
  } else if (gender === 'female') {
    result = result.replace(/\{if_female:([^}]+)\}/g, '$1')
    result = result.replace(/\{if_male:([^}]+)\}/g, '')
  } else {
    // If gender not specified, remove both blocks
    result = result.replace(/\{if_male:([^}]+)\}/g, '')
    result = result.replace(/\{if_female:([^}]+)\}/g, '')
  }

  // Replace simplified syntax first (e.g., {first_name}, {name})
  result = result.replace(/\{name\}/g, contact.name || '')
  result = result.replace(/\{first_name\}/g, firstName)
  result = result.replace(/\{preferred_name\}/g, preferredName)
  result = result.replace(/\{last_name\}/g, lastName)
  result = result.replace(/\{gender\}/g, gender)
  result = result.replace(/\{email\}/g, contact.email || '')
  result = result.replace(/\{codementor_username\}/g, contact.codementor_username || '')

  // Replace old contact variables (for backwards compatibility)
  result = result.replace(/\{contact\.name\}/g, contact.name || '')
  result = result.replace(/\{contact\.first_name\}/g, firstName)
  result = result.replace(/\{contact\.preferred_name\}/g, preferredName)
  result = result.replace(/\{contact\.last_name\}/g, lastName)
  result = result.replace(/\{contact\.gender\}/g, gender)
  result = result.replace(/\{contact\.email\}/g, contact.email || '')
  result = result.replace(/\{contact\.codementor_username\}/g, contact.codementor_username || '')

  // Replace old user variables (for backwards compatibility)
  result = result.replace(/\{user\.name\}/g, contact.name || '')
  result = result.replace(/\{user\.first_name\}/g, firstName)
  result = result.replace(/\{user\.preferred_name\}/g, preferredName)
  result = result.replace(/\{user\.last_name\}/g, lastName)
  result = result.replace(/\{user\.gender\}/g, gender)
  result = result.replace(/\{user\.email\}/g, contact.email || '')
  result = result.replace(/\{user\.codementor_username\}/g, contact.codementor_username || '')

  return result
}

// Bulk messaging
const openBulkMessageModal = () => {
  // Determine available platforms from selected contacts
  const hasEmail = selectedContacts.value.some(c => c.email)
  const hasCodementor = selectedContacts.value.some(c => c.codementor_username)

  bulkMessage.value = {
    platforms: [
      ...(hasEmail ? ['email'] : []),
      ...(hasCodementor ? ['codementor'] : [])
    ],
    usePreferredPlatforms: true,
    subject: '',
    body: ''
  }
  showBulkMessageModal.value = true
}

const closeBulkMessageModal = () => {
  showBulkMessageModal.value = false
  bulkMessage.value = {
    platforms: [],
    usePreferredPlatforms: false,
    subject: '',
    body: ''
  }
  bulkSelectedTemplate.value = ''
}

const openBulkEditModal = () => {
  // Reset bulk edit data
  bulkEditData.value = {
    platform_preference: [],
    timezone: '',
    is_active: null,
    source: '',
    is_favorite: null,
    gender: ''
  }
  showBulkEditModal.value = true
}

const closeBulkEditModal = () => {
  showBulkEditModal.value = false
  bulkEditData.value = {
    platform_preference: [],
    timezone: '',
    is_active: null,
    source: '',
    is_favorite: null,
    gender: ''
  }
}

const handleBulkEdit = async () => {
  if (selectedContactIds.value.size === 0) return

  // Prepare update data - only include fields that have values
  const updateData = {
    contact_ids: Array.from(selectedContactIds.value)
  }

  // Only include fields that are set
  if (bulkEditData.value.platform_preference.length > 0) {
    updateData.platform_preference = bulkEditData.value.platform_preference
  }
  if (bulkEditData.value.timezone) {
    updateData.timezone = bulkEditData.value.timezone
  }
  if (bulkEditData.value.is_active !== null) {
    updateData.is_active = bulkEditData.value.is_active
  }
  if (bulkEditData.value.source) {
    updateData.source = bulkEditData.value.source
  }
  if (bulkEditData.value.is_favorite !== null) {
    updateData.is_favorite = bulkEditData.value.is_favorite
  }
  if (bulkEditData.value.gender !== '') {
    updateData.gender = bulkEditData.value.gender
  }

  // Remove contact_ids if no other fields to update
  if (Object.keys(updateData).length === 1) {
    showStatusWithProgressLocal('Please select at least one field to update', 3000)
    return
  }

  try {
    showStatusWithProgressLocal(`Updating ${selectedContactIds.value.size} contacts...`, 5000)
    
    const result = await apiCall('/contacts/bulk-update/', {
      method: 'POST',
      body: JSON.stringify(updateData)
    })

    showStatusWithProgressLocal(`Successfully updated ${result.updated_count} contact(s)`, 5000)
    
    // Reload contacts and clear selection
    await loadContacts()
    selectedContactIds.value.clear()
    closeBulkEditModal()
  } catch (error) {
    console.error('Error updating contacts:', error)
    showStatusWithProgressLocal(`Error updating contacts: ${error.message || 'Unknown error'}`, 5000)
  }
}

const handleBulkDelete = async () => {
  if (selectedContactIds.value.size === 0) return

  if (!confirm(`Are you sure you want to delete ${selectedContactIds.value.size} contact(s)? This action cannot be undone.`)) {
    return
  }

  try {
    showStatusWithProgressLocal(`Deleting ${selectedContactIds.value.size} contacts...`, 5000)
    
    const result = await apiCall('/contacts/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({
        contact_ids: Array.from(selectedContactIds.value)
      })
    })

    showStatusWithProgressLocal(`Successfully deleted ${result.deleted_count} contact(s)`, 5000)
    
    // Remove deleted contacts from local state immediately
    const deletedIds = new Set(selectedContactIds.value)
    contacts.value = contacts.value.filter(c => !deletedIds.has(c.id))
    selectedContactIds.value.clear()
    
    // Reload to ensure sync
    await loadContacts()
  } catch (error) {
    console.error('Error deleting contacts:', error)
    showStatusWithProgressLocal(`Error deleting contacts: ${error.message || 'Unknown error'}`, 5000)
    // Reload on error to ensure sync
    await loadContacts()
  }
}

const handleBulkSend = async () => {
  if (!canSendBulkMessage.value) return

  if (!confirm(`Send this message to ${selectedContactIds.value.size} contact(s)?`)) {
    return
  }

  try {
    // Prepare message body with template variables (use first contact for preview)
    // The backend will handle per-contact template replacement
    const firstContact = selectedContacts.value[0]
    let body = bulkMessage.value.body
    let subject = bulkMessage.value.subject || ''
    
    // If using preferred platforms, we need to handle template replacement per contact
    // For now, send the template as-is and let backend handle it
    // Actually, we need to send the raw template and let backend do per-contact replacement
    
    // Append footer if email is being used
    if (bulkMessage.value.platforms.includes('email') || bulkMessage.value.usePreferredPlatforms) {
      let footerToUse = ''
      if (bulkSelectedTemplate.value) {
        const template = templates.value.find(t => t.id === parseInt(bulkSelectedTemplate.value))
        if (template && template.footer) {
          footerToUse = template.footer
        }
      }
      if (!footerToUse) {
        footerToUse = settings.value?.user?.footer || ''
      }
      if (footerToUse) {
        body = body + '\n\n' + footerToUse
      }
    }

    // Send ONE bulk request to backend - it handles everything
    await apiCall('/contacts/bulk-send/', {
      method: 'POST',
      body: JSON.stringify({
        contact_ids: Array.from(selectedContactIds.value),
        platforms: bulkMessage.value.platforms,
        subject: subject,
        body: body,
        use_preferred_platforms: bulkMessage.value.usePreferredPlatforms
      })
    })

    showStatusWithProgressLocal(
      `Bulk send initiated for ${selectedContactIds.value.size} contact(s). Processing in background.`,
      5000
    )

    // Close modal and clear selection immediately
    showBulkMessageModal.value = false
    selectedContactIds.value.clear()
    
    // Reload contacts after a short delay to see updates
    setTimeout(async () => {
      await loadContacts()
    }, 2000)
  } catch (error) {
    console.error('Bulk send error:', error)
    showStatusWithProgressLocal(`Bulk send failed: ${error.message || 'Unknown error'}`, 5000)
  }
}

const formatLastMessaged = (dateString) => {
  if (!dateString) return 'Never'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return 'Never'
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (e) {
    console.error('Error formatting last messaged date:', e)
    return 'Never'
  }
}

const exportContacts = async () => {
  try {
    const response = await apiFetch('/contacts/export/', {
      method: 'GET'
    })

    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'contacts_export.csv'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      showStatusWithProgressLocal('Contacts exported successfully', 3000)
    } else {
      showStatusWithProgressLocal('Export failed', 3000)
    }
  } catch (error) {
    console.error('Export error:', error)
    showStatusWithProgressLocal('Export failed', 3000)
  }
}

const handleFileSelect = (event) => {
  importFile.value = event.target.files[0]
  importStatus.value = ''
}

const handleImport = async () => {
  if (!importFile.value) return

  try {
    const formData = new FormData()
    formData.append('file', importFile.value)

    const data = await apiCall('/contacts/import/', {
      method: 'POST',
      body: formData,
      headers: {} // Let fetch set Content-Type for FormData
    })

    importStatus.value = `Import completed: ${data.created} created, ${data.updated} updated${data.errors.length > 0 ? `. Errors: ${data.errors.join(', ')}` : ''}`
    await loadContacts()
    setTimeout(() => {
      showImportModal.value = false
      importFile.value = null
      importStatus.value = ''
    }, 3000)
  } catch (error) {
    console.error('Import error:', error)
    importStatus.value = `Error: ${error.message || 'Import failed'}`
  }
}

// Data is loaded at app startup, no need to load here
onMounted(() => {
  // No status message needed
})
</script>
