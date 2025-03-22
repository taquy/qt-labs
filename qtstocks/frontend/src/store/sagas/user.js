import * as effects from 'redux-saga/effects';
import api from '../apis/user';
import { setUsers, setError } from '../slices/user';
import {
  FETCH_USERS,
  FETCH_USERS_SUCCESS,
  FETCH_USERS_FAILURE,
  CREATE_USER,
  UPDATE_USER,
  DELETE_USER,
  TOGGLE_ACTIVE,
  TOGGLE_ADMIN
} from '../actions/user';

function* fetchUsersSaga(action) {
  try {
    const response = yield effects.call(api.fetchUsers, action.page, action.limit);
    const users = Array.isArray(response.items) ? response.items : [];
    const hasMore = response.has_next || false;
    yield effects.put({ 
      type: FETCH_USERS_SUCCESS, 
      payload: {
        users,
        hasMore,
        page: response.current_page,
        total: response.total,
        pages: response.pages
      }
    });
  } catch (error) {
    const errorMessage = error.response?.data?.message || error.message;
    yield effects.put({ 
      type: FETCH_USERS_FAILURE, 
      payload: { error: errorMessage }
    });
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
    // First update the user
    yield effects.call(api.updateUser, action.userId, action.userData);
    // Then fetch the updated users list
    const usersResponse = yield effects.call(api.fetchUsers, 1, 20);
    const users = Array.isArray(usersResponse.items) ? usersResponse.items : [];
    yield effects.put(setUsers(users));
  } catch (error) {
    const errorMessage = error.response?.data?.message || error.message;
    yield effects.put(setError(errorMessage));
  }
}

function* deleteUserSaga(action) {
  try {
    // First delete the user
    yield effects.call(api.deleteUser, action.userId);
    // Then fetch the updated users list
    const usersResponse = yield effects.call(api.fetchUsers, 1, 20);
    const users = Array.isArray(usersResponse.items) ? usersResponse.items : [];
    yield effects.put(setUsers(users));
  } catch (error) {
    const errorMessage = error.response?.data?.message || error.message;
    yield effects.put(setError(errorMessage));
  }
}

function* toggleActiveSaga(action) {
  try {
    // First toggle the active status
    yield effects.call(api.toggleActive, action.userId);
    // Then fetch the updated users list
    const usersResponse = yield effects.call(api.fetchUsers, 1, 20);
    const users = Array.isArray(usersResponse.items) ? usersResponse.items : [];
    yield effects.put(setUsers(users));
  } catch (error) {
    const errorMessage = error.response?.data?.message || error.message;
    yield effects.put(setError(errorMessage));
  }
}

function* toggleAdminSaga(action) {
  try {
    // First toggle the admin status
    yield effects.call(api.toggleAdmin, action.userId);
    // Then fetch the updated users list
    const usersResponse = yield effects.call(api.fetchUsers, 1, 20);
    const users = Array.isArray(usersResponse.items) ? usersResponse.items : [];
    yield effects.put(setUsers(users));
  } catch (error) {
    const errorMessage = error.response?.data?.message || error.message;
    yield effects.put(setError(errorMessage));
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
