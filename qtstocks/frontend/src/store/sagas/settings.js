import * as effects from 'redux-saga/effects';
import { setError, setSettings, setLoading, clearError } from '../slices/settings';
import { handleApiError } from '../utils';

import { FETCH_SETTINGS, SAVE_SETTINGS } from '../actions/settings';

import api from '../apis/settings';

function* fetchSettingsSaga() {
  try {
    yield effects.put(setLoading(true));
    yield effects.put(clearError());
    const settings = yield effects.call(api.fetchSettings);
    yield effects.put(setSettings(settings));
  } catch (error) {
    yield effects.put(setError('Failed to fetch settings'));
    yield effects.call(handleApiError, error, 'fetchSettingsSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

function* saveSettingsSaga(action) {
  try {
    yield effects.put(setLoading(true));
    yield effects.put(clearError());
    const { stocks, metric } = action.payload;
    yield effects.call(api.saveSettings, stocks, metric);
    yield effects.call(fetchSettingsSaga);
  } catch (error) {
    yield effects.put(setError('Failed to save settings'));
    yield effects.call(handleApiError, error, 'saveSettingsSaga');
  } finally {
    yield effects.put(setLoading(false));
  }
}

export function* settingsSaga() {
  yield effects.takeLatest(FETCH_SETTINGS, fetchSettingsSaga);
  yield effects.takeLatest(SAVE_SETTINGS, saveSettingsSaga);
}
