import * as effects from 'redux-saga/effects';
import { setIsLoggedIn, setAuthToken, setCheckingLogin, setError } from '../slices/auth';
import { handleApiError } from '../utils';
import axios from 'axios';
import {
  LOGOUT,
  LOGIN,
  GOOGLE_LOGIN,
  CHECK_IS_LOGGED_IN
} from '../actions/auth';

import api from '../apis/auth';

function* checkIsLoggedInSaga() {
  const isLoggedIn = localStorage.getItem('isLoggedIn');
  const authToken = localStorage.getItem('authToken');
  yield effects.put(setCheckingLogin(true));
  if (isLoggedIn && authToken) {
    yield effects.put(setIsLoggedIn(true));
    yield effects.put(setAuthToken(authToken));
    yield effects.put(setError(''));
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
