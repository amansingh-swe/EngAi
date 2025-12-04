const BASE_URL = 'http://localhost:8080/api';

async function request(method, path, options = {}) {
  const { body, queryParams, pathParams, ...fetchOptions } = options;

  let url = `${BASE_URL}${path}`;

  // Handle path parameters
  if (pathParams) {
    Object.keys(pathParams).forEach(key => {
      url = url.replace(`{${key}}`, pathParams[key]);
    });
  }

  // Handle query parameters
  if (queryParams) {
    const queryString = new URLSearchParams(queryParams).toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  const fetchConfig = {
    method,
    headers: {
      'Content-Type': 'application/json',
      // Add authorization token if available in local storage or context
      // 'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
    ...fetchOptions,
  };

  if (body) {
    fetchConfig.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, fetchConfig);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`API Error (${method} ${url}):`, error);
    throw error;
  }
}

export const apiService = {
  // Users
  registerUser: (userData) => request('POST', '/users/register', { body: userData }),
  loginUser: (credentials) => request('POST', '/users/login', { body: credentials }),
  getUser: (userId) => request('GET', `/users/{user_id}`, { pathParams: { user_id: userId } }),
  updateUser: (userId, userData) => request('PATCH', `/users/{user_id}`, { pathParams: { user_id: userId }, body: userData }),

  // Groups
  createGroup: (groupData) => request('POST', '/groups', { body: groupData }),
  getGroups: (userId) => request('GET', '/groups', { queryParams: { user_id: userId } }),
  getGroup: (groupId) => request('GET', '/groups/{group_id}', { pathParams: { group_id: groupId } }),
  joinGroup: (groupId) => request('POST', `/groups/{group_id}/join`, { pathParams: { group_id: groupId } }),
  leaveGroup: (groupId) => request('POST', `/groups/{group_id}/leave`, { pathParams: { group_id: groupId } }),

  // Messages
  createMessage: (messageData) => request('POST', '/messages', { body: messageData }),
  getMessages: (groupId, params) => request('GET', `/messages/{group_id}`, { pathParams: { group_id: groupId }, queryParams: params }),

  // Upload
  uploadMedia: (formData) => request('POST', '/upload', { body: formData, headers: { 'Content-Type': 'multipart/form-data' } }),
};