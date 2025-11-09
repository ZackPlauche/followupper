<template>
  <div v-if="contact" :class="isModal ? 'fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4' : 'min-h-screen'">
    <div :class="isModal ? 'bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 w-full max-w-6xl max-h-[90vh] flex flex-col' : 'bg-slate-800/90 backdrop-blur-sm flex flex-col min-h-screen'">

      <!-- Header -->
      <div class="p-6 border-b border-slate-700/50">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-thin text-slate-100 mb-1">{{ contact.name }}</h3>
            <p class="text-slate-400 text-sm">{{ contact.email || contact.codementor_username || 'No contact info' }}</p>
            <p v-if="editingContact.timezone || contact.timezone" class="text-slate-500 text-xs mt-1">
              <Icon name="lucide:clock" class="w-3 h-3 inline mr-1" />
              Contact's time: {{ contactCurrentTime }}
            </p>
          </div>
          <button v-if="isModal" @click="$emit('close')" class="text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="lucide:x" class="w-6 h-6" />
          </button>
          <button v-else @click="goBack" class="text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="lucide:arrow-left" class="w-6 h-6" />
          </button>
        </div>
      </div>
      
      <!-- Content -->
      <div class="flex-1 overflow-y-auto">
        <div class="flex h-full">
          <!-- Left: Contact Information & Notes -->
          <div class="flex-1 flex flex-col p-6 border-r border-slate-600/30 space-y-6">
          <!-- Contact Information -->
          <div class="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
            <h4 class="text-lg font-light text-slate-100 mb-4">Contact Information</h4>
            <form @submit.prevent="handleUpdateContact" class="space-y-3">
              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Name *</label>
                <input v-model="editingContact.name" type="text" required
                       class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
              </div>
              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Email</label>
                <input v-model="editingContact.email" type="email"
                       class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
              </div>
              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Codementor Username</label>
                <input v-model="editingContact.codementor_username" type="text"
                       class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
              </div>
              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Platform Preference</label>
                <select v-model="editingContact.platform_preference"
                        class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                  <option value="email">Email</option>
                  <option value="codementor">Codementor</option>
                  <option value="both">Both</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Timezone</label>
                <select v-model="editingContact.timezone"
                        class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
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
                <p v-if="editingContact.timezone" class="text-xs text-slate-400 mt-1">
                  Current time: {{ contactCurrentTime }}
                </p>
              </div>
              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Status</label>
                <select v-model="editingContact.is_active"
                        class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                  <option :value="true">Active</option>
                  <option :value="false">Inactive</option>
                </select>
              </div>
              <div class="flex space-x-2 pt-2">
                <button type="submit"
                        class="flex-1 px-3 py-2 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-lg text-sm font-light hover:shadow-lg transition-all duration-300">
                  Save
                </button>
              </div>
            </form>
          </div>
          
          <!-- Notes Section -->
          <div class="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-lg font-light text-slate-100">Notes</h4>
              <button @click="showAddNoteForm = true" 
                      class="px-3 py-1 bg-emerald-600/50 text-emerald-300 rounded-lg text-xs font-light hover:bg-emerald-600/70 transition-colors">
                <Icon name="lucide:plus" class="w-4 h-4 inline mr-1" />
                Add Note
              </button>
            </div>
            <div v-if="notes.length === 0" class="text-center py-8 text-slate-400 text-sm">
              No notes yet. Click "Add Note" to add one.
            </div>
            <div v-else class="space-y-3">
              <div v-for="(note, index) in notes" :key="index" 
                   class="bg-slate-600/30 rounded-lg p-3 border border-slate-500/20">
                <div class="flex items-start justify-between mb-2">
                  <span class="text-xs text-slate-400">{{ formatDate(note.date) }}</span>
                </div>
                <div v-if="editingNoteIndex !== index" 
                     @click="startEditingNote(index)"
                     class="cursor-text hover:bg-slate-500/20 rounded p-1 transition-colors">
                  <p class="text-slate-200 text-sm whitespace-pre-wrap">{{ note.text }}</p>
                </div>
                <textarea v-else
                          v-model="editingNoteText"
                          @blur="saveNote(index)"
                          @keydown.ctrl.enter="saveNote(index)"
                          @keydown.esc="cancelEditingNote"
                          rows="3"
                          class="w-full bg-slate-500/50 border border-emerald-500/50 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                          autofocus></textarea>
              </div>
            </div>
          </div>
          
          <!-- Send Message Section -->
          <div class="bg-slate-700/30 rounded-xl p-4 border border-slate-600/30">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-lg font-light text-slate-100">{{ isChainMode ? 'Send Message Chain' : 'Send Message' }}</h4>
              <div class="flex items-center bg-slate-600/50 rounded-lg p-1 border border-slate-500/30">
                <button 
                  @click="isChainMode = false"
                  :class="!isChainMode ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="flex items-center px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                  <Icon name="fa:send" class="w-4 h-4" />
                </button>
                <button 
                  @click="handleChainModeToggle"
                  :class="isChainMode ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="flex items-center space-x-2 px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                  <Icon name="mage:link" class="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <!-- Single Message Mode -->
            <div v-if="!isChainMode" class="space-y-3">
              <div v-if="hasEmail">
                <label class="block text-xs font-light text-slate-300 mb-1">Subject</label>
                <input v-model="singleMessage.subject" type="text"
                       class="w-full bg-slate-500/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors"
                       placeholder="Message subject (optional)">
              </div>
              
              <div>
                <label class="block text-xs font-light text-slate-300 mb-1">Message *</label>
                <textarea v-model="singleMessage.body" rows="5" required
                          class="w-full bg-slate-500/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                          placeholder="Enter your message here..."></textarea>
              </div>
              
              <div v-if="singleMessage.schedule" class="space-y-3">
                <div class="flex items-end gap-3">
                  <div class="flex-1">
                    <label class="block text-xs font-light text-slate-300 mb-1">Send Date</label>
                    <input v-model="singleMessage.send_date" type="date"
                           class="w-full bg-slate-500/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                  </div>
                  <div class="flex-1">
                    <label class="block text-xs font-light text-slate-300 mb-1">Send Time</label>
                    <input v-model="singleMessage.send_time" type="time"
                           class="w-full bg-slate-500/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                  </div>
                  <div>
                    <label class="block text-xs font-light text-slate-300 mb-1">Timezone</label>
                    <div class="flex items-center bg-slate-600/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                      <button 
                        @click="singleMessage.timezone = 'my'"
                        :class="singleMessage.timezone === 'my' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                        class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                        Mine
                      </button>
                      <button 
                        @click="singleMessage.timezone = 'user'"
                        :class="singleMessage.timezone === 'user' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                        class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                        Contact
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="flex items-center pt-2">
                <button @click="saveSingleMessage"
                        class="flex-1 px-3 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-l-lg text-sm font-light hover:shadow-lg transition-all duration-300">
                  {{ singleMessage.schedule ? 'Schedule' : 'Send' }}
                </button>
                <button @click="singleMessage.schedule = !singleMessage.schedule"
                        class="px-2 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white border-l border-white/20 rounded-r-lg text-sm font-light hover:shadow-lg transition-all duration-300">
                  <Icon name="material-symbols:schedule-send" class="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <!-- Chain Mode -->
            <div v-else class="space-y-4">
              <!-- Global Chain Settings -->
              <div v-if="hasEmail">
                <label class="block text-xs font-light text-slate-300 mb-2">Subject (applies to all messages)</label>
                <input v-model="chainSubject" type="text"
                       class="w-full bg-slate-500/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors"
                       placeholder="Message subject (optional)">
              </div>
              
              <div>
                <label class="block text-xs font-light text-slate-300 mb-2">Footer/Signature (applies to all messages)</label>
                <textarea v-model="chainFooter" rows="3"
                          class="w-full bg-slate-500/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                          placeholder="Message footer"></textarea>
              </div>
              
              <!-- Chain Timing Settings -->
              <div class="space-y-3">
                <div>
                  <label class="block text-xs font-light text-slate-300 mb-2">Timing Type</label>
                  <div class="flex items-center bg-slate-600/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                    <button 
                      @click="chainSettings.timingType = 'interval'"
                      :class="chainSettings.timingType === 'interval' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                      class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                      Interval
                    </button>
                    <button 
                      @click="chainSettings.timingType = 'specific'"
                      :class="chainSettings.timingType === 'specific' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                      class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                      Specific
                    </button>
                  </div>
                </div>
                
                <div v-if="chainSettings.timingType === 'interval'" class="space-y-2">
                  <div class="flex items-center space-x-2">
                    <input type="checkbox" v-model="chainSettings.sendFirstImmediately" id="send-first-immediately"
                           class="w-4 h-4 rounded border-emerald-500/30 bg-slate-600/50 text-emerald-500 focus:ring-emerald-500 focus:ring-2">
                    <label for="send-first-immediately" class="text-xs text-slate-300 cursor-pointer">Send first message immediately</label>
                  </div>
                  
                  <div class="space-y-2">
                    <div class="flex items-end gap-2">
                      <div class="flex-1">
                        <label class="block text-xs font-light text-slate-300 mb-1">Start Date</label>
                        <input v-model="chainSettings.startDate" type="date"
                               class="w-full bg-slate-500/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                      </div>
                      <div class="flex-1">
                        <label class="block text-xs font-light text-slate-300 mb-1">Start Time</label>
                        <input v-model="chainSettings.startTime" type="time"
                               class="w-full bg-slate-500/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                      </div>
                      <div>
                        <label class="block text-xs font-light text-slate-300 mb-1">Timezone</label>
                        <div class="flex items-center bg-slate-600/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                          <button 
                            @click="chainSettings.timezone = 'my'"
                            :class="chainSettings.timezone === 'my' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                            class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                            Mine
                          </button>
                          <button 
                            @click="chainSettings.timezone = 'user'"
                            :class="chainSettings.timezone === 'user' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                            class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                            Contact
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-for="(message, index) in messageChain" :key="index"
                   class="bg-slate-600/30 rounded-lg p-4 border border-slate-500/20">
                <div class="flex items-start justify-between mb-3">
                  <h5 class="text-sm font-medium text-slate-200">Message {{ index + 1 }}</h5>
                  <button @click="removeMessageFromChain(index)" 
                          class="text-slate-400 hover:text-red-400 transition-colors">
                    <Icon name="lucide:trash-2" class="w-4 h-4" />
                  </button>
                </div>
                
                <div class="space-y-3">
                  <div>
                    <label class="block text-xs font-light text-slate-300 mb-1">Message *</label>
                    <textarea v-model="message.body" rows="4" required
                              class="w-full bg-slate-500/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                              placeholder="Enter your message here..."></textarea>
                  </div>
                  
                  <!-- Interval Mode -->
                  <div v-if="chainSettings.timingType === 'interval' && index > 0">
                    <label class="block text-xs font-light text-slate-300 mb-1">
                      Days after previous message
                    </label>
                    <input v-model.number="message.frequency_days" type="number" min="0" step="1"
                           class="w-full bg-slate-500/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors"
                           placeholder="0 = send immediately after previous">
                  </div>
                  
                  <!-- Specific Date/Time Mode -->
                  <div v-else-if="chainSettings.timingType === 'specific'" class="space-y-2">
                    <div class="flex items-end gap-2">
                      <div class="flex-1">
                        <label class="block text-xs font-light text-slate-300 mb-1">Send Date</label>
                        <input v-model="message.send_date" type="date"
                               class="w-full bg-slate-500/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                      </div>
                      <div class="flex-1">
                        <label class="block text-xs font-light text-slate-300 mb-1">Send Time</label>
                        <input v-model="message.send_time" type="time"
                               class="w-full bg-slate-500/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                      </div>
                      <div>
                        <label class="block text-xs font-light text-slate-300 mb-1">Timezone</label>
                        <div class="flex items-center bg-slate-600/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                          <button 
                            @click="message.timezone = 'my'"
                            :class="message.timezone === 'my' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                            class="px-2 py-1.5 rounded-md transition-colors text-xs font-light">
                            Mine
                          </button>
                          <button 
                            @click="message.timezone = 'user'"
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
              
              <button @click="addMessageToChain" 
                      class="w-full py-2 border-2 border-dashed border-emerald-500/30 rounded-lg text-emerald-300 hover:border-emerald-500/50 hover:bg-emerald-500/10 transition-colors flex items-center justify-center">
                <Icon name="lucide:plus" class="w-4 h-4 mr-2" />
                Add Another Message
              </button>
              
              <div class="flex space-x-2 pt-2">
                <button @click="saveMessageChain"
                        class="flex-1 px-3 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg text-sm font-light hover:shadow-lg transition-all duration-300">
                  Save Message Chain
                </button>
                <button @click="clearMessageChain"
                        class="px-3 py-2 bg-slate-600/50 text-slate-300 rounded-lg text-sm font-light hover:bg-slate-600/70 transition-colors">
                  Clear
                </button>
              </div>
              </div>
            </div>
          </div>
            
          <!-- Right: Upcoming Messages (1/3 width) -->
          <div class="w-1/3 relative pb-6 flex flex-col">
            <div class="flex flex-col p-6 min-h-0 sticky top-0">
              <h4 class="text-lg font-light text-slate-100 mb-4">Upcoming Messages</h4>
              <div v-if="allUpcomingMessages.length === 0" class="text-center py-8 text-slate-400 text-sm">
                No upcoming messages scheduled
              </div>
              <div v-else class="space-y-3 flex-1 overflow-y-auto">
                <div v-for="(item, index) in allUpcomingMessages" :key="item.id || `chain-${index}`" 
                     class="bg-slate-600/30 rounded-lg p-3 border border-slate-500/20">
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <div class="text-slate-100 font-medium mb-1 text-sm">{{ item.campaign_name || item.title }}</div>
                      <div class="text-xs text-slate-400 mb-2">{{ item.campaign_description || item.description || 'No description' }}</div>
                      <div class="flex flex-col space-y-2 text-xs">
                        <span class="text-slate-400">
                          <Icon name="lucide:calendar" class="w-3 h-3 inline mr-1" />
                          {{ formatDate(item.next_send_date || item.send_date) }}
                        </span>
                        <span v-if="item.status" :class="getStatusClass(item.status)" class="inline-flex px-2 py-1 rounded-full text-xs w-fit">
                          {{ item.status }}
                        </span>
                        <span v-else class="inline-flex px-2 py-1 rounded-full text-xs w-fit bg-blue-500/20 text-blue-400 border border-blue-500/30">
                          Scheduled
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Add Note Modal -->
    <div v-if="showAddNoteForm" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 w-full max-w-md">
        <h3 class="text-2xl font-thin text-slate-100 mb-6">Add Note</h3>
        <form @submit.prevent="handleAddNote" class="space-y-4">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Note *</label>
            <textarea v-model="newNote" rows="5" required
                      class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                      placeholder="Enter your note here..."></textarea>
          </div>
          <div class="flex space-x-3 pt-4">
            <button type="button" @click="showAddNoteForm = false"
                    class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
              Cancel
            </button>
            <button type="submit"
                    class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
              Add Note
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  contact: {
    type: Object,
    required: true
  },
  upcomingMessages: {
    type: Array,
    default: () => []
  },
  isModal: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close', 'update', 'add-note', 'update-note', 'send-message'])

