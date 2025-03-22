export const FETCH_USERS = 'user/fetchUsers';
export const CREATE_USER = 'user/createUser';
export const UPDATE_USER = 'user/updateUser';
export const DELETE_USER = 'user/deleteUser';
export const TOGGLE_ACTIVE = 'user/toggleActive';

export const fetchUsers = () => ({ type: FETCH_USERS });
export const createUser = (user) => ({ type: CREATE_USER, user });
export const updateUser = (userId, user) => ({ type: UPDATE_USER, userId, user });
export const deleteUser = (userId) => ({ type: DELETE_USER, userId });
export const toggleActive = (userId) => ({ type: TOGGLE_ACTIVE, userId });
