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
import ReservationsList from '@/pages/reservations/ReservationsList';
import ReservationDetail from '@/pages/reservations/ReservationDetail';
import CreateReservation from '@/pages/reservations/CreateReservation';
import TransfersList from '@/pages/transfers/TransfersList';
import TransferDetail from '@/pages/transfers/TransferDetail';
import CreateTransfer from '@/pages/transfers/CreateTransfer';
import StocktakeList from '@/pages/stocktake/StocktakeList';
import StocktakeDetail from '@/pages/stocktake/StocktakeDetail';
import CreateStocktake from '@/pages/stocktake/CreateStocktake';
import PurchaseOrdersList from '@/pages/purchase-orders/PurchaseOrdersList';
import PurchaseOrderDetail from '@/pages/purchase-orders/PurchaseOrderDetail';
import CreatePurchaseOrder from '@/pages/purchase-orders/CreatePurchaseOrder';
import ManufacturersList from '@/pages/manufacturers/ManufacturersList';

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
        ],
      },
      {
        path: 'reservations',
        children: [
          {
            index: true,
            element: <ReservationsList />,
          },
          {
            path: 'create',
            element: <CreateReservation />,
          },
          {
            path: ':id',
            element: <ReservationDetail />,
          },
        ],
      },
      {
        path: 'transfers',
        children: [
          {
            index: true,
            element: <TransfersList />,
          },
          {
            path: 'create',
            element: <CreateTransfer />,
          },
          {
            path: ':id',
            element: <TransferDetail />,
          },
        ],
      },
      {
        path: 'stocktake',
        children: [
          {
            index: true,
            element: <StocktakeList />,
          },
          {
            path: 'create',
            element: <CreateStocktake />,
          },
          {
            path: ':id',
            element: <StocktakeDetail />,
          },
        ],
      },
      {
        path: 'purchase-orders',
        children: [
          {
            index: true,
            element: <PurchaseOrdersList />,
          },
          {
            path: 'create',
            element: <CreatePurchaseOrder />,
          },
          {
            path: ':id',
            element: <PurchaseOrderDetail />,
          },
          {
            path: ':id/edit',
            element: <CreatePurchaseOrder />,
          },
        ],
      },
      {
        path: 'manufacturers',
        children: [
          {
            index: true,
            element: <ManufacturersList />,
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