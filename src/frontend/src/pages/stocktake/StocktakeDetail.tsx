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
  Modal,
  Progress,
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
  IconEye,
  IconNotes,
} from '@tabler/icons-react';
import { useForm } from '@mantine/form';
import { modals } from '@mantine/modals';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth, useHasPermission } from '@/states/authState';
import type { Stocktake, StocktakeItem } from '@/types/stock';

interface CountItemForm {
  actual_quantity: number;
  notes: string;
}

const StocktakeDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const hasPermission = useHasPermission();

  const [countingItem, setCountingItem] = useState<StocktakeItem | null>(null);
  const [showCountModal, setShowCountModal] = useState(false);

  const { data: stocktake, isLoading, error } = useQuery({
    queryKey: ['stocktake', id],
    queryFn: () => stockAPI.getStocktake(Number(id)),
    enabled: !!id,
  });

  const countForm = useForm<CountItemForm>({
    initialValues: {
      actual_quantity: 0,
      notes: '',
    },
    validate: {
      actual_quantity: (value) => (value < 0 ? 'Quantity cannot be negative' : null),
    },
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

  const countItemMutation = useMutation({
    mutationFn: ({ itemId, data }: { itemId: number; data: { actual_quantity: number; notes?: string } }) =>
      stockAPI.countStocktakeItem(Number(id), itemId, data),
    onSuccess: () => {
      notifications.show({
        title: 'Item Counted',
        message: 'Item count has been recorded successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stocktake', id] });
      setShowCountModal(false);
      setCountingItem(null);
      countForm.reset();
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to count item',
        color: 'red',
      });
    },
  });

  const handleStart = () => {
    modals.openConfirmModal({
      title: 'Start Stocktake',
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

  const handleCountItem = (item: StocktakeItem) => {
    setCountingItem(item);
    countForm.setValues({
      actual_quantity: item.actual_quantity || item.expected_quantity,
      notes: item.notes || '',
    });
    setShowCountModal(true);
  };

  const handleSubmitCount = (values: CountItemForm) => {
    if (!countingItem) return;

    countItemMutation.mutate({
      itemId: countingItem.id,
      data: {
        actual_quantity: values.actual_quantity,
        notes: values.notes || undefined,
      },
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

  const canStartStocktake = hasPermission('start_stocktake');
  const canCompleteStocktake = hasPermission('complete_stocktake');
  const canCancelStocktake = hasPermission('cancel_stocktake');
  const canCountItems = hasPermission('count_stocktake_items');

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
            <Title order={1}>{stocktake.name}</Title>
            <Text c="dimmed">{stocktake.description || 'Stock counting and variance tracking'}</Text>
          </div>
        </Group>

        <Group>
          {stocktake.status === 'planning' && canStartStocktake && (
            <Button
              leftSection={<IconPlayerPlay size={16} />}
              color="green"
              onClick={handleStart}
              loading={startMutation.isPending}
            >
              Start Stocktake
            </Button>
          )}
          {stocktake.status === 'in_progress' && canCompleteStocktake && stocktake.items_counted === stocktake.total_items && (
            <Button
              leftSection={<IconCheck size={16} />}
              color="green"
              onClick={handleComplete}
              loading={completeMutation.isPending}
            >
              Complete
            </Button>
          )}
          {['planning', 'in_progress'].includes(stocktake.status) && canCancelStocktake && (
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
                    {stocktake.items_counted}/{stocktake.total_items} items counted ({stocktake.progress_percentage}%)
                  </Text>
                  <Progress
                    value={stocktake.progress_percentage}
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

          <Paper shadow="xs" p="md">
            <Title order={3} mb="md">Items</Title>

            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Item</Table.Th>
                  <Table.Th>Expected</Table.Th>
                  <Table.Th>Actual</Table.Th>
                  <Table.Th>Variance</Table.Th>
                  <Table.Th>Status</Table.Th>
                  <Table.Th>Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {stocktake.items.map((item: StocktakeItem) => (
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
                    <Table.Td>{item.expected_quantity}</Table.Td>
                    <Table.Td>
                      {item.actual_quantity !== undefined ? item.actual_quantity : '-'}
                    </Table.Td>
                    <Table.Td>
                      {item.actual_quantity !== undefined ? (
                        <Badge color={item.variance === 0 ? 'green' : item.variance > 0 ? 'blue' : 'red'} variant="light">
                          {item.variance > 0 ? '+' : ''}{item.variance}
                        </Badge>
                      ) : (
                        '-'
                      )}
                    </Table.Td>
                    <Table.Td>
                      <Badge color={getItemStatusColor(item.status)} variant="light">
                        {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                      </Badge>
                    </Table.Td>
                    <Table.Td>
                      {stocktake.status === 'in_progress' && canCountItems && (
                        <ActionIcon
                          variant="light"
                          size="sm"
                          onClick={() => handleCountItem(item)}
                        >
                          <IconEdit size={16} />
                        </ActionIcon>
                      )}
                      {stocktake.status === 'completed' && (
                        <ActionIcon
                          variant="light"
                          size="sm"
                          disabled
                        >
                          <IconEye size={16} />
                        </ActionIcon>
                      )}
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
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
                <Text fw={500}>{stocktake.total_items}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">Items Counted</Text>
                <Text fw={500}>{stocktake.items_counted}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">Items Pending</Text>
                <Text fw={500}>{stocktake.items_pending}</Text>
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

      <Modal
        opened={showCountModal}
        onClose={() => {
          setShowCountModal(false);
          setCountingItem(null);
          countForm.reset();
        }}
        title={`Count: ${countingItem?.stock.item_name}`}
        size="md"
      >
        <form onSubmit={countForm.onSubmit(handleSubmitCount)}>
          <Stack gap="md">
            <Text size="sm" c="dimmed">
              Expected Quantity: {countingItem?.expected_quantity}
            </Text>

            <NumberInput
              label="Actual Quantity"
              placeholder="Enter actual count"
              min={0}
              {...countForm.getInputProps('actual_quantity')}
            />

            <Textarea
              label="Notes (Optional)"
              placeholder="Add any notes about the count..."
              autosize
              minRows={2}
              maxRows={4}
              {...countForm.getInputProps('notes')}
            />

            <Group justify="flex-end">
              <Button
                variant="light"
                onClick={() => {
                  setShowCountModal(false);
                  setCountingItem(null);
                  countForm.reset();
                }}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                loading={countItemMutation.isPending}
              >
                Save Count
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>
    </Container>
  );
};

export default StocktakeDetail;