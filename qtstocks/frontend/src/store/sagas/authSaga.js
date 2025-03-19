import { effects } from 'redux-saga';
import { setError, setIsLoggedIn, setAuthToken, setCheckingLogin } from '../slices/authSlice';
import { handleApiError } from '../utils';
import axios from 'axios';
import { API_ENDPOINTS } from '../../config';

export const LOGOUT = 'aytg/logout';
export const LOGIN = 'aytg/login';
export const GOOGLE_LOGIN = 'aytg/googleLogin';
export const CHECK_IS_LOGGED_IN = 'aytg/checkIsLoggedIn';

export const login = (username, password) => ({ type: LOGIN, payload: { username, password } });
export const logout = () => ({ type: LOGOUT });
export const googleLogin = (token) => ({ type: GOOGLE_LOGIN, payload: { token } });
export const checkIsLoggedIn = () => ({ type: CHECK_IS_LOGGED_IN });

const api = {
  logout: async () => {
    const response = await axios.post(API_ENDPOINTS.logout, {}, getRequestConfig());
    return response.data;
  },
  login: async (payload) => {
    const response = await axios.post(API_ENDPOINTS.login, payload);
    return response.data;
  },
  googleLogin: async (token) => {
    const response = await axios.post(API_ENDPOINTS.googleLogin, token);
    return response.data;
  },
};

function* checkIsLoggedInSaga() {
  const isLoggedIn = localStorage.getItem('isLoggedIn');
  const authToken = localStorage.getItem('authToken');
  yield effects.put(setCheckingLogin(true));
  if (isLoggedIn && authToken) {
    yield effects.put(setIsLoggedIn(true));
    yield effects.put(setAuthToken(authToken));
  } else {
    yield effects.put(setIsLoggedIn(false));
  }
  yield effects.put(setCheckingLogin(false));
}

function* googleLoginSaga(action) {
  try {
    const response = yield effects.call(api.googleLogin, action.payload);
    if (response.token) {
      yield effects.put(setIsLoggedIn(true));
      yield effects.put(setAuthToken(response.token));
    } else {
      yield effects.put(setError('Failed to login'));
    }
  } catch (error) {
    yield effects.put(setError('Failed to login'));
  }
}

function* loginSaga(action) {
  try {
    const response = yield effects.call(api.login, action.payload);
    yield effects.put(setIsLoggedIn(true));
    yield effects.put(setAuthToken(response.token));
  } catch (error) {
    yield effects.put(setError('Failed to login'));
  }
}

function* logoutSaga() {
  try {
    yield effects.call(api.logout);
    localStorage.removeItem('authToken');
    localStorage.removeItem('isLoggedIn');
    delete axios.defaults.headers.common['Authorization'];
    yield effects.put(setIsLoggedIn(false));
  } catch (error) {
    yield effects.put(setError('Failed to logout'));
    yield effects.call(handleApiError, error, 'logoutSaga');
  }
}

// Root Saga
export function* authSaga() {
  yield effects.takeLatest(LOGOUT, logoutSaga);
  yield effects.takeLatest(LOGIN, loginSaga);
  yield effects.takeLatest(GOOGLE_LOGIN, googleLoginSaga);
  yield effects.takeLatest(CHECK_IS_LOGGED_IN, checkIsLoggedInSaga);
}
