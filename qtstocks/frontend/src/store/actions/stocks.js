// Action Types
export const FETCH_STOCKS = 'stocks/fetchStocks';
export const FETCH_STATS = 'stocks/fetchStats';
export const PULL_STOCK_STATS = 'stocks/pullStockStats';
export const REMOVE_STATS = 'stocks/removeStats';
export const EXPORT_STOCK_DATA = 'stocks/exportStockData';
export const EXPORT_GRAPH_PDF = 'stocks/exportGraphPdf';
export const PULL_STOCK_LIST = 'stocks/pullStockList';
export const FETCH_EXCHANGES = 'stocks/fetchExchanges';
export const SET_MESSAGE = 'stocks/setMessage';
// Action Creators
export const fetchStats = () => ({ type: FETCH_STATS });
export const fetchStocks = (payload) => ({ type: FETCH_STOCKS, payload });
export const removeStats = (payload) => ({ type: REMOVE_STATS, payload });
export const pullStockStats = (payload) => ({ type: PULL_STOCK_STATS, payload });
export const exportCsv = () => ({ type: EXPORT_STOCK_DATA });
export const exportGraphPdf = () => ({ type: EXPORT_GRAPH_PDF });
export const pullStockList = () => ({ type: PULL_STOCK_LIST });
export const fetchExchanges = () => ({ type: FETCH_EXCHANGES });
export const setMessage = (payload) => ({ type: SET_MESSAGE, payload });
