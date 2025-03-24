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
  'CREATE_USER': 'createUser',
  'UPDATE_USER': 'updateUser',
  'DELETE_USER': 'deleteUser',
  'TOGGLE_ACTIVE': 'toggleActive',
  'TOGGLE_ADMIN': 'toggleAdmin',
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
      state.error[action.payload.action] = action.payload.message;
    },
    setLoader: (state, action) => {
      state.loaders[action.payload.action] = action.payload.value;
    },
    setCreateUser: (state, action) => {
      state.users = [...state.users, action.payload];
      state.error[ErrorActions.CREATE_USER] = null;
    },
    setUpdateUser: (state, action) => {
      const index = state.users.findIndex(user => user.id === action.payload.id);
      if (index !== -1) {
        state.users[index] = action.payload;
      }
      state.error[ErrorActions.UPDATE_USER] = null;
    },
    setDeleteUser: (state, action) => {
      state.users = state.users.filter(user => user.id !== action.payload);
      state.error[ErrorActions.DELETE_USER] = null;
    },
    setToggleActive: (state, action) => {
      const index = state.users.findIndex(user => user.id === action.payload.id);
      if (index !== -1) {
        state.users[index].is_active = !state.users[index].is_active;
      }
      state.error[ErrorActions.TOGGLE_ACTIVE] = null;
    },
    setToggleAdmin: (state, action) => {
      const index = state.users.findIndex(user => user.id === action.payload.id);
      if (index !== -1) {
        state.users[index].is_admin = !state.users[index].is_admin;
      }
      state.error[ErrorActions.TOGGLE_ADMIN] = null;
    },
  }
});

export const { 
  setUsers, 
  setError, 
  setUsersQuery, 
  getUsersQuery,
  setLoader,
  setCreateUser,
  setUpdateUser,
  setDeleteUser,
  setToggleActive,
  setToggleAdmin
} = userSlice.actions;
export default userSlice.reducer;

export { ErrorActions, LoaderActions };