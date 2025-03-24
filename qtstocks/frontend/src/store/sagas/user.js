import * as effects from 'redux-saga/effects';
import api from '../apis/user';
import { setUsers, setError, setLoader, getUsersQuery, setCreateUser, setUpdateUser, setDeleteUser, setToggleActive, setToggleAdmin } from '../slices/user';
import { LoaderActions, ErrorActions } from '../slices/user';
import { handleApiError } from '../utils';
import {
  FETCH_USERS,
  CREATE_USER,
  UPDATE_USER,
  DELETE_USER,
  TOGGLE_ACTIVE,
  TOGGLE_ADMIN,
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
    yield effects.put(setCreateUser(response));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.CREATE_USER,
      message: "Failed to create user",
    }));
  }
}

function* updateUserSaga(action) {
  try {
    yield effects.call(api.updateUser, action.userId, action.userData);
    yield effects.put(setUpdateUser(action.userData));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.UPDATE_USER,
      message: "Failed to update user",
    }));
  }
}

function* deleteUserSaga(action) {
  try {
    const response = yield effects.call(api.deleteUser, action.userId);
    yield effects.put(setDeleteUser(response));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.DELETE_USER,
      message: "Failed to delete user",
    }));
  }
}

function* toggleActiveSaga(action) {
  try {
    yield effects.call(api.toggleActive, action.payload.id);
    yield effects.put(setToggleActive(action.payload.id));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.TOGGLE_ACTIVE,
      message: "Failed to toggle active",
    }));
  }
}

function* toggleAdminSaga(action) {
  try {
    yield effects.call(api.toggleAdmin, action.payload.id);
    yield effects.put(setToggleAdmin(action.payload.id));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.TOGGLE_ADMIN,
      message: "Failed to toggle admin",
    }));
  }
}

export function* userSaga() {
  yield effects.takeLatest(FETCH_USERS, fetchUsersSaga);
  yield effects.takeLatest(CREATE_USER, createUserSaga);
  yield effects.takeLatest(UPDATE_USER, updateUserSaga);
  yield effects.takeLatest(DELETE_USER, deleteUserSaga);
  yield effects.takeLatest(TOGGLE_ACTIVE, toggleActiveSaga);
  yield effects.takeLatest(TOGGLE_ADMIN, toggleAdminSaga);
}
