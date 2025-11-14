<template>
  <div v-if="contact" :class="isModal ? 'fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4' : 'min-h-screen'">
    <div :class="isModal ? 'bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 w-full max-w-6xl max-h-[90vh] flex flex-col' : 'bg-slate-800/90 backdrop-blur-sm flex flex-col min-h-screen'">

      <!-- Header -->
      <div class="p-6 border-b border-slate-700/50">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-thin text-slate-100 mb-1">{{ contact.name }}</h3>
            <p class="text-slate-400 text-sm">{{ contact.email || contact.codementor_username || 'No contact info' }}</p>
            <div class="flex items-center gap-3 mt-2">
              <p v-if="editingContact.timezone || contact.timezone" class="text-slate-500 text-xs">
                <Icon name="lucide:clock" class="w-3 h-3 inline mr-1" />
                Contact's time: {{ contactCurrentTime }}
              </p>
              <a v-if="contact.codementor_username" 
                 :href="`https://www.codementor.io/@${contact.codementor_username}`" 
                 target="_blank"
                 class="text-blue-400 hover:text-blue-300 text-xs flex items-center gap-1 transition-colors">
                <Icon name="simple-icons:codementor" class="w-4 h-4" />
                Codementor Profile
              </a>
              <a v-if="contact.email" 
                 :href="`https://mail.google.com/mail/?view=cm&to=${contact.email}`" 
                 target="_blank"
                 class="text-blue-400 hover:text-blue-300 text-xs flex items-center gap-1 transition-colors">
                <Icon name="lucide:mail" class="w-4 h-4" />
                Open in Gmail
              </a>
            </div>
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
                <label class="block text-sm font-light text-slate-300 mb-1">Preferred Name</label>
                <input v-model="editingContact.preferred_name" type="text"
                       class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors"
                       placeholder="Leave blank to use first name">
              </div>
              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Gender</label>
                <div class="flex items-center bg-slate-600/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                  <button 
                    @click="editingContact.gender = ''"
                    :class="editingContact.gender === '' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                    class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                    Not specified
                  </button>
                  <button 
                    @click="editingContact.gender = 'male'"
                    :class="editingContact.gender === 'male' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                    class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                    Male
                  </button>
                  <button 
                    @click="editingContact.gender = 'female'"
                    :class="editingContact.gender === 'female' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                    class="px-3 py-1.5 rounded-md transition-colors text-xs font-light">
                    Female
                  </button>
                </div>
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
              <PlatformMultiSelect
                v-model="editingContact.platform_preference"
                :available-platforms="preferenceAvailablePlatforms"
                label="Platform Preference"
                label-class="block text-sm font-light text-slate-300 mb-1"
              />
              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Timezone</label>
                <select v-model="editingContact.timezone"
                        class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
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
                        class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
                  <option :value="true">Active</option>
                  <option :value="false">Inactive</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-light text-slate-300 mb-1">Source</label>
                <input v-model="editingContact.source" type="text"
                       class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors"
                       placeholder="e.g., manual, codementor, csv">
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
                          class="w-full bg-slate-600/50 border border-emerald-500/50 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors resize-none"
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
              <!-- Template Selection -->
              <div>
                <label class="block text-xs font-light text-slate-300 mb-1">Template (optional)</label>
                <select v-model="selectedTemplate" @change="applyTemplate"
                        class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors [&>option]:bg-slate-700 [&>option]:text-slate-100">
                  <option value="">None</option>
                  <option v-for="template in activeTemplates" :key="template.id" :value="template.id">{{ template.name }}</option>
                </select>
              </div>
              
              <!-- Subject (only for email) -->
              <div v-if="singleMessage.platforms.includes('email')">
                <label class="block text-xs font-light text-slate-300 mb-1">Subject *</label>
                <input v-model="singleMessage.subject" type="text" required
                       class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors"
                       placeholder="Message subject">
              </div>
              
              <div>
                <label class="block text-xs font-light text-slate-300 mb-1">Message *</label>
                <textarea v-model="singleMessage.body" rows="5" required
                          class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                          placeholder="Enter your message here..."></textarea>
              </div>
              
              <!-- Platform Selection -->
              <PlatformMultiSelect
                v-model="singleMessage.platforms"
                :available-platforms="singleMessageAvailablePlatforms"
                label="Platforms"
                label-class="block text-xs font-light text-slate-300 mb-2"
              />
              
              <div v-if="singleMessage.schedule" class="space-y-3">
                <div class="flex items-end gap-3">
                  <div class="flex-1">
                    <label class="block text-xs font-light text-slate-300 mb-1">Send Date</label>
                    <input v-model="singleMessage.send_date" type="date"
                           class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                  </div>
                  <div class="flex-1">
                    <label class="block text-xs font-light text-slate-300 mb-1">Send Time</label>
                    <input v-model="singleMessage.send_time" type="time"
                           class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
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
              <!-- Subject (only for email) -->
              <div v-if="chainSettings.platforms.includes('email')">
                <label class="block text-xs font-light text-slate-300 mb-2">Subject (applies to all messages) *</label>
                <input v-model="chainSubject" type="text" required
                       class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors"
                       placeholder="Message subject">
              </div>
              
              <div>
                <label class="block text-xs font-light text-slate-300 mb-2">Footer/Signature (applies to all messages)</label>
                <textarea v-model="chainFooter" rows="3"
                          class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                          placeholder="Message footer"></textarea>
              </div>
              
              <!-- Platform Selection -->
              <PlatformMultiSelect
                v-model="chainSettings.platforms"
                :available-platforms="chainAvailablePlatforms"
                label="Platforms"
                label-class="block text-xs font-light text-slate-300 mb-2"
              />
              
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
                               class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                      </div>
                      <div class="flex-1">
                        <label class="block text-xs font-light text-slate-300 mb-1">Start Time</label>
                        <input v-model="chainSettings.startTime" type="time"
                               class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
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
                              class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                              placeholder="Enter your message here..."></textarea>
                  </div>
                  
                  <!-- Interval Mode -->
                  <div v-if="chainSettings.timingType === 'interval' && index > 0">
                    <label class="block text-xs font-light text-slate-300 mb-1">
                      Days after previous message
                    </label>
                    <input v-model.number="message.frequency_days" type="number" min="0" step="1"
                           class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors"
                           placeholder="0 = send immediately after previous">
                  </div>
                  
                  <!-- Specific Date/Time Mode -->
                  <div v-else-if="chainSettings.timingType === 'specific'" class="space-y-2">
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
            
          <!-- Right: Upcoming Messages / History (1/3 width) -->
          <div class="w-1/3 relative pb-6 flex flex-col">
            <div class="flex flex-col p-6 min-h-0 sticky top-0">
              <div class="flex items-center justify-between mb-4">
                <h4 class="text-lg font-light text-slate-100">
                  {{ showMessageHistory ? 'Message History' : 'Upcoming Messages' }}
                </h4>
                <button @click="showMessageHistory = !showMessageHistory"
                        class="text-slate-400 hover:text-slate-200 transition-colors flex items-center"
                        :title="showMessageHistory ? 'Show upcoming messages' : 'Show message history'">
                  <Icon :name="showMessageHistory ? 'lucide:calendar' : 'solar:history-bold'" class="w-5 h-5" />
                </button>
              </div>
              
              <!-- Upcoming Messages View -->
              <div v-if="!showMessageHistory">
                <div v-if="allUpcomingMessages.length === 0" class="text-center py-8 text-slate-400 text-sm">
                  No upcoming messages scheduled
                </div>
                <div v-else class="space-y-3 overflow-y-auto">
                <div v-for="(item, index) in allUpcomingMessages" :key="item.id || `msg-${index}`" 
                     class="bg-slate-600/30 rounded-lg border border-slate-500/20 overflow-hidden">
                  <div class="p-3">
                    <div class="flex items-start justify-between mb-2">
                      <div class="flex-1">
                        <div v-if="item.type === 'message_sequence'" class="flex items-center gap-2 mb-1">
                          <div class="flex items-center gap-1">
                            <Icon name="mage:link" class="w-4 h-4 !text-emerald-400" />
                            <span class="text-slate-100 font-medium text-sm">{{ getSequenceTitle(item.sequenceId) }}</span>
                          </div>
                          <span class="text-xs text-slate-400">({{ item.unsentCount }} remaining)</span>
                        </div>
                        <div v-else-if="item.type === 'standalone' && editingMessage && !editingMessage.sequenceId && editingMessage.messageId === item.message?.id" class="space-y-3">
                          <div v-if="item.message?.platforms?.includes('email')">
                            <label class="block text-xs font-light text-slate-300 mb-1">Subject</label>
                            <input v-model="editingMessageData.subject"
                                   type="text"
                                   class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none"
                                   placeholder="Message subject" />
                          </div>
                          <div>
                            <label class="block text-xs font-light text-slate-300 mb-1">Body</label>
                            <textarea v-model="editingMessageData.body"
                                      rows="4"
                                      class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none resize-none"
                                      placeholder="Message body"></textarea>
                          </div>
                          <div class="flex gap-2">
                            <button @click="saveEditedMessage()"
                                    class="px-3 py-1.5 bg-emerald-500/20 text-emerald-300 rounded-lg text-xs hover:bg-emerald-500/30 transition-colors">
                              Save
                            </button>
                            <button @click="cancelEditingMessage"
                                    class="px-3 py-1.5 bg-slate-600/50 text-slate-300 rounded-lg text-xs hover:bg-slate-600/70 transition-colors">
                              Cancel
                            </button>
                          </div>
                        </div>
                        <div v-else class="text-slate-100 font-medium text-sm">{{ item.campaign_name || item.title }}</div>
                        <div v-if="item.type !== 'standalone' || !editingMessage || editingMessage.sequenceId !== null || editingMessage.messageId !== item.message?.id" class="text-xs text-slate-400 mb-2">{{ item.campaign_description || item.description || (item.type === 'standalone' && item.message ? (item.message.body?.substring(0, 100) + (item.message.body?.length > 100 ? '...' : '')) : 'No description') }}</div>
                        <div class="flex flex-col space-y-2 text-xs">
                          <span class="text-slate-400">
                            <Icon name="lucide:calendar" class="w-3 h-3 inline mr-1" />
                            {{ formatDate(item.next_send_date || item.send_date) }}
                          </span>
                          <div class="flex items-center gap-2 flex-wrap">
                            <span v-if="item.status" :class="getStatusClass(item.status)" class="inline-flex px-2 py-1 rounded-full text-xs w-fit">
                              {{ item.status }}
                            </span>
                            <span v-else class="inline-flex px-2 py-1 rounded-full text-xs w-fit bg-blue-500/20 text-blue-400 border border-blue-500/30">
                              Scheduled
                            </span>
                            <span v-if="item.platforms && item.platforms.length > 0" class="flex gap-1">
                              <span v-for="platform in item.platforms" :key="platform"
                                    class="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded text-xs">
                                {{ platform === 'email' ? 'Email' : 'Codementor' }}
                              </span>
                            </span>
                          </div>
                        </div>
                      </div>
                      <div class="flex items-start gap-2">
                        <button v-if="item.type === 'standalone' && item.message && item.message.status === 'pending'"
                                @click.stop="sendPendingMessage(null, item.message.id)"
                                class="text-emerald-400 hover:text-emerald-300 transition-colors"
                                title="Send now">
                          <Icon name="lucide:send" class="w-4 h-4" />
                        </button>
                        <button v-if="item.type === 'standalone' && item.message && item.message.status === 'pending' && (!editingMessage || editingMessage.sequenceId !== null || editingMessage.messageId !== item.message.id)"
                                @click.stop="startEditingMessage(null, item.message.id)"
                                class="text-slate-400 hover:text-slate-200 transition-colors"
                                title="Edit message">
                          <Icon name="lucide:pencil" class="w-4 h-4" />
                        </button>
                        <button v-if="!item.type && item.next_message"
                                @click.stop="sendCampaignMessage(item)"
                                class="text-emerald-400 hover:text-emerald-300 transition-colors"
                                title="Send now">
                          <Icon name="lucide:send" class="w-4 h-4" />
                        </button>
                        <button v-if="item.type === 'message_sequence'" 
                                @click.stop="cancelSequence(item.sequenceId)"
                                class="px-2 py-1 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition-colors"
                                title="Cancel sequence">
                          Cancel
                        </button>
                        <button v-if="item.type === 'message_sequence'"
                                @click.stop="toggleMessageDetail(index)"
                                class="text-slate-400 hover:text-slate-200 transition-colors">
                          <Icon :name="expandedMessageIndex === index ? 'lucide:chevron-up' : 'lucide:chevron-down'" class="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <!-- Expanded Message Details (only for message sequences) -->
                  <div v-if="expandedMessageIndex === index && item.type === 'message_sequence'" class="border-t border-slate-500/30">
                    <div class="p-3 pt-5 flex flex-col items-center">
                      <template v-for="(msg, msgIndex) in getSequenceMessages(item.sequenceId)" :key="msg.id || msgIndex">
                        <!-- Chain connector line -->
                        <div v-if="msgIndex > 0" class="w-[1px] h-6 " :class="msg.status === 'sent' ? 'bg-emerald-500/70' : 'bg-slate-500/30'"></div>
                        <div class="relative w-full bg-slate-700/50 rounded-lg p-3 border " :class="msg.status === 'sent' ? 'border-emerald-500/70' : 'border-transparent'">
                          <div class="absolute top-0 left-0 -translate-x-1/2 -translate-y-1/2 w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium z-10 border-2"
                               :class="msg.status === 'sent' ? 'bg-emerald-800 text-emerald-400 border-emerald-600' : msg.status === 'cancelled' ? 'bg-red-800 text-red-400 border-red-600' : 'bg-blue-800 text-blue-400 border-blue-600'">
                            {{ msgIndex + 1 }}
                          </div>
                          <div>
                            <div class="flex items-center justify-between mb-2 flex-wrap gap-2">
                              <div class="flex items-center gap-2 text-xs text-slate-400">
                                <Icon name="lucide:calendar" class="w-3 h-3" />
                                <span v-if="getMessageSendDate(item.sequenceId, msg.id)">
                                  {{ formatDate(getMessageSendDate(item.sequenceId, msg.id)) }}
                                </span>
                                <span v-else>No date set</span>
                              </div>
                              <div class="flex items-center gap-2 text-xs">
                                <span v-if="msg.status === 'sent'" class="text-emerald-400">✓ Sent</span>
                                <span v-else-if="msg.status === 'cancelled'" class="text-red-400">✗ Cancelled</span>
                                <span v-else class="text-blue-400">Pending</span>
                                <button v-if="msg.status === 'pending' && (!editingMessage || editingMessage.sequenceId !== item.sequenceId || editingMessage.messageId !== msg.id)"
                                        @click="sendPendingMessage(item.sequenceId, msg.id)"
                                        class="text-emerald-400 hover:text-emerald-300 transition-colors"
                                        title="Send now">
                                  <Icon name="lucide:send" class="w-3 h-3" />
                                </button>
                                <button v-if="msg.status === 'pending' && (!editingMessage || editingMessage.sequenceId !== item.sequenceId || editingMessage.messageId !== msg.id)"
                                        @click="startEditingMessage(item.sequenceId, msg.id)"
                                        class="text-slate-400 hover:text-slate-200 transition-colors"
                                        title="Edit message">
                                  <Icon name="lucide:pencil" class="w-3 h-3" />
                                </button>
                              </div>
                            </div>
                            
                            <!-- Edit Mode -->
                            <div v-if="editingMessage && editingMessage.sequenceId === item.sequenceId && editingMessage.messageId === msg.id" class="space-y-3">
                              <div v-if="getSequenceMessages(item.sequenceId)[0]?.platforms?.includes('email')">
                                <label class="block text-xs font-light text-slate-300 mb-1">Subject</label>
                                <input v-model="editingMessageData.subject"
                                       type="text"
                                       class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none"
                                       placeholder="Message subject" />
                              </div>
                              <div>
                                <label class="block text-xs font-light text-slate-300 mb-1">Body</label>
                                <textarea v-model="editingMessageData.body"
                                          rows="4"
                                          class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none resize-none"
                                          placeholder="Message body"></textarea>
                              </div>
                              <div class="flex gap-2">
                                <button @click="saveEditedMessage()"
                                        class="px-3 py-1.5 bg-emerald-500/20 text-emerald-300 rounded-lg text-xs hover:bg-emerald-500/30 transition-colors">
                                  Save
                                </button>
                                <button @click="cancelEditingMessage"
                                        class="px-3 py-1.5 bg-slate-600/50 text-slate-300 rounded-lg text-xs hover:bg-slate-600/70 transition-colors">
                                  Cancel
                                </button>
                              </div>
                            </div>
                            
                            <!-- View Mode -->
                            <div v-else>
                              <div v-if="msg.subject" class="text-slate-100 text-sm font-medium mb-2">{{ msg.subject }}</div>
                              <div class="text-slate-300 text-sm whitespace-pre-wrap">{{ msg.body || 'No content' }}</div>
                            </div>
                          </div>
                        </div>
                      </template>
                    </div>
                  </div>
                </div>
                </div>
              </div>
              
              <!-- Message History View -->
              <div v-else>
                <div v-if="messageHistory.length === 0" class="text-center py-8 text-slate-400 text-sm">
                  No messages sent yet
                </div>
                <div v-else class="space-y-3 overflow-y-auto">
                  <div v-for="(msg, index) in messageHistory" :key="msg.id || index"
                       class="bg-slate-600/30 rounded-lg p-3 border border-slate-500/20">
                    <div class="flex items-start justify-between mb-2">
                      <div class="text-xs text-slate-400">
                        <Icon name="lucide:clock" class="w-3 h-3 inline mr-1" />
                        {{ formatDate(msg.sent_at) }}
                      </div>
                      <div class="flex gap-1">
                        <span v-for="platform in msg.platforms" :key="platform"
                              class="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded text-xs">
                          {{ platform === 'email' ? 'Email' : 'Codementor' }}
                        </span>
                      </div>
                    </div>
                    <div v-if="msg.subject" class="text-slate-200 text-sm font-medium mb-1">{{ msg.subject }}</div>
                    <div class="text-slate-300 text-sm whitespace-pre-wrap">{{ msg.body }}</div>
                    <div class="mt-2 text-xs">
                      <span :class="msg.status === 'sent' ? 'text-emerald-400' : 'text-red-400'">
                        {{ msg.status === 'sent' ? '✓ Sent' : msg.status }}
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

