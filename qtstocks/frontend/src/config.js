const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5555/api';

export const API_ENDPOINTS = {
    login: `${API_BASE_URL}/login`,
    googleLogin: `${API_BASE_URL}/login/google`,
    register: `${API_BASE_URL}/auth/register`,
    stocksWithStats: `${API_BASE_URL}/stocks_with_stats`,
    settings: `${API_BASE_URL}/settings`,
    updateGraph: `${API_BASE_URL}/update_graph`,
    updateSetting: (key) => `${API_BASE_URL}/settings/${key}`,
    logout: `${API_BASE_URL}/logout`,
    stocks: `${API_BASE_URL}/stocks`,
    downloadStockList: `${API_BASE_URL}/download_stock_list`,
    fetchStockData: `${API_BASE_URL}/fetch_stock_data`,
    deleteSetting: (key) => `${API_BASE_URL}/settings/${key}`,
    removeAvailableStock: `${API_BASE_URL}/remove_stock_stats`,
};