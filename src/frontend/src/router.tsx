import { createBrowserRouter, Navigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import ProtectedRoute from '@/components/ProtectedRoute';
import Login from '@/pages/auth/Login';
import Dashboard from '@/pages/Dashboard';
import StockList from '@/pages/stock/StockList';
import StockDetail from '@/pages/stock/StockDetail';
import CreateStock from '@/pages/stock/CreateStock';
import EditStock from '@/pages/stock/EditStock';
import StockHistory from '@/pages/stock/StockHistory';
import CommittedStockList from '@/pages/stock/CommittedStockList';
import ReservationsList from '@/pages/stock/ReservationsList';
import TransfersList from '@/pages/stock/TransfersList';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'stock',
        children: [
          {
            index: true,
            element: <StockList />,
          },
          {
            path: 'create',
            element: <CreateStock />,
          },
          {
            path: ':id',
            element: <StockDetail />,
          },
          {
            path: ':id/edit',
            element: <EditStock />,
          },
          {
            path: 'history',
            element: <StockHistory />,
          },
          {
            path: 'committed',
            element: <CommittedStockList />,
          },
          {
            path: 'reservations',
            element: <ReservationsList />,
          },
          {
            path: 'transfers',
            element: <TransfersList />,
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
  },
]);

export default router;