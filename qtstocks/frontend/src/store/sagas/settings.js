import * as effects from 'redux-saga/effects';
import { FETCH_SETTINGS, SAVE_SETTINGS } from '../actions/settings';
import api from '../apis/settings';
import { setSettings, setError } from '../slices/settings';

function* fetchSettingsSaga({ setting_key }) {
  try {
    yield effects.put(setError(""))
    const setting_value = yield effects.call(api.fetchSettings, setting_key);
    yield effects.put(setSettings({
      setting_key,
      setting_value
    }));
  } catch (error) {
    yield effects.put(setError( error.message));
  }
}

function* saveSettingsSaga({ setting_key, setting_value }) {
  try {
    yield effects.put(setError(""))
    yield effects.call(api.saveSettings, { setting_key, setting_value });
  } catch (error) {
    yield effects.put(setError(error.message));
  }
}

export function* settingsSaga() {
  yield effects.takeEvery(FETCH_SETTINGS, fetchSettingsSaga);
  yield effects.takeEvery(SAVE_SETTINGS, saveSettingsSaga);
}
