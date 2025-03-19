import { configureStore } from '@reduxjs/toolkit';
import createSagaMiddleware from 'redux-saga';
import stockGraphReducer from './slices/stockGraphSlice';
import { stockGraphSaga } from './sagas/stockGraphSaga';
import authReducer from './slices/authSlice';
import settingsReducer from './slices/settingsSlice';
import { all } from 'redux-saga/effects';
import { authSaga } from './sagas/authSaga';
import { settingsSaga } from './sagas/settingsSaga';

const sagaMiddleware = createSagaMiddleware();

export const store = configureStore({
  reducer: {
    stockGraph: stockGraphReducer,
    auth: authReducer,
    settings: settingsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(sagaMiddleware)
});


function *rootSaga() {
  yield all([
    stockGraphSaga(),
    authSaga(),
    settingsSaga(),
  ]);
}

sagaMiddleware.run(rootSaga);

export default store;