import * as effects from 'redux-saga/effects';
import api from '../apis/user';
import { setUsers, setError, setLoader, setCreateUser, setUpdateUser, setToggleActive, setToggleAdmin, setUsersQuery } from '../slices/user';
import { LoaderActions, ErrorActions } from '../slices/user';
import { handleApiError } from '../utils';
import {
  FETCH_USERS,
  CREATE_USER,
  UPDATE_USER,
  DELETE_USER,
  TOGGLE_ACTIVE,
  TOGGLE_ADMIN,
  SET_ERROR,  
  SET_USERS_QUERY,
} from '../actions/user';

function* setLoaderSaga(action, status) {
  yield effects.put(setLoader({ type: action, value: status }));
}

function *setUsersQuerySaga(action) {
  yield effects.put(setUsersQuery(action.payload));
}

function* setErrorSaga(action, message) {
  yield effects.put(setError({
    action: action,
    message: message,
  }));
}

function* fetchUsersSaga() {
  yield effects.call(setLoaderSaga, LoaderActions.FETCH_USERS, true);
  try {
    const query = yield effects.select((state) => state.user.users_query);
    const results = yield effects.call(api.fetchUsers, query);
    let refresh = query.search.trim() !== "" || query.page === 1;
    refresh = refresh && results.items.length > 0;
    yield effects.put(setUsers({...results, ...query, refresh}));
  } catch (error) {
    yield effects.call(setErrorSaga, ErrorActions.FETCH_USERS, 'Failed to fetch users');
    yield effects.call(handleApiError, error, 'fetchStocksSaga');
  } finally {
    yield effects.call(setLoaderSaga, LoaderActions.FETCH_USERS, false);
  }
}

function* createUserSaga(action) {
  try {
    yield effects.call(setLoaderSaga, LoaderActions.CREATE_USER, true);
    const response = yield effects.call(api.createUser, action.user);
    yield effects.put(setCreateUser(response));
  } catch (error) {
    yield effects.call(setErrorSaga, ErrorActions.CREATE_USER, "Failed to create user");
  } finally {
    yield effects.call(setLoaderSaga, LoaderActions.CREATE_USER, false);
  }
}

function* updateUserSaga(action) {
  try {
    yield effects.call(setLoaderSaga, LoaderActions.UPDATE_USER, true);
    const response = yield effects.call(api.updateUser, action.payload);
    yield effects.put(setUpdateUser(response));
  } catch (error) {
    yield effects.call(setErrorSaga, ErrorActions.UPDATE_USER, "Failed to update user");
  } finally {
    yield effects.call(setLoaderSaga, LoaderActions.UPDATE_USER, false);
  }
}

function* deleteUserSaga(action) {
  try {
    yield effects.call(setLoaderSaga, LoaderActions.DELETE_USER, true);
    yield effects.call(api.deleteUser, action.payload);
    yield effects.call(fetchUsersSaga);
  } catch (error) {
    yield effects.call(setErrorSaga, ErrorActions.DELETE_USER, "Failed to delete user");
  } finally {
    yield effects.call(setLoaderSaga, LoaderActions.DELETE_USER, false);
  }
}

function* toggleActiveSaga(action) {
  try {
    yield effects.call(setLoaderSaga, LoaderActions.TOGGLE_ACTIVE, true);
    const response = yield effects.call(api.toggleActive, action.payload.id);
    yield effects.put(setToggleActive(response));
  } catch (error) {
    yield effects.call(setErrorSaga, ErrorActions.TOGGLE_ACTIVE, "Failed to toggle active");
  } finally {
    yield effects.call(setLoaderSaga, LoaderActions.TOGGLE_ACTIVE, false);
  }
}

function* toggleAdminSaga(action) {
  try {
    yield effects.call(setLoaderSaga, LoaderActions.TOGGLE_ADMIN, true);
    const response = yield effects.call(api.toggleAdmin, action.payload.id);
    yield effects.put(setToggleAdmin(response));
  } catch (error) {
    yield effects.call(setErrorSaga, ErrorActions.TOGGLE_ADMIN, "Failed to toggle admin");
  } finally {
    yield effects.call(setLoaderSaga, LoaderActions.TOGGLE_ADMIN, false);
  }
}

export function* userSaga() {
  yield effects.takeLatest(FETCH_USERS, fetchUsersSaga);
  yield effects.takeLatest(CREATE_USER, createUserSaga);
  yield effects.takeLatest(UPDATE_USER, updateUserSaga);
  yield effects.takeLatest(DELETE_USER, deleteUserSaga);
  yield effects.takeLatest(TOGGLE_ACTIVE, toggleActiveSaga);
  yield effects.takeLatest(TOGGLE_ADMIN, toggleAdminSaga);
  yield effects.takeLatest(SET_ERROR, setErrorSaga);
  yield effects.takeLatest(SET_USERS_QUERY, setUsersQuerySaga);
}
