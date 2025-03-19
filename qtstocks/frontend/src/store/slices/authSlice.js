import { createSlice } from '@reduxjs/toolkit';
import commonSlice from './commonSlice';
const initialState = {
  error: null,
  isLoggedIn: false,
  authToken: null,
  checkingLogin: true,
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
    ...commonSlice,
  }
});

export const {
  setError,
  setIsLoggedIn,
  setAuthToken,
  setCheckingLogin,
} = authSlice.actions;

export default authSlice.reducer;