const { updateContact, sendEmail, settings } = useApi()
const router = useRouter()

const goBack = () => {
  router.push('/contacts')
}

const editingContact = ref({ ...props.contact })
const notes = ref([])
const newNote = ref('')
const showAddNoteForm = ref(false)
const editingNoteIndex = ref(-1)
const editingNoteText = ref('')
const messageChain = ref([])
const isChainMode = ref(false)
const chainSubject = ref('')
const chainFooter = ref(settings.value?.user?.footer || '')
const chainSettings = ref({
  sendFirstImmediately: false,
  timingType: 'interval', // 'interval' or 'specific'
  startDate: '',
  startTime: '09:00',
  timezone: 'my' // 'my' or 'user'
})
const singleMessage = ref({
  subject: '',
  body: '',
  send_date: '',
  send_time: '09:00',
  schedule: false,
  timezone: 'my' // 'my' or 'user'
})

// Get user's timezone from settings (backend)
const userTimezone = computed(() => {
  // Use timezone from backend settings, fallback to browser timezone if not set
  if (settings.value?.user?.timezone) {
    return settings.value.user.timezone
  }
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone
  } catch {
    return 'UTC'
  }
})

const hasEmail = computed(() => {
  return !!(props.contact.email)
})

// Current time for display (updates every second)
const currentTime = ref(new Date())

