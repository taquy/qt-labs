import { createSlice } from '@reduxjs/toolkit';
import { sharedReducer, sharedInitialState } from './shared';
const initialState = {
  isLoggedIn: false,
  authToken: null,
  checkingLogin: true,
  userInfo: null,
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
    setUserInfo: (state, action) => {
      state.userInfo = action.payload;
    },
    ...sharedReducer,
  }
});

export const {
  setIsLoggedIn,
  setAuthToken,
  setCheckingLogin,
  setUserInfo,
  setError,
  setLoading,
  clearError,
} = authSlice.actions;

export default authSlice.reducer;
