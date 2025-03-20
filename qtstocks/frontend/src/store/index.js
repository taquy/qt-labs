import { configureStore } from '@reduxjs/toolkit';
import createSagaMiddleware from 'redux-saga';
import stocksReducer from './slices/stocks';
import { stocksSaga } from './sagas/stocks';
import authReducer from './slices/auth';
import settingsReducer from './slices/settings';
import { all } from 'redux-saga/effects';
import { authSaga } from './sagas/auth';
import { settingsSaga } from './sagas/settings';

const sagaMiddleware = createSagaMiddleware();

export const store = configureStore({
  reducer: {
    stocks: stocksReducer,
    auth: authReducer,
    settings: settingsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(sagaMiddleware)
});


function *rootSaga() {
  yield all([
    stocksSaga(),
    authSaga(),
    settingsSaga(),
  ]);
}

sagaMiddleware.run(rootSaga);

export default store;