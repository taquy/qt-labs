import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  availableStocks: [],
  selectedStocks: [],
  chartData: null,
  error: null,
  loading: false,
  settings: null
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
  setChartData,
  setError,
  setLoading,
  setSettings,
  clearError,
  clearChartData
} = stockGraphSlice.actions;

export default stockGraphSlice.reducer; 