const { updateContact, sendEmail, sendMessage, settings, loadContacts, templates } = useApi()
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
const expandedMessageIndex = ref(-1)
const showMessageHistory = ref(false)
const editingMessage = ref(null) // { messageId: number } or { sequenceId: number, messageId: number }
const editingMessageData = ref({ subject: '', body: '' })
const chainSubject = ref('')
const chainFooter = ref(settings.value?.user?.footer || '')
const selectedTemplate = ref('')

const activeTemplates = computed(() => {
  return templates.value.filter(t => t.is_active)
})

const applyTemplate = () => {
  if (!selectedTemplate.value) return
  const template = templates.value.find(t => t.id === parseInt(selectedTemplate.value))
  if (template) {
    if (template.subject) {
      singleMessage.value.subject = template.subject
    }
    if (template.body) {
      singleMessage.value.body = template.body
      // For email, append footer: template footer if exists, otherwise user settings footer
      if (singleMessage.value.platforms.includes('email')) {
        const footerToUse = template.footer || settings.value?.user?.footer || ''
        if (footerToUse) {
          singleMessage.value.body = singleMessage.value.body + '\n\n' + footerToUse
        }
      }
    }
  }
}
const messageSequencesData = ref([]) // Fetched from API
const messageHistoryData = ref([]) // Fetched from API
const standalonePendingMessages = ref([]) // Standalone scheduled messages (no sequence)
const { apiCall, apiFetch, API_BASE } = useApiFetch()
const chainSettings = ref({
  platforms: [], // ['email', 'codementor']
  sendFirstImmediately: false,
  timingType: 'interval', // 'interval' or 'specific'
  startDate: '',
  startTime: '09:00',
  timezone: 'my' // 'my' or 'user'
})
// Available platforms computed properties for the component
const singleMessageAvailablePlatforms = computed(() => {
  const allPlatforms = []
  if (props.contact.email) allPlatforms.push('email')
  if (props.contact.codementor_username) allPlatforms.push('codementor')
  return allPlatforms
})

