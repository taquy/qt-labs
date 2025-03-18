import { createSlice } from '@reduxjs/toolkit';

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
  chartData: null,
  error: null,
  loading: false,
  settings: null,
  metrics: METRICS,
  isLoggedIn: false,
  authToken: null,
};

const stockGraphSlice = createSlice({
  name: 'stockGraph',
  initialState,
  reducers: {
    setAuthToken: (state, action) => {
      state.authToken = action.payload;
      localStorage.setItem('authToken', action.payload);
    },
    setIsLoggedIn: (state, action) => {
      state.isLoggedIn = action.payload;
      localStorage.setItem('isLoggedIn', action.payload);
    },
    setStocks: (state, action) => {
      state.stocks = action.payload;
    },
    setAvailableStocks: (state, action) => {
      state.availableStocks = action.payload;
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
  setError,
  setLoading,
  setSettings,
  clearError,
  setStocks,
  setIsLoggedIn,
  setAuthToken,
} = stockGraphSlice.actions;

export default stockGraphSlice.reducer;