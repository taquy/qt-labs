import { createSlice } from '@reduxjs/toolkit';
import { commonState, commonSlice } from './commonSlice';

const METRICS = {
  'market_cap': 'Market Cap',
  'price': 'Price',
  'eps': 'EPS',
  'pe': 'P/E',
  'pb': 'P/B'
};

const initialState = {
  stocks: [],
  availableStocks: [],
  metrics: METRICS,
  fetchingStockStats: false,
  ...commonState,
};

const stockGraphSlice = createSlice({
  name: 'stockGraph',
  initialState,
  reducers: {
    setStocks: (state, action) => {
      state.stocks = action.payload;
    },
    setAvailableStocks: (state, action) => {
      state.availableStocks = action.payload;
    },
    setFetchingStockStats: (state, action) => {
      state.fetchingStockStats = action.payload;
    },
    ...commonSlice
  }
});

export const {
  setAvailableStocks,
  setError,
  setLoading,
  setStocks,
  setFetchingStockStats,
} = stockGraphSlice.actions;

export default stockGraphSlice.reducer;