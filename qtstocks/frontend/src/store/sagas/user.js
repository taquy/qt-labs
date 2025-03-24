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
    yield effects.put(setLoader(LoaderActions.CREATE_USER, true));
    const response = yield effects.call(api.createUser, action.user);
    yield effects.put(setCreateUser(response));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.CREATE_USER,
      message: "Failed to create user",
    }));
  } finally {
    yield effects.put(setLoader(LoaderActions.CREATE_USER, false));
  }
}

function* updateUserSaga(action) {
  try {
    yield effects.put(setLoader(LoaderActions.UPDATE_USER, true));
    yield effects.call(api.updateUser, action.userId, action.userData);
    yield effects.put(setUpdateUser(action.userData));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.UPDATE_USER,
      message: "Failed to update user",
    }));
  } finally {
    yield effects.put(setLoader(LoaderActions.UPDATE_USER, false));
  }
}

function* deleteUserSaga(action) {
  try {
    yield effects.put(setLoader(LoaderActions.DELETE_USER, true));
    const response = yield effects.call(api.deleteUser, action.userId);
    yield effects.put(setDeleteUser(response));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.DELETE_USER,
      message: "Failed to delete user",
    }));
  } finally {
    yield effects.put(setLoader(LoaderActions.DELETE_USER, false));
  }
}

function* toggleActiveSaga(action) {
  try {
    yield effects.put(setLoader(LoaderActions.TOGGLE_ACTIVE, true));
    yield effects.call(api.toggleActive, action.payload.id);
    yield effects.put(setToggleActive(action.payload.id));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.TOGGLE_ACTIVE,
      message: "Failed to toggle active",
    }));
  } finally {
    yield effects.put(setLoader(LoaderActions.TOGGLE_ACTIVE, false));
  }
}

function* toggleAdminSaga(action) {
  try {
    yield effects.put(setLoader(LoaderActions.TOGGLE_ADMIN, true));
    yield effects.call(api.toggleAdmin, action.payload.id);
    yield effects.put(setToggleAdmin(action.payload.id));
  } catch (error) {
    yield effects.put(setError({
      action: ErrorActions.TOGGLE_ADMIN,
      message: "Failed to toggle admin",
    }));
  } finally {
    yield effects.put(setLoader(LoaderActions.TOGGLE_ADMIN, false));
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
