import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { checkIsLoggedIn } from '../store/sagas/authSaga';
import PageLoader from './PageLoader';
const PrivateRoute = ({ children }) => {
  const dispatch = useDispatch();
  const location = useLocation();
  const { isLoggedIn, checkingLogin } = useSelector(state => state.auth);

  useEffect(() => {
    dispatch(checkIsLoggedIn());
  }, [dispatch]);

  if (checkingLogin) {
    return (
     <PageLoader/>
    );
  }

  if (!isLoggedIn) {
    // Redirect to login page but save the attempted url
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

export default PrivateRoute; 