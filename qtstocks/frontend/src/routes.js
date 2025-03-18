import { createBrowserRouter } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import Register from './components/Register';
import PrivateRoute from './components/PrivateRoute';
import PublicRoute from './components/PublicRoute';

export const routes = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        path: 'login',
        element: <PublicRoute><Login /></PublicRoute>
      },
      {
        path: 'register',
        element: <PublicRoute><Register /></PublicRoute>
      },
      {
        path: '',
        element: <PrivateRoute><Dashboard /></PrivateRoute>
      }
    ]
  }
]);
