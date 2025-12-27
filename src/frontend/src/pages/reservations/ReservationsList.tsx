import React, { useState, useMemo } from 'react';
import {
  Container,
  Card,
  Text,
  Title,
  Group,
  Button,
  Stack,
  Badge,
  ActionIcon,
  Modal,
  Select,
  TextInput,
  Alert,
  LoadingOverlay,
  Box,
  Tooltip
} from '@mantine/core';
import {
  IconPlus,
  IconRefresh,
  IconEye,
  IconEdit,
  IconX,
  IconCheck,
  IconAlertCircle,
  IconReservedLine,
  IconSearch,
  IconFilter
} from '@tabler/icons-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DataTable, type DataTableColumn } from 'mantine-datatable';
import { useNavigate } from 'react-router-dom';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';

import { stockAPI } from '@/api/stock';
import { useHasPermission } from '@/states/authState';
import type { StockReservation, PaginatedResponse } from '@/types/stock';

const ReservationsList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const hasPermission = useHasPermission();

  // State for filtering and pagination
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');

  // Modal states
  const [selectedReservation, setSelectedReservation] = useState<StockReservation | null>(null);
  const [fulfillOpened, { open: openFulfill, close: closeFulfill }] = useDisclosure(false);
  const [cancelOpened, { open: openCancel, close: closeCancel }] = useDisclosure(false);
  const [cancelReason, setCancelReason] = useState('');

  // Fetch reservations
  const {
    data: reservationsData,
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['reservations', page, pageSize, searchTerm, statusFilter, typeFilter],
    queryFn: () => stockAPI.getReservations({
      page,
      page_size: pageSize,
      search: searchTerm || undefined,
      status: statusFilter || undefined,
      reservation_type: typeFilter || undefined,
    }),
    staleTime: 30000,
  });

  const reservations = reservationsData?.results || [];
  const totalCount = reservationsData?.count || 0;
  const totalPages = Math.ceil(totalCount / pageSize);

  // Mutations for reservation operations
  const fulfillMutation = useMutation({
    mutationFn: (id: number) => stockAPI.fulfillReservation(id),
    onSuccess: () => {
      notifications.show({
        title: 'Reservation Fulfilled',
        message: 'Reservation has been fulfilled successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
      closeFulfill();
      setSelectedReservation(null);
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to fulfill reservation',
        color: 'red',
      });
    },
  });

  const cancelMutation = useMutation({
    mutationFn: (id: number) => stockAPI.cancelReservation(id),
    onSuccess: () => {
      notifications.show({
        title: 'Reservation Cancelled',
        message: 'Reservation has been cancelled successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
      closeCancel();
      setSelectedReservation(null);
      setCancelReason('');
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to cancel reservation',
        color: 'red',
      });
    },
  });

  const handleFulfill = (reservation: StockReservation) => {
    setSelectedReservation(reservation);
    openFulfill();
  };

  const handleCancel = (reservation: StockReservation) => {
    setSelectedReservation(reservation);
    openCancel();
  };

  const handleView = (reservation: StockReservation) => {
    navigate(`/reservations/${reservation.id}`);
  };

  const confirmFulfill = () => {
    if (selectedReservation) {
      fulfillMutation.mutate(selectedReservation.id);
    }
  };

  const confirmCancel = () => {
    if (selectedReservation && cancelReason.trim()) {
      cancelMutation.mutate(selectedReservation.id);
    } else {
      notifications.show({
        title: 'Validation Error',
        message: 'Please provide a reason for cancellation',
        color: 'red',
      });
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'active': 'blue',
      'expired': 'orange',
      'fulfilled': 'green',
      'cancelled': 'red',
    };
    return colors[status] || 'gray';
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'quote': 'purple',
      'hold': 'blue',
      'inspection': 'yellow',
      'transfer_prep': 'cyan',
      'maintenance': 'orange',
      'other': 'gray',
    };
    return colors[type] || 'gray';
  };

  const columns: DataTableColumn<StockReservation>[] = useMemo(() => [
    {
      accessor: 'id',
      title: 'ID',
      width: 80,
      sortable: true,
    },
    {
      accessor: 'stock.item_name',
      title: 'Stock Item',
      width: 300,
      render: (reservation) => (
        <div>
          <Text size="sm" fw={600}>{reservation.stock.item_name}</Text>
          <Text size="xs" c="dimmed">{reservation.stock.sku}</Text>
        </div>
      ),
    },
    {
      accessor: 'customer_name',
      title: 'Customer',
      width: 200,
      render: (reservation) => (
        <div>
          <Text size="sm">{reservation.customer_name || 'No customer'}</Text>
          {reservation.customer_phone && (
            <Text size="xs" c="dimmed">{reservation.customer_phone}</Text>
          )}
        </div>
      ),
    },
    {
      accessor: 'quantity',
      title: 'Qty',
      width: 80,
      textAlign: 'center',
    },
    {
      accessor: 'reservation_type',
      title: 'Type',
      width: 120,
      render: (reservation) => (
        <Badge
          size="sm"
          color={getTypeColor(reservation.reservation_type)}
          variant="light"
        >
          {reservation.reservation_type_display}
        </Badge>
      ),
    },
    {
      accessor: 'status',
      title: 'Status',
      width: 120,
      render: (reservation) => (
        <Badge
          size="sm"
          color={getStatusColor(reservation.status)}
          variant="light"
        >
          {reservation.status_display}
        </Badge>
      ),
    },
    {
      accessor: 'expires_at',
      title: 'Expires',
      width: 150,
      render: (reservation) => (
        <Text size="sm">
          {reservation.expires_at ? new Date(reservation.expires_at).toLocaleString() : 'No expiry'}
        </Text>
      ),
    },
    {
      accessor: 'actions',
      title: 'Actions',
      width: 150,
      textAlign: 'center',
      render: (reservation) => (
        <Group gap="xs" justify="center">
          <Tooltip label="View Details">
            <ActionIcon
              size="sm"
              variant="light"
              onClick={() => handleView(reservation)}
            >
              <IconEye size="1rem" />
            </ActionIcon>
          </Tooltip>

          {reservation.status === 'active' && hasPermission('reservations.fulfill_stockreservation') && (
            <Tooltip label="Fulfill Reservation">
              <ActionIcon
                size="sm"
                variant="light"
                color="green"
                onClick={() => handleFulfill(reservation)}
              >
                <IconCheck size="1rem" />
              </ActionIcon>
            </Tooltip>
          )}

          {reservation.status === 'active' && hasPermission('reservations.change_stockreservation') && (
            <Tooltip label="Cancel Reservation">
              <ActionIcon
                size="sm"
                variant="light"
                color="red"
                onClick={() => handleCancel(reservation)}
              >
                <IconX size="1rem" />
              </ActionIcon>
            </Tooltip>
          )}
        </Group>
      ),
    },
  ], [hasPermission]);

  const clearFilters = () => {
    setSearchTerm('');
    setStatusFilter('');
    setTypeFilter('');
    setPage(1);
  };

  return (
    <Container fluid>
      <Stack gap="md">
        {/* Header */}
        <Group justify="space-between" align="center">
          <div>
            <Title order={1}>Stock Reservations</Title>
            <Text c="dimmed">Manage stock reservations and holds</Text>
          </div>
          <Group>
            <ActionIcon variant="light" onClick={() => refetch()}>
              <IconRefresh size="1rem" />
            </ActionIcon>
            {hasPermission('reservations.add_stockreservation') && (
              <Button
                leftSection={<IconPlus size="1rem" />}
                onClick={() => navigate('/reservations/create')}
              >
                New Reservation
              </Button>
            )}
          </Group>
        </Group>

        {/* Filters */}
        <Card shadow="sm" padding="md" radius="md" withBorder>
          <Group gap="md" mb="md">
            <TextInput
              placeholder="Search by customer or stock item..."
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.currentTarget.value)}
              leftSection={<IconSearch size="1rem" />}
              style={{ flex: 1 }}
            />

            <Select
              placeholder="Filter by status"
              value={statusFilter}
              onChange={(value) => setStatusFilter(value || '')}
              data={[
                { value: '', label: 'All Statuses' },
                { value: 'active', label: 'Active' },
                { value: 'expired', label: 'Expired' },
                { value: 'fulfilled', label: 'Fulfilled' },
                { value: 'cancelled', label: 'Cancelled' },
              ]}
              style={{ width: 150 }}
            />

            <Select
              placeholder="Filter by type"
              value={typeFilter}
              onChange={(value) => setTypeFilter(value || '')}
              data={[
                { value: '', label: 'All Types' },
                { value: 'quote', label: 'Quote' },
                { value: 'hold', label: 'Hold' },
                { value: 'inspection', label: 'Inspection' },
                { value: 'transfer_prep', label: 'Transfer Prep' },
                { value: 'maintenance', label: 'Maintenance' },
                { value: 'other', label: 'Other' },
              ]}
              style={{ width: 150 }}
            />

            <Button variant="light" onClick={clearFilters}>
              Clear Filters
            </Button>
          </Group>
        </Card>

        {/* Error handling */}
        {isError && (
          <Alert
            icon={<IconAlertCircle size="1rem" />}
            title="Error loading reservations"
            color="red"
            variant="light"
          >
            {(error as any)?.response?.data?.detail || 'An unexpected error occurred. Please try again.'}
          </Alert>
        )}

        {/* Reservations Table */}
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Box pos="relative">
            <LoadingOverlay visible={isLoading} />
            <DataTable
              records={reservations}
              columns={columns}
              totalRecords={totalCount}
              recordsPerPage={pageSize}
              page={page}
              onPageChange={setPage}
              recordsPerPageOptions={[10, 25, 50, 100]}
              onRecordsPerPageChange={setPageSize}
              paginationActiveBackgroundColor="blue"
              noRecordsText="No reservations found"
              minHeight={400}
              fetching={isLoading}
              sortStatus={undefined}
            />
          </Box>
        </Card>

        {/* Summary */}
        <Group justify="space-between" align="center">
          <Text c="dimmed" size="sm">
            Showing {Math.min((page - 1) * pageSize + 1, totalCount)} to{' '}
            {Math.min(page * pageSize, totalCount)} of {totalCount} reservations
          </Text>
        </Group>
      </Stack>

      {/* Fulfill Reservation Modal */}
      <Modal
        opened={fulfillOpened}
        onClose={closeFulfill}
        title="Fulfill Reservation"
        centered
      >
        <Stack gap="md">
          <Alert
            icon={<IconReservedLine size="1rem" />}
            title="Confirm Fulfillment"
            color="blue"
          >
            Are you sure you want to fulfill this reservation? This action will:
            <ul>
              <li>Mark the reservation as fulfilled</li>
              <li>Remove the reserved stock from available inventory</li>
              <li>Cannot be undone</li>
            </ul>
          </Alert>

          {selectedReservation && (
            <Box p="md" bg="gray.0" style={{ borderRadius: '8px' }}>
              <Text fw={600}>{selectedReservation.stock.item_name}</Text>
              <Text size="sm" c="dimmed">
                Customer: {selectedReservation.customer_name} • Quantity: {selectedReservation.quantity}
              </Text>
            </Box>
          )}

          <Group justify="right">
            <Button variant="light" onClick={closeFulfill}>
              Cancel
            </Button>
            <Button
              color="green"
              onClick={confirmFulfill}
              loading={fulfillMutation.isPending}
            >
              Fulfill Reservation
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Cancel Reservation Modal */}
      <Modal
        opened={cancelOpened}
        onClose={closeCancel}
        title="Cancel Reservation"
        centered
      >
        <Stack gap="md">
          <Alert
            icon={<IconX size="1rem" />}
            title="Cancel Reservation"
            color="red"
          >
            Please provide a reason for cancelling this reservation.
          </Alert>

          {selectedReservation && (
            <Box p="md" bg="gray.0" style={{ borderRadius: '8px' }}>
              <Text fw={600}>{selectedReservation.stock.item_name}</Text>
              <Text size="sm" c="dimmed">
                Customer: {selectedReservation.customer_name} • Quantity: {selectedReservation.quantity}
              </Text>
            </Box>
          )}

          <TextInput
            label="Cancellation Reason"
            value={cancelReason}
            onChange={(event) => setCancelReason(event.currentTarget.value)}
            placeholder="Enter reason for cancellation..."
            required
          />

          <Group justify="right">
            <Button variant="light" onClick={closeCancel}>
              Cancel
            </Button>
            <Button
              color="red"
              onClick={confirmCancel}
              loading={cancelMutation.isPending}
              disabled={!cancelReason.trim()}
            >
              Cancel Reservation
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Container>
  );
};

export default ReservationsList;