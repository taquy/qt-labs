import axios from 'axios';
import { API_USER_ENDPOINTS } from '../../config';
import { getRequestConfig } from '../utils';

const api = {
  fetchUsers: async (payload) => {
    const query = new URLSearchParams(payload);
    const response = await axios.get(`${API_USER_ENDPOINTS.users}?${query.toString()}`, getRequestConfig());
    return response.data;
  },
  fetchUser: async (userId) => {
    const response = await axios.get(`${API_USER_ENDPOINTS.users}/${userId}`, getRequestConfig());
    return response.data;
  },
  createUser: async (user) => {
    const response = await axios.post(API_USER_ENDPOINTS.createUser, user, getRequestConfig());
    return response.data;
  },
  updateUser: async (payload) => { 
    const response = await axios.put(API_USER_ENDPOINTS.updateUser(payload.id), payload, getRequestConfig());
    return response.data;
  },
  deleteUser: async (userId) => {
    const response = await axios.delete(API_USER_ENDPOINTS.deleteUser(userId), getRequestConfig());
    return response.data;
  },
  toggleActive: async (userId) => {
    const response = await axios.post(API_USER_ENDPOINTS.toggleActive(userId), {}, getRequestConfig());
    return response.data;
  },
  toggleAdmin: async (userId) => {
    const response = await axios.post(`${API_USER_ENDPOINTS.toggleAdmin(userId)}`, {}, getRequestConfig());
    return response.data;
  },
};
export default api;
