
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Container,
  Title,
  Text,
  Paper,
  Group,
  Badge,
  Button,
  Stack,
  Grid,
  ActionIcon,
  LoadingOverlay,
  Alert,
  Table,
  NumberInput,
  Textarea,
  Progress,
  Pagination,
} from '@mantine/core';
import {
  IconArrowLeft,
  IconPlayerPlay,
  IconCheck,
  IconX,
  IconClipboard,
  IconAlertCircle,
  IconCalendar,
  IconUser,
  IconBuilding,
  IconPackage,
  IconEdit,
} from '@tabler/icons-react';
import { modals } from '@mantine/modals';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth, useHasPermission } from '@/states/authState';
import type { Stocktake, StocktakeItem } from '@/types/stock';

const StocktakeDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const hasPermission = useHasPermission();

  const [editingItemId, setEditingItemId] = useState<number | null>(null);
  const [editingValue, setEditingValue] = useState<number>(0);
  const [editingNotes, setEditingNotes] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 50; // Show 50 items per page

  const { data: stocktake, isLoading, error } = useQuery({
    queryKey: ['stocktake', id],
    queryFn: () => stockAPI.getStocktake(Number(id)),
    enabled: !!id,
  });

  // Fetch items separately with pagination
  const { data: itemsData, isLoading: itemsLoading } = useQuery({
    queryKey: ['stocktake-items', id, currentPage],
    queryFn: () => stockAPI.getStocktakeItems(Number(id), { page: currentPage, page_size: itemsPerPage }),
    enabled: !!id,
  });


  const startMutation = useMutation({
    mutationFn: () => stockAPI.startStocktake(Number(id)),
    onSuccess: (response) => {
      notifications.show({
        title: 'Stocktake Started',
        message: response.message || 'Stocktake has been started successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stocktake', id] });
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
    mutationFn: () => stockAPI.completeStocktake(Number(id)),
    onSuccess: (response) => {
      notifications.show({
        title: 'Stocktake Completed',
        message: response.message || 'Stocktake has been completed successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stocktake', id] });
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
    mutationFn: () => stockAPI.cancelStocktake(Number(id)),
    onSuccess: (response) => {
      notifications.show({
        title: 'Stocktake Cancelled',
        message: response.message || 'Stocktake has been cancelled successfully',
        color: 'orange',
      });
      queryClient.invalidateQueries({ queryKey: ['stocktake', id] });
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.error || error.message || 'Failed to cancel stocktake',
        color: 'red',
      });
    },
  });

  const approveMutation = useMutation({
    mutationFn: () => stockAPI.approveStocktake(Number(id)),
    onSuccess: (response) => {
      notifications.show({
        title: 'Stocktake Approved',
        message: response.message || 'Stocktake has been approved and adjustments applied to stock',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stocktake', id] });
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.error || error.message || 'Failed to approve stocktake',
        color: 'red',
      });
    },
  });

  const countItemMutation = useMutation({
    mutationFn: ({ itemId, data }: { itemId: number; data: { actual_quantity: number; notes?: string } }) =>
      stockAPI.countStocktakeItem(Number(id), itemId, data),
    onSuccess: () => {
      notifications.show({
        title: 'Saved',
        message: 'Count updated successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stocktake', id] });
      queryClient.invalidateQueries({ queryKey: ['stocktake-items', id] });
      setEditingItemId(null);
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to save count',
        color: 'red',
      });
    },
  });

  const handleStart = () => {
    modals.openConfirmModal({
      title: 'Start Stocktake',
      centered: true,
      children: (
        <Text>
          Are you sure you want to start this stocktake? This will begin the counting process.
        </Text>
      ),
      labels: { confirm: 'Start', cancel: 'Cancel' },
      confirmProps: { color: 'green' },
      onConfirm: () => startMutation.mutate(),
    });
  };

  const handleComplete = () => {
    modals.openConfirmModal({
      title: 'Complete Stocktake',
      centered: true,
      children: (
        <Text>
          Are you sure you want to complete this stocktake? This will finalize all counts and apply adjustments.
        </Text>
      ),
      labels: { confirm: 'Complete', cancel: 'Cancel' },
      confirmProps: { color: 'green' },
      onConfirm: () => completeMutation.mutate(),
    });
  };

  const handleCancel = () => {
    modals.openConfirmModal({
      title: 'Cancel Stocktake',
      centered: true,
      children: (
        <Text>
          Are you sure you want to cancel this stocktake? This action cannot be undone.
        </Text>
      ),
      labels: { confirm: 'Cancel Stocktake', cancel: 'Keep' },
      confirmProps: { color: 'red' },
      onConfirm: () => cancelMutation.mutate(),
    });
  };

  const handleApprove = () => {
    modals.openConfirmModal({
      title: 'Approve Stocktake',
      centered: true,
      children: (
        <Text>
          Are you sure you want to approve this stocktake? This will apply all adjustments to the actual stock quantities. This action cannot be undone.
        </Text>
      ),
      labels: { confirm: 'Approve & Apply Adjustments', cancel: 'Go Back' },
      confirmProps: { color: 'green' },
      onConfirm: () => approveMutation.mutate(),
    });
  };

  const handleStartEdit = (item: StocktakeItem) => {
    console.log('Starting edit for item:', item.id, item.stock.item_name);
    setEditingItemId(item.id);
    setEditingValue(item.physical_count ?? item.system_quantity);
    setEditingNotes(item.variance_notes || '');
  };

  const handleSaveCount = (itemId: number) => {
    countItemMutation.mutate({
      itemId,
      data: {
        actual_quantity: editingValue,
        notes: editingNotes || undefined,
      },
    });
  };

  const handleCancelEdit = () => {
    setEditingItemId(null);
    setEditingValue(0);
    setEditingNotes('');
  };

  const handleKeyPress = (e: React.KeyboardEvent, itemId: number) => {
    if (e.key === 'Enter') {
      handleSaveCount(itemId);
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      planned: 'gray',
      in_progress: 'blue',
      completed: 'green',
      cancelled: 'red',
      approved: 'teal',
    };
    return colors[status] || 'gray';
  };

  const getItemStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'gray',
      counted: 'blue',
      verified: 'green',
      discrepancy: 'red',
    };
    return colors[status] || 'gray';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Backend handles all permission checks - frontend just enables UI based on authentication
  const canStartStocktake = !!user;
  const canCompleteStocktake = !!user;
  const canCancelStocktake = !!user;
  const canCountItems = !!user; // Any authenticated user can attempt to count, backend will authorize

  if (isLoading) {
    return (
      <Container fluid>
        <LoadingOverlay visible />
        <Title order={1}>Loading...</Title>
      </Container>
    );
  }

  if (error) {
    return (
      <Container fluid>
        <Alert icon={<IconAlertCircle size={16} />} color="red">
          Failed to load stocktake details. Please try again.
        </Alert>
      </Container>
    );
  }

  if (!stocktake) {
    return (
      <Container fluid>
        <Alert icon={<IconAlertCircle size={16} />} color="orange">
          Stocktake not found.
        </Alert>
      </Container>
    );
  }

  // Get items and pagination info from backend
  const paginatedItems = itemsData?.results || [];
  const totalPages = itemsData?.total_pages || 0;
  const totalItems = itemsData?.count || 0;
  const startIndex = ((itemsData?.current_page || 1) - 1) * itemsPerPage;
  const endIndex = Math.min(startIndex + itemsPerPage, totalItems);

  return (
    <Container fluid>
      <Group justify="space-between" mb="xl">
        <Group>
          <ActionIcon
            variant="light"
            size="lg"
            onClick={() => navigate('/stocktake')}
          >
            <IconArrowLeft size={18} />
          </ActionIcon>
          <div>
            <Title order={1}>{stocktake.title}</Title>
            <Text c="dimmed">{stocktake.description || 'Stock counting and variance tracking'}</Text>
          </div>
        </Group>

        <Group>
          {stocktake.status === 'planned' && canStartStocktake && (
            <Button
              leftSection={<IconPlayerPlay size={16} />}
              color="green"
              onClick={handleStart}
              loading={startMutation.isPending}
            >
              Start Stocktake
            </Button>
          )}
          {stocktake.status === 'in_progress' && canCompleteStocktake && stocktake.total_items_counted === stocktake.total_items_planned && (
            <Button
              leftSection={<IconCheck size={16} />}
              color="green"
              onClick={handleComplete}
              loading={completeMutation.isPending}
            >
              Complete
            </Button>
          )}
          {stocktake.status === 'completed' && canCompleteStocktake && (
            <Button
              leftSection={<IconCheck size={16} />}
              color="teal"
              onClick={handleApprove}
              loading={approveMutation.isPending}
            >
              Approve & Apply Adjustments
            </Button>
          )}
          {['planned', 'in_progress'].includes(stocktake.status) && canCancelStocktake && (
            <Button
              leftSection={<IconX size={16} />}
              variant="light"
              color="red"
              onClick={handleCancel}
              loading={cancelMutation.isPending}
            >
              Cancel
            </Button>
          )}
        </Group>
      </Group>

      <Grid>
        <Grid.Col span={{ base: 12, md: 8 }}>
          <Paper shadow="xs" p="md" mb="md">
            <Group justify="space-between" mb="md">
              <Title order={3}>Stocktake Overview</Title>
              <Badge color={getStatusColor(stocktake.status)} size="lg">
                {stocktake.status.charAt(0).toUpperCase() + stocktake.status.slice(1).replace('_', ' ')}
              </Badge>
            </Group>

            <Stack gap="md">
              <Group>
                <IconBuilding size={16} />
                <Text fw={500}>Location:</Text>
                <Text>{stocktake.location?.name || 'All Locations'}</Text>
              </Group>

              <Group>
                <IconClipboard size={16} />
                <Text fw={500}>Progress:</Text>
                <div style={{ flex: 1 }}>
                  <Text size="sm" mb="xs">
                    {stocktake.total_items_counted || 0}/{stocktake.total_items_planned || 0} items counted ({stocktake.progress_percentage || 0}%)
                  </Text>
                  <Progress
                    value={stocktake.progress_percentage || 0}
                    size="md"
                    color={stocktake.progress_percentage === 100 ? 'green' : 'blue'}
                  />
                </div>
              </Group>

              {stocktake.total_variance !== 0 && (
                <Group>
                  <IconAlertCircle size={16} />
                  <Text fw={500}>Total Variance:</Text>
                  <Badge color={stocktake.total_variance > 0 ? 'green' : 'red'} variant="filled">
                    {stocktake.total_variance > 0 ? '+' : ''}{stocktake.total_variance}
                  </Badge>
                </Group>
              )}
            </Stack>
          </Paper>

          <Paper shadow="xs" p="md" pos="relative">
            <LoadingOverlay visible={itemsLoading} />
            <Title order={3} mb="md">Items</Title>

            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Item</Table.Th>
                  <Table.Th>Expected</Table.Th>
                  <Table.Th>Actual Count</Table.Th>
                  <Table.Th>Variance</Table.Th>
                  <Table.Th>Notes</Table.Th>
                  <Table.Th>Status</Table.Th>
                  {stocktake.status === 'in_progress' && canCountItems && <Table.Th>Actions</Table.Th>}
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {paginatedItems.map((item: StocktakeItem) => (
                  <Table.Tr key={item.id}>
                    <Table.Td>
                      <Group>
                        <IconPackage size={16} />
                        <div>
                          <Text fw={500}>{item.stock.item_name}</Text>
                          {item.stock.sku && (
                            <Text size="sm" c="dimmed">SKU: {item.stock.sku}</Text>
                          )}
                        </div>
                      </Group>
                    </Table.Td>
                    <Table.Td>{item.system_quantity}</Table.Td>
                    <Table.Td
                      onClick={() => {
                        console.log('Cell clicked. Status:', stocktake.status, 'Can count:', canCountItems);
                        if (stocktake.status === 'in_progress' && canCountItems) {
                          handleStartEdit(item);
                        } else {
                          console.log('Cannot edit: stocktake not in progress or no permission');
                        }
                      }}
                      style={{
                        cursor: stocktake.status === 'in_progress' && canCountItems ? 'pointer' : 'default',
                        backgroundColor: editingItemId === item.id ? '#f0f9ff' : undefined
                      }}
                    >
                      {editingItemId === item.id ? (
                        <NumberInput
                          value={editingValue}
                          onChange={(val) => setEditingValue(Number(val))}
                          onKeyDown={(e) => handleKeyPress(e, item.id)}
                          min={0}
                          size="xs"
                          styles={{ input: { width: '80px' } }}
                          autoFocus
                        />
                      ) : (
                        <Text
                          c={item.physical_count !== undefined && item.physical_count !== null ? undefined : 'dimmed'}
                          style={{ userSelect: 'none' }}
                        >
                          {item.physical_count !== undefined && item.physical_count !== null ? item.physical_count : (stocktake.status === 'in_progress' ? 'Click to count' : '-')}
                        </Text>
                      )}
                    </Table.Td>
                    <Table.Td>
                      {item.physical_count !== undefined && item.physical_count !== null ? (
                        <Badge color={item.variance_quantity === 0 ? 'green' : item.variance_quantity > 0 ? 'blue' : 'red'} variant="light">
                          {item.variance_quantity > 0 ? '+' : ''}{item.variance_quantity}
                        </Badge>
                      ) : (
                        '-'
                      )}
                    </Table.Td>
                    <Table.Td onClick={() => stocktake.status === 'in_progress' && canCountItems && editingItemId === item.id && {}} style={{ cursor: editingItemId === item.id ? 'pointer' : 'default', maxWidth: '200px' }}>
                      {editingItemId === item.id ? (
                        <Textarea
                          value={editingNotes}
                          onChange={(e) => setEditingNotes(e.currentTarget.value)}
                          placeholder="Add notes..."
                          size="xs"
                          autosize
                          minRows={1}
                        />
                      ) : (
                        <Text size="sm" c="dimmed" truncate="end">
                          {item.variance_notes || '-'}
                        </Text>
                      )}
                    </Table.Td>
                    <Table.Td>
                      {(() => {
                        const status = item.physical_count !== undefined && item.physical_count !== null
                          ? (item.variance_quantity === 0 ? 'counted' : 'discrepancy')
                          : 'pending';
                        return (
                          <Badge color={getItemStatusColor(status)} variant="light">
                            {status.charAt(0).toUpperCase() + status.slice(1)}
                          </Badge>
                        );
                      })()}
                    </Table.Td>
                    {stocktake.status === 'in_progress' && canCountItems && (
                      <Table.Td>
                        {editingItemId === item.id ? (
                          <Group gap="xs">
                            <ActionIcon
                              variant="filled"
                              color="green"
                              size="sm"
                              onClick={() => handleSaveCount(item.id)}
                              loading={countItemMutation.isPending}
                            >
                              <IconCheck size={16} />
                            </ActionIcon>
                            <ActionIcon
                              variant="light"
                              color="red"
                              size="sm"
                              onClick={handleCancelEdit}
                            >
                              <IconX size={16} />
                            </ActionIcon>
                          </Group>
                        ) : (
                          <ActionIcon
                            variant="light"
                            size="sm"
                            onClick={() => handleStartEdit(item)}
                          >
                            <IconEdit size={16} />
                          </ActionIcon>
                        )}
                      </Table.Td>
                    )}
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>

            {totalPages > 1 && (
              <Group justify="space-between" mt="md">
                <Text size="sm" c="dimmed">
                  Showing {startIndex + 1}-{endIndex} of {totalItems} items
                </Text>
                <Pagination
                  total={totalPages}
                  value={currentPage}
                  onChange={setCurrentPage}
                  size="sm"
                />
              </Group>
            )}
          </Paper>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 4 }}>
          <Paper shadow="xs" p="md" mb="md">
            <Title order={4} mb="md">Stocktake Details</Title>
            <Stack gap="sm">
              <div>
                <Text size="sm" c="dimmed">Created</Text>
                <Group gap="xs">
                  <IconCalendar size={14} />
                  <Text size="sm">{formatDate(stocktake.created_at)}</Text>
                </Group>
              </div>
              {stocktake.started_at && (
                <div>
                  <Text size="sm" c="dimmed">Started</Text>
                  <Group gap="xs">
                    <IconPlayerPlay size={14} />
                    <Text size="sm">{formatDate(stocktake.started_at)}</Text>
                  </Group>
                </div>
              )}
              {stocktake.completed_at && (
                <div>
                  <Text size="sm" c="dimmed">Completed</Text>
                  <Group gap="xs">
                    <IconCheck size={14} />
                    <Text size="sm">{formatDate(stocktake.completed_at)}</Text>
                  </Group>
                </div>
              )}
              <div>
                <Text size="sm" c="dimmed">Total Items</Text>
                <Text fw={500}>{stocktake.total_items_planned || 0}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">Items Counted</Text>
                <Text fw={500}>{stocktake.total_items_counted || 0}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">Items Pending</Text>
                <Text fw={500}>{(stocktake.total_items_planned || 0) - (stocktake.total_items_counted || 0)}</Text>
              </div>
            </Stack>
          </Paper>

          <Paper shadow="xs" p="md">
            <Title order={4} mb="md">People Involved</Title>
            <Stack gap="md">
              <div>
                <Group mb="xs">
                  <IconUser size={16} />
                  <Text fw={500}>Created by</Text>
                </Group>
                <Text>
                  {stocktake.created_by.first_name} {stocktake.created_by.last_name}
                </Text>
                <Text c="dimmed" size="sm">@{stocktake.created_by.username}</Text>
              </div>

              {stocktake.started_by && (
                <div>
                  <Group mb="xs">
                    <IconPlayerPlay size={16} />
                    <Text fw={500}>Started by</Text>
                  </Group>
                  <Text>
                    {stocktake.started_by.first_name} {stocktake.started_by.last_name}
                  </Text>
                  <Text c="dimmed" size="sm">@{stocktake.started_by.username}</Text>
                </div>
              )}

              {stocktake.completed_by && (
                <div>
                  <Group mb="xs">
                    <IconCheck size={16} />
                    <Text fw={500}>Completed by</Text>
                  </Group>
                  <Text>
                    {stocktake.completed_by.first_name} {stocktake.completed_by.last_name}
                  </Text>
                  <Text c="dimmed" size="sm">@{stocktake.completed_by.username}</Text>
                </div>
              )}
            </Stack>
          </Paper>
        </Grid.Col>
      </Grid>

    </Container>
  );
};

export default StocktakeDetail;