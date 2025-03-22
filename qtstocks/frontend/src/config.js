const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const API_AUTH_ENDPOINTS = {
    login: `${API_BASE_URL}/auth/login`,
    googleLogin: `${API_BASE_URL}/login/google`,
    register: `${API_BASE_URL}/auth/register`,
    logout: `${API_BASE_URL}/auth/logout`,
}

const API_SETTINGS_ENDPOINTS = {
    settings: (type) => `${API_BASE_URL}/settings/${type}`,
    deleteSetting: (key) => `${API_BASE_URL}/settings/${key}`,
    updateSetting: (key) => `${API_BASE_URL}/settings/${key}`,
}

const API_STOCK_ENDPOINTS = {
    stats: `${API_BASE_URL}/stocks/stats`,
    stocks: `${API_BASE_URL}/stocks`,
    pullStockList: `${API_BASE_URL}/stocks/pull_stock_list`,
    pullStockStats: `${API_BASE_URL}/stocks/pull_stock_stats`,
    removeStats: `${API_BASE_URL}/stocks/remove_stats`,
    exportCsv: `${API_BASE_URL}/stocks/export`,
    exportGraphPdf: `${API_BASE_URL}/stocks/export/pdf`,
    exchanges: `${API_BASE_URL}/stocks/exchanges`,
};

export { API_AUTH_ENDPOINTS, API_SETTINGS_ENDPOINTS, API_STOCK_ENDPOINTS };
