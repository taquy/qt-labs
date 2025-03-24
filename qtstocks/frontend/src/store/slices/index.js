import { combineReducers } from "redux";
import userReducer from "./user";
import settingsReducer from "./settings";
import stocksReducer from "./stocks";
import authReducer from "./auth";
import { RESET_STATE } from "../actions/auth";
const appReducer = combineReducers({
  user: userReducer,
  settings: settingsReducer,
  stocks: stocksReducer,
  auth: authReducer,
});

// Root reducer that resets state when RESET_STATE action is dispatched
const rootReducer = (state, action) => {
  if (action.type === RESET_STATE) {
    return appReducer(undefined, action); // Reset all reducers to initial state
  }
  return appReducer(state, action);
};

export default rootReducer;
