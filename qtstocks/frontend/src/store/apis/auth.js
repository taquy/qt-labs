import axios from 'axios';
import { API_AUTH_ENDPOINTS } from '../../config';
import { getRequestConfig } from '../utils';

const api = {
  logout: async () => {
    const response = await axios.post(API_AUTH_ENDPOINTS.logout, {}, getRequestConfig());
    return response.data;
  },
  login: async (payload) => {
    const response = await axios.post(API_AUTH_ENDPOINTS.login, payload);
    return response.data;
  },
  googleLogin: async (token) => {
    const response = await axios.post(API_AUTH_ENDPOINTS.googleLogin, token);
    return response.data;
  },
};

export default api;
