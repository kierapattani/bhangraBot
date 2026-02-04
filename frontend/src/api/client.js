const BASE_URL = ''

async function request(endpoint, options = {}) {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (response.status === 401) {
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (response.status === 204) {
    return null
  }

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Request failed')
  }

  return response.json()
}

export const api = {
  // Auth
  async getUser() {
    return request('/auth/me')
  },

  async logout() {
    return request('/auth/logout', { method: 'POST' })
  },

  // Messages
  async getMessages() {
    return request('/api/messages')
  },

  async getMessage(date) {
    return request(`/api/messages/${date}`)
  },

  async createMessage(date, message) {
    return request('/api/messages', {
      method: 'POST',
      body: JSON.stringify({ date, message }),
    })
  },

  async updateMessage(date, message) {
    return request(`/api/messages/${date}`, {
      method: 'PUT',
      body: JSON.stringify({ message }),
    })
  },

  async deleteMessage(date) {
    return request(`/api/messages/${date}`, { method: 'DELETE' })
  },

  async clearAllMessages() {
    return request('/api/messages', { method: 'DELETE' })
  },
}
