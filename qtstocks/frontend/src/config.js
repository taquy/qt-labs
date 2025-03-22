const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const API_AUTH_ENDPOINTS = {
    login: `${API_BASE_URL}/auth/login`,
    googleLogin: `${API_BASE_URL}/auth/login/google`,
    register: `${API_BASE_URL}/auth/register`,
    logout: `${API_BASE_URL}/auth/logout`,
    getUserInfo: `${API_BASE_URL}/auth/me`,
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

const API_USER_ENDPOINTS = {
    users: `${API_BASE_URL}/users`,
    createUser: `${API_BASE_URL}/users`,
    updateUser: `${API_BASE_URL}/users`,
    deleteUser: `${API_BASE_URL}/users`,
    toggleActive: (userId) => `${API_BASE_URL}/users/${userId}/toggle_active`,
    toggleAdmin: (userId) => `${API_BASE_URL}/users/${userId}/toggle_admin`,
}

export { API_AUTH_ENDPOINTS, API_SETTINGS_ENDPOINTS, API_STOCK_ENDPOINTS, API_USER_ENDPOINTS };
