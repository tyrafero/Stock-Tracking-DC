import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import apiClient from '@/api/client';
import type { AuthState, AuthUser, AuthTokens, LoginCredentials } from '@/types/auth';

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
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.message || 'Login failed',
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
        can_create_stock: true,
        can_edit_stock: true,
        can_view_stock: true,
        can_transfer_stock: true,
        can_commit_stock: true,
        can_fulfill_commitment: true,
        can_issue_stock: true,
        can_receive_stock: true,
        can_view_warehouse_receiving: true,
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
        can_create_stock: true,
        can_edit_stock: true,
        can_view_stock: true,
        can_transfer_stock: true,
        can_commit_stock: true,
        can_fulfill_commitment: true,
        can_issue_stock: true,
        can_receive_stock: true,
        can_view_warehouse_receiving: true,
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

export default useAuthStore;