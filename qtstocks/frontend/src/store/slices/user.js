import { createSlice } from '@reduxjs/toolkit';
import {
  FETCH_USERS_SUCCESS,
  FETCH_USERS_FAILURE,
  CREATE_USER,
  UPDATE_USER,
  DELETE_USER,
  TOGGLE_ACTIVE,
  TOGGLE_ADMIN
} from '../actions/user';

const initialState = {
  users: [],
  error: null,
  hasMore: true,
  total: 0,
  pages: 0,
  currentPage: 1
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUsers: (state, action) => {
      state.users = action.payload;
      state.error = null;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    appendUsers: (state, action) => {
      state.users = [...state.users, ...action.payload];
      state.error = null;
    },
    setHasMore: (state, action) => {
      state.hasMore = action.payload;
    },
    setPagination: (state, action) => {
      state.total = action.payload.total;
      state.pages = action.payload.pages;
      state.currentPage = action.payload.currentPage;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(FETCH_USERS_SUCCESS, (state, action) => {
        if (action.payload.page === 1) {
          state.users = action.payload.users;
        } else {
          state.users = [...state.users, ...action.payload.users];
        }
        state.hasMore = action.payload.hasMore;
        state.total = action.payload.total;
        state.pages = action.payload.pages;
        state.currentPage = action.payload.page;
        state.error = null;
      })
      .addCase(FETCH_USERS_FAILURE, (state, action) => {
        state.error = action.payload.error;
      })
      .addCase(CREATE_USER, (state, action) => {
        state.users = [...state.users, action.payload];
        state.error = null;
      })
      .addCase(UPDATE_USER, (state, action) => {
        const index = state.users.findIndex(user => user.id === action.payload.id);
        if (index !== -1) {
          state.users[index] = action.payload;
        }
        state.error = null;
      })
      .addCase(DELETE_USER, (state, action) => {
        state.users = state.users.filter(user => user.id !== action.payload);
        state.error = null;
      })
      .addCase(TOGGLE_ACTIVE, (state, action) => {
        const user = state.users.find(user => user.id === action.payload.id);
        if (user) {
          user.is_active = !user.is_active;
        }
        state.error = null;
      })
      .addCase(TOGGLE_ADMIN, (state, action) => {
        const user = state.users.find(user => user.id === action.payload.id);
        if (user) {
          user.is_admin = !user.is_admin;
        }
        state.error = null;
      });
  }
});

export const { setUsers, setError, appendUsers, setHasMore, setPagination } = userSlice.actions;
export default userSlice.reducer;
