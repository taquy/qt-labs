import { createSlice } from '@reduxjs/toolkit';

const METRICS = {
  'market_cap': 'Market Cap',
  'price': 'Price',
  'eps': 'EPS',
  'pe': 'P/E',
  'pb': 'P/B'
};

const initialState = {
  availableStocks: [],
  selectedStocks: [],
  chartData: null,
  error: null,
  loading: false,
  settings: null,
  metrics: METRICS,
};

const stockGraphSlice = createSlice({
  name: 'stockGraph',
  initialState,
  reducers: {
    setAvailableStocks: (state, action) => {
      state.availableStocks = action.payload;
    },
    setSelectedStocks: (state, action) => {
      state.selectedStocks = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setSettings: (state, action) => {
      state.settings = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  }
});

export const {
  setAvailableStocks,
  setSelectedStocks,
  setError,
  setLoading,
  setSettings,
  clearError,
} = stockGraphSlice.actions;

export default stockGraphSlice.reducer; 