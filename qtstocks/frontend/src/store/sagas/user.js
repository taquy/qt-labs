import * as effects from 'redux-saga/effects';
import api from '../apis/user';
import { setUsers, setError } from '../slices/user';
import { FETCH_USERS, CREATE_USER, UPDATE_USER, DELETE_USER, TOGGLE_ACTIVE } from '../actions/user';

function* fetchUsersSaga() {
  try {
    const response = yield effects.call(api.fetchUsers);
    yield effects.put(setUsers(response));
  } catch (error) {
    yield effects.put(setError(error));
  }
}

function* createUserSaga(action) {
  try {
    const response = yield effects.call(api.createUser, action.user);
    yield effects.put(setUsers(response));
  } catch (error) {
    yield effects.put(setError(error));
  }
}

function* updateUserSaga(action) {
  try {
    const response = yield effects.call(api.updateUser, action.user);
    yield effects.put(setUsers(response));
  } catch (error) {
    yield effects.put(setError(error));
  }
}

function* deleteUserSaga(action) {
  try {
    const response = yield effects.call(api.deleteUser, action.userId);
    yield effects.put(setUsers(response));
  } catch (error) {
    yield effects.put(setError(error));
  }
}

function* toggleActiveSaga(action) {
  try {
    const response = yield effects.call(api.toggleActive, action.userId);
    yield effects.put(setUsers(response));
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
