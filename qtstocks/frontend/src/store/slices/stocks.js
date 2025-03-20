import { createSlice } from '@reduxjs/toolkit';
import { sharedReducer, sharedInitialState } from './shared';

const METRICS = {
  'market_cap': 'Market Cap',
  'price': 'Price',
  'eps': 'EPS',
  'pe': 'P/E',
  'pb': 'P/B'
};

const LoaderActions = {
  'FETCH_STOCKS': 'fetchStocks',
  'PULL_STOCK_LIST': 'pullStockList',
  'FETCH_STOCK_DATA': 'fetchStockData',
  'EXPORT_STOCK_DATA': 'exportStockData',
  'EXPORT_GRAPH_PDF': 'exportGraphPdf'
}

const MessageActions = {
  'PULL_STOCK_LIST': 'pullStockList',
}

const initialState = {
  stocks: {
    items: [],
    current_page: 0,
    has_next: true,
  },
  availableStocks: [],
  metrics: METRICS,
  fetchingStockStats: false,
  exportedCsv: null,
  loaders: {
    [LoaderActions.FETCH_STOCKS]: false,
    [LoaderActions.PULL_STOCK_LIST]: false,
    [LoaderActions.FETCH_STOCK_DATA]: false,
    [LoaderActions.EXPORT_STOCK_DATA]: false,
    [LoaderActions.EXPORT_GRAPH_PDF]: false,
  },
  exchanges: [],
  messages: {},
  ...sharedInitialState,
};

const stockGraphSlice = createSlice({
  name: 'stocks',
  initialState,
  reducers: {
    setStocks: (state, action) => {
      if (action.payload) {
        state.stocks.items = [...state.stocks.items, ...action.payload.items];
        state.stocks.has_next = action.payload.has_next;
        state.stocks.current_page = action.payload.current_page;
      } else {
        state.stocks = {
          items: [],
          has_next: true,
        };
      }
    },
    setAvailableStocks: (state, action) => {
      state.availableStocks = action.payload ? action.payload : [];
    },
    setFetchingStockStats: (state, action) => {
      state.fetchingStockStats = action.payload;
    },
    setExportedCsv: (state, action) => {
      state.exportedCsv = action.payload;
    },
    setExportedGraphPdf: (state, action) => {
      state.exportedGraphPdf = action.payload;
    },
    setLoader: (state, action) => {
      state.loaders[action.payload.action] = action.payload.value;
    },
    setExchanges: (state, action) => {
      state.exchanges = action.payload ? action.payload : [];
    },
    setMessages: (state, action) => {
      state.messages[action.payload.action] = action.payload.message;
    },
    ...sharedReducer,
  }
});

export const {
  setAvailableStocks,
  setStocks,
  setFetchingStockStats,
  setError,
  setLoading,
  clearError,
  setExportedCsv,
  setExportedGraphPdf,
  setLoader,
  setExchanges,
  setMessages,
} = stockGraphSlice.actions;

export default stockGraphSlice.reducer;

export { LoaderActions, MessageActions };