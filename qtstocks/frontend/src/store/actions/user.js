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

export const fetchUsersSuccess = (users, hasMore) => ({
  type: FETCH_USERS_SUCCESS,
  users,
  hasMore
});

export const fetchUsersFailure = (error) => ({
  type: FETCH_USERS_FAILURE,
  error
});

export const createUser = (user) => ({
  type: CREATE_USER,
  user
});

export const updateUser = (userId, userData) => ({
  type: UPDATE_USER,
  userId,
  userData
});

export const deleteUser = (userId) => ({
  type: DELETE_USER,
  userId
});

export const toggleActive = (userId) => ({
  type: TOGGLE_ACTIVE,
  userId
});

export const toggleAdmin = (userId) => ({
  type: TOGGLE_ADMIN,
  userId
});
