import { Grid, Card, Text, Title, Group, Badge, Stack, LoadingOverlay } from '@mantine/core';
import { useAuth, useUserRole } from '@/states/authState';
import { useQuery } from '@tanstack/react-query';
import { stockAPI } from '@/api/stock';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const userRole = useUserRole();

  // Fetch dashboard data
  const { data: totalStockData, isLoading: isLoadingStock } = useQuery({
    queryKey: ['dashboard-total-stock'],
    queryFn: () => stockAPI.getStocks({ page: 1, page_size: 1 }),
    staleTime: 300000, // Cache for 5 minutes
  });

  const { data: lowStockData, isLoading: isLoadingLowStock } = useQuery({
    queryKey: ['dashboard-low-stock'],
    queryFn: () => stockAPI.getLowStock(),
    staleTime: 300000,
  });

  const { data: activeReservationsData, isLoading: isLoadingReservations } = useQuery({
    queryKey: ['dashboard-reservations'],
    queryFn: () => stockAPI.getActiveReservations(),
    staleTime: 300000,
  });

  const { data: pendingTransfersData, isLoading: isLoadingTransfers } = useQuery({
    queryKey: ['dashboard-transfers'],
    queryFn: () => stockAPI.getPendingTransfers(),
    staleTime: 300000,
  });

  const getRoleColor = (role: string) => {
    const colors: Record<string, string> = {
      admin: 'red',
      owner: 'violet',
      logistics: 'blue',
      warehouse: 'green',
      stocktake_manager: 'orange',
      sales: 'cyan',
      accountant: 'yellow',
      warehouse_boy: 'gray',
      pending: 'gray',
    };
    return colors[role] || 'gray';
  };

  return (
    <div>
      <Group justify="space-between" mb="xl">
        <div>
          <Title order={1}>Dashboard</Title>
          <Text c="dimmed" size="lg">
            Welcome back, {user?.first_name || user?.username}!
          </Text>
        </div>
        {userRole && (
          <Badge size="lg" color={getRoleColor(userRole)} variant="light">
            {userRole.charAt(0).toUpperCase() + userRole.slice(1).replace('_', ' ')}
          </Badge>
        )}
      </Group>

      <Grid>
        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <LoadingOverlay visible={isLoadingStock} />
            <Stack gap="xs">
              <Text size="sm" c="dimmed">
                Total Stock Items
              </Text>
              <Text size="xl" fw={700}>
                {totalStockData?.count?.toLocaleString() || '--'}
              </Text>
              <Text size="xs" c="dimmed">
                Items in inventory
              </Text>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <LoadingOverlay visible={isLoadingLowStock} />
            <Stack gap="xs">
              <Text size="sm" c="dimmed">
                Low Stock Items
              </Text>
              <Text size="xl" fw={700} c="orange">
                {lowStockData?.count || '--'}
              </Text>
              <Text size="xs" c="dimmed">
                Items below reorder level
              </Text>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <LoadingOverlay visible={isLoadingReservations} />
            <Stack gap="xs">
              <Text size="sm" c="dimmed">
                Active Reservations
              </Text>
              <Text size="xl" fw={700} c="blue">
                {activeReservationsData?.count || '--'}
              </Text>
              <Text size="xs" c="dimmed">
                Stock reserved for customers
              </Text>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <LoadingOverlay visible={isLoadingTransfers} />
            <Stack gap="xs">
              <Text size="sm" c="dimmed">
                Pending Transfers
              </Text>
              <Text size="xl" fw={700} c="yellow">
                {pendingTransfersData?.count || '--'}
              </Text>
              <Text size="xs" c="dimmed">
                Transfers awaiting approval
              </Text>
            </Stack>
          </Card>
        </Grid.Col>
      </Grid>

      <Grid mt="xl">
        <Grid.Col span={12}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={3} mb="md">
              Quick Actions
            </Title>
            <Text c="dimmed" mb="md">
              Your stock management system is ready! You have access to:
            </Text>
            <Grid>
              <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
                <Card padding="md" withBorder>
                  <Text fw={600} mb="xs">Stock Management</Text>
                  <Text size="sm" c="dimmed">View, edit, and manage your inventory</Text>
                </Card>
              </Grid.Col>
              <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
                <Card padding="md" withBorder>
                  <Text fw={600} mb="xs">Low Stock Alerts</Text>
                  <Text size="sm" c="dimmed">Monitor items below reorder levels</Text>
                </Card>
              </Grid.Col>
              <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
                <Card padding="md" withBorder>
                  <Text fw={600} mb="xs">Stock Transfers</Text>
                  <Text size="sm" c="dimmed">Transfer inventory between locations</Text>
                </Card>
              </Grid.Col>
              <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
                <Card padding="md" withBorder>
                  <Text fw={600} mb="xs">Reservations</Text>
                  <Text size="sm" c="dimmed">Manage customer reservations</Text>
                </Card>
              </Grid.Col>
            </Grid>
          </Card>
        </Grid.Col>
      </Grid>
    </div>
  );
};

export default Dashboard;