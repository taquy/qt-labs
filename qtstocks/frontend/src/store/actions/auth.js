
export const LOGOUT = 'auth/logout';
export const LOGIN = 'auth/login';
export const GOOGLE_LOGIN = 'auth/googleLogin';
export const CHECK_IS_LOGGED_IN = 'auth/checkIsLoggedIn';
export const GET_USER_INFO = 'auth/getUserInfo';
export const RESET_STATE = 'auth/resetState';
export const REGISTER = 'auth/register';

export const login = (email, password) => ({ type: LOGIN, payload: { email, password } });
export const logout = () => ({ type: LOGOUT });
export const googleLogin = (token) => ({ type: GOOGLE_LOGIN, payload: { token } });
export const checkIsLoggedIn = () => ({ type: CHECK_IS_LOGGED_IN });
export const getUserInfo = () => ({ type: GET_USER_INFO });
export const resetState = () => ({ type: RESET_STATE });
export const register = (payload) => ({ type: REGISTER, payload });
