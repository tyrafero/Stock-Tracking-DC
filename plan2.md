# Plan 2: Complete UI Migration from Django to React

## Overview
This plan outlines the complete migration of all Django UI components to modern React interfaces, including Reservations, Transfers, Stocktake, and Purchase Orders management with proper access control.

## Phase 1: Core Infrastructure Setup

### 1.1 Navigation & Routing Enhancement
- [ ] Add new routes for all modules in `router.tsx`
- [ ] Update sidebar navigation with new menu items
- [ ] Implement breadcrumb navigation for better UX
- [ ] Add role-based menu item visibility

### 1.2 Type Definitions Extension
- [ ] Add/verify StockTransfer types
- [ ] Add Stocktake types
- [ ] Add Purchase Order types
- [ ] Add User management types
- [ ] Add comprehensive permission types

### 1.3 API Client Extensions
- [ ] Verify/add Stocktake API methods
- [ ] Verify/add Purchase Order API methods
- [ ] Add User management API methods
- [ ] Add comprehensive error handling

## Phase 2: Reservations Management System

### 2.1 Reservations List Page (`/reservations`)
- [ ] Create `ReservationsList.tsx` component
- [ ] Table with columns: ID, Stock Item, Customer, Type, Status, Expires, Actions
- [ ] Filtering: Status, Type, Customer, Date range
- [ ] Sorting: Date, Customer name, Status
- [ ] Pagination with configurable page size
- [ ] Bulk actions: Cancel multiple, Fulfill multiple

### 2.2 Reservation Detail/Edit Modal
- [ ] View reservation details
- [ ] Edit reservation (if pending)
- [ ] Cancel reservation with reason
- [ ] Fulfill reservation
- [ ] Extend expiration date
- [ ] Print reservation slip

### 2.3 Create Reservation Flow
- [ ] Stock selection (searchable dropdown)
- [ ] Customer information form
- [ ] Reservation type selection
- [ ] Duration/expiration setting
- [ ] Notes and reason
- [ ] Email notification options

## Phase 3: Transfers Management System

### 3.1 Transfers List Page (`/transfers`)
- [ ] Create `TransfersList.tsx` component
- [ ] Table: ID, Stock Item, From Location, To Location, Quantity, Status, Requested By, Actions
- [ ] Status filtering: Pending, Approved, In Transit, Completed, Cancelled
- [ ] Location filtering: Source/Destination stores
- [ ] Date range filtering
- [ ] User filtering (requested by, approved by)

### 3.2 Transfer Operations
- [ ] Create new transfer request
- [ ] Approve/reject transfer (if authorized)
- [ ] Mark as dispatched/in transit
- [ ] Mark as received/completed
- [ ] Cancel transfer with reason
- [ ] Print transfer documentation

### 3.3 Transfer Detail View
- [ ] Complete transfer history timeline
- [ ] Attached documents/photos
- [ ] Communication log
- [ ] Location change tracking

## Phase 4: Stocktake Management System

### 4.1 Stocktake List Page (`/stocktake`)
- [ ] Create `StocktakeList.tsx` component
- [ ] Table: ID, Title, Location, Status, Created By, Start Date, End Date, Actions
- [ ] Status filtering: Draft, In Progress, Under Review, Completed
- [ ] Location filtering
- [ ] Date range filtering
- [ ] User filtering

### 4.2 Stocktake Creation/Management
- [ ] Create new stocktake session
- [ ] Select location/categories to include
- [ ] Assign users to stocktake
- [ ] Set deadlines and priorities
- [ ] Generate stocktake sheets (PDF)
- [ ] Import/export functionality

### 4.3 Stocktake Execution Interface
- [ ] Mobile-friendly data entry
- [ ] Barcode scanning integration
- [ ] Stock item lookup with images
- [ ] Quantity input with validation
- [ ] Notes and condition reporting
- [ ] Photo capture for discrepancies

### 4.4 Stocktake Review & Reports
- [ ] Variance reports (expected vs actual)
- [ ] Discrepancy investigation
- [ ] Approval workflow
- [ ] Stock adjustment generation
- [ ] Historical comparison

## Phase 5: Purchase Orders Management System

### 5.1 Purchase Orders List (`/purchase-orders`)
- [ ] Create `PurchaseOrdersList.tsx` component
- [ ] Table: PO Number, Supplier, Total Amount, Status, Created By, Order Date, Expected Date
- [ ] Status filtering: Draft, Sent, Acknowledged, Partial, Complete, Cancelled
- [ ] Supplier filtering
- [ ] Date range filtering
- [ ] Amount range filtering

### 5.2 Purchase Order Creation/Editing
- [ ] PO header information (supplier, dates, terms)
- [ ] Line items management (add/remove/edit)
- [ ] Stock item selection with pricing
- [ ] Quantity and unit price management
- [ ] Tax and discount calculations
- [ ] Approval workflow integration
- [ ] Document generation (PDF)

### 5.3 Purchase Order Operations
- [ ] Send PO to supplier (email integration)
- [ ] Receive partial/full shipments
- [ ] Invoice matching
- [ ] Payment tracking
- [ ] Return/exchange handling

