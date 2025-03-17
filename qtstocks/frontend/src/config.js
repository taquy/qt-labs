const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export const API_ENDPOINTS = {
    login: `${API_BASE_URL}/auth/login`,
    register: `${API_BASE_URL}/auth/register`,
    stocksWithStats: `${API_BASE_URL}/stocks/with-stats`,
    settings: `${API_BASE_URL}/settings`,
    updateGraph: `${API_BASE_URL}/stocks/graph`,
    updateSetting: (key) => `${API_BASE_URL}/settings/${key}`,
    logout: `${API_BASE_URL}/api/logout`,
    stocks: `${API_BASE_URL}/api/stocks`,
    downloadStockList: `${API_BASE_URL}/api/download_stock_list`,
    fetchStockData: `${API_BASE_URL}/api/fetch_stock_data`,
    deleteSetting: (key) => `${API_BASE_URL}/api/settings/${key}`
}; 