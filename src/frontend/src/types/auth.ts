export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface UserRole {
  id: number;
  user: number;
  role: 'pending' | 'admin' | 'owner' | 'logistics' | 'warehouse' | 'stocktake_manager' | 'warehouse_boy' | 'sales' | 'accountant';
  created_at: string;
  created_by?: number;
}

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_active: boolean;
  date_joined: string;
  role?: UserRole;
}

export interface AuthState {
  user: AuthUser | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface RolePermissions {
  can_manage_users: boolean;
  can_manage_access_control: boolean;
  can_create_purchase_order: boolean;
  can_edit_purchase_order: boolean;
  can_view_purchase_order: boolean;
  can_receive_purchase_order: boolean;
  can_view_purchase_order_amounts: boolean;
  can_create_stock: boolean;
  can_edit_stock: boolean;
  can_view_stock: boolean;
  can_transfer_stock: boolean;
  can_commit_stock: boolean;
  can_fulfill_commitment: boolean;
  can_issue_stock: boolean;
  can_receive_stock: boolean;
  can_view_warehouse_receiving: boolean;
  can_manage_payments?: boolean;
  can_create_invoices?: boolean;
  can_view_financial_reports?: boolean;
}