### 5.4 Purchase Order Receiving Interface
- [ ] Receiving workflow UI
- [ ] Quality inspection checklist
- [ ] Condition reporting
- [ ] Batch/serial number tracking
- [ ] Damage reporting with photos
- [ ] Stock location assignment

## Phase 6: User Management & Access Control

### 6.1 User Management Interface (`/admin/users`)
- [ ] User list with role assignments
- [ ] User creation/editing forms
- [ ] Role management interface
- [ ] Permission matrix view
- [ ] User activity logs
- [ ] Password reset functionality

### 6.2 Enhanced Permission System
- [ ] Role-based component rendering
- [ ] Function-level access control
- [ ] Data-level security (view own vs all)
- [ ] Audit trail for sensitive operations
- [ ] Session management

### 6.3 Organization Settings
- [ ] Store/warehouse management
- [ ] Category management
- [ ] System configuration
- [ ] Notification preferences
- [ ] Integration settings

## Phase 7: Advanced Features & UX Improvements

### 7.1 Dashboard Enhancements
- [ ] Module-specific widgets
- [ ] Quick action shortcuts
- [ ] Recent activity feed
- [ ] Alerts and notifications
- [ ] Performance metrics

### 7.2 Search & Navigation
- [ ] Global search functionality
- [ ] Recent items tracking
- [ ] Bookmarks/favorites
- [ ] Keyboard shortcuts
- [ ] Mobile navigation optimization

### 7.3 Reporting & Analytics
- [ ] Standard reports for each module
- [ ] Custom report builder
- [ ] Export functionality (PDF, Excel)
- [ ] Scheduled reports
- [ ] Data visualization charts

### 7.4 Integration Features
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Barcode generation/scanning
- [ ] Document management
- [ ] API key management for third-party integrations

## Phase 8: Quality Assurance & Testing

### 8.1 Component Testing
- [ ] Unit tests for all new components
- [ ] Integration tests for workflows
- [ ] Permission testing
- [ ] Mobile responsiveness testing
- [ ] Performance optimization

### 8.2 User Acceptance Testing
- [ ] Role-based testing scenarios
- [ ] Workflow validation
- [ ] Data integrity verification
- [ ] Security testing
- [ ] Browser compatibility

## Implementation Timeline

### Week 1-2: Infrastructure & Reservations
- Complete Phase 1 (Infrastructure)
- Complete Phase 2 (Reservations)

### Week 3-4: Transfers & Stocktake
- Complete Phase 3 (Transfers)
- Complete Phase 4 (Stocktake)

### Week 5-6: Purchase Orders
- Complete Phase 5 (Purchase Orders)

### Week 7: Access Control & Advanced Features
- Complete Phase 6 (User Management)
- Complete Phase 7 (Advanced Features)

### Week 8: Testing & Deployment
- Complete Phase 8 (QA & Testing)
- Production deployment

## Technical Architecture

### Component Structure
```
/src/pages/
  /reservations/
    ReservationsList.tsx
    ReservationDetail.tsx
    CreateReservation.tsx
  /transfers/
    TransfersList.tsx
    TransferDetail.tsx
    CreateTransfer.tsx
  /stocktake/
    StocktakeList.tsx
    StocktakeDetail.tsx
    CreateStocktake.tsx
    StocktakeExecution.tsx
  /purchase-orders/
    PurchaseOrdersList.tsx
    PurchaseOrderDetail.tsx
    CreatePurchaseOrder.tsx
    ReceivingInterface.tsx
  /admin/
    UserManagement.tsx
    RoleManagement.tsx
    SystemSettings.tsx

/src/components/
  /reservations/
  /transfers/
  /stocktake/
  /purchase-orders/
  /common/
    PermissionGuard.tsx
    SearchableSelect.tsx
    DataTable.tsx
    StatusBadge.tsx
```

### Permission System
```typescript
// Enhanced permission mapping
const PERMISSIONS = {
  reservations: {
    view: 'reservations.view_stockreservation',
    create: 'reservations.add_stockreservation',
    edit: 'reservations.change_stockreservation',
    delete: 'reservations.delete_stockreservation',
    fulfill: 'reservations.fulfill_stockreservation'
  },
  transfers: {
    view: 'transfers.view_stocktransfer',
    create: 'transfers.add_stocktransfer',
    approve: 'transfers.approve_stocktransfer',
    complete: 'transfers.complete_stocktransfer'
  },
  stocktake: {
    view: 'stocktake.view_stocktake',
    create: 'stocktake.add_stocktake',
    execute: 'stocktake.execute_stocktake',
    review: 'stocktake.review_stocktake'
  },
  purchase_orders: {
    view: 'po.view_purchaseorder',
    create: 'po.add_purchaseorder',
    approve: 'po.approve_purchaseorder',
    receive: 'po.receive_purchaseorder'
  }
};
```

## Success Metrics
- [ ] 100% feature parity with Django UI
- [ ] All user roles can perform their required functions
- [ ] Response time < 2s for all operations
- [ ] Mobile compatibility for field operations
- [ ] Zero data loss during operations
- [ ] Comprehensive audit trail