// Contact's current time in their timezone
const contactCurrentTime = computed(() => {
  const timezone = editingContact.value.timezone || props.contact.timezone
  if (!timezone) return ''
  try {
    const now = currentTime.value
    return new Intl.DateTimeFormat('en-US', {
      timeZone: timezone,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    }).format(now)
  } catch (e) {
    return ''
  }
})

// Update time every second
let timeInterval = null
onMounted(() => {
  loadNotes()
  loadMessageChain()
  // Update current time every second
  timeInterval = setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})

const scheduledMessageChains = computed(() => {
  const scheduled = []
  try {
    if (props.contact.message_chains) {
      const parsed = JSON.parse(props.contact.message_chains)
      if (Array.isArray(parsed) && parsed.length > 0) {
        parsed.forEach((chain, chainIndex) => {
          if (Array.isArray(chain)) {
            let currentDate = new Date()
            chain.forEach((msg, msgIndex) => {
              if (msg.schedule && msg.send_date && msg.send_time) {
                // Calculate send date (handle timezone)
                try {
                  const timezone = msg.timezone || 'UTC'
                  const sendDateStr = `${msg.send_date}T${msg.send_time}`
                  // Create date in the specified timezone
                  const sendDate = new Date(sendDateStr)
                  if (sendDate > currentDate) {
                    scheduled.push({
                      id: `chain-${chainIndex}-msg-${msgIndex}`,
                      title: 'Scheduled Message',
                      description: msg.subject || 'No subject',
                      send_date: sendDate.toISOString(),
                      type: 'scheduled_message'
                    })
                  }
                } catch (e) {
                  console.error('Error parsing scheduled date:', e)
                }
              } else if (msg.frequency_days !== undefined && !msg.sent) {
                // Interval-based chain - check if first message has chain_start_date
                const firstMsg = chain[0]
                if (firstMsg && firstMsg.chain_start_date && firstMsg.chain_start_time) {
                  // Calculate based on chain start time
                  try {
                    const startDateStr = `${firstMsg.chain_start_date}T${firstMsg.chain_start_time}`
                    const chainStartDate = new Date(startDateStr)
                    
                    // Calculate cumulative days up to this message
                    let cumulativeDays = 0
                    for (let i = 0; i < msgIndex; i++) {
                      if (chain[i] && chain[i].frequency_days !== undefined) {
                        cumulativeDays += chain[i].frequency_days || 0
                      }
                    }
                    
                    // Calculate send date: chain_start + cumulative_days + this message's frequency_days
                    const sendDate = new Date(chainStartDate)
                    sendDate.setDate(sendDate.getDate() + cumulativeDays + (msg.frequency_days || 0))
                    
                    if (sendDate > new Date()) {
                      scheduled.push({
                        id: `chain-${chainIndex}-msg-${msgIndex}`,
                        title: 'Message Chain',
                        description: msg.subject || msg.body.substring(0, 50) + '...',
                        send_date: sendDate.toISOString(),
                        type: 'message_chain'
                      })
                    }
                  } catch (e) {
                    console.error('Error calculating interval chain date:', e)
                  }
                } else {
                  // Fallback to old calculation if no start date
                  if (msgIndex === 0) {
                    currentDate = new Date()
                    currentDate.setDate(currentDate.getDate() + (msg.frequency_days || 0))
                  } else {
                    currentDate.setDate(currentDate.getDate() + (msg.frequency_days || 0))
                  }
                  if (currentDate > new Date()) {
                    scheduled.push({
                      id: `chain-${chainIndex}-msg-${msgIndex}`,
                      title: 'Message Chain',
                      description: msg.subject || msg.body.substring(0, 50) + '...',
                      send_date: currentDate.toISOString(),
                      type: 'message_chain'
                    })
                  }
                }
              }
            })
          }
        })
      }
    }
  } catch (e) {
    console.error('Error parsing message chains:', e)
  }
  return scheduled.sort((a, b) => new Date(a.send_date) - new Date(b.send_date))
})