const chainAvailablePlatforms = computed(() => {
  const allPlatforms = []
  if (props.contact.email) allPlatforms.push('email')
  if (props.contact.codementor_username) allPlatforms.push('codementor')
  return allPlatforms
})

const preferenceAvailablePlatforms = computed(() => {
  const allPlatforms = []
  if (props.contact.email) allPlatforms.push('email')
  if (props.contact.codementor_username) allPlatforms.push('codementor')
  return allPlatforms
})
const getTodayDate = () => {
  return new Date().toISOString().split('T')[0]
}

const getCurrentTime = () => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

const singleMessage = ref({
  platforms: [], // Will be set from defaultPlatforms
  subject: '',
  body: '',
  send_date: getTodayDate(),
  send_time: getCurrentTime(),
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

const defaultPlatforms = computed(() => {
  // Handle both old format (string) and new format (array)
  let preference = props.contact.platform_preference
  if (!preference) {
    preference = props.contact.email ? ['email'] : []
  } else if (typeof preference === 'string') {
    // Legacy format: 'email', 'codementor', or 'both'
    if (preference === 'both') {
      preference = ['email', 'codementor']
    } else {
      preference = [preference]
    }
  }
  // Ensure it's an array
  if (!Array.isArray(preference)) {
    preference = []
  }
  // Filter to only platforms the contact actually has
  return preference.filter(p => {
    if (p === 'email') return !!props.contact.email
    if (p === 'codementor') return !!props.contact.codementor_username
    return false
  })
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

// Fetch message sequences and history from API
const loadMessageSequences = async () => {
  try {
    messageSequencesData.value = await apiCall(`/message-sequences/?contact_id=${props.contact.id}`)
  } catch (e) {
    console.error('Error loading message sequences:', e)
  }
}

const loadMessageHistory = async () => {
  try {
    messageHistoryData.value = await apiCall(`/messages/?contact_id=${props.contact.id}&status=sent`)
  } catch (e) {
    console.error('Error loading message history:', e)
  }
}

const loadStandalonePendingMessages = async () => {
  try {
    const allPending = await apiCall(`/messages/?contact_id=${props.contact.id}&status=pending`)
    // Filter to only messages without a sequence (standalone scheduled messages)
    standalonePendingMessages.value = allPending.filter(msg => !msg.sequence)
  } catch (e) {
    console.error('Error loading standalone pending messages:', e)
  }
}

onMounted(() => {
  loadNotes()
  loadMessageSequences()
  loadMessageHistory()
  loadStandalonePendingMessages()
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

const messageSequences = computed(() => {
  const sequences = []
  const now = new Date()
  
  messageSequencesData.value.forEach((sequence) => {
    // Get all messages for this sequence, sorted by order
    const messages = (sequence.messages || []).sort((a, b) => a.order - b.order)
    
    // Filter to only pending messages (not sent, not cancelled)
    const unsentMessages = messages.filter(msg => msg.status === 'pending')
    
    if (unsentMessages.length === 0) {
      return // Skip sequences with no unsent messages
    }
    
    // Get earliest unsent message date
    let earliestSendDate = null
    const firstMsg = messages[0]
    
    if (sequence.timing_type === 'interval' && sequence.chain_start_date && sequence.chain_start_time) {
      // Interval chain - calculate dates for all unsent messages
      try {
        const startDateStr = `${sequence.chain_start_date}T${sequence.chain_start_time}`
        const chainStartDate = new Date(startDateStr)
        
        messages.forEach((msg, index) => {
          if (msg.status !== 'pending') return
          
          // Calculate cumulative days
          let cumulativeDays = 0
          for (let i = 0; i < index; i++) {
            cumulativeDays += (messages[i].frequency_days || 0)
          }
          cumulativeDays += (msg.frequency_days || 0)
          
          // Calculate this message's send date
          const msgSendDate = new Date(chainStartDate)
          msgSendDate.setDate(msgSendDate.getDate() + cumulativeDays)
          
          // Include all pending messages, even if overdue
          if (!earliestSendDate || msgSendDate < earliestSendDate) {
            earliestSendDate = msgSendDate
          }
        })
      } catch (e) {
        console.error('Error parsing interval chain dates:', e)
      }
    } else {
      // Specific date chain - check all unsent messages
      for (const msg of unsentMessages) {
        if (msg.send_date && msg.send_time) {
          try {
            const sendDateStr = `${msg.send_date}T${msg.send_time}`
            const sendDate = new Date(sendDateStr)
            // Include all pending messages, even if overdue
            if (!earliestSendDate || sendDate < earliestSendDate) {
              earliestSendDate = sendDate
            }
          } catch (e) {
            console.error('Error parsing send date:', e)
          }
        }
      }
    }
    
    // Show sequence if there's at least one pending message (even if overdue)
    if (earliestSendDate) {
      sequences.push({
        id: sequence.id,
        sequenceId: sequence.id,
        title: firstMsg?.subject || firstMsg?.body?.substring(0, 50) + '...' || 'Message Sequence',
        description: `Message Sequence (${unsentMessages.length} message${unsentMessages.length > 1 ? 's' : ''})`,
        send_date: earliestSendDate.toISOString(),
        type: 'message_sequence',
        totalMessages: messages.length,
        unsentCount: unsentMessages.length,
        platforms: firstMsg?.platforms || []
      })
    }
  })
  
  return sequences.sort((a, b) => new Date(a.send_date) - new Date(b.send_date))
})

const allUpcomingMessages = computed(() => {
  // Convert standalone pending messages to the format expected by the UI
  // Include all pending messages, even if their send date has passed (overdue)
  const standaloneMessages = standalonePendingMessages.value
    .filter(msg => {
      // Include messages with send_date and send_time (even if overdue)
      return !!(msg.send_date && msg.send_time)
    })
    .map(msg => ({
      id: msg.id,
      type: 'standalone',
      title: msg.subject || msg.body?.substring(0, 50) + '...' || 'Scheduled Message',
      description: msg.body?.substring(0, 100) + (msg.body?.length > 100 ? '...' : '') || 'No content',
      send_date: `${msg.send_date}T${msg.send_time}`,
      platforms: msg.platforms || [],
      status: 'pending',
      message: msg // Store full message object for editing
    }))
  
  const all = [...props.upcomingMessages, ...messageSequences.value, ...standaloneMessages]
  return all.sort((a, b) => {
    const dateA = new Date(a.next_send_date || a.send_date)
    const dateB = new Date(b.next_send_date || b.send_date)
    return dateA - dateB
  })
})

// Message history from contact
const messageHistory = computed(() => {
  return messageHistoryData.value.sort((a, b) => {
    const dateA = new Date(a.sent_at || 0)
    const dateB = new Date(b.sent_at || 0)
    return dateB - dateA // Most recent first
  })
})

const toggleMessageDetail = (index) => {
  if (expandedMessageIndex.value === index) {
    expandedMessageIndex.value = -1
  } else {
    expandedMessageIndex.value = index
  }
}

const getSequenceMessages = (sequenceId) => {
  const sequence = messageSequencesData.value.find(s => s.id === sequenceId)
  if (sequence && sequence.messages) {
    return sequence.messages.sort((a, b) => a.order - b.order)
  }
  return []
}

const getSequenceTitle = (sequenceId) => {
  const sequence = messageSequencesData.value.find(s => s.id === sequenceId)
  if (sequence && sequence.messages && sequence.messages.length > 0) {
    const firstMsg = sequence.messages[0]
    return firstMsg.subject || firstMsg.body?.substring(0, 50) + '...' || 'Message Sequence'
  }
  return 'Message Sequence'
}

const getMessageSendDate = (sequenceId, messageId) => {
  const sequence = messageSequencesData.value.find(s => s.id === sequenceId)
  if (!sequence) return null
  
  const message = sequence.messages?.find(m => m.id === messageId)
  if (!message) return null
  
  // If message has specific send_date and send_time, use those
  if (message.send_date && message.send_time) {
    // Ensure time format includes seconds for proper parsing
    const time = message.send_time.includes(':') && message.send_time.split(':').length === 2 
      ? `${message.send_time}:00` 
      : message.send_time
    return `${message.send_date}T${time}`
  }
  
  // If it's an interval chain, calculate from chain_start_date
  if (sequence.timing_type === 'interval' && sequence.chain_start_date && sequence.chain_start_time) {
    try {
      // Ensure time format includes seconds
      const startTime = sequence.chain_start_time.includes(':') && sequence.chain_start_time.split(':').length === 2
        ? `${sequence.chain_start_time}:00`
        : sequence.chain_start_time
      const startDateStr = `${sequence.chain_start_date}T${startTime}`
      const chainStartDate = new Date(startDateStr)
      
      // Calculate cumulative days up to this message
      const messages = sequence.messages.sort((a, b) => a.order - b.order)
      let cumulativeDays = 0
      for (const msg of messages) {
        if (msg.id === messageId) break
        cumulativeDays += (msg.frequency_days || 0)
      }
      // Add this message's frequency_days
      cumulativeDays += (message.frequency_days || 0)
      
      const sendDate = new Date(chainStartDate)
      sendDate.setDate(sendDate.getDate() + cumulativeDays)
      
      // Format as ISO string for consistency
      const year = sendDate.getFullYear()
      const month = String(sendDate.getMonth() + 1).padStart(2, '0')
      const day = String(sendDate.getDate()).padStart(2, '0')
      const time = sequence.chain_start_time || '09:00'
      const formattedTime = time.includes(':') && time.split(':').length === 2 ? `${time}:00` : time
      
      return `${year}-${month}-${day}T${formattedTime}`
    } catch (e) {
      console.error('Error calculating send date:', e)
    }
  }
  
  return null
}

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
  try {
    // Handle ISO format strings (YYYY-MM-DDTHH:MM or YYYY-MM-DDTHH:MM:SS)
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return 'Invalid date'
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (e) {
    console.error('Error formatting date:', e, dateString)
    return 'Invalid date'
  }
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
  // Always start with empty chain - form is for creating NEW chains only
  messageChain.value = []
  chainSubject.value = ''
  chainFooter.value = settings.value?.user?.footer || ''
  chainSettings.value = {
    platforms: [...defaultPlatforms.value], // Set default platforms
    sendFirstImmediately: false,
    timingType: 'interval',
    startDate: getTodayDate(),
    startTime: getCurrentTime(),
    timezone: 'my'
  }
}

const addMessageToChain = () => {
  const newMessage = {
    body: '',
    frequency_days: 1,
    send_date: getTodayDate(),
    send_time: getCurrentTime(),
    timezone: 'my'
  }
  messageChain.value.push(newMessage)
}

const handleChainModeToggle = () => {
  isChainMode.value = true
  // Always start fresh - clear any old data
  loadMessageChain()
  // Add the first message when switching to chain mode
  addMessageToChain()
}

const saveSingleMessage = async () => {
  if (!singleMessage.value.body.trim()) {
    alert('Please fill in the message body')
    return
  }

  if (!singleMessage.value.platforms || singleMessage.value.platforms.length === 0) {
    alert('Please select at least one platform')
    return
  }

  if (singleMessage.value.platforms.includes('email') && !singleMessage.value.subject.trim()) {
    alert('Subject is required for email messages')
    return
  }
  
  try {
    // If sending now (not scheduled), send immediately
    if (!singleMessage.value.schedule) {
      await sendMessage(props.contact.id, {
        platforms: singleMessage.value.platforms,
        subject: singleMessage.value.subject || '',
        body: singleMessage.value.body
      })
      
      emit('send-message', { ...singleMessage.value, sent: true })
    } else {
      // If scheduled, create a Message object via API
      const timezoneToUse = singleMessage.value.timezone === 'my' 
        ? userTimezone.value 
        : (props.contact.timezone || 'UTC')
      
      const createdMessage = await apiCall('/messages/', {
        method: 'POST',
        body: JSON.stringify({
          contact: props.contact.id,
          subject: singleMessage.value.subject || '',
          body: singleMessage.value.body,
          platforms: singleMessage.value.platforms,
          status: 'pending',
          send_date: singleMessage.value.send_date || null,
          send_time: singleMessage.value.send_time || getCurrentTime(),
          timezone: timezoneToUse,
          frequency_days: 0
        })
      })
      
      // Reload sequences and standalone messages to refresh UI
      await loadMessageSequences()
      await loadStandalonePendingMessages()
      emit('send-message', createdMessage)
    }
    
    // Reset form
    singleMessage.value = {
      platforms: [...defaultPlatforms.value], // Reset to default platforms
      subject: '',
      body: '',
      send_date: getTodayDate(),
      send_time: getCurrentTime(),
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

const startEditingMessage = (sequenceId, messageId) => {
  try {
    let msg = null
    
    if (sequenceId) {
      // Message is part of a sequence
      const messages = getSequenceMessages(sequenceId)
      msg = messages.find(m => m.id === messageId)
    } else {
      // Standalone message
      msg = standalonePendingMessages.value.find(m => m.id === messageId)
    }
    
    if (msg && msg.status === 'pending') {
      editingMessage.value = { sequenceId: sequenceId || null, messageId }
      editingMessageData.value = {
        subject: msg.subject || '',
        body: msg.body || ''
      }
    }
  } catch (e) {
    console.error('Error starting message edit:', e)
  }
}

const cancelEditingMessage = () => {
  editingMessage.value = null
  editingMessageData.value = { subject: '', body: '' }
}

const sendPendingMessage = async (sequenceId, messageId) => {
  try {
    let msg = null
    
    if (sequenceId) {
      // Message is part of a sequence
      const messages = getSequenceMessages(sequenceId)
      msg = messages.find(m => m.id === messageId)
    } else {
      // Standalone message
      msg = standalonePendingMessages.value.find(m => m.id === messageId)
    }
    
    if (!msg || msg.status !== 'pending') {
      alert('Message is not pending or not found')
      return
    }
    
    if (!confirm('Send this message now?')) {
      return
    }
    
    // Send the message via API
    await sendMessage(props.contact.id, {
      platforms: msg.platforms || [],
      subject: msg.subject || '',
      body: msg.body || ''
    })
    
    // Update the message status to 'sent' via PATCH
    await apiCall(`/messages/${messageId}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        status: 'sent',
        sent_at: new Date().toISOString()
      })
    })
    
    // Reload sequences and standalone messages to refresh UI
    await loadMessageSequences()
    await loadStandalonePendingMessages()
    await loadMessageHistory()
    
    alert('Message sent successfully!')
  } catch (error) {
    console.error('Error sending pending message:', error)
    alert('Error sending message: ' + (error.message || 'Unknown error'))
  }
}

const sendCampaignMessage = async (item) => {
  try {
    if (!item.next_message) {
      alert('No message content available')
      return
    }
    
    if (!confirm('Send this campaign message now?')) {
      return
    }
    
    // Determine platforms - check if email is available, default to email
    const platforms = []
    if (props.contact.email) {
      platforms.push('email')
    }
    if (props.contact.codementor_username) {
      platforms.push('codementor')
    }
    
    if (platforms.length === 0) {
      alert('Contact has no available platforms')
      return
    }
    
    // Extract subject if it's in the message (campaign messages might have subject in next_message)
    const messageContent = typeof item.next_message === 'string' 
      ? item.next_message 
      : (item.next_message.body || item.next_message || '')
    
    const subject = typeof item.next_message === 'object' && item.next_message.subject
      ? item.next_message.subject
      : (item.campaign_name || '')
    
    // Send the message via API
    await sendMessage(props.contact.id, {
      platforms: platforms,
      subject: subject,
      body: messageContent
    })
    
    // Update the campaign assignment's next_send_date (this would typically be handled by the backend)
    // For now, we'll just show success - the campaign system will handle the next send date
    alert('Campaign message sent successfully!')
    
    // Emit event to refresh campaign data if needed
    emit('update')
  } catch (error) {
    console.error('Error sending campaign message:', error)
    alert('Error sending message: ' + (error.message || 'Unknown error'))
  }
}

const saveEditedMessage = async () => {
  try {
    if (!editingMessageData.value.body.trim()) {
      alert('Message body cannot be empty')
      return
    }

    if (!editingMessage.value || !editingMessage.value.messageId) {
      alert('No message selected for editing')
      return
    }

    const messageId = editingMessage.value.messageId

    // Update the message via API
    await apiCall(`/messages/${messageId}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        subject: editingMessageData.value.subject.trim(),
        body: editingMessageData.value.body.trim()
      })
    })

    // Reload sequences and standalone messages to refresh UI
    await loadMessageSequences()
    await loadStandalonePendingMessages()
    
    // Clear editing state
    cancelEditingMessage()

    alert('Message updated successfully')
  } catch (error) {
    console.error('Error saving edited message:', error)
    alert('Error saving message: ' + (error.message || 'Unknown error'))
  }
}

const cancelSequence = async (sequenceId) => {
  if (!confirm('Are you sure you want to cancel this message sequence? All unsent messages will be cancelled.')) {
    return
  }

  try {
    await apiCall(`/contacts/${props.contact.id}/cancel-chain/`, {
      method: 'POST',
      body: JSON.stringify({ sequence_id: sequenceId })
    })

    // Reload sequences and standalone messages to refresh UI
    await loadMessageSequences()
    await loadStandalonePendingMessages()
    
    // Close expanded view if this sequence was expanded
    if (expandedMessageIndex.value !== -1) {
      const item = allUpcomingMessages.value[expandedMessageIndex.value]
      if (item && item.type === 'message_sequence' && item.sequenceId === sequenceId) {
        expandedMessageIndex.value = -1
      }
    }
    
    alert('Message sequence cancelled successfully')
  } catch (error) {
    console.error('Error cancelling sequence:', error)
    alert('Error cancelling sequence: ' + (error.message || 'Unknown error'))
  }
}

const saveMessageChain = async () => {
  // Validate platforms
  if (!chainSettings.value.platforms || chainSettings.value.platforms.length === 0) {
    alert('Please select at least one platform')
    return
  }

  // Validate subject if email is selected
  if (chainSettings.value.platforms.includes('email') && !chainSubject.value.trim()) {
    alert('Subject is required when email is selected')
    return
  }

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
  
  // Determine chain start date/time for interval mode
  let chainStartDate = null
  let chainStartTime = null
  if (chainSettings.value.timingType === 'interval') {
    if (chainSettings.value.startDate && chainSettings.value.startTime) {
      chainStartDate = chainSettings.value.startDate
      chainStartTime = chainSettings.value.startTime
    } else if (chainSettings.value.sendFirstImmediately) {
      chainStartDate = new Date().toISOString().split('T')[0]
      chainStartTime = new Date().toTimeString().slice(0, 5)
    } else {
      chainStartDate = chainSettings.value.startDate || new Date().toISOString().split('T')[0]
      chainStartTime = chainSettings.value.startTime || '09:00'
    }
  }
  
  try {
    // Create MessageSequence first
    const sequence = await apiCall('/message-sequences/', {
      method: 'POST',
      body: JSON.stringify({
        contact: props.contact.id,
        timing_type: chainSettings.value.timingType,
        chain_start_date: chainStartDate,
        chain_start_time: chainStartTime,
        chain_timezone: chainTimezoneToUse
      })
    })
    
    // Create Message objects for each message in the chain
    const messagePromises = messageChain.value.map(async (msg, index) => {
      // Combine body and footer
      let messageBody = msg.body || ''
      if (chainFooter.value && chainFooter.value.trim()) {
        messageBody += '\n\n' + chainFooter.value.trim()
      }
      
      // Determine timezone to use
      const timezoneToUse = (msg.timezone || 'my') === 'my' 
        ? userTimezone.value 
        : (props.contact.timezone || 'UTC')
      
      const messageData = {
        contact: props.contact.id,
        sequence: sequence.id,
        order: index,
        subject: chainSettings.value.platforms.includes('email') ? chainSubject.value : '',
        body: messageBody,
        platforms: chainSettings.value.platforms,
        status: 'pending'  // Always create as pending, we'll send the first one immediately if needed
      }
      
      if (chainSettings.value.timingType === 'interval') {
        messageData.frequency_days = msg.frequency_days || (index === 0 ? 0 : 1)
        // First message in interval chain doesn't need send_date/time (uses chain start)
        if (index > 0 || !chainSettings.value.sendFirstImmediately) {
          // Will be calculated from chain start
        }
      } else {
        // Specific mode
        messageData.send_date = msg.send_date || null
        messageData.send_time = msg.send_time || getCurrentTime()
        messageData.timezone = timezoneToUse
        messageData.frequency_days = 0
      }
      
      const msgResponse = await fetch(`${API_BASE}/messages/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(messageData)
      })
      
      if (!msgResponse.ok) {
        throw new Error(`Failed to create message ${index + 1}`)
      }
      
      const createdMessage = await msgResponse.json()
      
      // If this is the first message and sendFirstImmediately is true, send it now
      if (index === 0 && chainSettings.value.timingType === 'interval' && chainSettings.value.sendFirstImmediately) {
        try {
          const sendResponse = await fetch(`${API_BASE}/messages/${createdMessage.id}/send-now/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          })
          
          if (sendResponse.ok) {
            const sendResult = await sendResponse.json()
            // Update the created message with the email_message_id
            createdMessage.email_message_id = sendResult.email_message_id
            createdMessage.status = sendResult.status
          }
        } catch (error) {
          console.error('Error sending first message immediately:', error)
          // Don't fail the whole operation, just log the error
        }
      }
      
      return createdMessage
    })
    
    await Promise.all(messagePromises)
    
    // Reload sequences and standalone messages to refresh UI
    await loadMessageSequences()
    await loadStandalonePendingMessages()
    
    // Clear the form after saving
    loadMessageChain()
    isChainMode.value = false
    
    alert('Message sequence created successfully!')
  } catch (error) {
    console.error('Error saving message chain:', error)
    alert('Error saving message chain: ' + (error.message || 'Unknown error'))
  }
}

watch(() => props.contact, (newContact) => {
  if (newContact) {
    editingContact.value = { ...newContact }
    // Convert platform_preference to array if it's a string (legacy format)
    if (editingContact.value.platform_preference && typeof editingContact.value.platform_preference === 'string') {
      if (editingContact.value.platform_preference === 'both') {
        editingContact.value.platform_preference = ['email', 'codementor'].filter(p => {
          if (p === 'email') return !!newContact.email
          if (p === 'codementor') return !!newContact.codementor_username
          return false
        })
      } else {
        editingContact.value.platform_preference = [editingContact.value.platform_preference]
      }
    } else if (!editingContact.value.platform_preference) {
      editingContact.value.platform_preference = []
    }
    loadNotes()
    // Initialize default platforms for single message
    if (!singleMessage.value.platforms || singleMessage.value.platforms.length === 0) {
      singleMessage.value.platforms = [...defaultPlatforms.value]
    }
    // Reload sequences, history, and standalone messages when contact changes
    loadMessageSequences()
    loadMessageHistory()
    loadStandalonePendingMessages()
    // Don't load old chains into the form - form is for creating NEW chains only
    // Old chains are shown in "Upcoming Messages" section
    if (isChainMode.value) {
      loadMessageChain() // Only reset if already in chain mode
    }
  }
}, { immediate: true })

// Initialize platforms when defaultPlatforms changes
watch(defaultPlatforms, (newPlatforms) => {
  // Only set if platforms are empty or if we're adding a new platform that wasn't there
  if (newPlatforms.length > 0) {
    if (singleMessage.value.platforms.length === 0) {
      singleMessage.value.platforms = [...newPlatforms]
    }
  }
}, { immediate: true })

// Sync footer with default from settings (only if empty)
watch(() => settings.value?.user?.footer, (newFooter) => {
  if (newFooter && !chainFooter.value) {
    chainFooter.value = newFooter
  }
}, { immediate: true })
</script>

