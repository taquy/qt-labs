import * as effects from 'redux-saga/effects';
import { FETCH_SETTINGS, SAVE_SETTINGS } from '../actions/settings';
import api from '../apis/settings';
import { setSettings, setError } from '../slices/settings';

function* fetchSettingsSaga(action) {
  try {
    yield effects.put(setError(""))
    const response = yield effects.call(api.fetchSettings, action.payload);
    yield effects.put(setSettings({
      type: action.payload.type,
      settings: response
    }));
  } catch (error) {
    yield effects.put(setError( error.message));
  }
}

function* saveSettingsSaga(action) {
  try {
    yield effects.put(setError(""))
    const response = yield effects.call(api.saveSettings, action.payload);
    // console.log(response)
    // yield put(setSettings(action.payload.type, response));
  } catch (error) {
    console.log(error)
    yield effects.put(setError(error.message));
  }
}

export function* settingsSaga() {
  yield effects.takeLatest(FETCH_SETTINGS, fetchSettingsSaga);
  yield effects.takeLatest(SAVE_SETTINGS, saveSettingsSaga);
}
