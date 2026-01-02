import React from 'react';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import apiClient from '@/api/client';
import { mockApiService } from '@/api/mockService';
import { mockUser } from '@/api/mockData';
import type { AuthState, AuthUser, AuthTokens, LoginCredentials } from '@/types/auth';

const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true';

interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  setUser: (user: AuthUser | null) => void;
  setTokens: (tokens: AuthTokens | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  initialize: () => Promise<void>;
}

interface AuthStore extends AuthState, AuthActions {}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });

        try {
          const tokens = await apiClient.login(credentials.username, credentials.password);

          // Get user profile after login
          const user = await apiClient.get<AuthUser>('/auth/user/profile/');

          set({
            user,
            tokens,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          // Provide more specific error messages
          let errorMessage = 'Login failed';

          if (error.status === 401) {
            errorMessage = 'Invalid username or password';
          } else if (error.status === 403) {
            errorMessage = 'Account is disabled or not activated';
          } else if (error.status >= 500) {
            errorMessage = 'Server error. Please try again later.';
          } else if (error.message) {
            errorMessage = error.message;
          }

          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      logout: () => {
        apiClient.logout();
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          error: null,
        });
      },

      refreshToken: async () => {
        try {
          const tokens = await apiClient.refreshToken();
          set({ tokens, isAuthenticated: true });
        } catch (error) {
          // If refresh fails, logout user
          get().logout();
          throw error;
        }
      },

      setUser: (user: AuthUser | null) => {
        set({ user, isAuthenticated: !!user });
      },

      setTokens: (tokens: AuthTokens | null) => {
        set({ tokens, isAuthenticated: !!tokens });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      setError: (error: string | null) => {
        set({ error });
      },

      clearError: () => {
        set({ error: null });
      },

      initialize: async () => {
        // In demo mode, auto-login with mock user
        if (isDemoMode) {
          set({
            user: mockUser as AuthUser,
            tokens: { access: 'demo-token', refresh: 'demo-refresh' },
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          return;
        }

        const accessToken = apiClient.getAccessToken();
        const refreshToken = apiClient.getRefreshToken();

        if (!accessToken || !refreshToken) {
          set({ isAuthenticated: false, isLoading: false });
          return;
        }

        set({ isLoading: true });

        try {
          // Verify token and get user data
          await apiClient.post('/auth/token/verify/', { token: accessToken });
          const user = await apiClient.get<AuthUser>('/auth/user/profile/');

          set({
            user,
            tokens: { access: accessToken, refresh: refreshToken },
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          // Token is invalid, try to refresh
          try {
            const tokens = await apiClient.refreshToken();
            const user = await apiClient.get<AuthUser>('/auth/user/profile/');

            set({
              user,
              tokens,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } catch (refreshError) {
            // Refresh failed, logout user
            apiClient.clearTokens();
            set({
              user: null,
              tokens: null,
              isAuthenticated: false,
              isLoading: false,
              error: null,
            });
          }
        }
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Selectors for easy access
export const useAuth = () => {
  const store = useAuthStore();
  return {
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    isLoading: store.isLoading,
    error: store.error,
    login: store.login,
    logout: store.logout,
    clearError: store.clearError,
  };
};

export const useUserRole = () => {
  const user = useAuthStore((state) => state.user);
  return user?.role?.role || null;
};

export const useUserPermissions = () => {
  const user = useAuthStore((state) => state.user);

  // This would typically come from the API, but for now we'll return a basic structure
  // In a real implementation, you'd fetch permissions based on the user's role
  const getPermissionsForRole = (role: string) => {
    // This should match the role_permissions property from the Django UserRole model
    const rolePermissions: Record<string, any> = {
      admin: {
        can_manage_users: true,
        can_manage_access_control: true,
        can_create_purchase_order: true,
        can_edit_purchase_order: true,
        can_view_purchase_order: true,
        can_receive_purchase_order: true,
        can_view_purchase_order_amounts: true,
        can_send_purchase_order: true,
        can_approve_purchase_order: true,
        can_cancel_purchase_order: true,
        can_delete_purchase_order: true,
        can_create_stock: true,
        can_edit_stock: true,
        can_view_stock: true,
        can_transfer_stock: true,
        can_commit_stock: true,
        can_fulfill_commitment: true,
        can_issue_stock: true,
        can_receive_stock: true,
        can_view_warehouse_receiving: true,
        can_create_stocktake: true,
        can_start_stocktake: true,
        can_complete_stocktake: true,
        can_cancel_stocktake: true,
        can_delete_stocktake: true,
        can_manage_payments: true,
        can_create_invoices: true,
        can_view_financial_reports: true,
      },
      owner: {
        can_manage_users: true,
        can_manage_access_control: true,
        can_create_purchase_order: true,
        can_edit_purchase_order: true,
        can_view_purchase_order: true,
        can_receive_purchase_order: true,
        can_view_purchase_order_amounts: true,
        can_send_purchase_order: true,
        can_approve_purchase_order: true,
        can_cancel_purchase_order: true,
        can_delete_purchase_order: true,
        can_create_stock: true,
        can_edit_stock: true,
        can_view_stock: true,
        can_transfer_stock: true,
        can_commit_stock: true,
        can_fulfill_commitment: true,
        can_issue_stock: true,
        can_receive_stock: true,
        can_view_warehouse_receiving: true,
        can_create_stocktake: true,
        can_start_stocktake: true,
        can_complete_stocktake: true,
        can_cancel_stocktake: true,
        can_delete_stocktake: true,
        can_manage_payments: true,
        can_create_invoices: true,
        can_view_financial_reports: true,
      },
      logistics: {
        can_manage_users: false,
        can_manage_access_control: false,
        can_create_purchase_order: true,
        can_edit_purchase_order: true,
        can_view_purchase_order: true,
        can_receive_purchase_order: false,
        can_view_purchase_order_amounts: true,
        can_create_stock: false,
        can_edit_stock: false,
        can_view_stock: true,
        can_transfer_stock: true,
        can_commit_stock: true,
        can_fulfill_commitment: false,
        can_issue_stock: true,
        can_receive_stock: true,
        can_view_warehouse_receiving: false,
      },
      warehouse: {
        can_manage_users: false,
        can_manage_access_control: false,
        can_create_purchase_order: false,
        can_edit_purchase_order: false,
        can_view_purchase_order: true,
        can_receive_purchase_order: true,
        can_view_purchase_order_amounts: false,
        can_create_stock: true,
        can_edit_stock: true,
        can_view_stock: true,
        can_transfer_stock: true,
        can_commit_stock: true,
        can_fulfill_commitment: false,
        can_issue_stock: true,
        can_receive_stock: true,
        can_view_warehouse_receiving: true,
      },
      sales: {
        can_manage_users: false,
        can_manage_access_control: false,
        can_create_purchase_order: false,
        can_edit_purchase_order: false,
        can_view_purchase_order: false,
        can_receive_purchase_order: false,
        can_view_purchase_order_amounts: false,
        can_create_stock: false,
        can_edit_stock: false,
        can_view_stock: true,
        can_transfer_stock: true,
        can_commit_stock: true,
        can_fulfill_commitment: true,
        can_issue_stock: false,
        can_receive_stock: false,
        can_view_warehouse_receiving: false,
      },
    };

    return rolePermissions[role] || rolePermissions.sales;
  };

  return user?.role?.role ? getPermissionsForRole(user.role.role) : null;
};

// Permission checking hook - simplified to avoid re-render loops
export const useHasPermission = () => {
  const user = useAuthStore((state) => state.user);

  return React.useMemo(() => {
    return (permission: string) => {
      if (!user?.role?.role) {
        return false;
      }

      // Map Django permission strings to our permission keys
      const permissionMap: Record<string, string> = {
        'stock.add_stock': 'can_create_stock',
        'stock.change_stock': 'can_edit_stock',
        'stock.view_stock': 'can_view_stock',
        'stock.delete_stock': 'can_edit_stock',
        'stock.transfer_stock': 'can_transfer_stock',
        'stock.commit_stock': 'can_commit_stock',
        'stock.issue_stock': 'can_issue_stock',
        'stock.receive_stock': 'can_receive_stock',
        // Stocktake permissions
        'create_stocktake': 'can_create_stocktake',
        'start_stocktake': 'can_start_stocktake',
        'complete_stocktake': 'can_complete_stocktake',
        'cancel_stocktake': 'can_cancel_stocktake',
        'delete_stocktake': 'can_delete_stocktake',
        // Purchase order permissions
        'create_purchase_order': 'can_create_purchase_order',
        'send_purchase_order': 'can_send_purchase_order',
        'approve_purchase_order': 'can_approve_purchase_order',
        'receive_purchase_order': 'can_receive_purchase_order',
        'cancel_purchase_order': 'can_cancel_purchase_order',
        'delete_purchase_order': 'can_delete_purchase_order',
        // Manufacturer permissions
        'add_manufacturer': 'can_manage_manufacturers',
        'change_manufacturer': 'can_manage_manufacturers',
        'delete_manufacturer': 'can_manage_manufacturers',
      };

      // Get permissions directly for the user's role
      const rolePermissions = getRolePermissions(user.role.role);
      const mappedPermission = permissionMap[permission];

      if (!mappedPermission || !rolePermissions) {
        return false;
      }

      return rolePermissions[mappedPermission] || false;
    };
  }, [user?.role?.role]);
};

// Helper function to get permissions for a role
const getRolePermissions = (role: string) => {
  const rolePermissions: Record<string, any> = {
    admin: {
      can_manage_users: true,
      can_manage_access_control: true,
      can_create_purchase_order: true,
      can_edit_purchase_order: true,
      can_view_purchase_order: true,
      can_receive_purchase_order: true,
      can_view_purchase_order_amounts: true,
      can_send_purchase_order: true,
      can_approve_purchase_order: true,
      can_cancel_purchase_order: true,
      can_delete_purchase_order: true,
      can_create_stock: true,
      can_edit_stock: true,
      can_view_stock: true,
      can_transfer_stock: true,
      can_commit_stock: true,
      can_fulfill_commitment: true,
      can_issue_stock: true,
      can_receive_stock: true,
      can_view_warehouse_receiving: true,
      can_create_stocktake: true,
      can_start_stocktake: true,
      can_complete_stocktake: true,
      can_cancel_stocktake: true,
      can_delete_stocktake: true,
      can_manage_payments: true,
      can_create_invoices: true,
      can_view_financial_reports: true,
      can_manage_manufacturers: true,
    },
    // Add other roles as needed
  };

  return rolePermissions[role] || {};
};

export default useAuthStore;