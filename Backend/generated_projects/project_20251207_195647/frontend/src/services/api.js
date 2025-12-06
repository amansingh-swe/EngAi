const BASE_URL = "http://localhost:8080/api";

const api = {
  // Helper to get auth token
  getToken: () => localStorage.getItem('token'),

  // User Routes
  registerUser: async (userData) => {
    const response = await fetch(`${BASE_URL}/users/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Registration failed');
    }
    return response.json();
  },

  loginUser: async (credentials) => {
    const response = await fetch(`${BASE_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Login failed');
    }
    return response.json();
  },

  getUserProfile: async (userId) => {
    const token = api.getToken();
    const response = await fetch(`${BASE_URL}/users/${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `Failed to fetch user profile for ${userId}`);
    }
    return response.json();
  },

  updateUserProfile: async (userId, userData) => {
    const token = api.getToken();
    const response = await fetch(`${BASE_URL}/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(userData),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to update user profile');
    }
    return response.json();
  },

  deleteUserAccount: async (userId) => {
    const token = api.getToken();
    const response = await fetch(`${BASE_URL}/users/${userId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to delete user account');
    }
    return response.json();
  },

  // Group Routes
  createGroup: async (groupData) => {
    const token = api.getToken();
    const response = await fetch(`${BASE_URL}/groups`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(groupData),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to create group');
    }
    return response.json();
  },

  getGroupDetails: async (groupId) => {
    const token = api.getToken();
    const response = await fetch(`${BASE_URL}/groups/${groupId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `Failed to fetch group details for ${groupId}`);
    }
    return response.json();
  },

  getAllGroups: async (userId = null) => {
    const token = api.getToken();
    let url = `${BASE_URL}/groups`;
    if (userId) {
      url += `?user_id=${userId}`;
    }
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to fetch groups');
    }
    return response.json();
  },

  updateGroup: async (groupId, groupData) => {
    const token = api.getToken();
    const response = await fetch(`${BASE_URL}/groups/${groupId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(groupData),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to update group');
    }
    return response.json();
  },

  deleteGroup: async (groupId) => {
    const token = api.getToken();
    const response = await fetch(`${BASE_URL}/groups/${groupId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to delete group');
    }
    return response.json();
  },

  addMemberToGroup: async (groupId, userId) => {
    const token = api.getToken();
    const response = await fetch(`${BASE_URL}/groups/${groupId}/members`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ user_id: userId }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to add member');
    }
    return response.json();
  },

  removeMemberFromGroup: async (groupId, userId) => {
    const token = api.getToken();
    const response = await fetch(`${BASE_URL}/groups/${groupId}/members/${userId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to remove member');
    }
    return response.json();
  },

  // Message Routes
  getGroupMessages: async (groupId, params = {}) => {
    const token = api.getToken();
    const queryParams = new URLSearchParams(params).toString();
    const url = `${BASE_URL}/groups/${groupId}/messages${queryParams ? `?${queryParams}` : ''}`;
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to fetch messages');
    }
    return response.json();
  },

  sendMessage: async (messageData) => {
    const token = api.getToken();
    const response = await fetch(`${BASE_URL}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(messageData),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to send message');
    }
    return response.json();
  },

  // Media Upload
  uploadMedia: async (file) => {
    const token = api.getToken();
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${BASE_URL}/media/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to upload media');
    }
    return response.json();
  },
};

export default api;