import { createSlice } from '@reduxjs/toolkit';
import { sharedReducer, sharedInitialState } from './shared';

const initialState = {
  settings: null,
  ...sharedInitialState,
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setSettings: (state, action) => {
      state.settings = action.payload;
    },
    ...sharedReducer,
  }
});

export const {
  setSettings,
  setError,
  setLoading,
  clearError,
} = settingsSlice.actions;

export default settingsSlice.reducer;