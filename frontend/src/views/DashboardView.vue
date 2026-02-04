<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold text-purple-700">BhangraBot</h1>
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-600">{{ user?.email }}</span>
          <button
            @click="handleLogout"
            class="text-sm text-gray-500 hover:text-gray-700"
          >
            Logout
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
      <!-- Schedule Message Form -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-8">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">
          {{ editingDate ? 'Edit Message' : 'Schedule New Message' }}
        </h2>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Date
            </label>
            <input
              v-model="form.date"
              type="date"
              :min="minDate"
              :disabled="!!editingDate"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-100"
            />
            <p class="mt-1 text-sm text-gray-500">
              Messages are sent at 10:00 AM
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Message
            </label>
            <textarea
              v-model="form.message"
              rows="4"
              maxlength="1000"
              required
              placeholder="Enter your message..."
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
            ></textarea>
            <p class="mt-1 text-sm text-gray-500 text-right">
              {{ form.message.length }}/1000
            </p>
          </div>

          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="submitting"
              class="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
            >
              {{ submitting ? 'Saving...' : (editingDate ? 'Update' : 'Schedule') }}
            </button>
            <button
              v-if="editingDate"
              type="button"
              @click="cancelEdit"
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </form>

        <div v-if="formError" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-red-700 text-sm">{{ formError }}</p>
        </div>

        <div v-if="successMessage" class="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p class="text-green-700 text-sm">{{ successMessage }}</p>
        </div>
      </div>

      <!-- Scheduled Messages List -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-gray-800">Pending Messages</h2>
          <button
            v-if="messages.length > 0"
            @click="handleClearAll"
            class="text-sm text-red-600 hover:text-red-700"
          >
            Clear All
          </button>
        </div>

        <div v-if="loading" class="text-center py-8 text-gray-500">
          Loading...
        </div>

        <div v-else-if="messages.length === 0" class="text-center py-8 text-gray-500">
          No messages scheduled
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="msg in messages"
            :key="msg.date"
            class="flex items-start gap-4 p-4 bg-gray-50 rounded-lg"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-medium text-gray-800">{{ formatDate(msg.date) }}</span>
                <span class="text-xs text-gray-500 bg-gray-200 px-2 py-0.5 rounded">10:00 AM</span>
              </div>
              <p class="text-gray-600 break-words">{{ msg.message }}</p>
            </div>
            <div class="flex gap-2 shrink-0">
              <button
                @click="startEdit(msg)"
                class="p-2 text-gray-500 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                title="Edit"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                @click="handleDelete(msg.date)"
                class="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Delete"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/client'

const router = useRouter()

const user = ref(null)
const messages = ref([])
const loading = ref(true)
const submitting = ref(false)
const formError = ref('')
const successMessage = ref('')
const editingDate = ref(null)

const form = reactive({
  date: '',
  message: '',
})

const minDate = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toISOString().split('T')[0]
})

function formatDate(dateStr) {
  const date = new Date(dateStr + 'T00:00:00')
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

async function loadUser() {
  try {
    user.value = await api.getUser()
  } catch {
    router.push('/login')
  }
}

async function loadMessages() {
  loading.value = true
  try {
    const data = await api.getMessages()
    messages.value = data.messages
  } catch (err) {
    formError.value = err.message
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  formError.value = ''
  successMessage.value = ''
  submitting.value = true

  try {
    if (editingDate.value) {
      await api.updateMessage(form.date, form.message)
      successMessage.value = 'Message updated successfully!'
    } else {
      await api.createMessage(form.date, form.message)
      successMessage.value = 'Message scheduled successfully!'
    }
    form.date = ''
    form.message = ''
    editingDate.value = null
    await loadMessages()
  } catch (err) {
    formError.value = err.message
  } finally {
    submitting.value = false
  }
}

function startEdit(msg) {
  editingDate.value = msg.date
  form.date = msg.date
  form.message = msg.message
  formError.value = ''
  successMessage.value = ''
}

function cancelEdit() {
  editingDate.value = null
  form.date = ''
  form.message = ''
}

async function handleDelete(date) {
  if (!confirm('Delete this scheduled message?')) return

  try {
    await api.deleteMessage(date)
    await loadMessages()
    successMessage.value = 'Message deleted'
  } catch (err) {
    formError.value = err.message
  }
}

async function handleClearAll() {
  if (!confirm('Delete ALL scheduled messages? This cannot be undone.')) return

  try {
    await api.clearAllMessages()
    await loadMessages()
    successMessage.value = 'All messages cleared'
  } catch (err) {
    formError.value = err.message
  }
}

async function handleLogout() {
  try {
    await api.logout()
  } finally {
    router.push('/login')
  }
}

onMounted(() => {
  loadUser()
  loadMessages()
})
</script>
