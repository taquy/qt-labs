import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { checkIsLoggedIn } from '../../store/actions/auth';
import PageLoader from './PageLoader';

const PrivateRoute = ({ children }) => {
  const dispatch = useDispatch();
  const location = useLocation();
  const { isLoggedIn, checkingLogin, userInfo } = useSelector(state => state.auth);

  useEffect(() => {
    dispatch(checkIsLoggedIn());
  }, [dispatch]);

  if (checkingLogin) {
    return <PageLoader />;
  }

  if (!isLoggedIn) {
    // Save the attempted URL and redirect to login
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  const adminRoutes = ['/users', '/settings'];
  if (adminRoutes.includes(location.pathname) && !userInfo?.is_admin) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default PrivateRoute; 