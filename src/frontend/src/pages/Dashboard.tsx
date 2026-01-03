import { Grid, Card, Text, Title, Group, Badge, Stack, LoadingOverlay, Button, Table, Progress, Pill, Flex, Box } from '@mantine/core';
import {
  IconPackage,
  IconAlertTriangle,
  IconArrowsExchange,
  IconReservedLine,
  IconClock,
  IconTrendingUp,
  IconCheck,
  IconX,
  IconEye,
  IconClockHour4,
  IconHourglass
} from '@tabler/icons-react';
import { useAuth, useUserRole, useHasPermission } from '@/states/authState';
import { useQuery } from '@tanstack/react-query';
import { stockAPI } from '@/api/stock';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const userRole = useUserRole();
  const hasPermission = useHasPermission();
  const navigate = useNavigate();

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

  // Additional informative data
  const { data: awaitingCollectionData, isLoading: isLoadingCollection } = useQuery({
    queryKey: ['dashboard-awaiting-collection'],
    queryFn: () => stockAPI.getAwaitingCollectionTransfers(),
    staleTime: 300000,
  });

  const { data: committedStockData, isLoading: isLoadingCommitted } = useQuery({
    queryKey: ['dashboard-committed-stock'],
    queryFn: () => stockAPI.getCommittedStock({ page_size: 10 }),
    staleTime: 300000,
  });

  const { data: expiredReservationsData, isLoading: isLoadingExpired } = useQuery({
    queryKey: ['dashboard-expired-reservations'],
    queryFn: () => stockAPI.getExpiredReservations(),
    staleTime: 300000,
  });

  const { data: allTransfersData, isLoading: isLoadingAllTransfers } = useQuery({
    queryKey: ['dashboard-all-transfers'],
    queryFn: () => stockAPI.getTransfers({ page_size: 10, ordering: '-created_at' }),
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

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'yellow',
      approved: 'blue',
      dispatched: 'orange',
      awaiting_collection: 'purple',
      completed: 'green',
      cancelled: 'red',
    };
    return colors[status] || 'gray';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getAgingDays = (dateString: string) => {
    const created = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - created.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const handleTransferAction = async (transferId: number, action: 'approve' | 'complete' | 'cancel') => {
    try {
      switch (action) {
        case 'approve':
          await stockAPI.approveTransfer(transferId);
          break;
        case 'complete':
          await stockAPI.completeTransfer(transferId);
          break;
        case 'cancel':
          await stockAPI.cancelTransfer(transferId);
          break;
      }
      // Refetch data
      window.location.reload();
    } catch (error) {
      console.error('Transfer action failed:', error);
    }
  };

  return (
    <div>
      <Group justify="space-between" mb="xl">
        <div>
          <Title order={1}>Business Dashboard</Title>
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

      {/* Overview Cards */}
      <Grid mb="xl">
        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <LoadingOverlay visible={isLoadingStock} />
            <Stack gap="xs">
              <Group gap="xs">
                <IconPackage size={20} color="#228be6" />
                <Text size="sm" c="dimmed">Total Stock Items</Text>
              </Group>
              <Text size="xl" fw={700}>
                {totalStockData?.count?.toLocaleString() || '--'}
              </Text>
              <Button variant="light" size="xs" onClick={() => navigate('/stock')}>
                View All
              </Button>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <LoadingOverlay visible={isLoadingLowStock} />
            <Stack gap="xs">
              <Group gap="xs">
                <IconAlertTriangle size={20} color="#fd7e14" />
                <Text size="sm" c="dimmed">Low Stock Alert</Text>
              </Group>
              <Text size="xl" fw={700} c="orange">
                {lowStockData?.count || '--'}
              </Text>
              <Button variant="light" color="orange" size="xs" onClick={() => navigate('/stock?filter=low_stock')}>
                Review Items
              </Button>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <LoadingOverlay visible={isLoadingExpired} />
            <Stack gap="xs">
              <Group gap="xs">
                <IconClock size={20} color="#e03131" />
                <Text size="sm" c="dimmed">Expired Reservations</Text>
              </Group>
              <Text size="xl" fw={700} c="red">
                {expiredReservationsData?.length || '--'}
              </Text>
              <Button variant="light" color="red" size="xs" onClick={() => navigate('/reservations?filter=expired')}>
                Clean Up
              </Button>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <LoadingOverlay visible={isLoadingCommitted} />
            <Stack gap="xs">
              <Group gap="xs">
                <IconReservedLine size={20} color="#7c2d12" />
                <Text size="sm" c="dimmed">Committed Stock</Text>
              </Group>
              <Text size="xl" fw={700} c="brown">
                {committedStockData?.count || '--'}
              </Text>
              <Button variant="light" color="brown" size="xs" onClick={() => navigate('/stock/committed')}>
                View Details
              </Button>
            </Stack>
          </Card>
        </Grid.Col>
      </Grid>

      <Grid>
        {/* Transfer Actions Required */}
        <Grid.Col span={{ base: 12, lg: 8 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="md">
              <Group gap="xs">
                <IconArrowsExchange size={24} color="#228be6" />
                <Title order={3}>Transfer Actions Required</Title>
              </Group>
              <Button variant="light" size="sm" onClick={() => navigate('/transfers')}>
                View All Transfers
              </Button>
            </Group>

            <LoadingOverlay visible={isLoadingAllTransfers} />

            {allTransfersData?.results?.length > 0 ? (
              <Table striped highlightOnHover>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Item</Table.Th>
                    <Table.Th>From → To</Table.Th>
                    <Table.Th>Qty</Table.Th>
                    <Table.Th>Status</Table.Th>
                    <Table.Th>Age</Table.Th>
                    <Table.Th>Action</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {allTransfersData.results.slice(0, 5).map((transfer: any) => (
                    <Table.Tr key={transfer.id}>
                      <Table.Td>
                        <Text size="sm" fw={500}>{transfer.stock?.item_name || 'N/A'}</Text>
                      </Table.Td>
                      <Table.Td>
                        <Text size="xs">
                          {transfer.from_location?.name} → {transfer.to_location?.name}
                        </Text>
                      </Table.Td>
                      <Table.Td>
                        <Text size="sm">{transfer.quantity}</Text>
                      </Table.Td>
                      <Table.Td>
                        <Pill size="sm" color={getStatusColor(transfer.status)}>
                          {transfer.status}
                        </Pill>
                      </Table.Td>
                      <Table.Td>
                        <Flex align="center" gap="xs">
                          <IconClockHour4 size={16} />
                          <Text size="xs">{getAgingDays(transfer.created_at)}d</Text>
                        </Flex>
                      </Table.Td>
                      <Table.Td>
                        <Group gap="xs">
                          {transfer.status === 'pending' && hasPermission('approve_transfer') && (
                            <Button
                              size="xs"
                              color="green"
                              variant="light"
                              onClick={() => handleTransferAction(transfer.id, 'approve')}
                            >
                              <IconCheck size={14} />
                            </Button>
                          )}
                          {transfer.status === 'approved' && hasPermission('complete_transfer') && (
                            <Button
                              size="xs"
                              color="blue"
                              variant="light"
                              onClick={() => handleTransferAction(transfer.id, 'complete')}
                            >
                              Complete
                            </Button>
                          )}
                          <Button
                            size="xs"
                            variant="light"
                            onClick={() => navigate(`/transfers/${transfer.id}`)}
                          >
                            <IconEye size={14} />
                          </Button>
                        </Group>
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            ) : (
              <Text c="dimmed" ta="center" py="xl">
                No transfers requiring action
              </Text>
            )}
          </Card>
        </Grid.Col>

        {/* Aging Analysis */}
        <Grid.Col span={{ base: 12, lg: 4 }}>
          <Stack gap="md">
            {/* Awaiting Collection */}
            <Card shadow="sm" padding="lg" radius="md" withBorder>
              <Group justify="space-between" mb="md">
                <Group gap="xs">
                  <IconHourglass size={20} color="#9c36b5" />
                  <Title order={4}>Awaiting Collection</Title>
                </Group>
              </Group>

              <LoadingOverlay visible={isLoadingCollection} />

              <Stack gap="xs">
                <Text size="lg" fw={700} c="purple">
                  {awaitingCollectionData?.count || 0}
                </Text>
                <Text size="xs" c="dimmed">
                  Transfers ready for pickup
                </Text>
                {awaitingCollectionData?.count > 0 && (
                  <Button
                    variant="light"
                    color="purple"
                    size="xs"
                    onClick={() => navigate('/transfers?status=awaiting_collection')}
                  >
                    View Collection Queue
                  </Button>
                )}
              </Stack>
            </Card>

            {/* Stock Commitments */}
            <Card shadow="sm" padding="lg" radius="md" withBorder>
              <Group justify="space-between" mb="md">
                <Group gap="xs">
                  <IconTrendingUp size={20} color="#7c2d12" />
                  <Title order={4}>Recent Commitments</Title>
                </Group>
              </Group>

              <LoadingOverlay visible={isLoadingCommitted} />

              {committedStockData?.results?.length > 0 ? (
                <Stack gap="xs">
                  {committedStockData.results.slice(0, 3).map((commitment: any) => (
                    <Box key={commitment.id} p="xs" style={{ borderRadius: '4px', backgroundColor: '#f8f9fa' }}>
                      <Text size="sm" fw={500} truncate>
                        {commitment.stock?.item_name}
                      </Text>
                      <Group justify="space-between">
                        <Text size="xs" c="dimmed">
                          Qty: {commitment.quantity}
                        </Text>
                        <Text size="xs" c="dimmed">
                          {formatDate(commitment.created_at)}
                        </Text>
                      </Group>
                      <Text size="xs" c="blue">
                        ${commitment.deposit_amount}
                      </Text>
                    </Box>
                  ))}
                  <Button
                    variant="light"
                    color="brown"
                    size="xs"
                    onClick={() => navigate('/stock/committed')}
                  >
                    View All Commitments
                  </Button>
                </Stack>
              ) : (
                <Text c="dimmed" size="sm">
                  No recent commitments
                </Text>
              )}
            </Card>
          </Stack>
        </Grid.Col>
      </Grid>
    </div>
  );
};

export default Dashboard;