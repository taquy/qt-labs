import { createSlice } from '@reduxjs/toolkit';

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
  'CREATE_USER': 'createUser',
  'UPDATE_USER': 'updateUser',
  'DELETE_USER': 'deleteUser',
  'TOGGLE_ACTIVE': 'toggleActive',
  'TOGGLE_ADMIN': 'toggleAdmin',
}

const initialState = {
  users: {
    items: [],
    current_page: 0,
    has_next: true,
  },
  users_query: {
    page: 1,
    per_page: 20,
    search: '',
    refresh: false,
    sort_by: 'created_at',
    sort_direction: 'desc'
  },
  error: {
    [ErrorActions.FETCH_USERS]: "",
    [ErrorActions.CREATE_USER]: "",
    [ErrorActions.UPDATE_USER]: "",
    [ErrorActions.DELETE_USER]: "",
    [ErrorActions.TOGGLE_ACTIVE]: "",
    [ErrorActions.TOGGLE_ADMIN]: "",
  },
  loaders: {
    [LoaderActions.FETCH_USERS]: false
  }
};

const filterUsers = (users, query) => {
  if (!users) return [];
  
  // Remove duplicates
  const uniqueUsers = [...new Map(users.map(item => [item.id, item])).values()];
  
  // Apply search filter if search term exists
  if (query.search && query.search.trim()) {
    const searchTerm = query.search.toLowerCase().trim();
    return uniqueUsers.filter(user => 
      user.name?.toLowerCase().includes(searchTerm) ||
      user.email?.toLowerCase().includes(searchTerm)
    );
  }
  
  return uniqueUsers;
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUsersQuery: (state, action) => {
      if (!action.payload.sort_by) {
        action.payload.sort_by = 'created_at';
      }
      if (!action.payload.sort_direction) {
        action.payload.sort_direction = 'desc';
      }
      state.users_query = action.payload;
      // Apply filter to current items when query changes
      state.users.items = filterUsers(state.users.items, action.payload);
    },
    getUsersQuery: (state) => {
      return state.users_query;
    },
    setUsers: (state, action) => {
      if (action.payload) {
        const { items, has_next, current_page, refresh } = action.payload;
        const newItems = refresh ? items : [...state.users.items, ...items];
        state.users.items = filterUsers(newItems, state.users_query);
        state.users.has_next = refresh ? true : has_next;
        state.users.current_page = current_page;
      } else {
        state.users = {
          items: [],
          has_next: true,
        };
      }
      state.error[ErrorActions.FETCH_USERS] = "";
    },
    setError: (state, action) => {
      state.error[action.payload.action] = action.payload.message;
    },
    setLoader: (state, action) => {
      const { type, value } = action.payload;
      state.loaders[type] = value;
    },
    setCreateUser: (state, action) => {
      state.users = [...state.users, action.payload];
      state.error[ErrorActions.CREATE_USER] = "";
    },
    setUpdateUser: (state, action) => {
      const index = state.users.items.findIndex(user => user.id === action.payload.id);
      if (index !== -1) state.users.items[index] = action.payload;
      state.error[ErrorActions.UPDATE_USER] = "";
    },
    setToggleActive: (state, action) => {
      const index = state.users.items.findIndex(user => user.id === action.payload.id);
      if (index === -1) return;
      state.users.items[index] = action.payload;
      state.error[ErrorActions.TOGGLE_ACTIVE] = "";
    },
    setToggleAdmin: (state, action) => {
      const index = state.users.items.findIndex(user => user.id === action.payload.id);
      if (index === -1) return;
      state.users.items[index] = action.payload;
      state.error[ErrorActions.TOGGLE_ADMIN] = "";
    },
  },
});

export const { 
  setUsers, 
  setError, 
  setUsersQuery, 
  getUsersQuery,
  setLoader,
  setCreateUser,
  setUpdateUser,
  setToggleActive,
  setToggleAdmin
} = userSlice.actions;
export default userSlice.reducer;

export { ErrorActions, LoaderActions };