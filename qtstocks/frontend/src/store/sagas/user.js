import * as effects from 'redux-saga/effects';
import api from '../apis/user';
import { setUsers, setError } from '../slices/user';
import { FETCH_USERS, CREATE_USER, UPDATE_USER, DELETE_USER } from '../actions/user';
function* fetchUsersSaga() {
  // try {
    const response = yield effects.call(api.fetchUsers);
    yield effects.put(setUsers(response));
  // } catch (error) {
  //   yield effects.put(setError(error));
  // }
}

function* createUserSaga() {
  // try {
    const response = yield effects.call(api.createUser);
    yield effects.put(setUsers(response));
  // } catch (error) {
  //   yield effects.put(setError(error));
  // }
}

function* updateUserSaga() {
  // try {
    const response = yield effects.call(api.updateUser);
    yield effects.put(setUsers(response));
  // } catch (error) {
  //   yield effects.put(setError(error));
  // }
}

function* deleteUserSaga() {
  // try {
    const response = yield effects.call(api.deleteUser);
    yield effects.put(setUsers(response));
  // } catch (error) {
  //   yield effects.put(setError(error));
  // }
}

export function* userSaga() {
  yield effects.takeLatest(FETCH_USERS, fetchUsersSaga);
  yield effects.takeLatest(CREATE_USER, createUserSaga);
  yield effects.takeLatest(UPDATE_USER, updateUserSaga);
  yield effects.takeLatest(DELETE_USER, deleteUserSaga);
}
