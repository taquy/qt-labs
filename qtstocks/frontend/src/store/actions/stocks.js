// Action Types
export const FETCH_STOCKS = 'stocks/fetchStocks';
export const FETCH_AVAILABLE_STOCKS = 'stocks/fetchAvailableStocks';
export const FETCH_STOCK_DATA = 'stocks/fetchStockData';
export const REMOVE_AVAILABLE_STOCK = 'stocks/removeAvailableStock';
export const EXPORT_STOCK_DATA = 'stocks/exportStockData';
export const EXPORT_GRAPH_PDF = 'stocks/exportGraphPdf';
export const PULL_STOCK_LIST = 'stocks/pullStockList';
export const FETCH_EXCHANGES = 'stocks/fetchExchanges';

// Action Creators
export const fetchAvailableStocks = () => ({ type: FETCH_AVAILABLE_STOCKS });
export const fetchStocks = (payload) => ({ type: FETCH_STOCKS, payload });
export const removeAvailableStock = (payload) => ({ type: REMOVE_AVAILABLE_STOCK, payload });
export const fetchStockData = (payload) => ({ type: FETCH_STOCK_DATA, payload });
export const exportCsv = () => ({ type: EXPORT_STOCK_DATA });
export const exportGraphPdf = () => ({ type: EXPORT_GRAPH_PDF });
export const pullStockList = () => ({ type: PULL_STOCK_LIST });
export const fetchExchanges = () => ({ type: FETCH_EXCHANGES });
