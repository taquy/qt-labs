import { configureStore } from '@reduxjs/toolkit';
import createSagaMiddleware from 'redux-saga';
import stockGraphReducer from './slices/stockGraphSlice';
import { stockGraphSaga } from './sagas/stockGraphSaga';

const sagaMiddleware = createSagaMiddleware();

export const store = configureStore({
  reducer: {
    stockGraph: stockGraphReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(sagaMiddleware)
});

sagaMiddleware.run(stockGraphSaga);

export default store; 