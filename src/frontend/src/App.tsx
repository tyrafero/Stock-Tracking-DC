import { useEffect } from 'react';
import { RouterProvider } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import { ModalsProvider } from '@mantine/modals';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from '@/states/authState';
import { router } from '@/router';
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '@mantine/dates/styles.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const initialize = useAuthStore((state) => state.initialize);

  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider>
        <ModalsProvider
          modalProps={{
            centered: true,
            zIndex: 1000,
            overlayProps: {
              backgroundOpacity: 0.55,
              blur: 3,
            },
          }}
        >
          <Notifications position="top-right" zIndex={1000} />
          <RouterProvider router={router} />
        </ModalsProvider>
      </MantineProvider>
    </QueryClientProvider>
  );
}

export default App;
