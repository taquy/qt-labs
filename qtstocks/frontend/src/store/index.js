import { configureStore } from '@reduxjs/toolkit';
import createSagaMiddleware from 'redux-saga';
import { stocksSaga } from './sagas/stocks';
import { authSaga } from './sagas/auth';
import { settingsSaga } from './sagas/settings';
import { userSaga } from './sagas/user';
import rootReducer from './slices';
import { all } from 'redux-saga/effects';

const sagaMiddleware = createSagaMiddleware();

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(sagaMiddleware)
});

function *rootSaga() {
  yield all([
    stocksSaga(),
    authSaga(),
    settingsSaga(),
    userSaga(),
  ]);
}

sagaMiddleware.run(rootSaga);

export default store;