const allUpcomingMessages = computed(() => {
  const all = [...props.upcomingMessages, ...scheduledMessageChains.value]
  return all.sort((a, b) => {
    const dateA = new Date(a.next_send_date || a.send_date)
    const dateB = new Date(b.next_send_date || b.send_date)
    return dateA - dateB
  })
})

const loadNotes = () => {
  try {
    if (props.contact.notes) {
      const parsed = JSON.parse(props.contact.notes)
      if (Array.isArray(parsed)) {
        notes.value = parsed
      } else {
        notes.value = [{ text: props.contact.notes, date: props.contact.updated_at || props.contact.created_at }]
      }
    } else {
      notes.value = []
    }
  } catch (e) {
    if (props.contact.notes) {
      notes.value = [{ text: props.contact.notes, date: props.contact.updated_at || props.contact.created_at }]
    } else {
      notes.value = []
    }
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getStatusClass = (status) => {
  const classes = {
    'active': 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
    'paused': 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
    'blacklisted': 'bg-red-500/20 text-red-400 border border-red-500/30',
    'completed': 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
  }
  return classes[status] || 'bg-slate-500/20 text-slate-400 border border-slate-500/30'
}

const handleUpdateContact = async () => {
  try {
    await updateContact(props.contact.id, editingContact.value)
    emit('update', editingContact.value)
  } catch (error) {
    console.error('Error updating contact:', error)
  }
}

const handleAddNote = async () => {
  if (!newNote.value.trim()) return
  
  const note = {
    text: newNote.value.trim(),
    date: new Date().toISOString()
  }
  
  notes.value.push(note)
  const notesJson = JSON.stringify(notes.value)
  
  try {
    await updateContact(props.contact.id, {
      ...props.contact,
      notes: notesJson
    })
    emit('add-note', note)
    newNote.value = ''
    showAddNoteForm.value = false
  } catch (error) {
    console.error('Error adding note:', error)
  }
}

const startEditingNote = (index) => {
  editingNoteIndex.value = index
  editingNoteText.value = notes.value[index].text
}

const saveNote = async (index) => {
  if (editingNoteIndex.value === -1) return
  
  notes.value[index].text = editingNoteText.value.trim()
  notes.value[index].date = new Date().toISOString()
  
  const notesJson = JSON.stringify(notes.value)
  
  try {
    await updateContact(props.contact.id, {
      ...props.contact,
      notes: notesJson
    })
    emit('update-note', { index, note: notes.value[index] })
    editingNoteIndex.value = -1
    editingNoteText.value = ''
  } catch (error) {
    console.error('Error updating note:', error)
  }
}

const cancelEditingNote = () => {
  editingNoteIndex.value = -1
  editingNoteText.value = ''
}

const loadMessageChain = () => {
  try {
    if (props.contact.message_chains) {
      const parsed = JSON.parse(props.contact.message_chains)
      if (Array.isArray(parsed) && parsed.length > 0) {
        messageChain.value = parsed[0] // Load the first chain for now
      } else {
        messageChain.value = []
      }
    } else {
      messageChain.value = []
    }
  } catch (e) {
    messageChain.value = []
  }
}

const addMessageToChain = () => {
  const newMessage = {
    body: '',
    frequency_days: 1,
    send_date: '',
    send_time: '09:00',
    timezone: 'my'
  }
  messageChain.value.push(newMessage)
}

const handleChainModeToggle = () => {
  isChainMode.value = true
  if (messageChain.value.length === 0) {
    // When switching to chain mode, add the first message
    addMessageToChain()
  }
}

const saveSingleMessage = async () => {
  if (!singleMessage.value.body.trim()) {
    alert('Please fill in the message body')
    return
  }
  
  try {
    // If sending now (not scheduled), send immediately
    if (!singleMessage.value.schedule) {
      if (hasEmail.value && !singleMessage.value.subject.trim()) {
        alert('Subject is required for email messages')
        return
      }
      
      await sendEmail({
        to_email: props.contact.email || props.contact.codementor_username,
        subject: singleMessage.value.subject || 'No subject',
        body: singleMessage.value.body
      })
      
      emit('send-message', { ...singleMessage.value, sent: true })
    } else {
      // If scheduled, save to message_chains
      // Determine timezone to use
      const timezoneToUse = singleMessage.value.timezone === 'my' 
        ? userTimezone.value 
        : (props.contact.timezone || 'UTC')
      
      const chain = [{
        subject: singleMessage.value.subject || '',
        body: singleMessage.value.body,
        send_date: singleMessage.value.send_date || '',
        send_time: singleMessage.value.send_time || '09:00',
        frequency_days: 0,
        schedule: true,
        timezone: timezoneToUse
      }]
      
      const chainsJson = JSON.stringify([chain])
      
      const updatedContact = await updateContact(props.contact.id, {
        ...props.contact,
        message_chains: chainsJson
      })
      
      // Update local contact data to refresh upcoming messages
      Object.assign(props.contact, { message_chains: chainsJson })
      emit('update', { ...props.contact, message_chains: chainsJson })
      emit('send-message', chain)
    }
    
    // Reset form
    singleMessage.value = {
      subject: '',
      body: '',
      send_date: '',
      send_time: '09:00',
      schedule: false,
      timezone: 'my'
    }
  } catch (error) {
    console.error('Error saving/sending message:', error)
    alert('Error sending message: ' + (error.message || 'Unknown error'))
  }
}

const removeMessageFromChain = (index) => {
  messageChain.value.splice(index, 1)
}

const clearMessageChain = () => {
  messageChain.value = []
}

const saveMessageChain = async () => {
  // Validate that all messages have body
  if (messageChain.value.some(msg => !msg.body.trim())) {
    alert('Please fill in the message body for all messages')
    return
  }
  
  // Validate specific date/time mode
  if (chainSettings.value.timingType === 'specific') {
    if (messageChain.value.some(msg => !msg.send_date || !msg.send_time)) {
      alert('Please fill in send date and time for all messages in specific mode')
      return
    }
  }
  
  // Validate interval mode
  if (chainSettings.value.timingType === 'interval') {
    // Start date/time is always required for calculating subsequent messages
    // If sendFirstImmediately is checked and no start date/time is set, we'll use current time
    // But it's better to let the user set it explicitly for subsequent messages
    if (!chainSettings.value.startDate || !chainSettings.value.startTime) {
      if (!chainSettings.value.sendFirstImmediately) {
        alert('Please set a start date and time for interval chains')
        return
      }
      // If sendFirstImmediately is checked, we'll use current time, but warn the user
      // that subsequent messages will be calculated from now
    }
  }
  
  // Determine chain timezone for interval mode
  const chainTimezoneToUse = chainSettings.value.timingType === 'interval'
    ? (chainSettings.value.timezone === 'my' 
        ? userTimezone.value 
        : (props.contact.timezone || 'UTC'))
    : null
  
  // Process messages based on timing type
  const processedChain = messageChain.value.map((msg, index) => {
    // Combine body and footer
    let messageBody = msg.body || ''
    if (chainFooter.value && chainFooter.value.trim()) {
      messageBody += '\n\n' + chainFooter.value.trim()
    }
    
    const processedMsg = {
      ...msg,
      body: messageBody,
      subject: hasEmail.value ? chainSubject.value : ''
    }
    
    // Determine timezone to use
    const timezoneToUse = (msg.timezone || 'my') === 'my' 
      ? userTimezone.value 
      : (props.contact.timezone || 'UTC')
    
    if (chainSettings.value.timingType === 'interval') {
      // Interval mode: use frequency_days
      processedMsg.frequency_days = msg.frequency_days || 0
      processedMsg.schedule = false
      
      // Store chain metadata in first message
      if (index === 0) {
        // First message always sends at start time (or immediately), so frequency_days is always 0
        processedMsg.frequency_days = 0
        // Use specified start date/time if provided, otherwise use current time (when sendFirstImmediately is checked)
        if (chainSettings.value.startDate && chainSettings.value.startTime) {
          processedMsg.chain_start_date = chainSettings.value.startDate
          processedMsg.chain_start_time = chainSettings.value.startTime
          processedMsg.chain_timezone = chainTimezoneToUse
        } else if (chainSettings.value.sendFirstImmediately) {
          // If sendFirstImmediately is checked but no start time set, use current time
          processedMsg.chain_start_date = new Date().toISOString().split('T')[0]
          processedMsg.chain_start_time = new Date().toTimeString().slice(0, 5)
          processedMsg.chain_timezone = chainTimezoneToUse
        } else {
          // Fallback: use specified or default
          processedMsg.chain_start_date = chainSettings.value.startDate || new Date().toISOString().split('T')[0]
          processedMsg.chain_start_time = chainSettings.value.startTime || '09:00'
          processedMsg.chain_timezone = chainTimezoneToUse
        }
        processedMsg.sent = false // Track if this message has been sent
      } else {
        processedMsg.sent = false // Track if this message has been sent
      }
    } else {
      // Specific mode: use send_date and send_time
      processedMsg.send_date = msg.send_date || ''
      processedMsg.send_time = msg.send_time || '09:00'
      processedMsg.schedule = true
      processedMsg.timezone = timezoneToUse
      processedMsg.frequency_days = 0
    }
    
    return processedMsg
  })
  
  // Store the chain as JSON
  const chainsJson = JSON.stringify([processedChain])
  
  try {
    // If interval mode and sendFirstImmediately, send the first message now
    if (chainSettings.value.timingType === 'interval' && chainSettings.value.sendFirstImmediately && processedChain.length > 0) {
      const firstMessage = processedChain[0]
      try {
        // Body already includes footer from processing above
        await sendEmail({
          to_email: props.contact.email || props.contact.codementor_username,
          subject: firstMessage.subject || 'No subject',
          body: firstMessage.body
        })
        // Mark first message as sent
        firstMessage.sent = true
        // Update the chain JSON with sent flag
        const updatedChain = [processedChain]
        const updatedChainsJson = JSON.stringify(updatedChain)
        
        const updatedContact = await updateContact(props.contact.id, {
          ...props.contact,
          message_chains: updatedChainsJson
        })
        
        Object.assign(props.contact, { message_chains: updatedChainsJson })
        emit('update', { ...props.contact, message_chains: updatedChainsJson })
        emit('send-message', processedChain)
        
        alert('First message sent! Remaining messages will be sent based on the interval schedule.')
        return
      } catch (error) {
        console.error('Error sending first message:', error)
        alert('Error sending first message: ' + (error.message || 'Unknown error'))
        // Continue to save the chain anyway
      }
    }
    
    const updatedContact = await updateContact(props.contact.id, {
      ...props.contact,
      message_chains: chainsJson
    })
    
    // Update local contact data to refresh upcoming messages
    Object.assign(props.contact, { message_chains: chainsJson })
    emit('update', { ...props.contact, message_chains: chainsJson })
    emit('send-message', processedChain)
  } catch (error) {
    console.error('Error saving message chain:', error)
    alert('Error saving message chain: ' + (error.message || 'Unknown error'))
  }
}

watch(() => props.contact, (newContact) => {
  if (newContact) {
    editingContact.value = { ...newContact }
    loadNotes()
    loadMessageChain()
  }
}, { immediate: true })

// Sync footer with default from settings (only if empty)
watch(() => settings.value?.user?.footer, (newFooter) => {
  if (newFooter && !chainFooter.value) {
    chainFooter.value = newFooter
  }
}, { immediate: true })
</script>

