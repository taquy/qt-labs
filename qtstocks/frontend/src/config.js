export const API_BASE_URL = 'http://localhost:5555';
export const API_ENDPOINTS = {
    login: `${API_BASE_URL}/api/login`,
    logout: `${API_BASE_URL}/api/logout`,
    stocks: `${API_BASE_URL}/api/stocks`,
    stocksWithStats: `${API_BASE_URL}/api/stocks_with_stats`,
    updateGraph: `${API_BASE_URL}/api/update_graph`,
    downloadStockList: `${API_BASE_URL}/api/download_stock_list`,
    fetchStockData: `${API_BASE_URL}/api/fetch_stock_data`,
    settings: `${API_BASE_URL}/api/settings`,
    updateSetting: (key) => `${API_BASE_URL}/api/settings/${key}`,
    deleteSetting: (key) => `${API_BASE_URL}/api/settings/${key}`
}; 