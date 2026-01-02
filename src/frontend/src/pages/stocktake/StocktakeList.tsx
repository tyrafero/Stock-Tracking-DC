// @ts-nocheck
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Container,
  Title,
  Text,
  Paper,
  Group,
  Button,
  Stack,
  TextInput,
  Select,
  Table,
  Badge,
  ActionIcon,
  Menu,
  Pagination,
  Progress,
  LoadingOverlay,
  Alert,
} from '@mantine/core';
import {
  IconPlus,
  IconSearch,
  IconFilter,
  IconDots,
  IconEye,
  IconEdit,
  IconPlayerPlay,
  IconCheck,
  IconX,
  IconTrash,
  IconClipboard,
  IconAlertCircle,
  IconCalendar,
  IconUser,
  IconBuilding,
} from '@tabler/icons-react';
import { modals } from '@mantine/modals';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth, useHasPermission } from '@/states/authState';
import type { Stocktake, PaginatedResponse } from '@/types/stock';

const StocktakeList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const hasPermission = useHasPermission();

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);

  const { data: stocktakesData, isLoading, error } = useQuery({
    queryKey: ['stocktakes', searchQuery, statusFilter, currentPage],
    queryFn: () => stockAPI.getStocktakes({
      search: searchQuery,
      status: statusFilter || undefined,
      page: currentPage,
      page_size: 20,
    }),
  });

  const startMutation = useMutation({
    mutationFn: (id: number) => stockAPI.startStocktake(id),
    onSuccess: (response) => {
      notifications.show({
        title: 'Stocktake Started',
        message: response.message || 'Stocktake has been started successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stocktakes'] });
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.error || error.message || 'Failed to start stocktake',
        color: 'red',
      });
    },
  });

  const completeMutation = useMutation({
    mutationFn: (id: number) => stockAPI.completeStocktake(id),
    onSuccess: (response) => {
      notifications.show({
        title: 'Stocktake Completed',
        message: response.message || 'Stocktake has been completed successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stocktakes'] });
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.error || error.message || 'Failed to complete stocktake',
        color: 'red',
      });
    },
  });

  const cancelMutation = useMutation({
    mutationFn: (id: number) => stockAPI.cancelStocktake(id),
    onSuccess: (response) => {
      notifications.show({
        title: 'Stocktake Cancelled',
        message: response.message || 'Stocktake has been cancelled successfully',
        color: 'orange',
      });
      queryClient.invalidateQueries({ queryKey: ['stocktakes'] });
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.error || error.message || 'Failed to cancel stocktake',
        color: 'red',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => stockAPI.deleteStocktake(id),
    onSuccess: () => {
      notifications.show({
        title: 'Stocktake Deleted',
        message: 'Stocktake has been deleted successfully',
        color: 'red',
      });
      queryClient.invalidateQueries({ queryKey: ['stocktakes'] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to delete stocktake',
        color: 'red',
      });
    },
  });

  const handleStart = (stocktake: Stocktake) => {
    modals.openConfirmModal({
      title: 'Start Stocktake',
      children: (
        <Text>
          Are you sure you want to start "{stocktake.title}"? This will begin the counting process.
        </Text>
      ),
      labels: { confirm: 'Start', cancel: 'Cancel' },
      confirmProps: { color: 'green' },
      onConfirm: () => startMutation.mutate(stocktake.id),
    });
  };

  const handleComplete = (stocktake: Stocktake) => {
    modals.openConfirmModal({
      title: 'Complete Stocktake',
      children: (
        <Text>
          Are you sure you want to complete "{stocktake.title}"? This will finalize the count and apply adjustments.
        </Text>
      ),
      labels: { confirm: 'Complete', cancel: 'Cancel' },
      confirmProps: { color: 'green' },
      onConfirm: () => completeMutation.mutate(stocktake.id),
    });
  };

  const handleCancel = (stocktake: Stocktake) => {
    modals.openConfirmModal({
      title: 'Cancel Stocktake',
      children: (
        <Text>
          Are you sure you want to cancel "{stocktake.title}"? This action cannot be undone.
        </Text>
      ),
      labels: { confirm: 'Cancel Stocktake', cancel: 'Keep' },
      confirmProps: { color: 'red' },
      onConfirm: () => cancelMutation.mutate(stocktake.id),
    });
  };

  const handleDelete = (stocktake: Stocktake) => {
    modals.openConfirmModal({
      title: 'Delete Stocktake',
      children: (
        <Text>
          Are you sure you want to delete "{stocktake.title}"? This action cannot be undone.
        </Text>
      ),
      labels: { confirm: 'Delete', cancel: 'Cancel' },
      confirmProps: { color: 'red' },
      onConfirm: () => deleteMutation.mutate(stocktake.id),
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      planning: 'gray',
      in_progress: 'blue',
      completed: 'green',
      cancelled: 'red',
    };
    return colors[status] || 'gray';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const canCreateStocktake = hasPermission('create_stocktake');
  const canStartStocktake = hasPermission('start_stocktake');
  const canCompleteStocktake = hasPermission('complete_stocktake');
  const canCancelStocktake = hasPermission('cancel_stocktake');
  const canDeleteStocktake = hasPermission('delete_stocktake');

  return (
    <Container fluid>
      <Group justify="space-between" mb="xl">
        <div>
          <Title order={1}>Stocktakes</Title>
          <Text c="dimmed">Manage stock counting and variance tracking</Text>
        </div>
        {canCreateStocktake && (
          <Button
            leftSection={<IconPlus size={16} />}
            onClick={() => navigate('/stocktake/create')}
          >
            Create Stocktake
          </Button>
        )}
      </Group>

      <Paper shadow="xs" p="md" mb="md">
        <Group>
          <TextInput
            placeholder="Search stocktakes..."
            leftSection={<IconSearch size={16} />}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ flex: 1 }}
          />
          <Select
            placeholder="Status"
            leftSection={<IconFilter size={16} />}
            data={[
              { value: '', label: 'All Statuses' },
              { value: 'planning', label: 'Planning' },
              { value: 'in_progress', label: 'In Progress' },
              { value: 'completed', label: 'Completed' },
              { value: 'cancelled', label: 'Cancelled' },
            ]}
            value={statusFilter}
            onChange={(value) => setStatusFilter(value || '')}
            clearable
            w={150}
          />
        </Group>
      </Paper>

      <Paper shadow="xs" p="md">
        {isLoading ? (
          <LoadingOverlay visible />
        ) : error ? (
          <Alert icon={<IconAlertCircle size={16} />} color="red">
            Failed to load stocktakes. Please try again.
          </Alert>
        ) : stocktakesData?.results.length === 0 ? (
          <Stack align="center" py="xl">
            <IconClipboard size={48} stroke={1.5} color="gray" />
            <Text size="lg" fw={500}>No stocktakes found</Text>
            <Text c="dimmed" ta="center">
              {searchQuery || statusFilter
                ? 'Try adjusting your search filters'
                : 'Create your first stocktake to start tracking inventory counts'
              }
            </Text>
            {canCreateStocktake && !searchQuery && !statusFilter && (
              <Button
                leftSection={<IconPlus size={16} />}
                onClick={() => navigate('/stocktake/create')}
              >
                Create Stocktake
              </Button>
            )}
          </Stack>
        ) : (
          <>
            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Name</Table.Th>
                  <Table.Th>Location</Table.Th>
                  <Table.Th>Status</Table.Th>
                  <Table.Th>Progress</Table.Th>
                  <Table.Th>Created</Table.Th>
                  <Table.Th>Created By</Table.Th>
                  <Table.Th>Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {stocktakesData?.results.map((stocktake: Stocktake) => (
                  <Table.Tr key={stocktake.id}>
                    <Table.Td>
                      <div>
                        <Text fw={500}>{stocktake.title}</Text>
                        {stocktake.description && (
                          <Text size="sm" c="dimmed">{stocktake.description}</Text>
                        )}
                      </div>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <IconBuilding size={14} />
                        <Text size="sm">{stocktake.location?.name || 'All Locations'}</Text>
                      </Group>
                    </Table.Td>
                    <Table.Td>
                      <Badge color={getStatusColor(stocktake.status)} variant="light">
                        {stocktake.status.charAt(0).toUpperCase() + stocktake.status.slice(1).replace('_', ' ')}
                      </Badge>
                    </Table.Td>
                    <Table.Td>
                      <div>
                        <Text size="sm" mb="xs">
                          {stocktake.items_counted}/{stocktake.total_items} items
                        </Text>
                        <Progress
                          value={stocktake.progress_percentage}
                          size="sm"
                          color={stocktake.progress_percentage === 100 ? 'green' : 'blue'}
                        />
                      </div>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <IconCalendar size={14} />
                        <Text size="sm">{formatDate(stocktake.created_at)}</Text>
                      </Group>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <IconUser size={14} />
                        <Text size="sm">
                          {stocktake.created_by.first_name} {stocktake.created_by.last_name}
                        </Text>
                      </Group>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <ActionIcon
                          variant="light"
                          size="sm"
                          onClick={() => navigate(`/stocktake/${stocktake.id}`)}
                        >
                          <IconEye size={16} />
                        </ActionIcon>

                        <Menu shadow="md" width={200}>
                          <Menu.Target>
                            <ActionIcon variant="light" size="sm">
                              <IconDots size={16} />
                            </ActionIcon>
                          </Menu.Target>

                          <Menu.Dropdown>
                            <Menu.Item
                              leftSection={<IconEye size={14} />}
                              onClick={() => navigate(`/stocktake/${stocktake.id}`)}
                            >
                              View Details
                            </Menu.Item>

                            {stocktake.status === 'planning' && canStartStocktake && (
                              <Menu.Item
                                leftSection={<IconPlayerPlay size={14} />}
                                onClick={() => handleStart(stocktake)}
                              >
                                Start Stocktake
                              </Menu.Item>
                            )}

                            {stocktake.status === 'in_progress' && canCompleteStocktake && stocktake.items_counted === stocktake.total_items && (
                              <Menu.Item
                                leftSection={<IconCheck size={14} />}
                                onClick={() => handleComplete(stocktake)}
                                color="green"
                              >
                                Complete
                              </Menu.Item>
                            )}

                            {['planning', 'in_progress'].includes(stocktake.status) && canCancelStocktake && (
                              <Menu.Item
                                leftSection={<IconX size={14} />}
                                onClick={() => handleCancel(stocktake)}
                                color="orange"
                              >
                                Cancel
                              </Menu.Item>
                            )}

                            {stocktake.status === 'planning' && canDeleteStocktake && (
                              <Menu.Item
                                leftSection={<IconTrash size={14} />}
                                onClick={() => handleDelete(stocktake)}
                                color="red"
                              >
                                Delete
                              </Menu.Item>
                            )}
                          </Menu.Dropdown>
                        </Menu>
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>

            {stocktakesData && stocktakesData.count > 20 && (
              <Group justify="center" mt="md">
                <Pagination
                  value={currentPage}
                  onChange={setCurrentPage}
                  total={Math.ceil(stocktakesData.count / 20)}
                  size="sm"
                />
              </Group>
            )}
          </>
        )}
      </Paper>
    </Container>
  );
};

export default StocktakeList;