import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { checkIsLoggedIn } from '../store/actions/auth';
import PageLoader from './PageLoader';
const PrivateRoute = ({ children }) => {
  const dispatch = useDispatch();
  const location = useLocation();
  const { isLoggedIn, checkingLogin, userInfo } = useSelector(state => state.auth);

  useEffect(() => {
    dispatch(checkIsLoggedIn());
  }, [dispatch]);

  useEffect(() => {
    console.log(userInfo);
  }, [userInfo]);

  if (checkingLogin) {
    return (
     <PageLoader/>
    );
  }

  if (!isLoggedIn) {
    // Redirect to login page but save the attempted url
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  // Check if user is admin for /users path
  if (location.pathname === '/users' && !userInfo?.is_admin) {
    return <Navigate to="/" replace />;
  }
  return children;
};

export default PrivateRoute; 