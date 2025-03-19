import { createSlice } from '@reduxjs/toolkit';
import { sharedReducer, sharedInitialState } from './sharedSlice';

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
  ...sharedInitialState,
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
} = stockGraphSlice.actions;

export default stockGraphSlice.reducer;