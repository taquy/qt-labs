import Login from './components/Login';
import Dashboard from './components/Dashboard';
import StockAnalysis from './components/StockAnalysis';
import UserManagement from './components/UserManagement';
import Layout from './components/Layout';
import PublicRoute from './components/PublicRoute';
import PrivateRoute from './components/PrivateRoute';
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
        element: <StockAnalysis />
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
