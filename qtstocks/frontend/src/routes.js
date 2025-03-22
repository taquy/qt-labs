import { createBrowserRouter } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import Register from './components/Register';
import PrivateRoute from './components/PrivateRoute';
import PublicRoute from './components/PublicRoute';
import StockAnalysis from './components/StockAnalysis';
import UserManagement from './components/UserManagement';
import Settings from './components/Settings';

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
      },
      {
        path: 'stocks',
        element: <PrivateRoute><StockAnalysis /></PrivateRoute>
      },
      {
        path: 'users',
        element: <PrivateRoute><UserManagement /></PrivateRoute>
      },
      {
        path: 'settings',
        element: <PrivateRoute><Settings /></PrivateRoute>
      }
    ]
  }
]);
