import { createSlice } from '@reduxjs/toolkit';
import {
  CREATE_USER,
  UPDATE_USER,
  DELETE_USER,
  TOGGLE_ACTIVE_SUCCESS,
  TOGGLE_ACTIVE_FAILURE,
  TOGGLE_ADMIN_SUCCESS,
  TOGGLE_ADMIN_FAILURE
} from '../actions/user';

const ErrorActions = {
  'FETCH_USERS': 'fetchUsers',
}

const LoaderActions = {
  'FETCH_USERS': 'fetchUsers',
}

const initialState = {
  users: [],
  users_query: {
    page: 1,
    per_page: 20,
    search: '',
    refresh: false
  },
  error: null,
  loaders: {
    [LoaderActions.FETCH_USERS]: false
  }
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUsersQuery: (state, action) => {
      state.users_query = action.payload;
    },
    getUsersQuery: (state) => {
      return state.users_query;
    },
    setUsers: (state, action) => {
      state.users = action.payload;
      state.error = null;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    setLoader: (state, action) => {
      state.loaders[action.payload.action] = action.payload.value;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(CREATE_USER, (state, action) => {
        if (action.payload) {
          state.users = [...state.users, action.payload];
        }
        state.error = null;
      })
      .addCase(UPDATE_USER, (state, action) => {
        if (action.payload && action.payload.id) {
          const index = state.users.findIndex(user => user.id === action.payload.id);
          if (index !== -1) {
            state.users[index] = action.payload;
          }
        }
        state.error = null;
      })
      .addCase(DELETE_USER, (state, action) => {
        if (action.payload) {
          state.users = state.users.filter(user => user.id !== action.payload);
        }
        state.error = null;
      })
      .addCase(TOGGLE_ACTIVE_SUCCESS, (state, action) => {
        if (action.payload && action.payload.id) {
          const index = state.users.findIndex(user => user.id === action.payload.id);
          if (index !== -1) {
            state.users[index].is_active = !state.users[index].is_active;
          }
        }
        state.error = null;
      })
      .addCase(TOGGLE_ACTIVE_FAILURE, (state, action) => {
        state.error = action.payload.error;
      })
      .addCase(TOGGLE_ADMIN_SUCCESS, (state, action) => {
        if (action.payload && action.payload.id) {
          const index = state.users.findIndex(user => user.id === action.payload.id);
          if (index !== -1) {
            state.users[index].is_admin = !state.users[index].is_admin;
          }
        }
        state.error = null;
      })
      .addCase(TOGGLE_ADMIN_FAILURE, (state, action) => {
        state.error = action.payload.error;
      });
  }
});

export const { 
  setUsers, 
  setError, 
  setUsersQuery, 
  getUsersQuery,
  setLoader,
} = userSlice.actions;
export default userSlice.reducer;

export { ErrorActions, LoaderActions };