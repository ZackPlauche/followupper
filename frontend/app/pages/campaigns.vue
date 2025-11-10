<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-4xl font-thin gradient-title mb-2">
          Campaigns
        </h1>
        <p class="text-slate-300 font-light">Manage your follow-up campaigns and sequences</p>
      </div>
      <div class="flex space-x-3">
        <button @click="showCreateCampaignForm = true"
                class="px-6 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105">
          <Icon name="lucide:plus" class="w-5 h-5 inline mr-2" />
          Create Campaign
        </button>
        <button @click="showCreateOneOffForm = true"
                class="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl font-light hover:shadow-lg transition-all duration-300 hover:scale-105">
          <Icon name="lucide:user-plus" class="w-5 h-5 inline mr-2" />
          Create One-Off
        </button>
      </div>
    </div>

    <!-- Campaigns List -->
    <div v-if="campaigns.length > 0" class="space-y-6">
      <div v-for="campaign in campaigns" :key="campaign.id"
           class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-xl border border-emerald-500/20 p-6">
        
        <!-- Campaign Header -->
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center space-x-4">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center"
                 :class="getCampaignIconClass(campaign.campaign_type)">
              <Icon :name="getCampaignIcon(campaign.campaign_type)" class="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 class="text-xl font-thin text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
                {{ campaign.name }}
              </h3>
              <p class="text-slate-400 text-sm">{{ campaign.description || 'No description provided.' }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <div class="flex items-center space-x-2">
              <div class="w-2 h-2 rounded-full" :class="campaign.is_active ? 'bg-emerald-400' : 'bg-slate-500'"></div>
              <span class="text-xs text-slate-400">{{ campaign.is_active ? 'Active' : 'Inactive' }}</span>
            </div>
            <div class="flex space-x-2">
              <button @click="editCampaign(campaign)"
                      class="px-3 py-1 bg-slate-600/50 text-slate-300 rounded-lg font-light hover:bg-slate-600/70 transition-colors text-sm">
                Edit
              </button>
              <button @click="handleDeleteCampaign(campaign.id)"
                      class="px-3 py-1 bg-red-600/50 text-red-300 rounded-lg font-light hover:bg-red-600/70 transition-colors text-sm">
                Delete
              </button>
            </div>
          </div>
        </div>

        <!-- Campaign Details -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div class="text-sm">
            <span class="text-slate-400">Type:</span>
            <span class="text-slate-200 font-medium ml-2 capitalize">{{ campaign.campaign_type.replace('_', ' ') }}</span>
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
            </div>
          </div>
          
          <!-- Assignments Table -->
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-700/50">
              <thead class="bg-slate-700/30">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">Contact</th>
                  <th class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">Status</th>
                  <th v-if="campaign.campaign_type === 'sequence'" class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">Current Step</th>
                  <th class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">Next Send</th>
                  <th class="px-4 py-2 text-left text-xs font-light text-slate-400 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-slate-800/30 divide-y divide-slate-700/30">
                <tr v-for="assignment in getCampaignAssignments(campaign.id)" :key="assignment.id" class="hover:bg-slate-700/20">
                  <td class="px-4 py-2 text-sm text-slate-200">
                    <button @click="openContactProfile(assignment.contact)" 
                            class="text-left hover:text-emerald-400 transition-colors cursor-pointer">
                      <div class="font-medium">{{ assignment.contact_name || 'Unknown' }}</div>
                      <div class="text-xs text-slate-400">{{ assignment.contact_email || '' }}</div>
                    </button>
                  </td>
                  <td class="px-4 py-2">
                    <span class="inline-flex px-2 py-1 text-xs rounded-full"
                          :class="getStatusClass(assignment.status)">
                      {{ assignment.status }}
                    </span>
                  </td>
                  <td v-if="campaign.campaign_type === 'sequence'" class="px-4 py-2 text-sm text-slate-300">
                    {{ assignment.current_step }}/{{ campaign.step_count || 'N/A' }}
                  </td>
                  <td class="px-4 py-2 text-sm text-slate-300">
                    {{ assignment.next_send_date ? formatDate(assignment.next_send_date) : 'Not scheduled' }}
                  </td>
                  <td class="px-4 py-2 text-sm">
                    <button @click="editAssignment(assignment)" class="text-emerald-400 hover:text-emerald-300 mr-3">Edit</button>
                    <button @click="removeAssignment(assignment.id, campaign.id)" class="text-red-400 hover:text-red-300">Remove</button>
                  </td>
                </tr>
                <tr v-if="getCampaignAssignments(campaign.id).length === 0">
                  <td :colspan="campaign.campaign_type === 'sequence' ? 5 : 4" class="px-4 py-4 text-center text-sm text-slate-400">
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
    <div v-else class="text-center py-12 bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-xl border border-emerald-500/20">
      <Icon name="lucide:target" class="w-16 h-16 text-slate-400 mx-auto mb-4" />
      <p class="text-slate-400 text-lg">No campaigns created yet. Click "Create Campaign" to get started!</p>
    </div>

    <!-- Create/Edit Campaign Modal -->
    <div v-if="showCreateCampaignForm || showEditCampaignForm" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div class="bg-slate-800 rounded-2xl shadow-2xl border border-emerald-500/20 w-full max-w-4xl max-h-[90vh] overflow-y-auto p-8 space-y-6">
        <h2 class="text-3xl font-thin gradient-title mb-4">
          {{ editingCampaign ? 'Edit Campaign' : 'Create New Campaign' }}
        </h2>

        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Campaign Name</label>
          <input v-model="newCampaign.name" type="text" placeholder="e.g., Weekly Check-ins"
                 class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
        </div>

        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Description (Optional)</label>
          <textarea v-model="newCampaign.description" placeholder="Describe what this campaign is for..."
                    class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors h-24 resize-none"></textarea>
        </div>

        <div>
          <label class="block text-sm font-light text-slate-300 mb-2">Campaign Type</label>
          <select v-model="newCampaign.campaign_type"
                  class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
            <option value="recurring">Recurring</option>
            <option value="sequence">Sequence</option>
          </select>
        </div>

        <div v-if="newCampaign.campaign_type === 'recurring'">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">Frequency</label>
              <select v-model="newCampaign.frequency_type" @change="updateFrequencyDays"
                      class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="yearly">Yearly</option>
                <option value="custom">Custom (Days)</option>
              </select>
            </div>
            
            <div v-if="newCampaign.frequency_type === 'custom'">
              <label class="block text-sm font-light text-slate-300 mb-2">Custom Frequency (Days)</label>
              <input v-model="newCampaign.default_frequency_days" type="number" min="1" max="365"
                     class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>
            
            <div v-if="newCampaign.frequency_type === 'weekly'">
              <label class="block text-sm font-light text-slate-300 mb-2">Send On</label>
              <select v-model="newCampaign.send_day"
                      class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
                <option value="0">Monday</option>
                <option value="1">Tuesday</option>
                <option value="2">Wednesday</option>
                <option value="3">Thursday</option>
                <option value="4">Friday</option>
                <option value="5">Saturday</option>
                <option value="6">Sunday</option>
              </select>
            </div>
            
            <div v-if="newCampaign.frequency_type === 'monthly' || newCampaign.frequency_type === 'quarterly'">
              <label class="block text-sm font-light text-slate-300 mb-2">Send On</label>
              <select v-model="newCampaign.send_day"
                      class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
                <option value="1">1st of the month</option>
                <option value="15">15th of the month</option>
                <option value="last">Last day of the month</option>
              </select>
            </div>
            
            <div v-if="newCampaign.frequency_type === 'yearly'">
              <label class="block text-sm font-light text-slate-300 mb-2">Send On</label>
              <input v-model="yearlyDateInput" type="date" 
                     @input="handleYearlyDateChange"
                     class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
              <p class="text-xs text-slate-400 mt-1">Select a specific date (month and day) to send each year</p>
            </div>
            
            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">Send Time</label>
              <input v-model="newCampaign.send_time" type="time"
                     class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
            </div>
            
            <div>
              <label class="block text-sm font-light text-slate-300 mb-2">Timezone</label>
              <div class="flex items-center bg-slate-700/50 rounded-lg p-1 border border-slate-500/30 w-fit">
                <button 
                  type="button"
                  @click="newCampaign.timezone = 'contact'"
                  :class="newCampaign.timezone === 'contact' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                  Contact
                </button>
                <button 
                  type="button"
                  @click="newCampaign.timezone = 'UTC'"
                  :class="newCampaign.timezone === 'UTC' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                  UTC
                </button>
                <button 
                  type="button"
                  @click="newCampaign.timezone = 'America/New_York'"
                  :class="newCampaign.timezone === 'America/New_York' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                  ET
                </button>
                <button 
                  type="button"
                  @click="newCampaign.timezone = 'America/Chicago'"
                  :class="newCampaign.timezone === 'America/Chicago' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                  CT
                </button>
                <button 
                  type="button"
                  @click="newCampaign.timezone = 'America/Denver'"
                  :class="newCampaign.timezone === 'America/Denver' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                  MT
                </button>
                <button 
                  type="button"
                  @click="newCampaign.timezone = 'America/Los_Angeles'"
                  :class="newCampaign.timezone === 'America/Los_Angeles' ? 'bg-slate-500/50 text-slate-100' : 'text-slate-400 hover:text-slate-200'"
                  class="px-3 py-1.5 rounded-md transition-colors text-sm font-light">
                  PT
                </button>
              </div>
              <p class="text-xs text-slate-400 mt-1">Select "Contact" to send at the specified time in each contact's local timezone</p>
            </div>
          </div>
        </div>

        <div v-if="newCampaign.campaign_type === 'recurring'">
          <label class="block text-sm font-light text-slate-300 mb-2">Message Template</label>
          <textarea v-model="newCampaign.message_template" placeholder="Hey {first_name}! Just checking in..."
                    class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors h-32 resize-none"></textarea>
          <div class="text-xs text-slate-400 mt-2">
            <p>Available variables: <code class="bg-slate-700/50 px-2 py-1 rounded">{first_name}</code>, <code class="bg-slate-700/50 px-2 py-1 rounded">{name}</code>, <code class="bg-slate-700/50 px-2 py-1 rounded">{email}</code></p>
          </div>
        </div>

        <div v-if="newCampaign.campaign_type === 'sequence'">
          <label class="block text-sm font-light text-slate-300 mb-2">Sequence Steps</label>
          <div class="space-y-4">
            <div v-for="(step, index) in newCampaign.steps" :key="index" class="bg-slate-700/30 rounded-xl p-4 space-y-3">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-medium text-slate-300">Step {{ index + 1 }}</h4>
                <button @click="removeStep(index)" class="px-3 py-1 bg-red-600/50 text-red-300 rounded-lg hover:bg-red-600/70 transition-colors text-sm">
                  <Icon name="lucide:trash-2" class="w-4 h-4" />
                </button>
              </div>
              
              <div>
                <label class="block text-xs text-slate-400 mb-1">Subject</label>
                <input v-model="step.subject" type="text" placeholder="Step subject (optional)"
                       class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
              </div>
              
              <textarea v-model="step.message" :placeholder="`Step ${index + 1} message...`"
                        class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors h-24 resize-none"></textarea>
              
              <div class="flex items-center space-x-3">
                <div class="flex-1">
                  <label class="block text-xs text-slate-400 mb-1">Delay (Days)</label>
                  <input v-model="step.delay_days" type="number" min="0" placeholder="0"
                         class="w-full bg-slate-600/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors">
                </div>
                <div class="text-xs text-slate-400 pt-6">
                  <p>Variables: <code class="bg-slate-700/50 px-2 py-1 rounded">{first_name}</code>, <code class="bg-slate-700/50 px-2 py-1 rounded">{name}</code>, <code class="bg-slate-700/50 px-2 py-1 rounded">{email}</code></p>
                </div>
              </div>
            </div>
            
            <button @click="addStep" class="w-full px-4 py-3 bg-slate-600/50 text-slate-300 rounded-xl hover:bg-slate-600/70 transition-colors border-2 border-dashed border-slate-600">
              <Icon name="lucide:plus" class="w-5 h-5 inline mr-2" />
              Add Step
            </button>
          </div>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Status</label>
            <select v-model="newCampaign.is_active"
                    class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 focus:border-emerald-400 focus:outline-none transition-colors">
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">When someone is added to this campaign:</label>
            <div class="space-y-2">
              <label class="flex items-center space-x-3">
                <input v-model="newCampaign.start_immediately" type="radio" value="immediate" name="start_behavior"
                       class="form-radio h-4 w-4 text-emerald-500 border-slate-600 bg-slate-700/50 focus:ring-emerald-400">
                <span class="text-sm text-slate-300">Send first message immediately</span>
              </label>
              <label class="flex items-center space-x-3">
                <input v-model="newCampaign.start_immediately" type="radio" value="scheduled" name="start_behavior"
                       class="form-radio h-4 w-4 text-emerald-500 border-slate-600 bg-slate-700/50 focus:ring-emerald-400">
                <span class="text-sm text-slate-300">Wait until next scheduled time</span>
              </label>
            </div>
          </div>
        </div>

        <div class="flex justify-end space-x-4 mt-6">
          <button @click="closeCampaignModal"
                  class="px-6 py-3 bg-slate-600/50 text-slate-300 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
            Cancel
          </button>
          <button @click="handleSaveCampaign"
                  class="px-6 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white rounded-xl font-light hover:shadow-lg transition-all duration-300"
                  :disabled="!newCampaign.name || !newCampaign.campaign_type">
            {{ editingCampaign ? 'Update Campaign' : 'Create Campaign' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add Contacts Modal -->
    <div v-if="showAddPersonModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-2xl font-thin text-slate-100 mb-6">Add Contacts to {{ selectedCampaignForAssignment?.name }}</h3>
        
        <form @submit.prevent="handleAddAssignment" class="space-y-4">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-3">Select Contacts *</label>
            <div class="bg-slate-700/30 rounded-xl border border-emerald-500/30 p-4 max-h-96 overflow-y-auto">
              <div v-if="getAvailableContactsForCampaign().length === 0" class="text-slate-400 text-sm text-center py-4">
                <div v-if="availableContacts.length === 0">No active contacts available</div>
                <div v-else>All active contacts are already assigned to this campaign</div>
              </div>
              <div v-else class="space-y-2">
                <label v-for="contact in getAvailableContactsForCampaign()" :key="contact.id"
                       class="flex items-center space-x-3 p-3 rounded-lg hover:bg-slate-600/30 cursor-pointer transition-colors">
                  <input type="checkbox" :value="contact.id" v-model="selectedContactIds"
                         class="w-5 h-5 text-emerald-500 bg-slate-600 border-slate-500 rounded focus:ring-emerald-400 focus:ring-2">
                  <div class="flex-1">
                    <div class="text-slate-100 font-medium">{{ contact.name }}</div>
                    <div class="text-slate-400 text-sm">
                      {{ contact.email || contact.codementor_username || 'No contact info' }}
                    </div>
                  </div>
                </label>
              </div>
            </div>
            <p v-if="selectedContactIds.length > 0" class="text-xs text-slate-400 mt-2">
              {{ selectedContactIds.length }} contact{{ selectedContactIds.length !== 1 ? 's' : '' }} selected
            </p>
          </div>
          
          <div class="flex space-x-3 pt-4">
            <button type="button" @click="closeAddPersonModal"
                    class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
              Cancel
            </button>
            <button type="submit" :disabled="selectedContactIds.length === 0"
                    class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
              Add Contacts
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Next Message Modal -->
    <div v-if="showEditNextMessageModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-emerald-500/20 p-8 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-2xl font-thin text-slate-100 mb-6">Edit Next Message for {{ selectedCampaignForNextMessage?.name }}</h3>
        
        <form @submit.prevent="handleSaveNextMessage" class="space-y-4">
          <div>
            <label class="block text-sm font-light text-slate-300 mb-2">Next Message Override *</label>
            <textarea v-model="nextMessageOverride" rows="10" required
                      class="w-full bg-slate-700/50 border border-emerald-500/30 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 focus:border-emerald-400 focus:outline-none transition-colors resize-none"></textarea>
            <p class="mt-2 text-xs text-slate-400 font-light">This message will be sent to all contacts in this campaign for their next scheduled send.</p>
          </div>
          
          <div class="flex space-x-3 pt-4">
            <button type="button" @click="closeEditNextMessageModal"
                    class="flex-1 bg-slate-600/50 text-slate-300 px-4 py-3 rounded-xl font-light hover:bg-slate-600/70 transition-colors">
              Cancel
            </button>
            <button type="submit"
                    class="flex-1 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white px-4 py-3 rounded-xl font-light hover:shadow-lg transition-all duration-300">
              Save Next Message
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Contact Profile -->
    <ContactProfile 
      v-if="showContactProfileModal && selectedContact"
      :contact="selectedContact"
      :upcoming-messages="sortedUpcomingMessages"
      @close="closeContactProfileModal"
      @update="handleContactUpdate"
      @send-message="handleSendMessageFromProfile"
    />

    <!-- Status Bar -->
    <div v-if="showStatusBar" class="fixed bottom-6 right-6 bg-slate-800/90 backdrop-blur-sm rounded-xl shadow-2xl border border-emerald-500/20 overflow-hidden transition-all duration-300">
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
import { ref, onMounted, computed } from 'vue'
import { useApi } from '../composables/useApi'

useHead({
  title: 'Campaigns - Followupper'
})

const { campaigns, templates, contacts, createCampaign, updateCampaign, deleteCampaign, loadCampaigns, updateContact } = useApi()

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

const handleSaveCampaign = async () => {
  try {
    const campaignData = { ...newCampaign.value }

    if (editingCampaign.value) {
      // Update existing campaign
      showStatusWithProgressLocal('Updating campaign...', 3000)
      const updatedCampaign = await updateCampaign(editingCampaign.value.id, campaignData)
      console.log('Updated campaign:', updatedCampaign)
      // Reload campaigns to ensure we have the latest data
      await loadCampaigns()
      showStatusWithProgressLocal('Campaign updated successfully!', 5000)
    } else {
      // Create new campaign
      showStatusWithProgressLocal('Creating campaign...', 3000)
      const createdCampaign = await createCampaign(campaignData)
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
    'paused': 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
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

const handleAddAssignment = async () => {
  if (selectedContactIds.value.length === 0) {
    return
  }

  try {
    const contactCount = selectedContactIds.value.length
    showStatusWithProgressLocal(`Adding ${contactCount} contact${contactCount !== 1 ? 's' : ''} to campaign...`, 3000)
    
    // Create assignments for all selected contacts
    const promises = selectedContactIds.value.map(contactId => 
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

const handleSaveNextMessage = async () => {
  try {
    showStatusWithProgressLocal('Saving next message override...', 3000)
    await updateCampaign(selectedCampaignForNextMessage.value.id, {
      ...selectedCampaignForNextMessage.value,
      next_message_override: nextMessageOverride.value
    })
    await loadCampaigns()
    showStatusWithProgressLocal('Next message override saved successfully!', 5000)
    closeEditNextMessageModal()
  } catch (error) {
    console.error('Error saving next message:', error)
    showStatusWithProgressLocal(`Error: ${error.message}`, 5000)
  }
}

const editAssignment = (assignment) => {
  // TODO: Implement assignment editing
  console.log('Edit assignment:', assignment)
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
