import { createSlice } from '@reduxjs/toolkit';

const SettingsTypes = {
  STOCK_TABLE: 'stockTable',
  STOCK_GRAPH: 'stockGraph',
  STOCK_SELECTOR: 'stockSelector',
}

const initialState = {
  settings: {},
  error: null,
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setSettings: (state, action) => {
      const { setting_key, setting_value } = action.payload;
      state.settings[setting_key] = setting_value;
    },
    setError: (state, action) => {
      state.error = action.payload.error;
    },
  }
});

export const {
  setSettings ,
  setError,
} = settingsSlice.actions;
export default settingsSlice.reducer;

export { SettingsTypes };