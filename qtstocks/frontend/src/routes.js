import Login from './components/auth/Login';
import Dashboard from './components/Dashboard';
import StockManagement from './components/StockManagement';
import UserManagement from './components/UserManagement';
import Layout from './components/Layout';
import PublicRoute from './components/auth/PublicRoute';
import PrivateRoute from './components/auth/PrivateRoute';
import Register from './components/auth/Register';
import Settings from './components/Settings';

const routes = [
  {
    path: '/login',
    element: (
      <PublicRoute>
        <Login />
      </PublicRoute>
    )
  },
  {
    path: '/register',
    element: (
      <PublicRoute>
        <Register />
      </PublicRoute>
    )
  },
  {
    path: '/',
    element: (
      <PrivateRoute>
        <Layout />
      </PrivateRoute>
    ),
    children: [
      {
        path: '',
        element: <Dashboard />
      },
      {
        path: 'stocks',
        element: <StockManagement />
      },
      {
        path: 'users',
        element: <UserManagement />
      },
      {
        path: 'settings',
        element: <Settings />
      }
    ]
  }
];

export default routes;
