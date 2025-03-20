import { createSlice } from '@reduxjs/toolkit';
import { sharedReducer, sharedInitialState } from './shared';
const initialState = {
  isLoggedIn: false,
  authToken: null,
  checkingLogin: true,
  ...sharedInitialState,
};

const authSlice = createSlice({
  name: 'auth',
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
    setCheckingLogin: (state, action) => {
      state.checkingLogin = action.payload;
    },
    ...sharedReducer,
  }
});

export const {
  setIsLoggedIn,
  setAuthToken,
  setCheckingLogin,
  setError,
  setLoading,
  clearError,
} = authSlice.actions;

export default authSlice.reducer;
