<template>
  <div v-if="contact">
    <ContactProfile 
      :contact="contact"
      :upcoming-messages="upcomingMessages"
      :is-modal="false"
      @update="handleContactUpdate"
      @send-message="handleSendMessage"
    />
  </div>
  <div v-else class="text-center py-12">
    <p class="text-slate-400">Contact not found</p>
  </div>
</template>

<script setup>
const route = useRoute()
const router = useRouter()
const api = useApi()

const contact = ref(null)
const upcomingMessages = ref([])

const loadContactData = async () => {
  const contactId = parseInt(route.params.id)
  contact.value = api.contacts.value.find(c => c.id === contactId)
  
  if (!contact.value) {
    await api.loadContacts()
    contact.value = api.contacts.value.find(c => c.id === contactId)
  }
  
  if (contact.value) {
    await loadContactAssignments(contactId)
  }
}

const loadContactAssignments = async (contactId) => {
  try {
    const { apiCall } = useApiFetch()
    const allAssignments = []
    
    // Load assignments from all campaigns
    for (const campaign of api.campaigns.value) {
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

const handleContactUpdate = (updatedContact) => {
  Object.assign(contact.value, updatedContact)
  const contactIndex = api.contacts.value.findIndex(c => c.id === contact.value.id)
  if (contactIndex !== -1) {
    Object.assign(api.contacts.value[contactIndex], updatedContact)
  }
}

const handleSendMessage = (messageData) => {
  // Message sent successfully
}

onMounted(async () => {
  await loadContactData()
})

watch(() => route.params.id, async () => {
  await loadContactData()
})
</script>

