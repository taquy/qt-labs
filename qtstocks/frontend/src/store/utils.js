// Helper function to handle API errors
const handleApiError = (error, saga) => {
  if (error.response?.status === 401) {
    localStorage.removeItem('authToken');
    localStorage.removeItem('isLoggedIn');
    window.location.href = '/login';
  }
  return saga;
}

const getRequestConfig = () => ({
  headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` },
  withCredentials: true
});

export { handleApiError, getRequestConfig };
