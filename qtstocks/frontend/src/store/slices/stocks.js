import { createSlice } from '@reduxjs/toolkit';

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
  'PULL_STOCK_STATS': 'pullStockStats',
  'EXPORT_STOCK_DATA': 'exportStockData',
  'EXPORT_GRAPH_PDF': 'exportGraphPdf',
  'REMOVE_STATS': 'removeStats',
}

const MessageActions = {
  'PULL_STOCK_LIST': 'pullStockList',
}

const ErrorActions = {
  'STOCK_SELECTOR': 'stockSelector',
  'STOCK_GRAPH': 'stockGraph',
  'STOCK_TABLE': 'stockTable',
}

const initialState = {
  stocks: {
    items: [],
    current_page: 0,
    has_next: true,
  },
  stats: [],
  metrics: METRICS,
  exportedCsv: null,
  loaders: {
    [LoaderActions.FETCH_STOCKS]: false,
    [LoaderActions.PULL_STOCK_LIST]: false,
    [LoaderActions.PULL_STOCK_STATS]: false,
    [LoaderActions.EXPORT_STOCK_DATA]: false,
    [LoaderActions.EXPORT_GRAPH_PDF]: false,
    [LoaderActions.REMOVE_STATS]: false,
  },
  exchanges: [],
  messages: {},
  errors: {
    [ErrorActions.STOCK_SELECTOR]: "",
    [ErrorActions.STOCK_GRAPH]: "",
    [ErrorActions.STOCK_TABLE]: "",
  },
};

const stockGraphSlice = createSlice({
  name: 'stocks',
  initialState,
  reducers: {
    setStocks: (state, action) => {
      if (action.payload) {
        state.stocks.items = action.payload.refresh ? action.payload.items : [...state.stocks.items, ...action.payload.items];
        state.stocks.has_next = action.payload.refresh ? true : action.payload.has_next;
        state.stocks.current_page = action.payload.current_page;
      } else {
        state.stocks = {
          items: [],
          has_next: true,
        };
      }
    },
    setStats: (state, action) => {
      state.stats = action.payload ? action.payload : [];
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
    setError: (state, action) => {
      state.errors[action.payload.action] = action.payload.message;
    },
    clearError: (state, action) => {
      state.errors[action.payload.action] = "";
    },
  }
});

export const {
  setStats,
  setStocks,
  setError,
  clearError,
  setExportedCsv,
  setExportedGraphPdf,
  setLoader,
  setExchanges,
  setMessages,
  removeStats,
} = stockGraphSlice.actions;

export default stockGraphSlice.reducer;

export { LoaderActions, MessageActions, ErrorActions };