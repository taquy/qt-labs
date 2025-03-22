export const FETCH_USERS = 'FETCH_USERS';
export const FETCH_USERS_SUCCESS = 'FETCH_USERS_SUCCESS';
export const FETCH_USERS_FAILURE = 'FETCH_USERS_FAILURE';
export const CREATE_USER = 'CREATE_USER';
export const UPDATE_USER = 'UPDATE_USER';
export const DELETE_USER = 'DELETE_USER';
export const TOGGLE_ACTIVE = 'TOGGLE_ACTIVE';
export const TOGGLE_ADMIN = 'TOGGLE_ADMIN';

export const fetchUsers = (page = 1, limit = 20) => ({
  type: FETCH_USERS,
  page,
  limit
});

export const fetchUsersSuccess = (users, hasMore, page, total, pages) => ({
  type: FETCH_USERS_SUCCESS,
  payload: {
    users,
    hasMore,
    page,
    total,
    pages
  }
});

export const fetchUsersFailure = (error) => ({
  type: FETCH_USERS_FAILURE,
  payload: { error }
});

export const createUser = (userData) => ({
  type: CREATE_USER,
  payload: userData
});

export const updateUser = (userId, userData) => ({
  type: UPDATE_USER,
  payload: { id: userId, ...userData }
});

export const deleteUser = (userId) => ({
  type: DELETE_USER,
  payload: userId
});

export const toggleActive = (userId) => ({
  type: TOGGLE_ACTIVE,
  payload: { id: userId }
});

export const toggleAdmin = (userId) => ({
  type: TOGGLE_ADMIN,
  payload: { id: userId }
});
