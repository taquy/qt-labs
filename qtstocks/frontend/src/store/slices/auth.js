import { createSlice } from '@reduxjs/toolkit';

const ErrorActions = {
  REGISTER: "register",
  LOGIN: "login",
  GOOGLE_LOGIN: "googleLogin",
  LOGOUT: "logout",
  GET_USER_INFO: "getUserInfo",
};

const initialState = {
  isLoggedIn: false,
  isRegistered: false,
  authToken: null,
  checkingLogin: true,
  userInfo: null,
  loading: false,
  errors: {
    [ErrorActions.REGISTER]: "",
    [ErrorActions.LOGIN]: "",
    [ErrorActions.GOOGLE_LOGIN]: "",
    [ErrorActions.LOGOUT]: "",
    [ErrorActions.GET_USER_INFO]: "",
  },
  message: "",
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
      state.errors[action.payload.action] = action.payload.message;
    },
    setMessage: (state, action) => {
      state.message = action.payload;
    },
    setIsRegistered: (state, action) => {
      state.isRegistered = action.payload;
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
  setMessage,
  setIsRegistered,
} = authSlice.actions;

export default authSlice.reducer;

export { ErrorActions };
