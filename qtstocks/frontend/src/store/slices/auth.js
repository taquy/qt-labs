import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isLoggedIn: false,
  authToken: null,
  checkingLogin: true,
  userInfo: null,
  loading: false,
  error: null,
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
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    }
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
