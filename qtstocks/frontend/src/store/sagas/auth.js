import * as effects from 'redux-saga/effects';
import { setIsLoggedIn, setAuthToken, setCheckingLogin, setError, setUserInfo, setMessage, setLoading } from '../slices/auth';
import { handleApiError } from '../utils';
import axios from 'axios';
import {
  LOGOUT,
  LOGIN,
  GOOGLE_LOGIN,
  CHECK_IS_LOGGED_IN,
  GET_USER_INFO,
  RESET_STATE,
  SET_MESSAGE,
  REGISTER,
  SET_ERROR
} from '../actions/auth';

import api from '../apis/auth';

function* registerSaga(action) {
  try {
    yield effects.put(setError(''));
    yield effects.put(setLoading(true));
    const response = yield effects.call(api.register, action.payload);
    yield effects.put(setMessage(response.message));
  } catch (error) {
    yield effects.put(setError('Failed to register'));
    yield effects.call(handleApiError, error, 'registerSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

function* getUserInfoSaga() {
  try {
    yield effects.put(setLoading(true));
    const response = yield effects.call(api.getUserInfo);
    yield effects.put(setUserInfo(response));
  } catch (error) {
    yield effects.put(setError('Failed to get user info'));
    yield effects.call(handleApiError, error, 'getUserInfoSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

function* checkIsLoggedInSaga() {
  try {
    yield effects.put(setLoading(true));
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const authToken = localStorage.getItem('authToken');
    yield effects.put(setCheckingLogin(true));
    if (isLoggedIn && authToken) {
    yield effects.put(setIsLoggedIn(true));
    yield effects.put(setAuthToken(authToken));
    yield effects.put(setError(''));
    // Set axios default header for subsequent requests
    axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
    // Get user info after confirming login
    yield effects.call(getUserInfoSaga);
  } else {
    yield effects.put(setIsLoggedIn(false));
    yield effects.put({
      type: RESET_STATE
    });
    delete axios.defaults.headers.common['Authorization'];
  }
  yield effects.put(setCheckingLogin(false));
  } finally {
    yield effects.put(setLoading(false));
  }
}

function* googleLoginSaga(action) {
  try {
    yield effects.put(setError(''));
    yield effects.put(setLoading(true));
    const response = yield effects.call(api.googleLogin, action.payload);
    if (response.token) {
      yield effects.put(setIsLoggedIn(true));
      yield effects.put(setAuthToken(response.token));
      yield effects.call(getUserInfoSaga);
    } else {
      yield effects.put(setError('Failed to login'));
    }
  } catch (error) {
    yield effects.put(setError('Failed to login'));
    yield effects.call(handleApiError, error, 'googleLoginSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

function* loginSaga(action) {
  try {
    yield effects.put(setError(''));
    yield effects.put(setLoading(true));
    const response = yield effects.call(api.login, action.payload);
    if (response.token) {
      yield effects.put(setIsLoggedIn(true));
      yield effects.put(setAuthToken(response.token));
      yield effects.call(getUserInfoSaga);
    } else {
      yield effects.put(setError('Failed to login'));
    }
  } catch (error) {
    yield effects.put(setError('Failed to login'));
    yield effects.call(handleApiError, error, 'loginSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

function* logoutSaga() {
  try {
    yield effects.put(setError(''));
    yield effects.put(setLoading(true));
    yield effects.call(api.logout);
    localStorage.removeItem('authToken');
    localStorage.removeItem('isLoggedIn');
    delete axios.defaults.headers.common['Authorization'];
    yield effects.put(setIsLoggedIn(false));
  } catch (error) {
    yield effects.put(setError('Failed to logout'));
    yield effects.call(handleApiError, error, 'logoutSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

function* setMessageSaga(action) {
  yield effects.put(setMessage(action.payload));
}

function* setErrorSaga(action) {
  yield effects.put(setError(action.payload));
}

// Root Saga
export function* authSaga() {
  yield effects.takeLatest(LOGOUT, logoutSaga);
  yield effects.takeLatest(LOGIN, loginSaga);
  yield effects.takeLatest(GOOGLE_LOGIN, googleLoginSaga);
  yield effects.takeLatest(CHECK_IS_LOGGED_IN, checkIsLoggedInSaga);
  yield effects.takeLatest(GET_USER_INFO, getUserInfoSaga);
  yield effects.takeLatest(SET_MESSAGE, setMessageSaga);
  yield effects.takeLatest(REGISTER, registerSaga);
  yield effects.takeLatest(SET_ERROR, setErrorSaga);
}
