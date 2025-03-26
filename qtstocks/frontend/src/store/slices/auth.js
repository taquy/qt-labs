import { createSlice } from '@reduxjs/toolkit';

const ErrorActions = {
  register: null,
  login: null,
  googleLogin: null,
  logout: null,
  getUserInfo: null,
};

const initialState = {
  isLoggedIn: false,
  authToken: null,
  checkingLogin: true,
  userInfo: null,
  loading: false,
  errors: {
    [ErrorActions.register]: null,
    [ErrorActions.login]: null,
    [ErrorActions.googleLogin]: null,
    [ErrorActions.logout]: null,
    [ErrorActions.getUserInfo]: null,
  },
  message: null,
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
      state.errors[action.payload.action] = action.payload.error;
    },
    setMessage: (state, action) => {
      state.message = action.payload;
    },
  }
});

export const {
  setIsLoggedIn,
  setAuthToken,
  setCheckingLogin,
  setUserInfo,
  setError,
  setLoading,
  setMessage,
} = authSlice.actions;

export default authSlice.reducer;

export { ErrorActions };
