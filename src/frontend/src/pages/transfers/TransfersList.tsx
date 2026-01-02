// @ts-nocheck
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
  IconCheck,
  IconTruck,
  IconX,
  IconAlertCircle,
  IconArrowRight,
  IconSearch,
  IconPackage
} from '@tabler/icons-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DataTable, type DataTableColumn } from 'mantine-datatable';
import { useNavigate } from 'react-router-dom';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';

import { stockAPI } from '@/api/stock';
import { useHasPermission } from '@/states/authState';
import type { StockTransfer, PaginatedResponse } from '@/types/stock';

const TransfersList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const hasPermission = useHasPermission();

  // State for filtering and pagination
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  // Modal states
  const [selectedTransfer, setSelectedTransfer] = useState<StockTransfer | null>(null);
  const [approveOpened, { open: openApprove, close: closeApprove }] = useDisclosure(false);
  const [completeOpened, { open: openComplete, close: closeComplete }] = useDisclosure(false);
  const [collectOpened, { open: openCollect, close: closeCollect }] = useDisclosure(false);

  // Fetch transfers
  const {
    data: transfersData,
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['transfers', page, pageSize, searchTerm, statusFilter],
    queryFn: () => stockAPI.getTransfers({
      page,
      page_size: pageSize,
      search: searchTerm || undefined,
      status: statusFilter || undefined,
    }),
    staleTime: 30000,
  });

  const transfers = transfersData?.results || [];
  const totalCount = transfersData?.count || 0;

  // Mutations for transfer operations
  const approveMutation = useMutation({
    mutationFn: (id: number) => stockAPI.approveTransfer(id),
    onSuccess: () => {
      notifications.show({
        title: 'Transfer Approved',
        message: 'Transfer has been approved successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['transfers'] });
      closeApprove();
      setSelectedTransfer(null);
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to approve transfer',
        color: 'red',
      });
    },
  });

  const completeMutation = useMutation({
    mutationFn: (id: number) => stockAPI.completeTransfer(id),
    onSuccess: () => {
      notifications.show({
        title: 'Transfer Completed',
        message: 'Transfer has been completed successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['transfers'] });
      closeComplete();
      setSelectedTransfer(null);
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to complete transfer',
        color: 'red',
      });
    },
  });

  const collectMutation = useMutation({
    mutationFn: (id: number) => stockAPI.collectTransfer(id),
    onSuccess: () => {
      notifications.show({
        title: 'Transfer Collected',
        message: 'Transfer has been marked as collected',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['transfers'] });
      closeCollect();
      setSelectedTransfer(null);
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to mark transfer as collected',
        color: 'red',
      });
    },
  });

  const handleApprove = (transfer: StockTransfer) => {
    setSelectedTransfer(transfer);
    openApprove();
  };

  const handleComplete = (transfer: StockTransfer) => {
    setSelectedTransfer(transfer);
    openComplete();
  };

  const handleCollect = (transfer: StockTransfer) => {
    setSelectedTransfer(transfer);
    openCollect();
  };

  const handleView = (transfer: StockTransfer) => {
    navigate(`/transfers/${transfer.id}`);
  };

  const confirmApprove = () => {
    if (selectedTransfer) {
      approveMutation.mutate(selectedTransfer.id);
    }
  };

  const confirmComplete = () => {
    if (selectedTransfer) {
      completeMutation.mutate(selectedTransfer.id);
    }
  };

  const confirmCollect = () => {
    if (selectedTransfer) {
      collectMutation.mutate(selectedTransfer.id);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'pending': 'yellow',
      'approved': 'blue',
      'in_transit': 'cyan',
      'awaiting_collection': 'orange',
      'completed': 'green',
      'cancelled': 'red',
    };
    return colors[status] || 'gray';
  };

  const columns: DataTableColumn<StockTransfer>[] = useMemo(() => [
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
      render: (transfer) => (
        <div>
          <Text size="sm" fw={600}>{transfer.stock.item_name}</Text>
          <Text size="xs" c="dimmed">{transfer.stock.sku}</Text>
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
      accessor: 'from_location',
      title: 'From',
      width: 150,
      render: (transfer) => (
        <Text size="sm">{transfer.from_location?.name || 'Unknown'}</Text>
      ),
    },
    {
      accessor: 'to_location',
      title: 'To',
      width: 150,
      render: (transfer) => (
        <Text size="sm">{transfer.to_location?.name || 'Unknown'}</Text>
      ),
    },
    {
      accessor: 'status',
      title: 'Status',
      width: 140,
      render: (transfer) => (
        <Badge
          size="sm"
          color={getStatusColor(transfer.status)}
          variant="light"
        >
          {transfer.status_display}
        </Badge>
      ),
    },
    {
      accessor: 'created_by',
      title: 'Requested By',
      width: 150,
      render: (transfer) => (
        <Text size="sm">{transfer.created_by?.username || 'Unknown'}</Text>
      ),
    },
    {
      accessor: 'created_at',
      title: 'Created',
      width: 120,
      render: (transfer) => (
        <Text size="sm">
          {new Date(transfer.created_at).toLocaleDateString()}
        </Text>
      ),
    },
    {
      accessor: 'actions',
      title: 'Actions',
      width: 180,
      textAlign: 'center',
      render: (transfer) => (
        <Group gap="xs" justify="center">
          <Tooltip label="View Details">
            <ActionIcon
              size="sm"
              variant="light"
              onClick={() => handleView(transfer)}
            >
              <IconEye size="1rem" />
            </ActionIcon>
          </Tooltip>

          {transfer.status === 'pending' && (
            <Tooltip label="Approve Transfer">
              <ActionIcon
                size="sm"
                variant="light"
                color="green"
                onClick={() => handleApprove(transfer)}
              >
                <IconCheck size="1rem" />
              </ActionIcon>
            </Tooltip>
          )}

          {transfer.status === 'approved' && (
            <Tooltip label="Mark as Dispatched">
              <ActionIcon
                size="sm"
                variant="light"
                color="blue"
                onClick={() => handleComplete(transfer)}
              >
                <IconTruck size="1rem" />
              </ActionIcon>
            </Tooltip>
          )}

          {transfer.status === 'awaiting_collection' && (
            <Tooltip label="Mark as Collected">
              <ActionIcon
                size="sm"
                variant="light"
                color="orange"
                onClick={() => handleCollect(transfer)}
              >
                <IconPackage size="1rem" />
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
    setPage(1);
  };

  return (
    <Container fluid>
      <Stack gap="md">
        {/* Header */}
        <Group justify="space-between" align="center">
          <div>
            <Title order={1}>Stock Transfers</Title>
            <Text c="dimmed">Manage stock transfers between locations</Text>
          </div>
          <Group>
            <ActionIcon variant="light" onClick={() => refetch()}>
              <IconRefresh size="1rem" />
            </ActionIcon>
            {hasPermission('transfers.add_stocktransfer') && (
              <Button
                leftSection={<IconPlus size="1rem" />}
                onClick={() => navigate('/transfers/create')}
              >
                New Transfer
              </Button>
            )}
          </Group>
        </Group>

        {/* Filters */}
        <Card shadow="sm" padding="md" radius="md" withBorder>
          <Group gap="md" mb="md">
            <TextInput
              placeholder="Search by stock item or location..."
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
                { value: 'pending', label: 'Pending' },
                { value: 'approved', label: 'Approved' },
                { value: 'in_transit', label: 'In Transit' },
                { value: 'awaiting_collection', label: 'Awaiting Collection' },
                { value: 'completed', label: 'Completed' },
                { value: 'cancelled', label: 'Cancelled' },
              ]}
              style={{ width: 180 }}
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
            title="Error loading transfers"
            color="red"
            variant="light"
          >
            {(error as any)?.response?.data?.detail || 'An unexpected error occurred. Please try again.'}
          </Alert>
        )}

        {/* Transfers Table */}
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Box pos="relative">
            <LoadingOverlay visible={isLoading} />
            <DataTable
              records={transfers}
              columns={columns}
              totalRecords={totalCount}
              recordsPerPage={pageSize}
              page={page}
              onPageChange={setPage}
              recordsPerPageOptions={[10, 25, 50, 100]}
              onRecordsPerPageChange={setPageSize}
              paginationActiveBackgroundColor="blue"
              noRecordsText="No transfers found"
              minHeight={400}
              fetching={isLoading}
            />
          </Box>
        </Card>

        {/* Summary */}
        <Group justify="space-between" align="center">
          <Text c="dimmed" size="sm">
            Showing {Math.min((page - 1) * pageSize + 1, totalCount)} to{' '}
            {Math.min(page * pageSize, totalCount)} of {totalCount} transfers
          </Text>
        </Group>
      </Stack>

      {/* Approve Transfer Modal */}
      <Modal
        opened={approveOpened}
        onClose={closeApprove}
        title="Approve Transfer"
        centered
      >
        <Stack gap="md">
          <Alert
            icon={<IconCheck size="1rem" />}
            title="Approve Transfer"
            color="green"
          >
            Are you sure you want to approve this transfer? The transfer will be marked as approved and ready for dispatch.
          </Alert>

          {selectedTransfer && (
            <Box p="md" bg="gray.0" style={{ borderRadius: '8px' }}>
              <Text fw={600}>{selectedTransfer.stock.item_name}</Text>
              <Text size="sm" c="dimmed">
                From: {selectedTransfer.from_location?.name} → To: {selectedTransfer.to_location?.name}
              </Text>
              <Text size="sm" c="dimmed">Quantity: {selectedTransfer.quantity}</Text>
            </Box>
          )}

          <Group justify="right">
            <Button variant="light" onClick={closeApprove}>
              Cancel
            </Button>
            <Button
              color="green"
              onClick={confirmApprove}
              loading={approveMutation.isPending}
            >
              Approve Transfer
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Complete Transfer Modal */}
      <Modal
        opened={completeOpened}
        onClose={closeComplete}
        title="Mark Transfer as Dispatched"
        centered
      >
        <Stack gap="md">
          <Alert
            icon={<IconTruck size="1rem" />}
            title="Mark as Dispatched"
            color="blue"
          >
            Mark this transfer as dispatched. The stock will be in transit to the destination.
          </Alert>

          {selectedTransfer && (
            <Box p="md" bg="gray.0" style={{ borderRadius: '8px' }}>
              <Text fw={600}>{selectedTransfer.stock.item_name}</Text>
              <Text size="sm" c="dimmed">
                From: {selectedTransfer.from_location?.name} → To: {selectedTransfer.to_location?.name}
              </Text>
              <Text size="sm" c="dimmed">Quantity: {selectedTransfer.quantity}</Text>
            </Box>
          )}

          <Group justify="right">
            <Button variant="light" onClick={closeComplete}>
              Cancel
            </Button>
            <Button
              color="blue"
              onClick={confirmComplete}
              loading={completeMutation.isPending}
            >
              Mark as Dispatched
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Collect Transfer Modal */}
      <Modal
        opened={collectOpened}
        onClose={closeCollect}
        title="Mark Transfer as Collected"
        centered
      >
        <Stack gap="md">
          <Alert
            icon={<IconPackage size="1rem" />}
            title="Mark as Collected"
            color="orange"
          >
            Confirm that this transfer has been collected at the destination. This will complete the transfer process.
          </Alert>

          {selectedTransfer && (
            <Box p="md" bg="gray.0" style={{ borderRadius: '8px' }}>
              <Text fw={600}>{selectedTransfer.stock.item_name}</Text>
              <Text size="sm" c="dimmed">
                From: {selectedTransfer.from_location?.name} → To: {selectedTransfer.to_location?.name}
              </Text>
              <Text size="sm" c="dimmed">Quantity: {selectedTransfer.quantity}</Text>
            </Box>
          )}

          <Group justify="right">
            <Button variant="light" onClick={closeCollect}>
              Cancel
            </Button>
            <Button
              color="orange"
              onClick={confirmCollect}
              loading={collectMutation.isPending}
            >
              Mark as Collected
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Container>
  );
};

export default TransfersList;