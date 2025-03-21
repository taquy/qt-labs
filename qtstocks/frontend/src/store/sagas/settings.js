import { call, put, takeLatest } from 'redux-saga/effects';
import { FETCH_SETTINGS, SAVE_SETTINGS } from '../actions/settings';
import api from '../apis/settings';
import { setSettings, setError } from '../slices/settings';

function* fetchSettingsSaga(action) {
  try {
    yield put(setError(""))
    const response = yield call(api.fetchSettings);
    yield put(setSettings(action.payload.type, response));
  } catch (error) {
    yield put(setError( error.message));
  }
}

function* saveSettingsSaga(action) {
  try {
    yield put(setError(""))
    yield call(api.saveSettingsSaga, action.payload);
  } catch (error) {
    yield put(setError( error.message));
  }
}

export default function* settingsSaga() {
  yield takeLatest(FETCH_SETTINGS, fetchSettingsSaga);
  yield takeLatest(SAVE_SETTINGS, saveSettingsSaga);
}
