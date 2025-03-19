import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { checkIsLoggedIn } from '../store/sagas/stockGraphSaga';
import PageLoader from './PageLoader';

const PublicRoute = ({ children }) => {
  const dispatch = useDispatch();
  const location = useLocation();
  const { isLoggedIn, checkingLogin } = useSelector(state => state.stockGraph);

  useEffect(() => {
    dispatch(checkIsLoggedIn());
  }, [dispatch]);

  if (checkingLogin) {
    return <PageLoader/>
  }

  if (isLoggedIn) {
    // Redirect to home page but save the attempted url
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  return children;
};

export default PublicRoute;