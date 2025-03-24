import * as effects from 'redux-saga/effects';
import api from '../apis/user';
import { setUsers, setError, setLoader, getUsersQuery } from '../slices/user';
import { LoaderActions, ErrorActions } from '../slices/user';
import { handleApiError } from '../utils';
import {
  FETCH_USERS,
  CREATE_USER,
  UPDATE_USER,
  DELETE_USER,
  TOGGLE_ACTIVE_REQUEST,
  TOGGLE_ACTIVE_SUCCESS,
  TOGGLE_ACTIVE_FAILURE,
  TOGGLE_ADMIN_REQUEST,
  TOGGLE_ADMIN_SUCCESS,
  TOGGLE_ADMIN_FAILURE
} from '../actions/user';

function* fetchUsersSaga() {
  try {
    const state_query = yield effects.select(getUsersQuery);
    const query = {...state_query.payload.users.users_query};
    yield effects.put(setLoader(LoaderActions.FETCH_USERS, true));
    const results = yield effects.call(api.fetchUsers, query);
    let refresh = query.search.trim() !== "" || query.page === 1;
    refresh = refresh && results.items.length > 0;
    yield effects.put(setUsers({...results, refresh}));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.STOCK_SELECTOR,
      message: 'Failed to fetch users',
    }));
    yield effects.call(handleApiError, error, 'fetchStocksSaga');
  } finally {
    yield effects.put(setLoader(LoaderActions.FETCH_USERS, false));
  }
}

function* createUserSaga(action) {
  try {
    const response = yield effects.call(api.createUser, action.user);
    const users = Array.isArray(response) ? response : [];
    yield effects.put(setUsers(users));
  } catch (error) {
    const errorMessage = error.response?.data?.message || error.message;
    yield effects.put(setError(errorMessage));
  }
}

function* updateUserSaga(action) {
  try {
    yield effects.call(api.updateUser, action.userId, action.userData);
    yield effects.call(fetchUsersSaga);
  } catch (error) {
    const errorMessage = error.response?.data?.message || error.message;
    yield effects.put(setError(errorMessage));
  }
}

function* deleteUserSaga(action) {
  try {
    yield effects.call(api.deleteUser, action.userId);
    yield effects.call(fetchUsersSaga);
  } catch (error) {
    const errorMessage = error.response?.data?.message || error.message;
    yield effects.put(setError(errorMessage));
  }
}

function* toggleActiveSaga(action) {
  try {
    yield effects.call(api.toggleActive, action.payload.id);
    yield effects.put({ 
      type: TOGGLE_ACTIVE_SUCCESS, 
      payload: { id: action.payload.id }
    });
  } catch (error) {
    const errorMessage = error.response?.data?.message || error.message;
    yield effects.put({ 
      type: TOGGLE_ACTIVE_FAILURE, 
      payload: { error: errorMessage }
    });
  }
}

function* toggleAdminSaga(action) {
  try {
    yield effects.call(api.toggleAdmin, action.payload.id);
    yield effects.put({ 
      type: TOGGLE_ADMIN_SUCCESS, 
      payload: { id: action.payload.id }
    });
  } catch (error) {
    const errorMessage = error.response?.data?.message || error.message;
    yield effects.put({ 
      type: TOGGLE_ADMIN_FAILURE, 
      payload: { error: errorMessage }
    });
  }
}

export function* userSaga() {
  yield effects.takeLatest(FETCH_USERS, fetchUsersSaga);
  yield effects.takeLatest(CREATE_USER, createUserSaga);
  yield effects.takeLatest(UPDATE_USER, updateUserSaga);
  yield effects.takeLatest(DELETE_USER, deleteUserSaga);
  yield effects.takeLatest(TOGGLE_ACTIVE_REQUEST, toggleActiveSaga);
  yield effects.takeLatest(TOGGLE_ADMIN_REQUEST, toggleAdminSaga);
}
