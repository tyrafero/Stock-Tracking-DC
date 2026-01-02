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
  Tooltip,
  LoadingOverlay,
  Alert,
} from '@mantine/core';
import {
  IconArrowLeft,
  IconCheck,
  IconX,
  IconClock,
  IconAlertCircle,
  IconCalendar,
  IconUser,
  IconPackage,
  IconBuilding,
  IconNotes,
} from '@tabler/icons-react';
import { modals } from '@mantine/modals';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth } from '@/states/authState';

const ReservationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const { data: reservation, isLoading, error } = useQuery({
    queryKey: ['reservation', id],
    queryFn: () => stockAPI.getReservation(Number(id)),
    enabled: !!id,
  });

  const fulfillMutation = useMutation({
    mutationFn: () => stockAPI.fulfillReservation(Number(id)),
    onSuccess: () => {
      notifications.show({
        title: 'Reservation Fulfilled',
        message: 'Reservation has been fulfilled successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['reservation', id] });
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to fulfill reservation',
        color: 'red',
      });
    },
  });

  const cancelMutation = useMutation({
    mutationFn: () => stockAPI.cancelReservation(Number(id)),
    onSuccess: () => {
      notifications.show({
        title: 'Reservation Cancelled',
        message: 'Reservation has been cancelled successfully',
        color: 'orange',
      });
      queryClient.invalidateQueries({ queryKey: ['reservation', id] });
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to cancel reservation',
        color: 'red',
      });
    },
  });

  const handleFulfill = () => {
    modals.openConfirmModal({
      title: 'Fulfill Reservation',
      children: (
        <Text>
          Are you sure you want to fulfill this reservation? This will issue the stock
          and mark the reservation as completed.
        </Text>
      ),
      labels: { confirm: 'Fulfill', cancel: 'Cancel' },
      confirmProps: { color: 'green' },
      onConfirm: () => fulfillMutation.mutate(),
    });
  };

  const handleCancel = () => {
    modals.openConfirmModal({
      title: 'Cancel Reservation',
      children: (
        <Text>
          Are you sure you want to cancel this reservation? This action cannot be undone.
        </Text>
      ),
      labels: { confirm: 'Cancel Reservation', cancel: 'Keep Reservation' },
      confirmProps: { color: 'red' },
      onConfirm: () => cancelMutation.mutate(),
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'yellow',
      fulfilled: 'green',
      cancelled: 'red',
      expired: 'gray',
    };
    return colors[status] || 'blue';
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
          Failed to load reservation details. Please try again.
        </Alert>
      </Container>
    );
  }

  if (!reservation) {
    return (
      <Container fluid>
        <Alert icon={<IconAlertCircle size={16} />} color="orange">
          Reservation not found.
        </Alert>
      </Container>
    );
  }

  const canFulfill = reservation.status === 'active' && reservation.stock.available_for_sale >= reservation.quantity;
  const canCancel = reservation.status === 'active';

  return (
    <Container fluid>
      <Group justify="space-between" mb="xl">
        <Group>
          <ActionIcon
            variant="light"
            size="lg"
            onClick={() => navigate('/reservations')}
          >
            <IconArrowLeft size={18} />
          </ActionIcon>
          <div>
            <Title order={1}>Reservation #{reservation.id}</Title>
            <Text c="dimmed">View and manage reservation details</Text>
          </div>
        </Group>

        <Group>
          {canFulfill && (
            <Button
              leftSection={<IconCheck size={16} />}
              color="green"
              onClick={handleFulfill}
              loading={fulfillMutation.isPending}
            >
              Fulfill
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
              <Title order={3}>Reservation Information</Title>
              <Badge color={getStatusColor(reservation.status)} size="lg">
                {reservation.status.charAt(0).toUpperCase() + reservation.status.slice(1)}
              </Badge>
            </Group>

            <Stack gap="md">
              <Group>
                <IconPackage size={16} />
                <Text fw={500}>Stock Item:</Text>
                <Text>{reservation.stock.item_name}</Text>
              </Group>

              <Group>
                <IconBuilding size={16} />
                <Text fw={500}>Location:</Text>
                <Text>{reservation.stock.location?.name || 'N/A'}</Text>
              </Group>

              <Grid>
                <Grid.Col span={6}>
                  <Text fw={500}>Quantity Reserved:</Text>
                  <Text size="lg">{reservation.quantity}</Text>
                </Grid.Col>
                <Grid.Col span={6}>
                  <Text fw={500}>Available Stock:</Text>
                  <Text size="lg" c={reservation.stock.available_for_sale < reservation.quantity ? 'red' : 'green'}>
                    {reservation.stock.available_for_sale}
                  </Text>
                </Grid.Col>
              </Grid>

              {reservation.notes && (
                <>
                  <Divider />
                  <div>
                    <Group mb="xs">
                      <IconNotes size={16} />
                      <Text fw={500}>Notes:</Text>
                    </Group>
                    <Text>{reservation.notes}</Text>
                  </div>
                </>
              )}
            </Stack>
          </Paper>

          <Paper shadow="xs" p="md">
            <Title order={3} mb="md">Timeline</Title>
            <Stack gap="md">
              <Group>
                <IconCalendar size={16} />
                <div>
                  <Text fw={500}>Created</Text>
                  <Text c="dimmed" size="sm">{formatDate(reservation.reserved_at)}</Text>
                </div>
              </Group>

              <Group>
                <IconClock size={16} />
                <div>
                  <Text fw={500}>Expires</Text>
                  <Text c="dimmed" size="sm">{formatDate(reservation.expires_at)}</Text>
                </div>
              </Group>

              {reservation.fulfilled_at && (
                <Group>
                  <IconCheck size={16} />
                  <div>
                    <Text fw={500}>Fulfilled</Text>
                    <Text c="dimmed" size="sm">{formatDate(reservation.fulfilled_at)}</Text>
                  </div>
                </Group>
              )}

              {reservation.cancelled_at && (
                <Group>
                  <IconX size={16} />
                  <div>
                    <Text fw={500}>Cancelled</Text>
                    <Text c="dimmed" size="sm">{formatDate(reservation.cancelled_at)}</Text>
                  </div>
                </Group>
              )}
            </Stack>
          </Paper>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 4 }}>
          <Paper shadow="xs" p="md" mb="md">
            <Title order={4} mb="md">Reserved By</Title>
            <Group>
              <IconUser size={16} />
              <div>
                <Text fw={500}>
                  {reservation.reserved_by.first_name} {reservation.reserved_by.last_name}
                </Text>
                <Text c="dimmed" size="sm">@{reservation.reserved_by.username}</Text>
              </div>
            </Group>
          </Paper>

          <Paper shadow="xs" p="md">
            <Title order={4} mb="md">Stock Details</Title>
            <Stack gap="sm">
              <div>
                <Text size="sm" c="dimmed">SKU</Text>
                <Text>{reservation.stock.sku || 'N/A'}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">Current Stock</Text>
                <Text>{reservation.stock.quantity}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">Available</Text>
                <Text>{reservation.stock.available_for_sale}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">Reserved</Text>
                <Text>{reservation.stock.reserved_quantity}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">Committed</Text>
                <Text>{reservation.stock.committed_quantity}</Text>
              </div>
            </Stack>
          </Paper>
        </Grid.Col>
      </Grid>
    </Container>
  );
};

export default ReservationDetail;