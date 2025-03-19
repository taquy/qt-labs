import axios from 'axios';
import { API_SETTINGS_ENDPOINTS } from '../../config';
import { getRequestConfig } from '../utils';
import * as effects from 'redux-saga/effects';
import { setError, setSettings, setLoading, clearError } from '../slices/settingsSlice';
import { handleApiError } from '../utils';

export const FETCH_SETTINGS = 'settings/fetchSettings';
export const SAVE_SETTINGS = 'settings/saveSettings';

export const fetchSettings = () => ({ type: FETCH_SETTINGS });
export const saveSettings = (stocks, metric) => ({ type: SAVE_SETTINGS, payload: { stocks, metric } });

const api = {
  fetchSettings: async () => {
    const response = await axios.get(API_SETTINGS_ENDPOINTS.settings, getRequestConfig());
    return response.data.settings;
  },
  saveSettings: async (stocks, metric) => {
    const payload = {
      value: {
        selectedSymbols: stocks.map(stock => stock.symbol),
        selectedMetric: metric
      }
    };
    await axios.put(
      API_SETTINGS_ENDPOINTS.updateSetting('stockGraph'), payload, getRequestConfig()
    );
  },
};

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
