import * as effects from 'redux-saga/effects';
import api from '../apis/user';
import { setUsers, setError } from '../slices/user';
import { FETCH_USERS, CREATE_USER, UPDATE_USER, DELETE_USER, TOGGLE_ACTIVE } from '../actions/user';

function* fetchUsersSaga() {
  try {
    const response = yield effects.call(api.fetchUsers);
    // Ensure response is an array
    const users = Array.isArray(response) ? response : [];
    yield effects.put(setUsers(users));
  } catch (error) {
    yield effects.put(setError(error));
    yield effects.put(setUsers([])); // Set empty array on error
  }
}

function* createUserSaga(action) {
  try {
    const response = yield effects.call(api.createUser, action.user);
    const users = Array.isArray(response) ? response : [];
    yield effects.put(setUsers(users));
  } catch (error) {
    yield effects.put(setError(error));
  }
}

function* updateUserSaga(action) {
  try {
    const response = yield effects.call(api.updateUser, action.user);
    const users = Array.isArray(response) ? response : [];
    yield effects.put(setUsers(users));
  } catch (error) {
    yield effects.put(setError(error));
  }
}

function* deleteUserSaga(action) {
  try {
    const response = yield effects.call(api.deleteUser, action.userId);
    const users = Array.isArray(response) ? response : [];
    yield effects.put(setUsers(users));
  } catch (error) {
    yield effects.put(setError(error));
  }
}

function* toggleActiveSaga(action) {
  try {
    // First toggle the active status
    yield effects.call(api.toggleActive, action.userId);
    // Then fetch the updated users list
    const response = yield effects.call(api.fetchUsers);
    const users = Array.isArray(response) ? response : [];
    yield effects.put(setUsers(users));
  } catch (error) {
    yield effects.put(setError(error));
  }
}

export function* userSaga() {
  yield effects.takeLatest(FETCH_USERS, fetchUsersSaga);
  yield effects.takeLatest(CREATE_USER, createUserSaga);
  yield effects.takeLatest(UPDATE_USER, updateUserSaga);
  yield effects.takeLatest(DELETE_USER, deleteUserSaga);
  yield effects.takeLatest(TOGGLE_ACTIVE, toggleActiveSaga);
}
