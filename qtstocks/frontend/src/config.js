const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

export const API_AUTH_ENDPOINTS = {
    login: `${API_BASE_URL}/auth/login`,
    googleLogin: `${API_BASE_URL}/login/google`,
    register: `${API_BASE_URL}/auth/register`,
    logout: `${API_BASE_URL}/logout`,
}

export const API_SETTINGS_ENDPOINTS = {
    settings: `${API_BASE_URL}/settings`,
    deleteSetting: (key) => `${API_BASE_URL}/settings/${key}`,
    updateSetting: (key) => `${API_BASE_URL}/settings/${key}`,
}

export const API_STOCK_ENDPOINTS = {
    stocksWithStats: `${API_BASE_URL}/stocks/stats`,
    stocks: `${API_BASE_URL}/stocks`,
    pullStockList: `${API_BASE_URL}/stocks/pull_stock_list`,
    fetchStockData: `${API_BASE_URL}/fetch_stock_data`,
    removeAvailableStock: `${API_BASE_URL}/remove_stock_stats`,
    exportCsv: `${API_BASE_URL}/export_csv`,
    exportGraphPdf: `${API_BASE_URL}/export_graph_pdf`,
    exchanges: `${API_BASE_URL}/stocks/exchanges`,
};
