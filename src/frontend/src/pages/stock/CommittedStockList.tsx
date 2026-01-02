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
  TextInput,
  Alert,
  LoadingOverlay,
  Box,
  Tooltip,
  NumberFormatter
} from '@mantine/core';
import {
  IconRefresh,
  IconEye,
  IconCheck,
  IconAlertCircle,
  IconSearch,
  IconShoppingCart,
  IconPackage,
  IconUser,
  IconCurrencyDollar
} from '@tabler/icons-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DataTable, type DataTableColumn } from 'mantine-datatable';
import { useNavigate } from 'react-router-dom';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';

import { stockAPI } from '@/api/stock';
import { useHasPermission } from '@/states/authState';
import type { CommittedStock, PaginatedResponse } from '@/types/stock';

const CommittedStockList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const hasPermission = useHasPermission();

  // State for filtering and pagination
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [searchTerm, setSearchTerm] = useState('');

  // Modal states
  const [selectedCommitment, setSelectedCommitment] = useState<CommittedStock | null>(null);
  const [fulfillOpened, { open: openFulfill, close: closeFulfill }] = useDisclosure(false);

  // Fetch committed stock
  const {
    data: committedData,
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['committed-stock', page, pageSize, searchTerm],
    queryFn: () => stockAPI.getCommittedStock({
      page,
      page_size: pageSize,
      search: searchTerm || undefined,
    }),
    staleTime: 30000,
  });

  const commitments = committedData?.results || [];
  const totalCount = committedData?.count || 0;

  // Mutation for fulfilling commitment
  const fulfillMutation = useMutation({
    mutationFn: (id: number) => stockAPI.fulfillCommitment(id),
    onSuccess: () => {
      notifications.show({
        title: 'Commitment Fulfilled',
        message: 'Stock commitment has been fulfilled successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['committed-stock'] });
      closeFulfill();
      setSelectedCommitment(null);
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to fulfill commitment',
        color: 'red',
      });
    },
  });

  const handleFulfill = (commitment: CommittedStock) => {
    setSelectedCommitment(commitment);
    openFulfill();
  };

  const confirmFulfill = () => {
    if (selectedCommitment) {
      fulfillMutation.mutate(selectedCommitment.id);
    }
  };

  const columns: DataTableColumn<CommittedStock>[] = useMemo(() => [
    {
      accessor: 'id',
      title: 'ID',
      width: 80,
      sortable: true,
    },
    {
      accessor: 'stock.item_name',
      title: 'Stock Item',
      width: 250,
      render: (commitment) => (
        <div>
          <Text size="sm" fw={600}>{commitment.stock.item_name}</Text>
          {commitment.stock.sku && (
            <Text size="xs" c="dimmed">SKU: {commitment.stock.sku}</Text>
          )}
        </div>
      ),
    },
    {
      accessor: 'customer_order_number',
      title: 'Order #',
      width: 120,
      render: (commitment) => (
        <Badge size="sm" variant="light" color="blue">
          {commitment.customer_order_number}
        </Badge>
      ),
    },
    {
      accessor: 'customer_name',
      title: 'Customer',
      width: 180,
      render: (commitment) => (
        <div>
          <Group gap="xs">
            <IconUser size="0.9rem" />
            <Text size="sm" fw={500}>{commitment.customer_name}</Text>
          </Group>
          {commitment.customer_phone && (
            <Text size="xs" c="dimmed">{commitment.customer_phone}</Text>
          )}
        </div>
      ),
    },
    {
      accessor: 'quantity',
      title: 'Qty',
      width: 80,
      textAlign: 'center',
      render: (commitment) => (
        <Badge size="sm" variant="light" color="orange">
          {commitment.quantity}
        </Badge>
      ),
    },
    {
      accessor: 'deposit_amount',
      title: 'Deposit',
      width: 120,
      textAlign: 'right',
      render: (commitment) => (
        <Group gap="xs" justify="flex-end">
          <IconCurrencyDollar size="0.9rem" />
          <NumberFormatter
            value={commitment.deposit_amount}
            prefix="$"
            thousandSeparator
            decimalScale={2}
            fixedDecimalScale
          />
        </Group>
      ),
    },
    {
      accessor: 'committed_at',
      title: 'Committed',
      width: 120,
      render: (commitment) => (
        <Text size="sm">
          {new Date(commitment.committed_at).toLocaleDateString()}
        </Text>
      ),
    },
    {
      accessor: 'is_fulfilled',
      title: 'Status',
      width: 120,
      render: (commitment) => (
        <Badge
          size="sm"
          color={commitment.is_fulfilled ? 'green' : 'orange'}
          variant="light"
        >
          {commitment.is_fulfilled ? 'Fulfilled' : 'Pending'}
        </Badge>
      ),
    },
    {
      accessor: 'fulfilled_at',
      title: 'Fulfilled',
      width: 120,
      render: (commitment) => (
        <Text size="sm">
          {commitment.fulfilled_at
            ? new Date(commitment.fulfilled_at).toLocaleDateString()
            : '-'}
        </Text>
      ),
    },
    {
      accessor: 'actions',
      title: 'Actions',
      width: 120,
      textAlign: 'center',
      render: (commitment) => (
        <Group gap="xs" justify="center">
          <Tooltip label="View Stock Details">
            <ActionIcon
              size="sm"
              variant="light"
              onClick={() => navigate(`/stock/${commitment.stock.id}`)}
            >
              <IconEye size="1rem" />
            </ActionIcon>
          </Tooltip>

          {!commitment.is_fulfilled && (
            <Tooltip label="Fulfill Commitment">
              <ActionIcon
                size="sm"
                variant="light"
                color="green"
                onClick={() => handleFulfill(commitment)}
              >
                <IconCheck size="1rem" />
              </ActionIcon>
            </Tooltip>
          )}
        </Group>
      ),
    },
  ], []);

  const clearFilters = () => {
    setSearchTerm('');
    setPage(1);
  };

  return (
    <Container fluid>
      <Stack gap="md">
        {/* Header */}
        <Group justify="space-between" align="center">
          <div>
            <Title order={1}>Committed Stock</Title>
            <Text c="dimmed">Manage stock commitments with customer deposits</Text>
          </div>
          <Group>
            <ActionIcon variant="light" onClick={() => refetch()}>
              <IconRefresh size="1rem" />
            </ActionIcon>
          </Group>
        </Group>

        {/* Filters */}
        <Card shadow="sm" padding="md" radius="md" withBorder>
          <Group gap="md" mb="md">
            <TextInput
              placeholder="Search by stock item, customer, or order number..."
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.currentTarget.value)}
              leftSection={<IconSearch size="1rem" />}
              style={{ flex: 1 }}
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
            title="Error loading committed stock"
            color="red"
            variant="light"
          >
            {(error as any)?.response?.data?.detail || 'An unexpected error occurred. Please try again.'}
          </Alert>
        )}

        {/* Committed Stock Table */}
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Box pos="relative">
            <LoadingOverlay visible={isLoading} />
            <DataTable
              records={commitments}
              columns={columns}
              totalRecords={totalCount}
              recordsPerPage={pageSize}
              page={page}
              onPageChange={setPage}
              recordsPerPageOptions={[10, 25, 50, 100]}
              onRecordsPerPageChange={setPageSize}
              paginationActiveBackgroundColor="blue"
              noRecordsText="No committed stock found"
              minHeight={400}
              fetching={isLoading}
            />
          </Box>
        </Card>

        {/* Summary */}
        <Group justify="space-between" align="center">
          <Text c="dimmed" size="sm">
            Showing {Math.min((page - 1) * pageSize + 1, totalCount)} to{' '}
            {Math.min(page * pageSize, totalCount)} of {totalCount} commitments
          </Text>
        </Group>
      </Stack>

      {/* Fulfill Commitment Modal */}
      <Modal
        opened={fulfillOpened}
        onClose={closeFulfill}
        title="Fulfill Commitment"
        centered
      >
        <Stack gap="md">
          <Alert
            icon={<IconCheck size="1rem" />}
            title="Fulfill Commitment"
            color="green"
          >
            Are you sure you want to fulfill this commitment? This will release the committed stock and mark the order as complete.
          </Alert>

          {selectedCommitment && (
            <Box p="md" bg="gray.0" style={{ borderRadius: '8px' }}>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c="dimmed">Stock Item:</Text>
                  <Text size="sm" fw={600}>{selectedCommitment.stock.item_name}</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="dimmed">Order #:</Text>
                  <Badge size="sm" variant="light" color="blue">
                    {selectedCommitment.customer_order_number}
                  </Badge>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="dimmed">Customer:</Text>
                  <Text size="sm" fw={500}>{selectedCommitment.customer_name}</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="dimmed">Quantity:</Text>
                  <Text size="sm" fw={500}>{selectedCommitment.quantity}</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="dimmed">Deposit:</Text>
                  <Text size="sm" fw={600} c="green">
                    <NumberFormatter
                      value={selectedCommitment.deposit_amount}
                      prefix="$"
                      thousandSeparator
                      decimalScale={2}
                      fixedDecimalScale
                    />
                  </Text>
                </Group>
              </Stack>
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
              Fulfill Commitment
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Container>
  );
};

export default CommittedStockList;
