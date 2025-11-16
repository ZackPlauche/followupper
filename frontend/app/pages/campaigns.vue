<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl lg:text-4xl font-thin gradient-title mb-2">
          Campaigns
        </h1>
        <p class="text-slate-300 font-light text-sm sm:text-base">Manage your follow-up campaigns and sequences</p>
      </div>
      <div class="flex flex-col sm:flex-row gap-2 sm:gap-3">
        <button @click="showCreateCampaignForm = true"
          class="px-4 sm:px-6 py-2 sm:py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105 text-sm sm:text-base">
          <Icon name="lucide:plus" class="w-4 h-4 sm:w-5 sm:h-5 inline mr-2" />
          <span class="hidden sm:inline">Create Campaign</span>
          <span class="sm:hidden">New Campaign</span>
        </button>
        <button @click="showCreateOneOffForm = true"
          class="px-4 sm:px-6 py-2 sm:py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105 text-sm sm:text-base">
          <Icon name="lucide:user-plus" class="w-4 h-4 sm:w-5 sm:h-5 inline mr-2" />
          <span class="hidden sm:inline">Create One-Off</span>
          <span class="sm:hidden">One-Off</span>
        </button>
      </div>
    </div>

    <!-- Campaigns List -->
    <div v-if="campaigns.length > 0" class="space-y-6">
      <div v-for="campaign in campaigns" :key="campaign.id"
        class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-xl border border-emerald-500/20 p-6">

        <!-- Campaign Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
          <div class="flex items-start sm:items-center space-x-3 sm:space-x-4 flex-1 min-w-0">
            <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl flex items-center justify-center flex-shrink-0"
              :class="getCampaignIconClass(campaign.campaign_type)">
              <Icon :name="getCampaignIcon(campaign.campaign_type)" class="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-lg sm:text-xl font-thin text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400 break-words">
                {{ campaign.name }}
              </h3>
              <p class="text-slate-400 text-xs sm:text-sm break-words">{{ campaign.description || 'No description provided.' }}</p>
            </div>
          </div>
          <div class="flex items-center justify-between sm:justify-end space-x-3 flex-shrink-0">
            <div class="flex items-center space-x-2">
              <div class="w-2 h-2 rounded-full" :class="campaign.is_active ? 'bg-emerald-400' : 'bg-slate-500'"></div>
              <span class="text-xs text-slate-400 hidden sm:inline">{{ campaign.is_active ? 'Active' : 'Inactive' }}</span>
            </div>
            <div class="flex space-x-2">
              <button v-if="campaign.message_template || campaign.next_message_override"
                @click="openTestMessageModal(campaign)"
                class="px-3 sm:px-3 py-2 sm:py-1 bg-blue-600/50 text-blue-300 rounded-lg font-light hover:bg-blue-600/70 transition-colors text-sm">
                Test
              </button>
              <button @click="editCampaign(campaign)"
                class="px-3 sm:px-3 py-2 sm:py-1 bg-slate-600/50 text-slate-300 rounded-lg font-light hover:bg-slate-600/70 transition-colors text-sm">
                Edit
              </button>
              <button @click="handleDeleteCampaign(campaign.id)"
                class="px-3 sm:px-3 py-2 sm:py-1 bg-red-600/50 text-red-300 rounded-lg font-light hover:bg-red-600/70 transition-colors text-sm">
                Delete
              </button>
            </div>
          </div>
        </div>

        <!-- Campaign Details -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div class="text-sm">
            <span class="text-slate-400">Type:</span>
            <span class="text-slate-200 font-medium ml-2 capitalize">{{ campaign.campaign_type.replace('_', ' ')
              }}</span>
          </div>
          <div v-if="campaign.campaign_type === 'recurring'" class="text-sm">
            <span class="text-slate-400">Frequency:</span>
            <span class="text-slate-200 font-medium ml-2">{{ formatFrequency(campaign) }}</span>
          </div>
          <div v-if="campaign.campaign_type === 'sequence'" class="text-sm">
            <span class="text-slate-400">Steps:</span>
            <span class="text-slate-200 font-medium ml-2">{{ campaign.step_count }}</span>
          </div>
          <div class="text-sm">
            <span class="text-slate-400">Assignments:</span>
            <span class="text-slate-200 font-medium ml-2">
              {{ campaign.assignment_counts.active }} active,
              {{ campaign.assignment_counts.paused }} paused,
              {{ campaign.assignment_counts.blacklisted }} blacklisted
            </span>
          </div>
        </div>

        <!-- Assignments Table -->
        <div class="pt-4 border-t border-slate-700/50">
          <div class="flex items-center justify-between mb-3">
            <div class="flex space-x-3">
              <button @click="addAssignment(campaign)"
                class="px-4 py-2 bg-emerald-600/50 text-emerald-300 rounded-lg font-light hover:bg-emerald-600/70 transition-colors text-sm">
                Add Contacts
              </button>
              <button v-if="campaign.campaign_type === 'recurring'" @click="editNextMessage(campaign)"
                class="px-4 py-2 bg-purple-600/50 text-purple-300 rounded-lg font-light hover:bg-purple-600/70 transition-colors text-sm">
                Edit Next Message
              </button>
              <button v-if="selectedAssignmentIds[campaign.id]?.size > 0"
                @click="openBulkEditModal(campaign)"
                class="px-4 py-2 bg-blue-600/50 text-blue-300 rounded-lg font-light hover:bg-blue-600/70 transition-colors text-sm">
                Bulk Edit ({{ selectedAssignmentIds[campaign.id]?.size }})
              </button>
              <button v-if="selectedAssignmentIds[campaign.id]?.size > 0"
                @click="handleBulkDeleteAssignments(campaign)"
                class="px-4 py-2 bg-red-600/50 text-red-300 rounded-lg font-light hover:bg-red-600/70 transition-colors text-sm">
                Delete ({{ selectedAssignmentIds[campaign.id]?.size }})
              </button>
            </div>
          </div>

          <!-- Assignments Table -->
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-700/50">
              <thead class="bg-slate-700/30">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">
                    <input type="checkbox" 
                      :checked="isAllAssignmentsSelected(campaign.id)"
                      @change="toggleSelectAllAssignments(campaign.id)"
                      class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                  </th>
                  <th class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">Contact</th>
                  <th class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">Status</th>
                  <th v-if="campaign.campaign_type === 'recurring'"
                    class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">Frequency</th>
                  <th v-if="campaign.campaign_type === 'sequence'"
                    class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">Current Step</th>
                  <th class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">Next Send</th>
                  <th class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">Message</th>
                  <th class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-slate-800/30 divide-y divide-slate-700/30">
                <tr v-for="assignment in getCampaignAssignments(campaign.id)" :key="assignment.id"
                  :class="assignment.status === 'paused' ? 'opacity-50 hover:bg-slate-700/10' : 'hover:bg-slate-700/20'">
                  <td class="px-4 py-2">
                    <input type="checkbox" 
                      :checked="isAssignmentSelected(campaign.id, assignment.id)"
                      @change="toggleAssignmentSelection(campaign.id, assignment.id)"
                      class="w-4 h-4 rounded border cursor-pointer focus:ring-2 focus:ring-emerald-500" />
                  </td>
                  <td class="px-4 py-2 text-sm text-slate-200">
                    <button @click="openContactProfile(assignment.contact)"
                      class="text-left hover:text-emerald-400 transition-colors cursor-pointer">
                      <div class="font-medium">{{ assignment.contact_name || 'Unknown' }}</div>
                    </button>
                  </td>
                  <td class="px-4 py-2">
                    <span class="inline-flex px-2 py-1 text-xs rounded-full" :class="getStatusClass(assignment.status)">
                      {{ assignment.status }}
                    </span>
                  </td>
                  <td v-if="campaign.campaign_type === 'recurring'" class="px-4 py-2 text-sm">
                    <div v-if="editingFrequencyAssignmentId === assignment.id" class="space-y-2">
                      <div class="flex items-center gap-2">
                        <select v-model="editingFrequencyValue" @change="handleFrequencyTypeChange"
                          class="bg-slate-700/50 border border-emerald-500/30 rounded-lg px-2 py-1 text-slate-100 text-xs focus:border-emerald-400 focus:outline-none">
                          <option :value="null">Use Campaign Default</option>
                          <option :value="1">Daily</option>
                          <option :value="7">Weekly</option>
                          <option :value="30">Monthly</option>
                          <option :value="90">Quarterly</option>
                          <option :value="365">Yearly</option>
                          <option value="custom">Custom...</option>
                        </select>
                        <input v-if="editingFrequencyValue === 'custom'" v-model.number="customFrequencyDays" type="number" min="1"
                          placeholder="Days"
                          class="w-20 bg-slate-700/50 border border-emerald-500/30 rounded-lg px-2 py-1 text-slate-100 text-xs focus:border-emerald-400 focus:outline-none">
                      </div>
                      <div v-if="editingFrequencyValue === 7" class="flex items-center gap-2">
                        <span class="text-xs text-slate-400">Day:</span>
                        <select v-model="editingSendDay"
                          class="bg-slate-700/50 border border-emerald-500/30 rounded-lg px-2 py-1 text-slate-100 text-xs focus:border-emerald-400 focus:outline-none">
                          <option value="0">Monday</option>
                          <option value="1">Tuesday</option>
                          <option value="2">Wednesday</option>
                          <option value="3">Thursday</option>
                          <option value="4">Friday</option>
                          <option value="5">Saturday</option>
                          <option value="6">Sunday</option>
                        </select>
                      </div>
                      <div v-if="editingFrequencyValue === 30 || editingFrequencyValue === 90" class="flex items-center gap-2">
                        <span class="text-xs text-slate-400">Day:</span>
                        <select v-model="editingSendDay"
                          class="bg-slate-700/50 border border-emerald-500/30 rounded-lg px-2 py-1 text-slate-100 text-xs focus:border-emerald-400 focus:outline-none">
                          <option v-for="day in 31" :key="day" :value="day.toString()">{{ day }}{{ getDaySuffix(day) }}</option>
                          <option value="last">Last day</option>
                        </select>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="text-xs text-slate-400">Time:</span>
                        <input v-model="editingSendTime" type="time"
                          class="bg-slate-700/50 border border-emerald-500/30 rounded-lg px-2 py-1 text-slate-100 text-xs focus:border-emerald-400 focus:outline-none">
                      </div>
                      <div class="flex items-center gap-2">
                        <button @click="saveFrequency(assignment, campaign.id)"
                          class="px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded text-xs hover:bg-emerald-500/30 transition-colors">
                          Save
                        </button>
                        <button @click="cancelFrequencyEdit"
                          class="px-2 py-1 bg-slate-600/50 text-slate-300 rounded text-xs hover:bg-slate-600/70 transition-colors">
                          Cancel
                        </button>
                      </div>
                    </div>
                    <div v-else class="flex items-center gap-2">
                      <span class="text-slate-300 text-xs">{{ getAssignmentFrequencyDisplay(assignment, campaign) }}</span>
                      <button @click="startFrequencyEdit(assignment, campaign)"
                        class="text-emerald-400 hover:text-emerald-300 text-xs">Change</button>
                    </div>
                  </td>
                  <td v-if="campaign.campaign_type === 'sequence'" class="px-4 py-2 text-sm text-slate-300">
                    {{ assignment.current_step }}/{{ campaign.step_count || 'N/A' }}
                  </td>
                  <td class="px-4 py-2 text-sm text-slate-300">
                    <div v-if="editingNextSendDateId === assignment.id" class="flex items-center gap-2">
                      <input v-model="editingNextSendDate" type="datetime-local"
                        class="bg-slate-700/50 border border-emerald-500/30 rounded-lg px-2 py-1 text-slate-100 text-xs focus:border-emerald-400 focus:outline-none">
                      <button @click="saveNextSendDate(assignment, campaign.id)"
                        class="px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded text-xs hover:bg-emerald-500/30 transition-colors">
                        Save
                      </button>
                      <button @click="cancelNextSendDateEdit"
                        class="px-2 py-1 bg-slate-600/50 text-slate-300 rounded text-xs hover:bg-slate-600/70 transition-colors">
                        Cancel
                      </button>
                    </div>
                    <div v-else class="flex items-center gap-2">
                      <span>{{ assignment.next_send_date ? formatDate(assignment.next_send_date) : 'Not scheduled' }}</span>
                      <button @click="startNextSendDateEdit(assignment)"
                        class="text-emerald-400 hover:text-emerald-300 text-xs">Edit</button>
                    </div>
                  </td>
                  <td class="px-4 py-2 text-sm text-slate-300">
                    <div class="flex items-center gap-2">
                      <Icon v-if="assignment.custom_message_override" name="lucide:file-text" class="w-4 h-4 text-emerald-400" title="Custom message" />
                      <button @click="openCustomMessageModal(assignment, campaign)"
                        class="text-emerald-400 hover:text-emerald-300 text-xs">
                        {{ assignment.custom_message_override ? 'Edit' : 'Set' }} Message
                      </button>
                    </div>
                  </td>
                  <td class="px-4 py-2 text-sm">
                    <div class="flex items-center gap-2 flex-wrap">
                      <button @click="togglePauseAssignment(assignment, campaign.id)"
                        :class="assignment.status === 'active' ? 'text-emerald-400 hover:text-emerald-300' : 'text-slate-400 hover:text-slate-300'"
                        class="text-xs" :title="assignment.status === 'active' ? 'Pause' : 'Resume'">
                        <Icon :name="assignment.status === 'active' ? 'lucide:play' : 'lucide:pause'" class="w-4 h-4" />
                      </button>
                      <button v-if="campaign.message_template || assignment.custom_message_override"
                        @click="confirmSendNow(assignment, campaign.id)"
                        class="text-blue-400 hover:text-blue-300 text-xs" title="Send Now">
                        <Icon name="lucide:send" class="w-4 h-4" />
                      </button>
                      <button @click="removeAssignment(assignment.id, campaign.id)"
                        class="text-red-400 hover:text-red-300 text-xs" title="Remove">
                        <Icon name="lucide:trash-2" class="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="getCampaignAssignments(campaign.id).length === 0">
                  <td :colspan="campaign.campaign_type === 'sequence' ? 8 : (campaign.campaign_type === 'recurring' ? 8 : 7)"
                    class="px-4 py-4 text-center text-sm text-slate-400">
                    No assignments yet. Click "Add Contacts" to assign contacts to this campaign.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else
      class="text-center py-12 bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-xl border border-emerald-500/20">
      <Icon name="lucide:target" class="w-16 h-16 text-slate-400 mx-auto mb-4" />
      <p class="text-slate-400 text-lg">No campaigns created yet. Click "Create Campaign" to get started!</p>
    </div>

    <!-- Create/Edit Campaign Modal -->
    <CampaignFormModal
      :show="showCreateCampaignForm || showEditCampaignForm"
      :campaign="newCampaign"
      :is-edit="!!editingCampaign"
      :templates="templates"
      @close="closeCampaignModal"
      @save="handleSaveCampaign"
    />

    <!-- Add Contacts Modal -->
    <AddContactsModal
      :show="showAddPersonModal"
      :campaign="selectedCampaignForAssignment"
      :available-contacts="getAvailableContactsForCampaign()"
      :all-contacts="availableContacts"
      :selected-contact-ids="selectedContactIds"
      @close="closeAddPersonModal"
      @save="handleAddAssignment"
    />

    <!-- Edit Next Message Modal -->
    <EditNextMessageModal
      :show="showEditNextMessageModal"
      :campaign="selectedCampaignForNextMessage"
      :message="nextMessageOverride"
      @close="closeEditNextMessageModal"
      @save="handleSaveNextMessage"
    />

    <!-- Contact Profile -->
    <ContactProfile v-if="showContactProfileModal && selectedContact" :contact="selectedContact"
      :upcoming-messages="sortedUpcomingMessages" @close="closeContactProfileModal" @update="handleContactUpdate"
      @send-message="handleSendMessageFromProfile" />

    <!-- Test Message Modal -->
    <div v-if="showTestMessageModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
      <div
        class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full h-full sm:h-auto sm:max-w-md sm:max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex justify-between items-center p-4 sm:p-6 border-b border-slate-700/50 flex-shrink-0">
          <h3 class="text-xl sm:text-2xl font-thin text-slate-100">Test Campaign Message</h3>
          <button @click="closeTestMessageModal" class="text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="lucide:x" class="w-6 h-6" />
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-4 sm:p-6 min-h-0">
          <div class="space-y-4">
            <!-- Search Bar -->
            <div>
              <label class="block text-xs font-light text-slate-300 mb-2">Search Contacts</label>
              <input v-model="testContactSearch" type="text" placeholder="Search by name, email, or username..."
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>

            <div>
              <label class="block text-xs font-light text-slate-300 mb-2">Select Contact</label>
              <select v-model="testContactId"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                <option value="">-- Select a contact --</option>
                <option v-for="contact in filteredTestContacts" :key="contact.id" :value="contact.id">
                  {{ contact.name }} ({{ contact.email || contact.codementor_username || 'No contact info' }})
                </option>
              </select>
            </div>

            <div v-if="testContactId">
              <label class="block text-xs font-light text-slate-300 mb-2">Platforms (using contact's preferred platforms)</label>
              <div class="space-y-2">
                <label class="flex items-center space-x-2">
                  <input type="checkbox" v-model="testPlatforms" value="email"
                    :disabled="!selectedTestContact?.email"
                    class="w-4 h-4 text-emerald-500 bg-slate-700/50 border-emerald-500/30 rounded focus:ring-emerald-400">
                  <span class="text-xs text-slate-300">Email</span>
                  <span v-if="!selectedTestContact?.email" class="text-xs text-slate-500">(not available)</span>
                </label>
                <label class="flex items-center space-x-2">
                  <input type="checkbox" v-model="testPlatforms" value="codementor"
                    :disabled="!selectedTestContact?.codementor_username"
                    class="w-4 h-4 text-emerald-500 bg-slate-700/50 border-emerald-500/30 rounded focus:ring-emerald-400">
                  <span class="text-xs text-slate-300">Codementor</span>
                  <span v-if="!selectedTestContact?.codementor_username" class="text-xs text-slate-500">(not available)</span>
                </label>
              </div>
            </div>

            <div v-if="testSending" class="text-sm text-slate-400 text-center py-4">
              Sending test message...
            </div>
            <div v-if="testResult" class="text-sm py-4"
              :class="testResult.error ? 'text-red-400' : 'text-emerald-400'">
              {{ testResult.message || testResult.error }}
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex space-x-3 p-4 sm:p-6 border-t border-slate-700/50 flex-shrink-0">
          <button @click="closeTestMessageModal"
            class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
            Close
          </button>
          <button @click="handleTestMessage" :disabled="!testContactId || testPlatforms.length === 0 || testSending"
            class="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
            Send Test
          </button>
        </div>
      </div>
    </div>

    <!-- Custom Message Modal -->
    <div v-if="showCustomMessageModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
      <div
        class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full h-full sm:h-auto sm:max-w-6xl sm:max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex justify-between items-center p-4 sm:p-6 border-b border-slate-700/50 flex-shrink-0">
          <h3 class="text-xl sm:text-2xl font-thin text-slate-100">Custom Message for {{ customMessageAssignment?.contact_name }}</h3>
          <button @click="closeCustomMessageModal" class="text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="lucide:x" class="w-6 h-6" />
          </button>
        </div>

        <!-- Scrollable Content -->
        <div class="flex-1 flex flex-col sm:flex-row gap-4 sm:gap-6 overflow-y-auto p-4 sm:p-6 min-h-0">
          <!-- Left: Message Composition -->
          <div class="flex-1 space-y-4">
            <!-- Variable Hints Info Block -->
            <VariableHints :show-frequency="customMessageCampaign?.campaign_type === 'recurring'" mb-class="" />

            <div>
              <label class="block text-xs font-light text-slate-300 mb-1">Message Body</label>
              <textarea v-model="customMessageText" rows="12"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                placeholder="Leave empty to use campaign default message"></textarea>
              <p class="text-xs text-slate-500 mt-1">Leave empty to use the campaign's default message template.</p>
            </div>
          </div>

          <!-- Right: Preview Section -->
          <div class="w-full sm:w-96 border-t sm:border-t-0 sm:border-l border-slate-700/50 pt-4 sm:pl-6 sm:pt-0 flex-shrink-0">
            <h4 class="text-lg font-light text-slate-100 mb-4">Preview</h4>

            <!-- Message Preview -->
            <div class="bg-slate-700/30 rounded-lg p-4 border border-slate-600/30 mb-4">
              <div v-if="customMessageText.trim()" class="text-sm text-slate-300 whitespace-pre-wrap">
                {{ previewCustomMessage }}
              </div>
              <div v-else class="text-sm text-slate-500 italic">
                (Will use campaign default message)
              </div>
            </div>

            <!-- User Data Section -->
            <div class="bg-slate-800/30 border border-emerald-500/20 rounded-xl p-3">
              <h5 class="text-sm font-light text-emerald-400 mb-2">Preview Data</h5>
              <div class="text-xs text-slate-300 space-y-1">
                <div><strong>Name:</strong> {{ customMessageContact?.name || 'John Doe' }}</div>
                <div><strong>Preferred Name:</strong> {{ customMessageContact?.preferred_name || 'Johnny' }}</div>
                <div><strong>Gender:</strong> {{ customMessageContact?.gender || 'Male' }}</div>
                <div><strong>Email:</strong> {{ customMessageContact?.email || 'john.doe@example.com' }}</div>
                <div><strong>Codementor:</strong> {{ customMessageContact?.codementor_username || 'johndoe' }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex space-x-3 p-4 sm:p-6 border-t border-slate-700/50 flex-shrink-0">
          <button @click="closeCustomMessageModal"
            class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
            Cancel
          </button>
          <button @click="saveCustomMessage"
            class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
            Save Message
          </button>
        </div>
      </div>
    </div>

    <!-- Send Now Confirmation Modal -->
    <div v-if="sendNowConfirmAssignment"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
      <div
        class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full h-full sm:h-auto sm:max-w-md sm:max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex justify-between items-center p-4 sm:p-6 border-b border-slate-700/50 flex-shrink-0">
          <h3 class="text-xl sm:text-2xl font-thin text-slate-100">Send Message Now</h3>
          <button @click="cancelSendNow" class="text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="lucide:x" class="w-6 h-6" />
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-4 sm:p-6 min-h-0">
          <div class="space-y-4">
            <p class="text-sm text-slate-300">
              Are you sure you want to send the campaign message to <strong>{{ sendNowConfirmAssignment?.contact_name }}</strong> right now?
            </p>
            <p class="text-xs text-slate-400">
              This will send the message immediately and schedule the next message according to the campaign frequency.
            </p>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex space-x-3 p-4 sm:p-6 border-t border-slate-700/50 flex-shrink-0">
          <button @click="cancelSendNow"
            class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
            Cancel
          </button>
          <button @click="handleSendNow"
            class="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
            Send Now
          </button>
        </div>
      </div>
    </div>

    <!-- Bulk Edit Modal -->
    <div v-if="showBulkEditModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-0 sm:p-4">
      <div
        class="bg-slate-800/90 backdrop-blur-sm rounded-none sm:rounded-2xl shadow-2xl border-0 sm:border border-emerald-500/20 w-full h-full sm:h-auto sm:max-w-2xl sm:max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex justify-between items-center p-4 sm:p-6 border-b border-slate-700/50 flex-shrink-0">
          <h3 class="text-xl sm:text-2xl font-thin text-slate-100">Bulk Edit ({{ selectedAssignmentIds[bulkEditCampaign?.id]?.size || 0 }} assignments)</h3>
          <button @click="closeBulkEditModal" class="text-slate-400 hover:text-slate-200 transition-colors">
            <Icon name="lucide:x" class="w-6 h-6" />
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-4 sm:p-6 min-h-0">
          <div class="space-y-6">
            <!-- Status -->
            <div>
              <label class="block text-xs font-light text-slate-300 mb-2">Status</label>
              <select v-model="bulkEditStatus"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                <option :value="null">Don't change</option>
                <option value="active">Active</option>
                <option value="paused">Paused</option>
              </select>
            </div>

            <!-- Frequency (only for recurring campaigns) -->
            <div v-if="bulkEditCampaign?.campaign_type === 'recurring'">
              <label class="block text-xs font-light text-slate-300 mb-2">Frequency</label>
              <select v-model="bulkEditFrequencyValue" @change="handleBulkFrequencyTypeChange"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                <option :value="null">Don't change</option>
                <option :value="'default'">Use Campaign Default</option>
                <option :value="1">Daily</option>
                <option :value="7">Weekly</option>
                <option :value="30">Monthly</option>
                <option :value="90">Quarterly</option>
                <option :value="365">Yearly</option>
                <option value="custom">Custom...</option>
              </select>

              <div v-if="bulkEditFrequencyValue === 'custom'" class="mt-2">
                <input v-model.number="bulkEditCustomFrequencyDays" type="number" min="1"
                  placeholder="Days"
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
              </div>

              <div v-if="bulkEditFrequencyValue === 7" class="mt-2">
                <label class="block text-xs font-light text-slate-300 mb-2">Day of Week</label>
                <select v-model="bulkEditSendDay"
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                  <option value="0">Monday</option>
                  <option value="1">Tuesday</option>
                  <option value="2">Wednesday</option>
                  <option value="3">Thursday</option>
                  <option value="4">Friday</option>
                  <option value="5">Saturday</option>
                  <option value="6">Sunday</option>
                </select>
              </div>

              <div v-if="bulkEditFrequencyValue === 30 || bulkEditFrequencyValue === 90" class="mt-2">
                <label class="block text-xs font-light text-slate-300 mb-2">Day of Month</label>
                <select v-model="bulkEditSendDay"
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
                  <option v-for="day in 31" :key="day" :value="day.toString()">{{ day }}{{ getDaySuffix(day) }}</option>
                  <option value="last">Last day</option>
                </select>
              </div>

              <div v-if="bulkEditFrequencyValue && bulkEditFrequencyValue !== null && bulkEditFrequencyValue !== 'default'" class="mt-2">
                <label class="block text-xs font-light text-slate-300 mb-2">Send Time</label>
                <input v-model="bulkEditSendTime" type="time"
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
              </div>
            </div>

            <!-- Next Send Date -->
            <div>
              <label class="block text-xs font-light text-slate-300 mb-2">Next Send Date</label>
              <input v-model="bulkEditNextSendDate" type="datetime-local"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm focus:border-emerald-400 focus:outline-none transition-colors">
              <p class="text-xs text-slate-500 mt-1">Leave empty to not change</p>
            </div>

            <!-- Custom Message -->
            <div>
              <label class="block text-xs font-light text-slate-300 mb-2">Custom Message</label>
              <textarea v-model="bulkEditMessage" rows="6"
                class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-lg px-3 py-2 text-slate-100 text-sm placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"
                placeholder="Leave empty to not change, or enter a message to set for all selected assignments"></textarea>
              <p class="text-xs text-slate-500 mt-1">Leave empty to not change, or enter a message to set for all selected assignments</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex space-x-3 p-4 sm:p-6 border-t border-slate-700/50 flex-shrink-0">
          <button @click="closeBulkEditModal"
            class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
            Cancel
          </button>
          <button @click="handleBulkEdit"
            class="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
            Update {{ selectedAssignmentIds[bulkEditCampaign?.id]?.size || 0 }} Assignment(s)
          </button>
        </div>
      </div>
    </div>

    <!-- Status Bar -->
    <div v-if="showStatusBar"
      class="fixed bottom-6 right-6 bg-slate-800/90 backdrop-blur-sm rounded-xl shadow-2xl border border-emerald-500/20 overflow-hidden transition-all duration-300">
      <div class="px-6 py-3 text-sm text-slate-300 font-light">
        <div class="flex items-center space-x-3">
          <div class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
          <span>{{ statusMessage }}</span>
        </div>
        <div class="w-full bg-slate-600/50 rounded-full h-1 mt-2">
          <div class="bg-gradient-to-r from-emerald-400 to-cyan-400 h-1 rounded-full transition-all duration-100"
            :style="{ width: statusProgress + '%' }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
useHead({
  title: 'Campaigns - Followupper'
})

const { campaigns, templates, contacts, createCampaign, updateCampaign, deleteCampaign, loadCampaigns, updateContact } = useApi()
const { apiCall } = useApiFetch()

// Local UI state
const showCreateCampaignForm = ref(false)
const showEditCampaignForm = ref(false)
const showCreateOneOffForm = ref(false)
const editingCampaign = ref(null)
const showAddPersonModal = ref(false)
const showEditNextMessageModal = ref(false)
const showContactProfileModal = ref(false)
const selectedCampaignForAssignment = ref(null)
const selectedCampaignForNextMessage = ref(null)
const selectedContact = ref(null)
const contactAssignments = ref([])
const expandedAssignments = ref({})
const campaignAssignments = ref({})
const nextMessageOverride = ref('')
const selectedContactIds = ref([])
const yearlyDateInput = ref('')
const editingFrequencyAssignmentId = ref(null)
const editingFrequencyValue = ref(null)
const customFrequencyDays = ref(null)
const editingSendDay = ref('')
const editingSendTime = ref('09:00')
const editingNextSendDateId = ref(null)
const editingNextSendDate = ref('')
const showCustomMessageModal = ref(false)
const customMessageAssignment = ref(null)
const customMessageCampaign = ref(null)
const customMessageText = ref('')
const sendNowConfirmAssignment = ref(null)
const sendNowConfirmCampaignId = ref(null)
const testUsePreferredPlatforms = ref(true)
const selectedAssignmentIds = ref({}) // { campaignId: Set<assignmentId> }
const showTestMessageModal = ref(false)
const testCampaign = ref(null)
const testContactId = ref('')
const testPlatforms = ref([])
const testSending = ref(false)
const testResult = ref(null)
const testContactSearch = ref('')
const showBulkEditModal = ref(false)
const bulkEditCampaign = ref(null)
const bulkEditStatus = ref(null)
const bulkEditFrequencyValue = ref(null)
const bulkEditCustomFrequencyDays = ref(null)
const bulkEditSendDay = ref('')
const bulkEditSendTime = ref('09:00')
const bulkEditNextSendDate = ref('')
const bulkEditMessage = ref('')
const newCampaign = ref({
  name: '',
  description: '',
  campaign_type: 'recurring',
  is_active: true,
  frequency_type: 'weekly',
  default_frequency_days: 7,
  send_day: '1',
  send_time: '09:00',
  timezone: 'contact',
  message_template: '',
  start_immediately: 'scheduled',
  steps: []
})

// Template selection state
const selectedTemplate = ref('')

// Status bar state
const statusMessage = ref('')
const showStatusBar = ref(false)
const statusTimer = ref(null)
const statusProgress = ref(100)

const showStatusWithProgressLocal = (message, duration = 5000) => {
  statusMessage.value = message
  showStatusBar.value = true
  statusProgress.value = 100

  if (statusTimer.value) {
    clearTimeout(statusTimer.value)
  }

  const progressInterval = setInterval(() => {
    statusProgress.value -= (100 / (duration / 50))
    if (statusProgress.value <= 0) {
      clearInterval(progressInterval)
    }
  }, 50)

  statusTimer.value = setTimeout(() => {
    showStatusBar.value = false
    statusTimer.value = null
    clearInterval(progressInterval)
  }, duration)
}

// Campaign type helpers
const getCampaignIcon = (type) => {
  switch (type) {
    case 'recurring': return 'lucide:repeat'
    case 'sequence': return 'lucide:list-ordered'
    case 'one_off': return 'lucide:user'
    default: return 'lucide:target'
  }
}

const getCampaignIconClass = (type) => {
  switch (type) {
    case 'recurring': return 'bg-gradient-to-r from-blue-500 to-cyan-500'
    case 'sequence': return 'bg-gradient-to-r from-emerald-500 to-green-500'
    case 'one_off': return 'bg-gradient-to-r from-purple-500 to-pink-500'
    default: return 'bg-gradient-to-r from-slate-500 to-slate-600'
  }
}


// Yearly date handling
const handleYearlyDateChange = (event) => {
  const fullDate = event.target.value // YYYY-MM-DD
  if (fullDate) {
    const parts = fullDate.split('-')
    if (parts.length === 3) {
      newCampaign.value.send_day = `${parts[1]}-${parts[2]}` // MM-DD
    }
  }
}

// Frequency management
const updateFrequencyDays = () => {
  switch (newCampaign.value.frequency_type) {
    case 'daily':
      newCampaign.value.default_frequency_days = 1
      yearlyDateInput.value = ''
      break
    case 'weekly':
      newCampaign.value.default_frequency_days = 7
      yearlyDateInput.value = ''
      // Set default day to current day of week if not set (0=Monday, 6=Sunday)
      if (!newCampaign.value.send_day || newCampaign.value.send_day === '') {
        const today = new Date()
        const dayOfWeek = (today.getDay() + 6) % 7 // Convert Sunday=0 to Monday=0
        newCampaign.value.send_day = dayOfWeek.toString()
      }
      break
    case 'monthly':
      newCampaign.value.default_frequency_days = 30
      yearlyDateInput.value = ''
      break
    case 'quarterly':
      newCampaign.value.default_frequency_days = 90
      yearlyDateInput.value = ''
      break
    case 'yearly':
      newCampaign.value.default_frequency_days = 365
      // If send_day is a full date, extract just MM-DD
      if (newCampaign.value.send_day && newCampaign.value.send_day.includes('-')) {
        const parts = newCampaign.value.send_day.split('-')
        if (parts.length === 3) {
          newCampaign.value.send_day = `${parts[1]}-${parts[2]}` // MM-DD
          // Update yearlyDateInput for display
          yearlyDateInput.value = newCampaign.value.send_day ? `${new Date().getFullYear()}-${newCampaign.value.send_day}` : ''
        }
      } else if (newCampaign.value.send_day && newCampaign.value.send_day.match(/^\d{2}-\d{2}$/)) {
        // Already in MM-DD format, update yearlyDateInput
        yearlyDateInput.value = `${new Date().getFullYear()}-${newCampaign.value.send_day}`
      } else {
        // Default to Jan 1 if no date set
        newCampaign.value.send_day = '01-01'
        yearlyDateInput.value = `${new Date().getFullYear()}-01-01`
      }
      break
    case 'custom':
      yearlyDateInput.value = ''
      // Keep current value
      break
  }
}

// Step management functions
const addStep = () => {
  newCampaign.value.steps.push({
    subject: '',
    message: '',
    delay_days: 0
  })
}

const removeStep = (index) => {
  newCampaign.value.steps.splice(index, 1)
}

// Form handlers
const closeCampaignModal = () => {
  showCreateCampaignForm.value = false
  showEditCampaignForm.value = false
  editingCampaign.value = null
  selectedTemplate.value = ''
  yearlyDateInput.value = ''
  newCampaign.value = {
    name: '',
    description: '',
    campaign_type: 'recurring',
    is_active: true,
    frequency_type: 'weekly',
    default_frequency_days: 7,
    send_day: '1',
    send_time: '09:00',
    timezone: 'contact',
    message_template: '',
    subject_template: '',
    footer_template: '',
    start_immediately: 'scheduled',
    steps: []
  }
}

const editCampaign = (campaign) => {
  editingCampaign.value = campaign
  newCampaign.value = {
    name: campaign.name,
    description: campaign.description || '',
    campaign_type: campaign.campaign_type,
    is_active: campaign.is_active,
    frequency_type: campaign.frequency_type || 'weekly',
    default_frequency_days: campaign.default_frequency_days || 7,
    send_day: campaign.send_day || '1',
    send_time: campaign.send_time || '09:00',
    timezone: campaign.timezone || 'contact',
    message_template: campaign.message_template || '',
    subject_template: campaign.subject_template || '',
    footer_template: campaign.footer_template || '',
    start_immediately: campaign.start_immediately || 'scheduled',
    steps: (campaign.steps || []).map(step => ({
      subject: step.subject || '',
      message: step.message || '',
      delay_days: step.delay_days || 0
    }))
  }

  // Handle yearly date input - convert MM-DD to YYYY-MM-DD for date input
  if (campaign.frequency_type === 'yearly' && campaign.send_day) {
    const parts = campaign.send_day.split('-')
    if (parts.length === 2) {
      const currentYear = new Date().getFullYear()
      yearlyDateInput.value = `${currentYear}-${parts[0]}-${parts[1]}` // YYYY-MM-DD
    }
  } else {
    yearlyDateInput.value = ''
  }

  showEditCampaignForm.value = true
}

const handleSaveCampaign = async (campaignData) => {
  try {
    const data = campaignData || { ...newCampaign.value }

    if (editingCampaign.value) {
      // Update existing campaign
      showStatusWithProgressLocal('Updating campaign...', 3000)
      const updatedCampaign = await updateCampaign(editingCampaign.value.id, data)
      console.log('Updated campaign:', updatedCampaign)
      // Reload campaigns to ensure we have the latest data
      await loadCampaigns()
      showStatusWithProgressLocal('Campaign updated successfully!', 5000)
    } else {
      // Create new campaign
      showStatusWithProgressLocal('Creating campaign...', 3000)
      const createdCampaign = await createCampaign(data)
      campaigns.value.push(createdCampaign)
      showStatusWithProgressLocal('Campaign created successfully!', 3000)
    }
    closeCampaignModal()
  } catch (error) {
    console.error('Error saving campaign:', error)
    showStatusWithProgressLocal(`Error saving campaign: ${error.message}`, 5000)
  }
}

const handleDeleteCampaign = async (id) => {
  if (!confirm('Are you sure you want to delete this campaign? This action cannot be undone.')) {
    return
  }

  try {
    showStatusWithProgressLocal('Deleting campaign...', 3000)
    await deleteCampaign(id)
    campaigns.value = campaigns.value.filter(c => c.id !== id)
    showStatusWithProgressLocal('Campaign deleted successfully!', 3000)
  } catch (error) {
    console.error('Error deleting campaign:', error)
    showStatusWithProgressLocal(`Error deleting campaign: ${error.message}`, 5000)
  }
}

// Assignment management
// Initialize assignments - always load them
const initializeAssignments = async () => {
  for (const campaign of campaigns.value) {
    await loadCampaignAssignments(campaign.id)
  }
}

const loadCampaignAssignments = async (campaignId) => {
  try {
    const data = await apiCall(`/campaigns/${campaignId}/assignments/`)
    campaignAssignments.value[campaignId] = data
  } catch (error) {
    console.error('Error loading assignments:', error)
  }
}

const getCampaignAssignments = (campaignId) => {
  return campaignAssignments.value[campaignId] || []
}


const getStatusClass = (status) => {
  const classes = {
    'active': 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
    'paused': 'bg-slate-500/20 text-slate-400 border border-slate-500/30',
    'blacklisted': 'bg-red-500/20 text-red-400 border border-red-500/30',
    'completed': 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
  }
  return classes[status] || 'bg-slate-500/20 text-slate-400 border border-slate-500/30'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatFrequency = (campaign) => {
  if (!campaign.frequency_type) {
    return `${campaign.default_frequency_days} days`
  }

  const frequencyType = campaign.frequency_type
  const sendDay = campaign.send_day
  const sendTime = campaign.send_time || '09:00'

  switch (frequencyType) {
    case 'daily':
      return `Daily at ${sendTime}`
    case 'weekly':
      if (sendDay !== undefined && sendDay !== null && sendDay !== '') {
        const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        const dayIndex = parseInt(sendDay)
        if (!isNaN(dayIndex) && dayIndex >= 0 && dayIndex <= 6) {
          return `Weekly (${dayNames[dayIndex]}) at ${sendTime}`
        }
      }
      return `Weekly at ${sendTime}`
    case 'monthly':
      if (sendDay === '1') {
        return `Monthly (1st) at ${sendTime}`
      } else if (sendDay === '15') {
        return `Monthly (15th) at ${sendTime}`
      } else if (sendDay === 'last') {
        return `Monthly (last day) at ${sendTime}`
      }
      return `Monthly at ${sendTime}`
    case 'quarterly':
      if (sendDay === '1') {
        return `Quarterly (1st) at ${sendTime}`
      } else if (sendDay === '15') {
        return `Quarterly (15th) at ${sendTime}`
      } else if (sendDay === 'last') {
        return `Quarterly (last day) at ${sendTime}`
      }
      return `Quarterly at ${sendTime}`
    case 'yearly':
      if (sendDay && sendDay.includes('-')) {
        const parts = sendDay.split('-')
        if (parts.length === 2) {
          const month = parseInt(parts[0])
          const day = parseInt(parts[1])
          const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
          const monthName = monthNames[month - 1] || month
          return `Yearly (${monthName} ${day}) at ${sendTime}`
        }
      }
      return `Yearly at ${sendTime}`
    case 'custom':
      return `Every ${campaign.default_frequency_days} days at ${sendTime}`
    default:
      return `${campaign.default_frequency_days} days`
  }
}

const addAssignment = (campaign) => {
  selectedCampaignForAssignment.value = campaign
  // Filter out contacts that are already assigned to this campaign
  const existingContactIds = getCampaignAssignments(campaign.id).map(a => a.contact)
  selectedContactIds.value = []
  showAddPersonModal.value = true
}

const closeAddPersonModal = () => {
  showAddPersonModal.value = false
  selectedCampaignForAssignment.value = null
  selectedContactIds.value = []
}

const handleAddAssignment = async (contactIds) => {
  const ids = contactIds || selectedContactIds.value
  if (ids.length === 0) {
    return
  }

  try {
    const contactCount = ids.length
    showStatusWithProgressLocal(`Adding ${contactCount} contact${contactCount !== 1 ? 's' : ''} to campaign...`, 3000)

    // Create assignments for all selected contacts
    const promises = ids.map(contactId =>
      apiCall(`/campaigns/${selectedCampaignForAssignment.value.id}/assignments/`, {
        method: 'POST',
        body: JSON.stringify({
          contact: parseInt(contactId),
          status: 'active'
        })
      })
    )

    const results = await Promise.allSettled(promises)
    const successful = results.filter(r => r.status === 'fulfilled').length
    const failed = results.length - successful

    await loadCampaignAssignments(selectedCampaignForAssignment.value.id)
    await loadCampaigns() // Reload to update assignment counts

    if (failed === 0) {
      showStatusWithProgressLocal(`${successful} contact${successful !== 1 ? 's' : ''} added to campaign successfully!`, 5000)
    } else {
      showStatusWithProgressLocal(`${successful} contact${successful !== 1 ? 's' : ''} added, ${failed} failed`, 5000)
    }

    closeAddPersonModal()
  } catch (error) {
    console.error('Error adding assignments:', error)
    showStatusWithProgressLocal(`Error: ${error.message}`, 5000)
  }
}

const editNextMessage = async (campaign) => {
  // Reload campaign to get latest data including next_message_override
  try {
    const updatedCampaign = await apiCall(`/campaigns/${campaign.id}/`)
    selectedCampaignForNextMessage.value = updatedCampaign
    nextMessageOverride.value = updatedCampaign.next_message_override || ''
  } catch (error) {
    console.error('Error loading campaign:', error)
    // Fallback to current campaign data
    selectedCampaignForNextMessage.value = campaign
    nextMessageOverride.value = campaign.next_message_override || ''
  }
  showEditNextMessageModal.value = true
}

const closeEditNextMessageModal = () => {
  showEditNextMessageModal.value = false
  selectedCampaignForNextMessage.value = null
  nextMessageOverride.value = ''
}

const handleSaveNextMessage = async (message) => {
  try {
    const msg = message || nextMessageOverride.value
    showStatusWithProgressLocal('Saving next message override...', 3000)
    await updateCampaign(selectedCampaignForNextMessage.value.id, {
      ...selectedCampaignForNextMessage.value,
      next_message_override: msg
    })
    await loadCampaigns()
    showStatusWithProgressLocal('Next message override saved successfully!', 5000)
    closeEditNextMessageModal()
  } catch (error) {
    console.error('Error saving next message:', error)
    showStatusWithProgressLocal(`Error: ${error.message}`, 5000)
  }
}

const getAssignmentFrequencyDisplay = (assignment, campaign) => {
  // Determine frequency type and settings
  let frequencyType = campaign.frequency_type || 'custom'
  let sendDay = assignment.custom_send_day || campaign.send_day || ''
  let sendTime = assignment.custom_send_time || campaign.send_time || '09:00'
  
  // If assignment has custom frequency, determine type from days
  if (assignment.custom_frequency_days) {
    const days = assignment.custom_frequency_days
    if (days === 1) frequencyType = 'daily'
    else if (days === 7) frequencyType = 'weekly'
    else if (days === 30) frequencyType = 'monthly'
    else if (days === 90) frequencyType = 'quarterly'
    else if (days === 365) frequencyType = 'yearly'
    else frequencyType = 'custom'
  }
  
  // Format based on frequency type
  switch (frequencyType) {
    case 'daily':
      return `Daily at ${sendTime}`
    case 'weekly':
      if (sendDay !== undefined && sendDay !== null && sendDay !== '') {
        const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        const dayIndex = parseInt(sendDay)
        if (!isNaN(dayIndex) && dayIndex >= 0 && dayIndex <= 6) {
          return `Weekly on ${dayNames[dayIndex]}s at ${sendTime}`
        }
      }
      return `Weekly at ${sendTime}`
    case 'monthly':
      if (sendDay === 'last') {
        return `Monthly on the last day at ${sendTime}`
      } else if (sendDay) {
        const day = parseInt(sendDay)
        if (!isNaN(day)) {
          return `Monthly on the ${day}${getDaySuffix(day)} at ${sendTime}`
        }
        return `Monthly on the ${sendDay} at ${sendTime}`
      }
      return `Monthly at ${sendTime}`
    case 'quarterly':
      if (sendDay === 'last') {
        return `Quarterly on the last day at ${sendTime}`
      } else if (sendDay) {
        const day = parseInt(sendDay)
        if (!isNaN(day)) {
          return `Quarterly on the ${day}${getDaySuffix(day)} at ${sendTime}`
        }
        return `Quarterly on the ${sendDay} at ${sendTime}`
      }
      return `Quarterly at ${sendTime}`
    case 'yearly':
      if (sendDay && sendDay.includes('-')) {
        const parts = sendDay.split('-')
        if (parts.length === 2) {
          const month = parseInt(parts[0])
          const day = parseInt(parts[1])
          const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
          const monthName = monthNames[month - 1] || month
          return `Yearly on ${monthName} ${day} at ${sendTime}`
        }
      }
      return `Yearly at ${sendTime}`
    case 'custom':
      if (assignment.custom_frequency_days) {
        return `Every ${assignment.custom_frequency_days} days at ${sendTime}`
      }
      return `Every ${campaign.default_frequency_days || 7} days at ${sendTime}`
    default:
      return 'Campaign Default'
  }
}

const startFrequencyEdit = (assignment, campaign) => {
  editingFrequencyAssignmentId.value = assignment.id
  editingFrequencyValue.value = assignment.custom_frequency_days || null
  customFrequencyDays.value = assignment.custom_frequency_days || null
  editingSendDay.value = assignment.custom_send_day || campaign.send_day || ''
  editingSendTime.value = assignment.custom_send_time || campaign.send_time || '09:00'
  
  if (editingFrequencyValue.value && ![1, 7, 30, 90, 365].includes(editingFrequencyValue.value)) {
    editingFrequencyValue.value = 'custom'
  }
}

const getDaySuffix = (day) => {
  if (day >= 11 && day <= 13) return 'th'
  switch (day % 10) {
    case 1: return 'st'
    case 2: return 'nd'
    case 3: return 'rd'
    default: return 'th'
  }
}

const handleFrequencyTypeChange = () => {
  // Set default send_day based on frequency type
  if (editingFrequencyValue.value === 7) {
    // Weekly - default to Monday if not set
    if (!editingSendDay.value) editingSendDay.value = '0'
  } else if (editingFrequencyValue.value === 30 || editingFrequencyValue.value === 90) {
    // Monthly/Quarterly - default to 1st if not set
    if (!editingSendDay.value) editingSendDay.value = '1'
  }
}

const cancelFrequencyEdit = () => {
  editingFrequencyAssignmentId.value = null
  editingFrequencyValue.value = null
  customFrequencyDays.value = null
  editingSendDay.value = ''
  editingSendTime.value = '09:00'
}

const saveFrequency = async (assignment, campaignId) => {
  try {
    const campaign = campaigns.value.find(c => c.id === campaignId)
    
    // If using campaign default, clear all custom fields
    if (editingFrequencyValue.value === null) {
      showStatusWithProgressLocal('Updating frequency...', 2000)
      await apiCall(`/campaigns/${campaignId}/assignments/${assignment.id}/`, {
        method: 'PUT',
        body: JSON.stringify({
          custom_frequency_days: null,  // IntegerField accepts null
          custom_send_time: '',  // CharField needs empty string, not null
          custom_send_day: ''  // CharField needs empty string, not null
        })
      })
    } else {
      let frequencyDays = null
      if (editingFrequencyValue.value === 'custom') {
        frequencyDays = customFrequencyDays.value
      } else {
        frequencyDays = editingFrequencyValue.value
      }

      // Determine if we need to set custom send_day
      // Only set it if it differs from campaign default
      let customSendDay = undefined // Don't send field if not needed
      if (campaign && (editingFrequencyValue.value === 7 || editingFrequencyValue.value === 30 || editingFrequencyValue.value === 90)) {
        // Convert to string for comparison to ensure type consistency
        const editingDayStr = String(editingSendDay.value || '')
        const campaignDayStr = String(campaign.send_day || '')
        if (editingDayStr !== campaignDayStr) {
          // Set to the custom value (even if it's "0")
          customSendDay = editingDayStr
        } else if (assignment.custom_send_day) {
          // If it matches the default but assignment had a custom value, clear it with empty string
          customSendDay = ''
        }
      } else if (assignment.custom_send_day) {
        // If frequency type doesn't require send_day but assignment had one, clear it
        customSendDay = ''
      }

      // Only set custom_send_time if it differs from campaign default
      let customSendTime = undefined
      if (campaign) {
        if (editingSendTime.value !== campaign.send_time) {
          customSendTime = editingSendTime.value || ''
        } else if (assignment.custom_send_time) {
          // If it matches the default but assignment had a custom value, clear it
          customSendTime = ''
        }
      }

      showStatusWithProgressLocal('Updating frequency...', 2000)
      const updateData = {
        custom_frequency_days: frequencyDays
      }
      // Only include custom_send_day if we need to update it
      if (customSendDay !== undefined) {
        updateData.custom_send_day = customSendDay
      }
      // Only include custom_send_time if we need to update it
      if (customSendTime !== undefined) {
        updateData.custom_send_time = customSendTime
      }
      await apiCall(`/campaigns/${campaignId}/assignments/${assignment.id}/`, {
        method: 'PUT',
        body: JSON.stringify(updateData)
      })
    }

    await loadCampaignAssignments(campaignId)
    await loadCampaigns() // Reload to update assignment counts
    showStatusWithProgressLocal('Frequency updated successfully!', 3000)
    cancelFrequencyEdit()
  } catch (error) {
    console.error('Error updating frequency:', error)
    showStatusWithProgressLocal(`Error: ${error.message}`, 5000)
  }
}

const editAssignment = (assignment, campaign) => {
  // Start frequency editing
  startFrequencyEdit(assignment, campaign)
}

const removeAssignment = async (assignmentId, campaignId) => {
  if (!confirm('Are you sure you want to remove this assignment?')) {
    return
  }

  try {
    showStatusWithProgressLocal('Removing assignment...', 3000)
    await apiCall(`/campaigns/${campaignId}/assignments/${assignmentId}/`, {
      method: 'DELETE'
    })

    await loadCampaignAssignments(campaignId)
    await loadCampaigns() // Reload to update assignment counts
    showStatusWithProgressLocal('Assignment removed successfully!', 5000)
  } catch (error) {
    console.error('Error removing assignment:', error)
    showStatusWithProgressLocal(`Error: ${error.message}`, 5000)
  }
}

// Bulk selection functions
const toggleAssignmentSelection = (campaignId, assignmentId) => {
  if (!selectedAssignmentIds.value[campaignId]) {
    selectedAssignmentIds.value[campaignId] = new Set()
  }
  if (selectedAssignmentIds.value[campaignId].has(assignmentId)) {
    selectedAssignmentIds.value[campaignId].delete(assignmentId)
  } else {
    selectedAssignmentIds.value[campaignId].add(assignmentId)
  }
}

const isAssignmentSelected = (campaignId, assignmentId) => {
  return selectedAssignmentIds.value[campaignId]?.has(assignmentId) || false
}

const toggleSelectAllAssignments = (campaignId) => {
  if (!selectedAssignmentIds.value[campaignId]) {
    selectedAssignmentIds.value[campaignId] = new Set()
  }
  const assignments = getCampaignAssignments(campaignId)
  const allSelected = assignments.every(a => selectedAssignmentIds.value[campaignId].has(a.id))
  
  if (allSelected) {
    selectedAssignmentIds.value[campaignId].clear()
  } else {
    assignments.forEach(a => selectedAssignmentIds.value[campaignId].add(a.id))
  }
}

const isAllAssignmentsSelected = (campaignId) => {
  const assignments = getCampaignAssignments(campaignId)
  if (assignments.length === 0) return false
  return assignments.every(a => selectedAssignmentIds.value[campaignId]?.has(a.id))
}

// Test message functions
const openTestMessageModal = (campaign) => {
  testCampaign.value = campaign
  testContactId.value = ''
  testPlatforms.value = []
  testUsePreferredPlatforms.value = false
  testResult.value = null
  showTestMessageModal.value = true
}

const closeTestMessageModal = () => {
  showTestMessageModal.value = false
  testCampaign.value = null
  testContactId.value = ''
  testPlatforms.value = []
  testResult.value = null
  testContactSearch.value = ''
}

const availableTestContacts = computed(() => {
  return contacts.value.filter(c => c.email || c.codementor_username)
})

const filteredTestContacts = computed(() => {
  let result
  if (!testContactSearch.value.trim()) {
    result = [...availableTestContacts.value]
  } else {
    const query = testContactSearch.value.toLowerCase().trim()
    result = availableTestContacts.value.filter(contact => {
      const name = (contact.name || '').toLowerCase()
      const email = (contact.email || '').toLowerCase()
      const codementor = (contact.codementor_username || '').toLowerCase()
      return name.includes(query) || email.includes(query) || codementor.includes(query)
    })
  }
  // Sort alphabetically by name, case-insensitive
  return result.sort((a, b) => {
    const nameA = (a.name || '').toLowerCase()
    const nameB = (b.name || '').toLowerCase()
    return nameA.localeCompare(nameB)
  })
})

const selectedTestContact = computed(() => {
  if (!testContactId.value) return null
  return contacts.value.find(c => c.id === parseInt(testContactId.value))
})

watch(() => selectedTestContact.value, (contact) => {
  if (contact) {
    // Always use contact's preferred platforms by default
    const preference = contact.platform_preference || []
    if (Array.isArray(preference) && preference.length > 0) {
      // Filter to only include platforms the contact actually has
      testPlatforms.value = preference.filter(p => {
        if (p === 'email') return !!contact.email
        if (p === 'codementor') return !!contact.codementor_username
        return false
      })
    } else if (preference === 'both') {
      testPlatforms.value = []
      if (contact.email) testPlatforms.value.push('email')
      if (contact.codementor_username) testPlatforms.value.push('codementor')
    } else if (preference) {
      // Single platform preference
      testPlatforms.value = []
      if (preference === 'email' && contact.email) testPlatforms.value.push('email')
      if (preference === 'codementor' && contact.codementor_username) testPlatforms.value.push('codementor')
    } else {
      // No preference set, default to available platforms
      testPlatforms.value = []
      if (contact.email) testPlatforms.value.push('email')
      if (contact.codementor_username) testPlatforms.value.push('codementor')
    }
    // Ensure we're using preferred platforms
    testUsePreferredPlatforms.value = true
  }
})

// Next send date editing
const startNextSendDateEdit = (assignment) => {
  editingNextSendDateId.value = assignment.id
  if (assignment.next_send_date) {
    const date = new Date(assignment.next_send_date)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    editingNextSendDate.value = `${year}-${month}-${day}T${hours}:${minutes}`
  } else {
    // Default to tomorrow at 9 AM
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    tomorrow.setHours(9, 0, 0, 0)
    const year = tomorrow.getFullYear()
    const month = String(tomorrow.getMonth() + 1).padStart(2, '0')
    const day = String(tomorrow.getDate()).padStart(2, '0')
    editingNextSendDate.value = `${year}-${month}-${day}T09:00`
  }
}

const cancelNextSendDateEdit = () => {
  editingNextSendDateId.value = null
  editingNextSendDate.value = ''
}

const saveNextSendDate = async (assignment, campaignId) => {
  try {
    showStatusWithProgressLocal('Updating next send date...', 2000)
    await apiCall(`/campaigns/${campaignId}/assignments/${assignment.id}/`, {
      method: 'PUT',
      body: JSON.stringify({
        next_send_date: editingNextSendDate.value ? new Date(editingNextSendDate.value).toISOString() : null
      })
    })
    await loadCampaignAssignments(campaignId)
    showStatusWithProgressLocal('Next send date updated!', 3000)
    cancelNextSendDateEdit()
  } catch (error) {
    console.error('Error updating next send date:', error)
    showStatusWithProgressLocal(`Error: ${error.message}`, 5000)
  }
}

// Custom message editing
const openCustomMessageModal = (assignment, campaign) => {
  customMessageAssignment.value = assignment
  customMessageCampaign.value = campaign
  customMessageText.value = assignment.custom_message_override || ''
  showCustomMessageModal.value = true
}

const closeCustomMessageModal = () => {
  showCustomMessageModal.value = false
  customMessageAssignment.value = null
  customMessageCampaign.value = null
  customMessageText.value = ''
}

const customMessageContact = computed(() => {
  if (!customMessageAssignment.value) return null
  // Try to find contact by ID or by name/email
  const assignment = customMessageAssignment.value
  if (assignment.contact?.id) {
    return assignment.contact
  }
  if (assignment.contact_id) {
    return contacts.value.find(c => c.id === assignment.contact_id) || null
  }
  // Fallback: try to find by name or email
  if (assignment.contact_name) {
    return contacts.value.find(c => c.name === assignment.contact_name) || null
  }
  if (assignment.contact_email) {
    return contacts.value.find(c => c.email === assignment.contact_email) || null
  }
  return null
})

const previewCustomMessage = computed(() => {
  if (!customMessageText.value.trim()) return ''
  const { replaceTemplateVariables } = useTemplateVariables()
  const frequencyType = customMessageCampaign.value?.campaign_type === 'recurring' 
    ? (customMessageCampaign.value?.frequency_type || 'weekly')
    : null
  return replaceTemplateVariables(customMessageText.value, customMessageContact.value || {}, frequencyType, true)
})

const saveCustomMessage = async () => {
  if (!customMessageAssignment.value || !customMessageCampaign.value) return
  
  try {
    showStatusWithProgressLocal('Updating message...', 2000)
    await apiCall(`/campaigns/${customMessageCampaign.value.id}/assignments/${customMessageAssignment.value.id}/`, {
      method: 'PUT',
      body: JSON.stringify({
        custom_message_override: customMessageText.value.trim() || ''
      })
    })
    await loadCampaignAssignments(customMessageCampaign.value.id)
    showStatusWithProgressLocal('Message updated!', 3000)
    closeCustomMessageModal()
  } catch (error) {
    console.error('Error updating message:', error)
    showStatusWithProgressLocal(`Error: ${error.message}`, 5000)
  }
}

// Pause/Resume assignment
const togglePauseAssignment = async (assignment, campaignId) => {
  try {
    const newStatus = assignment.status === 'active' ? 'paused' : 'active'
    showStatusWithProgressLocal(`${newStatus === 'active' ? 'Resuming' : 'Pausing'} assignment...`, 2000)
    await apiCall(`/campaigns/${campaignId}/assignments/${assignment.id}/`, {
      method: 'PUT',
      body: JSON.stringify({
        status: newStatus
      })
    })
    await loadCampaignAssignments(campaignId)
    showStatusWithProgressLocal(`Assignment ${newStatus === 'active' ? 'resumed' : 'paused'}!`, 3000)
  } catch (error) {
    console.error('Error toggling assignment status:', error)
    showStatusWithProgressLocal(`Error: ${error.message}`, 5000)
  }
}

// Send now with confirmation
const confirmSendNow = (assignment, campaignId) => {
  sendNowConfirmAssignment.value = assignment
  sendNowConfirmCampaignId.value = campaignId
}

const cancelSendNow = () => {
  sendNowConfirmAssignment.value = null
  sendNowConfirmCampaignId.value = null
}

const handleSendNow = async () => {
  if (!sendNowConfirmAssignment.value || !sendNowConfirmCampaignId.value) return
  
  const assignment = sendNowConfirmAssignment.value
  const campaignId = sendNowConfirmCampaignId.value
  
  try {
    showStatusWithProgressLocal('Sending message...', 3000)
    await apiCall(`/campaigns/${campaignId}/assignments/${assignment.id}/send-now/`, {
      method: 'POST'
    })
    await loadCampaignAssignments(campaignId)
    showStatusWithProgressLocal('Message sent successfully!', 3000)
    cancelSendNow()
  } catch (error) {
    console.error('Error sending message:', error)
    showStatusWithProgressLocal(`Error: ${error.message}`, 5000)
  }
}

const handleTestMessage = async () => {
  if (!testContactId.value || !testCampaign.value) return
  
  // Use the platforms that were set from the contact's preferences
  const platformsToSend = testPlatforms.value
  
  if (platformsToSend.length === 0) return

  testSending.value = true
  testResult.value = null

  try {
    const result = await apiCall(`/campaigns/${testCampaign.value.id}/test-message/`, {
      method: 'POST',
      body: JSON.stringify({
        contact_id: parseInt(testContactId.value),
        platforms: testPlatforms.value
      })
    })

    testResult.value = {
      message: result.message || 'Test message sent successfully!',
      error: null
    }
  } catch (error) {
    testResult.value = {
      message: null,
      error: error.message || 'Failed to send test message'
    }
  } finally {
    testSending.value = false
  }
}

// Bulk edit functions
const openBulkEditModal = (campaign) => {
  bulkEditCampaign.value = campaign
  bulkEditStatus.value = null
  bulkEditFrequencyValue.value = null
  bulkEditCustomFrequencyDays.value = null
  bulkEditSendDay.value = ''
  bulkEditSendTime.value = '09:00'
  bulkEditNextSendDate.value = ''
  bulkEditMessage.value = ''
  showBulkEditModal.value = true
}

const closeBulkEditModal = () => {
  showBulkEditModal.value = false
  bulkEditCampaign.value = null
  bulkEditStatus.value = null
  bulkEditFrequencyValue.value = null
  bulkEditCustomFrequencyDays.value = null
  bulkEditSendDay.value = ''
  bulkEditSendTime.value = '09:00'
  bulkEditNextSendDate.value = ''
  bulkEditMessage.value = ''
}

const handleBulkFrequencyTypeChange = () => {
  if (bulkEditFrequencyValue.value === 7) {
    if (!bulkEditSendDay.value) bulkEditSendDay.value = '0'
  } else if (bulkEditFrequencyValue.value === 30 || bulkEditFrequencyValue.value === 90) {
    if (!bulkEditSendDay.value) bulkEditSendDay.value = '1'
  }
}

const handleBulkEdit = async () => {
  if (!bulkEditCampaign.value) return
  const campaignId = bulkEditCampaign.value.id
  const assignmentIds = Array.from(selectedAssignmentIds.value[campaignId] || [])
  
  if (assignmentIds.length === 0) return

  try {
    showStatusWithProgressLocal(`Updating ${assignmentIds.length} assignment(s)...`, 5000)
    
    const campaign = campaigns.value.find(c => c.id === campaignId)
    
    // Update all selected assignments
    for (const assignmentId of assignmentIds) {
      const updateData = {}
      
      // Status
      if (bulkEditStatus.value !== null) {
        updateData.status = bulkEditStatus.value
      }
      
      // Frequency (only for recurring campaigns)
      if (campaign.campaign_type === 'recurring' && bulkEditFrequencyValue.value !== null) {
        if (bulkEditFrequencyValue.value === 'default') {
          // Use campaign default - clear all custom fields
          updateData.custom_frequency_days = null
          updateData.custom_send_day = ''
          updateData.custom_send_time = ''
        } else {
          let frequencyDays = null
          if (bulkEditFrequencyValue.value === 'custom') {
            frequencyDays = bulkEditCustomFrequencyDays.value
          } else {
            frequencyDays = bulkEditFrequencyValue.value
          }
          updateData.custom_frequency_days = frequencyDays
          
          // Set custom send_day if applicable
          if (bulkEditFrequencyValue.value === 7 || bulkEditFrequencyValue.value === 30 || bulkEditFrequencyValue.value === 90) {
            const editingDayStr = String(bulkEditSendDay.value || '')
            const campaignDayStr = String(campaign.send_day || '')
            if (editingDayStr !== campaignDayStr) {
              updateData.custom_send_day = editingDayStr
            } else {
              updateData.custom_send_day = ''
            }
          }
          
          // Set custom_send_time
          if (bulkEditSendTime.value && bulkEditSendTime.value !== campaign.send_time) {
            updateData.custom_send_time = bulkEditSendTime.value
          } else if (bulkEditSendTime.value === campaign.send_time) {
            updateData.custom_send_time = ''
          }
        }
      }
      
      // Next send date
      if (bulkEditNextSendDate.value) {
        updateData.next_send_date = new Date(bulkEditNextSendDate.value).toISOString()
      }
      
      // Custom message
      if (bulkEditMessage.value !== undefined) {
        updateData.custom_message_override = bulkEditMessage.value.trim() || ''
      }
      
      await apiCall(`/campaigns/${campaignId}/assignments/${assignmentId}/`, {
        method: 'PUT',
        body: JSON.stringify(updateData)
      })
    }

    await loadCampaignAssignments(campaignId)
    await loadCampaigns()
    selectedAssignmentIds.value[campaignId] = new Set()
    closeBulkEditModal()
    showStatusWithProgressLocal(`Successfully updated ${assignmentIds.length} assignment(s)!`, 5000)
  } catch (error) {
    console.error('Error bulk updating assignments:', error)
    showStatusWithProgressLocal(`Error: ${error.message}`, 5000)
  }
}

const handleBulkDeleteAssignments = async (campaign) => {
  const campaignId = campaign.id
  const assignmentIds = Array.from(selectedAssignmentIds.value[campaignId] || [])
  
  if (assignmentIds.length === 0) return

  if (!confirm(`Are you sure you want to delete ${assignmentIds.length} assignment(s)? This action cannot be undone.`)) {
    return
  }

  try {
    showStatusWithProgressLocal(`Deleting ${assignmentIds.length} assignment(s)...`, 5000)
    
    for (const assignmentId of assignmentIds) {
      await apiCall(`/campaigns/${campaignId}/assignments/${assignmentId}/`, {
        method: 'DELETE'
      })
    }

    await loadCampaignAssignments(campaignId)
    await loadCampaigns()
    selectedAssignmentIds.value[campaignId] = new Set()
    showStatusWithProgressLocal(`Successfully deleted ${assignmentIds.length} assignment(s)!`, 5000)
  } catch (error) {
    console.error('Error bulk deleting assignments:', error)
    showStatusWithProgressLocal(`Error: ${error.message}`, 5000)
  }
}

const availableContacts = computed(() => {
  return contacts.value.filter(contact => contact.is_active)
})

const getAvailableContactsForCampaign = () => {
  if (!selectedCampaignForAssignment.value) {
    return availableContacts.value
  }
  const existingContactIds = getCampaignAssignments(selectedCampaignForAssignment.value.id).map(a => a.contact)
  return availableContacts.value.filter(c => !existingContactIds.includes(c.id))
}

const sortedUpcomingMessages = computed(() => {
  return [...contactAssignments.value]
    .filter(a => a.next_send_date && a.status === 'active')
    .sort((a, b) => new Date(a.next_send_date) - new Date(b.next_send_date))
})

const openContactProfile = async (contactId) => {
  // Find the contact
  const contact = contacts.value.find(c => c.id === contactId)
  if (!contact) {
    console.error('Contact not found:', contactId)
    return
  }

  selectedContact.value = contact

  // Load all assignments for this contact across all campaigns
  await loadContactAssignments(contactId)

  showContactProfileModal.value = true
}

const closeContactProfileModal = () => {
  showContactProfileModal.value = false
  selectedContact.value = null
  contactAssignments.value = []
}

const handleContactUpdate = (updatedContact) => {
  // Update local state
  Object.assign(selectedContact.value, updatedContact)
  const contactIndex = contacts.value.findIndex(c => c.id === selectedContact.value.id)
  if (contactIndex !== -1) {
    Object.assign(contacts.value[contactIndex], updatedContact)
  }
  showStatusWithProgressLocal('Contact updated successfully', 3000)
}

const handleSendMessageFromProfile = (messageData) => {
  showStatusWithProgressLocal('Message sent successfully', 3000)
}

const loadContactAssignments = async (contactId) => {
  try {
    const allAssignments = []

    // Load assignments from all campaigns
    for (const campaign of campaigns.value) {
      try {
        const assignments = await apiCall(`/campaigns/${campaign.id}/assignments/`)
        // Filter for this contact and add campaign info
        const contactAssigns = assignments
          .filter(a => a.contact === contactId)
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

    contactAssignments.value = allAssignments
  } catch (error) {
    console.error('Error loading contact assignments:', error)
    contactAssignments.value = []
  }
}

onMounted(async () => {
  // Campaigns are loaded globally by initializeApp in app.vue
  console.log('Campaigns page mounted - campaigns already loaded globally')
  // Initialize assignments - always load them
  await initializeAssignments()
})
</script>
