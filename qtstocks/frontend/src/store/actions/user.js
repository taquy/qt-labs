export const FETCH_USERS = 'FETCH_USERS';
export const CREATE_USER = 'CREATE_USER';
export const UPDATE_USER = 'UPDATE_USER';
export const DELETE_USER = 'DELETE_USER';
export const TOGGLE_ACTIVE_REQUEST = 'TOGGLE_ACTIVE_REQUEST';
export const TOGGLE_ACTIVE_SUCCESS = 'TOGGLE_ACTIVE_SUCCESS';
export const TOGGLE_ACTIVE_FAILURE = 'TOGGLE_ACTIVE_FAILURE';
export const TOGGLE_ADMIN_REQUEST = 'TOGGLE_ADMIN_REQUEST';
export const TOGGLE_ADMIN_SUCCESS = 'TOGGLE_ADMIN_SUCCESS';
export const TOGGLE_ADMIN_FAILURE = 'TOGGLE_ADMIN_FAILURE';

export const fetchUsers = (page = 1, limit = 20) => ({
  type: FETCH_USERS,
  page,
  limit
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

export const toggleActiveRequest = (userId) => ({
  type: TOGGLE_ACTIVE_REQUEST,
  payload: { id: userId }
});

export const toggleActiveSuccess = (userId) => ({
  type: TOGGLE_ACTIVE_SUCCESS,
  payload: { id: userId }
});

export const toggleActiveFailure = (error) => ({
  type: TOGGLE_ACTIVE_FAILURE,
  payload: { error }
});

export const toggleAdminRequest = (userId) => ({
  type: TOGGLE_ADMIN_REQUEST,
  payload: { id: userId }
});

export const toggleAdminSuccess = (userId) => ({
  type: TOGGLE_ADMIN_SUCCESS,
  payload: { id: userId }
});

export const toggleAdminFailure = (error) => ({
  type: TOGGLE_ADMIN_FAILURE,
  payload: { error }
});
