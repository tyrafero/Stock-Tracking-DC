import { create } from 'zustand';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  autoClose?: boolean;
  autoCloseDelay?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  timestamp: number;
}

interface NotificationState {
  notifications: Notification[];
}

interface NotificationActions {
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => string;
  removeNotification: (id: string) => void;
  clearAll: () => void;
  showSuccess: (title: string, message: string) => string;
  showError: (title: string, message: string) => string;
  showWarning: (title: string, message: string) => string;
  showInfo: (title: string, message: string) => string;
}

interface NotificationStore extends NotificationState, NotificationActions {}

export const useNotificationStore = create<NotificationStore>((set, get) => ({
  notifications: [],

  addNotification: (notification) => {
    const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newNotification: Notification = {
      ...notification,
      id,
      timestamp: Date.now(),
      autoClose: notification.autoClose ?? true,
      autoCloseDelay: notification.autoCloseDelay ?? 5000,
    };

    set((state) => ({
      notifications: [newNotification, ...state.notifications],
    }));

    // Auto-remove notification if autoClose is enabled
    if (newNotification.autoClose) {
      setTimeout(() => {
        get().removeNotification(id);
      }, newNotification.autoCloseDelay);
    }

    return id;
  },

  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }));
  },

  clearAll: () => {
    set({ notifications: [] });
  },

  showSuccess: (title, message) => {
    return get().addNotification({
      type: 'success',
      title,
      message,
    });
  },

  showError: (title, message) => {
    return get().addNotification({
      type: 'error',
      title,
      message,
      autoClose: false, // Errors should not auto-close
    });
  },

  showWarning: (title, message) => {
    return get().addNotification({
      type: 'warning',
      title,
      message,
      autoCloseDelay: 7000, // Warnings stay longer
    });
  },

  showInfo: (title, message) => {
    return get().addNotification({
      type: 'info',
      title,
      message,
    });
  },
}));

// Convenient hooks
export const useNotifications = () => {
  const notifications = useNotificationStore((state) => state.notifications);
  const removeNotification = useNotificationStore((state) => state.removeNotification);
  const clearAll = useNotificationStore((state) => state.clearAll);

  return {
    notifications,
    removeNotification,
    clearAll,
  };
};

export const useNotify = () => {
  const showSuccess = useNotificationStore((state) => state.showSuccess);
  const showError = useNotificationStore((state) => state.showError);
  const showWarning = useNotificationStore((state) => state.showWarning);
  const showInfo = useNotificationStore((state) => state.showInfo);

  return {
    success: showSuccess,
    error: showError,
    warning: showWarning,
    info: showInfo,
  };
};

export default useNotificationStore;