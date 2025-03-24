export const FETCH_USERS = 'FETCH_USERS';
export const CREATE_USER = 'CREATE_USER';
export const UPDATE_USER = 'UPDATE_USER';
export const DELETE_USER = 'DELETE_USER';
export const TOGGLE_ACTIVE = 'TOGGLE_ACTIVE';
export const TOGGLE_ADMIN = 'TOGGLE_ADMIN';
export const SET_ERROR = 'SET_ERROR';
export const SET_USERS_QUERY = 'SET_USERS_QUERY';

export const setUsersQuery = (query) => ({
  type: SET_USERS_QUERY,
  payload: query
});

export const fetchUsers = () => ({
  type: FETCH_USERS
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

export const setError = (action, message) => ({
  type: SET_ERROR,
  payload: { action, message }
});
