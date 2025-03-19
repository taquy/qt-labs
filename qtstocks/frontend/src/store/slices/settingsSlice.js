import { createSlice } from '@reduxjs/toolkit';
import { commonState, commonSlice } from './commonSlice';

const initialState = {
  settings: null,
  ...commonState,
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
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
    ...commonSlice
  }
});

export const {
  setSettings,
  setError,
  setLoading,
} = settingsSlice.actions;

export default settingsSlice.reducer;