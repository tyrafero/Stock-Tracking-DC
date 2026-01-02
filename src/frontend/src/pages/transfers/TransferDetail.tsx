import React from 'react';
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
  Divider,
  ActionIcon,
  LoadingOverlay,
  Alert,
  Timeline,
} from '@mantine/core';
import {
  IconArrowLeft,
  IconCheck,
  IconX,
  IconTruck,
  IconAlertCircle,
  IconCalendar,
  IconUser,
  IconPackage,
  IconBuilding,
  IconNotes,
  IconArrowRight,
  IconClock,
  IconHandStop,
} from '@tabler/icons-react';
import { modals } from '@mantine/modals';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth, useHasPermission } from '@/states/authState';

const TransferDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const hasPermission = useHasPermission();

  const { data: transfer, isLoading, error } = useQuery({
    queryKey: ['transfer', id],
    queryFn: () => stockAPI.getTransfer(Number(id)),
    enabled: !!id,
  });

  const approveMutation = useMutation({
    mutationFn: () => stockAPI.approveTransfer(Number(id)),
    onSuccess: () => {
      notifications.show({
        title: 'Transfer Approved',
        message: 'Transfer has been approved successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['transfer', id] });
      queryClient.invalidateQueries({ queryKey: ['transfers'] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to approve transfer',
        color: 'red',
      });
    },
  });

  const completeMutation = useMutation({
    mutationFn: () => stockAPI.completeTransfer(Number(id)),
    onSuccess: () => {
      notifications.show({
        title: 'Transfer Completed',
        message: 'Transfer has been completed successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['transfer', id] });
      queryClient.invalidateQueries({ queryKey: ['transfers'] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to complete transfer',
        color: 'red',
      });
    },
  });

  const collectMutation = useMutation({
    mutationFn: () => stockAPI.collectTransfer(Number(id)),
    onSuccess: () => {
      notifications.show({
        title: 'Transfer Collected',
        message: 'Transfer has been collected successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['transfer', id] });
      queryClient.invalidateQueries({ queryKey: ['transfers'] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to collect transfer',
        color: 'red',
      });
    },
  });

  const cancelMutation = useMutation({
    mutationFn: () => stockAPI.cancelTransfer(Number(id)),
    onSuccess: () => {
      notifications.show({
        title: 'Transfer Cancelled',
        message: 'Transfer has been cancelled successfully',
        color: 'orange',
      });
      queryClient.invalidateQueries({ queryKey: ['transfer', id] });
      queryClient.invalidateQueries({ queryKey: ['transfers'] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to cancel transfer',
        color: 'red',
      });
    },
  });

  const handleApprove = () => {
    modals.openConfirmModal({
      title: 'Approve Transfer',
      children: (
        <Text>
          Are you sure you want to approve this transfer? This will move the stock to
          "in transit" status and reduce available quantities at the source location.
        </Text>
      ),
      labels: { confirm: 'Approve', cancel: 'Cancel' },
      confirmProps: { color: 'green' },
      onConfirm: () => approveMutation.mutate(),
    });
  };

  const handleComplete = () => {
    modals.openConfirmModal({
      title: 'Complete Transfer',
      children: (
        <Text>
          Are you sure you want to complete this transfer? This will move the stock from
          the source location to the destination location.
        </Text>
      ),
      labels: { confirm: 'Complete', cancel: 'Cancel' },
      confirmProps: { color: 'green' },
      onConfirm: () => completeMutation.mutate(),
    });
  };

  const handleCollect = () => {
    modals.openConfirmModal({
      title: 'Mark as Collected',
      children: (
        <Text>
          Are you sure you want to mark this transfer as collected? This will
          complete the transfer and update stock quantities at the destination.
        </Text>
      ),
      labels: { confirm: 'Collect', cancel: 'Cancel' },
      confirmProps: { color: 'green' },
      onConfirm: () => collectMutation.mutate(),
    });
  };

  const handleCancel = () => {
    modals.openConfirmModal({
      title: 'Cancel Transfer',
      children: (
        <Text>
          Are you sure you want to cancel this transfer? This action cannot be undone.
        </Text>
      ),
      labels: { confirm: 'Cancel Transfer', cancel: 'Keep Transfer' },
      confirmProps: { color: 'red' },
      onConfirm: () => cancelMutation.mutate(),
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'yellow',
      in_transit: 'blue',
      awaiting_collection: 'cyan',
      completed: 'green',
      collected: 'green',
      cancelled: 'red',
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
          Failed to load transfer details. Please try again.
        </Alert>
      </Container>
    );
  }

  if (!transfer) {
    return (
      <Container fluid>
        <Alert icon={<IconAlertCircle size={16} />} color="orange">
          Transfer not found.
        </Alert>
      </Container>
    );
  }

  // For now, allow any authenticated user to manage transfers
  // TODO: Implement proper permission checks later
  const canApprove = transfer.status === 'pending';
  const canComplete = (transfer.status === 'pending' || transfer.status === 'in_transit');
  const canCollect = transfer.status === 'awaiting_collection';
  const canCancel = ['pending', 'in_transit'].includes(transfer.status);

  return (
    <Container fluid>
      <Group justify="space-between" mb="xl">
        <Group>
          <ActionIcon
            variant="light"
            size="lg"
            onClick={() => navigate('/transfers')}
          >
            <IconArrowLeft size={18} />
          </ActionIcon>
          <div>
            <Title order={1}>Transfer #{transfer.id}</Title>
            <Text c="dimmed">View and manage transfer details</Text>
          </div>
        </Group>

        <Group>
          {canApprove && (
            <Button
              leftSection={<IconCheck size={16} />}
              color="green"
              onClick={handleApprove}
              loading={approveMutation.isPending}
            >
              Approve
            </Button>
          )}
          {canComplete && (
            <Button
              leftSection={<IconCheck size={16} />}
              color="green"
              onClick={handleComplete}
              loading={completeMutation.isPending}
            >
              Complete
            </Button>
          )}
          {canCollect && (
            <Button
              leftSection={<IconCheck size={16} />}
              color="green"
              onClick={handleCollect}
              loading={collectMutation.isPending}
            >
              Mark Collected
            </Button>
          )}
          {canCancel && (
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
              <Title order={3}>Transfer Information</Title>
              <Badge color={getStatusColor(transfer.status)} size="lg">
                {transfer.status.charAt(0).toUpperCase() + transfer.status.slice(1)}
              </Badge>
            </Group>

            <Stack gap="md">
              <Group>
                <IconPackage size={16} />
                <Text fw={500}>Stock Item:</Text>
                <Text>{transfer.stock.item_name}</Text>
              </Group>

              <Group>
                <IconBuilding size={16} />
                <Text fw={500}>From:</Text>
                <Text>{transfer.from_location?.name || 'N/A'}</Text>
                <IconArrowRight size={16} />
                <Text fw={500}>To:</Text>
                <Text>{transfer.to_location?.name || 'N/A'}</Text>
              </Group>

              <Group>
                <Text fw={500}>Quantity:</Text>
                <Text size="lg">{transfer.quantity}</Text>
              </Group>

              {transfer.notes && (
                <>
                  <Divider />
                  <div>
                    <Group mb="xs">
                      <IconNotes size={16} />
                      <Text fw={500}>Notes:</Text>
                    </Group>
                    <Text>{transfer.notes}</Text>
                  </div>
                </>
              )}
            </Stack>
          </Paper>

          <Paper shadow="xs" p="md">
            <Title order={3} mb="md">Transfer Timeline</Title>
            <Timeline active={getTimelineActive(transfer.status)}>
              <Timeline.Item
                bullet={<IconClock size={12} />}
                title="Transfer Requested"
              >
                <Text c="dimmed" size="sm">
                  {formatDate(transfer.created_at)}
                </Text>
                <Text size="sm">
                  Requested by {transfer.created_by.first_name} {transfer.created_by.last_name}
                </Text>
              </Timeline.Item>

              <Timeline.Item
                bullet={<IconCheck size={12} />}
                title="Transfer Approved"
                color={transfer.approved_at ? 'green' : 'gray'}
              >
                {transfer.approved_at ? (
                  <>
                    <Text c="dimmed" size="sm">
                      {formatDate(transfer.approved_at)}
                    </Text>
                    {transfer.approved_by && (
                      <Text size="sm">
                        Approved by {transfer.approved_by.first_name} {transfer.approved_by.last_name}
                      </Text>
                    )}
                  </>
                ) : (
                  <Text c="dimmed" size="sm">Pending approval</Text>
                )}
              </Timeline.Item>

              <Timeline.Item
                bullet={<IconTruck size={12} />}
                title="Transfer Completed"
                color={transfer.completed_at ? 'blue' : 'gray'}
              >
                {transfer.completed_at ? (
                  <>
                    <Text c="dimmed" size="sm">
                      {formatDate(transfer.completed_at)}
                    </Text>
                    {transfer.completed_by && (
                      <Text size="sm">
                        Completed by {transfer.completed_by.first_name} {transfer.completed_by.last_name}
                      </Text>
                    )}
                  </>
                ) : (
                  <Text c="dimmed" size="sm">In transit</Text>
                )}
              </Timeline.Item>

              <Timeline.Item
                bullet={<IconHandStop size={12} />}
                title="Transfer Collected"
                color={transfer.collected_at ? 'green' : 'gray'}
              >
                {transfer.collected_at ? (
                  <>
                    <Text c="dimmed" size="sm">
                      {formatDate(transfer.collected_at)}
                    </Text>
                    {transfer.collected_by && (
                      <Text size="sm">
                        Collected by {transfer.collected_by.first_name} {transfer.collected_by.last_name}
                      </Text>
                    )}
                  </>
                ) : (
                  <Text c="dimmed" size="sm">Awaiting collection</Text>
                )}
              </Timeline.Item>
            </Timeline>
          </Paper>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 4 }}>
          <Paper shadow="xs" p="md" mb="md">
            <Title order={4} mb="md">Transfer Details</Title>
            <Stack gap="sm">
              <div>
                <Text size="sm" c="dimmed">Stock Item</Text>
                <Text fw={500}>{transfer.stock.item_name}</Text>
                {transfer.stock.sku && (
                  <Text size="sm" c="dimmed">SKU: {transfer.stock.sku}</Text>
                )}
              </div>
              <div>
                <Text size="sm" c="dimmed">Quantity</Text>
                <Text fw={500}>{transfer.quantity}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">From Location</Text>
                <Text fw={500}>{transfer.from_location?.name || 'N/A'}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">To Location</Text>
                <Text fw={500}>{transfer.to_location?.name || 'N/A'}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">Status</Text>
                <Badge color={getStatusColor(transfer.status)} variant="light">
                  {transfer.status.charAt(0).toUpperCase() + transfer.status.slice(1)}
                </Badge>
              </div>
            </Stack>
          </Paper>

          <Paper shadow="xs" p="md">
            <Title order={4} mb="md">People Involved</Title>
            <Stack gap="md">
              <div>
                <Group mb="xs">
                  <IconUser size={16} />
                  <Text fw={500}>Requested by</Text>
                </Group>
                <Text>
                  {transfer.created_by.first_name} {transfer.created_by.last_name}
                </Text>
                <Text c="dimmed" size="sm">@{transfer.created_by.username}</Text>
              </div>

              {transfer.approved_by && (
                <div>
                  <Group mb="xs">
                    <IconCheck size={16} />
                    <Text fw={500}>Approved by</Text>
                  </Group>
                  <Text>
                    {transfer.approved_by.first_name} {transfer.approved_by.last_name}
                  </Text>
                  <Text c="dimmed" size="sm">@{transfer.approved_by.username}</Text>
                </div>
              )}

              {transfer.completed_by && (
                <div>
                  <Group mb="xs">
                    <IconTruck size={16} />
                    <Text fw={500}>Completed by</Text>
                  </Group>
                  <Text>
                    {transfer.completed_by.first_name} {transfer.completed_by.last_name}
                  </Text>
                  <Text c="dimmed" size="sm">@{transfer.completed_by.username}</Text>
                </div>
              )}

              {transfer.collected_by && (
                <div>
                  <Group mb="xs">
                    <IconHandStop size={16} />
                    <Text fw={500}>Collected by</Text>
                  </Group>
                  <Text>
                    {transfer.collected_by.first_name} {transfer.collected_by.last_name}
                  </Text>
                  <Text c="dimmed" size="sm">@{transfer.collected_by.username}</Text>
                </div>
              )}
            </Stack>
          </Paper>
        </Grid.Col>
      </Grid>
    </Container>
  );
};

function getTimelineActive(status: string): number {
  switch (status) {
    case 'pending': return 0;
    case 'in_transit': return 1;
    case 'completed': return 2;
    case 'awaiting_collection': return 2;
    case 'collected': return 3;
    case 'cancelled': return -1;
    default: return 0;
  }
}

export default TransferDetail;