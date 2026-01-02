import React from 'react';
import {
  Container,
  Grid,
  Card,
  Text,
  Title,
  Group,
  Badge,
  Stack,
  Button,
  ActionIcon,
  Tooltip,
  Image,
  Divider,
  Box,
  LoadingOverlay,
  Alert,
  NumberInput,
  Modal,
  TextInput,
  Textarea,
  Select,
  Table,
  Pagination
} from '@mantine/core';
import {
  IconEdit,
  IconTrash,
  IconShoppingCart,
  IconPackage,
  IconArrowLeft,
  IconPlus,
  IconMinus,
  IconAlertCircle,
  IconMapPin,
  IconReservedLine,
  IconLock,
  IconHistory,
  IconRefresh,
  IconArrowsExchange
} from '@tabler/icons-react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useDisclosure } from '@mantine/hooks';
import { useState } from 'react';
import { notifications } from '@mantine/notifications';

import { stockAPI } from '@/api/stock';
import { useHasPermission } from '@/states/authState';
import type { Stock, StockHistory, StockReservation, CommittedStock } from '@/types/stock';

const StockDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const hasPermission = useHasPermission();

  // Modal states
  const [issueOpened, { open: openIssue, close: closeIssue }] = useDisclosure(false);
  const [receiveOpened, { open: openReceive, close: closeReceive }] = useDisclosure(false);
  const [reserveOpened, { open: openReserve, close: closeReserve }] = useDisclosure(false);
  const [commitOpened, { open: openCommit, close: closeCommit }] = useDisclosure(false);

  // Form states
  const [issueQuantity, setIssueQuantity] = useState<number>(1);
  const [receiveQuantity, setReceiveQuantity] = useState<number>(1);
  const [issueNote, setIssueNote] = useState('');
  const [receiveNote, setReceiveNote] = useState('');
  const [receiveAisle, setReceiveAisle] = useState('');

  // Reserve form states
  const [reserveQuantity, setReserveQuantity] = useState<number>(1);
  const [reservationType, setReservationType] = useState<string>('hold');
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [reserveReason, setReserveReason] = useState('');
  const [expiresAt, setExpiresAt] = useState('');

  // Commit form states
  const [commitQuantity, setCommitQuantity] = useState<number>(1);
  const [orderNumber, setOrderNumber] = useState('');
  const [depositAmount, setDepositAmount] = useState<number>(0);
  const [commitCustomerName, setCommitCustomerName] = useState('');
  const [commitCustomerPhone, setCommitCustomerPhone] = useState('');
  const [commitCustomerEmail, setCommitCustomerEmail] = useState('');
  const [commitNotes, setCommitNotes] = useState('');

  // History pagination
  const [historyPage, setHistoryPage] = useState(1);

  // Fetch stock data
  const {
    data: stock,
    isLoading,
    isError,
    error
  } = useQuery({
    queryKey: ['stock', Number(id)],
    queryFn: () => stockAPI.getStock(Number(id)),
    enabled: !!id,
    staleTime: 30000,
  });

  // Fetch stock history
  const {
    data: stockHistory,
    isLoading: historyLoading,
  } = useQuery({
    queryKey: ['stock-history', Number(id)],
    queryFn: () => stockAPI.getStockHistory(Number(id)),
    enabled: !!id,
    staleTime: 30000,
  });

  // Fetch stock reservations for this item
  const {
    data: reservationsData,
    isLoading: reservationsLoading,
  } = useQuery({
    queryKey: ['reservations', Number(id)],
    queryFn: () => stockAPI.getReservations({ stock: Number(id) }),
    enabled: !!id,
    staleTime: 30000,
  });

  // Fetch committed stock for this item
  const {
    data: commitmentData,
    isLoading: commitmentLoading,
  } = useQuery({
    queryKey: ['committed-stock', Number(id)],
    queryFn: () => stockAPI.getCommittedStock({ stock: Number(id) }),
    enabled: !!id,
    staleTime: 30000,
  });

  // Issue stock mutation
  const issueMutation = useMutation({
    mutationFn: (data: { quantity: number; note?: string }) =>
      stockAPI.issueStock(Number(id), data),
    onSuccess: () => {
      notifications.show({
        title: 'Stock Issued',
        message: 'Stock has been issued successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stock', Number(id)] });
      queryClient.invalidateQueries({ queryKey: ['stock-history', Number(id)] });
      closeIssue();
      setIssueQuantity(1);
      setIssueNote('');
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to issue stock',
        color: 'red',
      });
    },
  });

  // Receive stock mutation
  const receiveMutation = useMutation({
    mutationFn: (data: { quantity: number; note?: string; aisle?: string }) =>
      stockAPI.receiveStock(Number(id), data),
    onSuccess: () => {
      notifications.show({
        title: 'Stock Received',
        message: 'Stock has been received successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stock', Number(id)] });
      queryClient.invalidateQueries({ queryKey: ['stock-history', Number(id)] });
      closeReceive();
      setReceiveQuantity(1);
      setReceiveNote('');
      setReceiveAisle('');
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to receive stock',
        color: 'red',
      });
    },
  });

  // Reserve stock mutation
  const reserveMutation = useMutation({
    mutationFn: (data: {
      stock_id: number;
      quantity: number;
      reservation_type: string;
      customer_name?: string;
      customer_phone?: string;
      customer_email?: string;
      reason: string;
      expires_at: string;
    }) => stockAPI.reserveStock(Number(id), data),
    onSuccess: () => {
      notifications.show({
        title: 'Stock Reserved',
        message: 'Stock has been reserved successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stock', Number(id)] });
      queryClient.invalidateQueries({ queryKey: ['reservations', Number(id)] });
      closeReserve();
      resetReserveForm();
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to reserve stock',
        color: 'red',
      });
    },
  });

  // Commit stock mutation
  const commitMutation = useMutation({
    mutationFn: (data: {
      stock_id: number;
      quantity: number;
      customer_order_number: string;
      deposit_amount: number;
      customer_name: string;
      customer_phone?: string;
      customer_email?: string;
      notes?: string;
    }) => stockAPI.commitStock(Number(id), data),
    onSuccess: () => {
      notifications.show({
        title: 'Stock Committed',
        message: 'Stock has been committed successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stock', Number(id)] });
      queryClient.invalidateQueries({ queryKey: ['committed-stock', Number(id)] });
      closeCommit();
      resetCommitForm();
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to commit stock',
        color: 'red',
      });
    },
  });

  const handleEdit = () => {
    if (!hasPermission('stock.change_stock')) {
      notifications.show({
        title: 'Permission denied',
        message: 'You do not have permission to edit stock items',
        color: 'red',
      });
      return;
    }
    navigate(`/stock/${id}/edit`);
  };

  const handleIssueStock = () => {
    issueMutation.mutate({
      quantity: issueQuantity,
      note: issueNote || undefined,
    });
  };

  const handleReceiveStock = () => {
    receiveMutation.mutate({
      quantity: receiveQuantity,
      note: receiveNote || undefined,
      aisle: receiveAisle || undefined,
    });
  };

  const handleReserveStock = () => {
    if (!customerName.trim() || !expiresAt) {
      notifications.show({
        title: 'Validation Error',
        message: 'Customer name and expiration date are required',
        color: 'red',
      });
      return;
    }

    reserveMutation.mutate({
      stock_id: Number(id),
      quantity: reserveQuantity,
      reservation_type: reservationType,
      customer_name: customerName.trim(),
      customer_phone: customerPhone.trim() || undefined,
      customer_email: customerEmail.trim() || undefined,
      reason: reserveReason.trim(),
      expires_at: expiresAt,
    });
  };

  const handleCommitStock = () => {
    if (!orderNumber.trim() || !commitCustomerName.trim()) {
      notifications.show({
        title: 'Validation Error',
        message: 'Order number and customer name are required',
        color: 'red',
      });
      return;
    }

    commitMutation.mutate({
      stock_id: Number(id),
      quantity: commitQuantity,
      customer_order_number: orderNumber.trim(),
      deposit_amount: depositAmount,
      customer_name: commitCustomerName.trim(),
      customer_phone: commitCustomerPhone.trim() || undefined,
      customer_email: commitCustomerEmail.trim() || undefined,
      notes: commitNotes.trim() || undefined,
    });
  };

  const resetReserveForm = () => {
    setReserveQuantity(1);
    setReservationType('hold');
    setCustomerName('');
    setCustomerPhone('');
    setCustomerEmail('');
    setReserveReason('');
    setExpiresAt('');
  };

  const resetCommitForm = () => {
    setCommitQuantity(1);
    setOrderNumber('');
    setDepositAmount(0);
    setCommitCustomerName('');
    setCommitCustomerPhone('');
    setCommitCustomerEmail('');
    setCommitNotes('');
  };

  const getConditionColor = (condition: string) => {
    const colors: Record<string, string> = {
      'new': 'green',
      'demo_unit': 'blue',
      'bstock': 'orange',
      'open_box': 'yellow',
      'refurbished': 'violet',
    };
    return colors[condition] || 'gray';
  };

  const getStockStatusColor = (stock: Stock) => {
    if (stock.quantity === 0) return 'red';
    if (stock.is_low_stock) return 'orange';
    return 'green';
  };

  if (isLoading) {
    return (
      <Container fluid>
        <LoadingOverlay visible />
      </Container>
    );
  }

  if (isError || !stock) {
    return (
      <Container fluid>
        <Alert
          icon={<IconAlertCircle size="1rem" />}
          title="Error loading stock item"
          color="red"
          variant="light"
        >
          {(error as any)?.response?.data?.detail || 'Stock item not found'}
        </Alert>
      </Container>
    );
  }

  return (
    <Container fluid>
      <Stack gap="md">
        {/* Header */}
        <Group justify="space-between" align="center">
          <Group>
            <ActionIcon
              variant="light"
              onClick={() => navigate('/stock')}
            >
              <IconArrowLeft size="1.2rem" />
            </ActionIcon>
            <div>
              <Title order={1}>{stock.item_name}</Title>
              <Text c="dimmed" size="sm">SKU: {stock.sku}</Text>
            </div>
          </Group>

          <Group gap="sm">
            {hasPermission('stock.receive_stock') && (
              <Button
                leftSection={<IconPlus size="1rem" />}
                variant="light"
                color="green"
                onClick={openReceive}
              >
                Receive
              </Button>
            )}

            {hasPermission('stock.issue_stock') && (
              <Button
                leftSection={<IconMinus size="1rem" />}
                variant="light"
                color="orange"
                onClick={openIssue}
                disabled={stock.available_for_sale === 0}
              >
                Issue
              </Button>
            )}

            {hasPermission('stock.transfer_stock') && (
              <Button
                leftSection={<IconReservedLine size="1rem" />}
                variant="light"
                color="blue"
                onClick={openReserve}
                disabled={stock.available_for_sale === 0}
              >
                Reserve
              </Button>
            )}

            {hasPermission('stock.commit_stock') && (
              <Button
                leftSection={<IconLock size="1rem" />}
                variant="light"
                color="purple"
                onClick={openCommit}
                disabled={stock.available_for_sale === 0}
              >
                Commit
              </Button>
            )}

            {hasPermission('stock.transfer_stock') && (
              <Button
                leftSection={<IconArrowsExchange size="1rem" />}
                variant="light"
                color="teal"
                onClick={() => navigate(`/transfers/create?stock_id=${id}`)}
                disabled={stock.available_for_sale === 0}
              >
                Transfer
              </Button>
            )}

            <ActionIcon
              variant="light"
              onClick={() => {
                queryClient.invalidateQueries({ queryKey: ['stock', Number(id)] });
                queryClient.invalidateQueries({ queryKey: ['stock-history', Number(id)] });
                queryClient.invalidateQueries({ queryKey: ['reservations', Number(id)] });
                queryClient.invalidateQueries({ queryKey: ['committed-stock', Number(id)] });
              }}
            >
              <IconRefresh size="1rem" />
            </ActionIcon>

            {hasPermission('stock.change_stock') && (
              <Button
                leftSection={<IconEdit size="1rem" />}
                onClick={handleEdit}
              >
                Edit
              </Button>
            )}
          </Group>
        </Group>

        <Grid>
          {/* Left Column - Stock Details */}
          <Grid.Col span={{ base: 12, md: 8 }}>
            <Stack gap="md">
              {/* Stock Image and Basic Info */}
              <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Grid>
                  <Grid.Col span={{ base: 12, sm: 4 }}>
                    {stock.image_url ? (
                      <Image
                        src={stock.image_url}
                        alt={stock.item_name}
                        radius="md"
                        h={200}
                        fit="contain"
                      />
                    ) : (
                      <Box
                        h={200}
                        bg="gray.1"
                        display="flex"
                        style={{ alignItems: 'center', justifyContent: 'center' }}
                      >
                        <IconPackage size={48} color="gray" />
                      </Box>
                    )}
                  </Grid.Col>
                  <Grid.Col span={{ base: 12, sm: 8 }}>
                    <Stack gap="md">
                      <div>
                        <Title order={3}>{stock.item_name}</Title>
                        <Text size="sm" c="dimmed" mt="xs">
                          SKU: {stock.sku}
                        </Text>
                      </div>

                      <Group>
                        <Badge
                          color={getConditionColor(stock.condition)}
                          variant="light"
                        >
                          {stock.condition_display}
                        </Badge>
                        <Badge
                          color={getStockStatusColor(stock)}
                          variant="light"
                        >
                          {stock.quantity === 0 ? 'Out of Stock' :
                           stock.is_low_stock ? 'Low Stock' : 'In Stock'}
                        </Badge>
                        {stock.category && (
                          <Badge variant="outline">
                            {stock.category.group}
                          </Badge>
                        )}
                      </Group>

                      {stock.note && (
                        <div>
                          <Text size="sm" fw={600}>Notes:</Text>
                          <Text size="sm" c="dimmed">{stock.note}</Text>
                        </div>
                      )}
                    </Stack>
                  </Grid.Col>
                </Grid>
              </Card>

              {/* Active Reservations */}
              {reservationsData?.results && reservationsData.results.length > 0 && (
                <Card shadow="sm" padding="lg" radius="md" withBorder>
                  <Group mb="md">
                    <IconReservedLine size="1rem" />
                    <Title order={4}>Active Reservations</Title>
                  </Group>
                  <Stack gap="xs">
                    {reservationsData.results.map((reservation: StockReservation) => (
                      <Box key={reservation.id} p="xs" bg="blue.0" style={{ borderRadius: '4px' }}>
                        <Group justify="space-between">
                          <div>
                            <Text size="sm" fw={600}>
                              {reservation.customer_name || 'No customer'}
                            </Text>
                            <Text size="xs" c="dimmed">
                              {reservation.quantity} units • {reservation.reservation_type_display}
                            </Text>
                          </div>
                          <Badge color="blue" size="sm">
                            {reservation.status_display}
                          </Badge>
                        </Group>
                      </Box>
                    ))}
                  </Stack>
                </Card>
              )}

              {/* Committed Stock */}
              {commitmentData?.results && commitmentData.results.length > 0 && (
                <Card shadow="sm" padding="lg" radius="md" withBorder>
                  <Group mb="md">
                    <IconLock size="1rem" />
                    <Title order={4}>Committed Stock</Title>
                  </Group>
                  <Stack gap="xs">
                    {commitmentData.results.map((commitment: CommittedStock) => (
                      <Box key={commitment.id} p="xs" bg="purple.0" style={{ borderRadius: '4px' }}>
                        <Group justify="space-between">
                          <div>
                            <Text size="sm" fw={600}>
                              {commitment.customer_name}
                            </Text>
                            <Text size="xs" c="dimmed">
                              Order: {commitment.customer_order_number} • {commitment.quantity} units
                            </Text>
                            <Text size="xs" c="dimmed">
                              Deposit: ${commitment.deposit_amount}
                            </Text>
                          </div>
                          <Badge color={commitment.is_fulfilled ? 'green' : 'purple'} size="sm">
                            {commitment.is_fulfilled ? 'Fulfilled' : 'Pending'}
                          </Badge>
                        </Group>
                      </Box>
                    ))}
                  </Stack>
                </Card>
              )}

              {/* Stock History */}
              <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Group mb="md">
                  <IconHistory size="1rem" />
                  <Title order={4}>Stock History</Title>
                </Group>

                {historyLoading ? (
                  <Text c="dimmed" size="sm">Loading history...</Text>
                ) : stockHistory && stockHistory.length > 0 ? (
                  <Box>
                    <Table>
                      <Table.Thead>
                        <Table.Tr>
                          <Table.Th>Date</Table.Th>
                          <Table.Th>Action</Table.Th>
                          <Table.Th>Quantity</Table.Th>
                          <Table.Th>By</Table.Th>
                          <Table.Th>Notes</Table.Th>
                        </Table.Tr>
                      </Table.Thead>
                      <Table.Tbody>
                        {stockHistory
                          .slice((historyPage - 1) * 10, historyPage * 10)
                          .map((history: StockHistory) => (
                          <Table.Tr key={history.id}>
                            <Table.Td>
                              <Text size="xs">
                                {history.timestamp ? new Date(history.timestamp).toLocaleDateString() : 'N/A'}
                              </Text>
                            </Table.Td>
                            <Table.Td>
                              <Badge size="sm" color={
                                history.receive_quantity > 0 ? 'green' :
                                history.issue_quantity > 0 ? 'orange' : 'gray'
                              }>
                                {history.receive_quantity > 0 ? 'Receive' :
                                 history.issue_quantity > 0 ? 'Issue' : 'Update'}
                              </Badge>
                            </Table.Td>
                            <Table.Td>
                              <Text size="sm">
                                {history.receive_quantity > 0 ? `+${history.receive_quantity}` :
                                 history.issue_quantity > 0 ? `-${history.issue_quantity}` : history.quantity}
                              </Text>
                            </Table.Td>
                            <Table.Td>
                              <Text size="xs" c="dimmed">
                                {history.received_by || history.issued_by || history.created_by || 'System'}
                              </Text>
                            </Table.Td>
                            <Table.Td>
                              {history.note ? (
                                <Tooltip label={history.note} multiline w={300}>
                                  <Text size="xs" c="dimmed" style={{ maxWidth: '200px', cursor: 'help' }} truncate>
                                    {history.note}
                                  </Text>
                                </Tooltip>
                              ) : (
                                <Text size="xs" c="dimmed">—</Text>
                              )}
                            </Table.Td>
                          </Table.Tr>
                        ))}
                      </Table.Tbody>
                    </Table>
                    {stockHistory.length > 10 && (
                      <Group justify="center" mt="md">
                        <Pagination
                          total={Math.ceil(stockHistory.length / 10)}
                          value={historyPage}
                          onChange={setHistoryPage}
                          size="sm"
                        />
                      </Group>
                    )}
                  </Box>
                ) : (
                  <Text c="dimmed" size="sm">No history available</Text>
                )}
              </Card>
            </Stack>
          </Grid.Col>

          {/* Right Column - Stock Metrics */}
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Stack gap="md">
              {/* Quantity Information */}
              <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Title order={4} mb="md">Stock Levels</Title>
                <Stack gap="sm">
                  <Group justify="space-between">
                    <Text size="sm">Total Stock:</Text>
                    <Text size="sm" fw={600}>{stock.total_stock}</Text>
                  </Group>
                  <Group justify="space-between">
                    <Text size="sm">On Hand:</Text>
                    <Text size="sm" fw={600}>{stock.quantity}</Text>
                  </Group>
                  <Group justify="space-between">
                    <Text size="sm">Available for Sale:</Text>
                    <Text size="sm" fw={600} c={stock.available_for_sale > 0 ? 'green' : 'red'}>
                      {stock.available_for_sale}
                    </Text>
                  </Group>
                  <Group justify="space-between">
                    <Text size="sm">Reserved:</Text>
                    <Text size="sm" fw={600}>{stock.reserved_quantity}</Text>
                  </Group>
                  <Group justify="space-between">
                    <Text size="sm">Committed:</Text>
                    <Text size="sm" fw={600}>{stock.committed_quantity}</Text>
                  </Group>
                </Stack>
              </Card>

              {/* Stock Locations */}
              {stock.locations && stock.locations.length > 0 && (
                <Card shadow="sm" padding="lg" radius="md" withBorder>
                  <Group mb="md">
                    <IconMapPin size="1rem" />
                    <Title order={4}>Stock Locations</Title>
                  </Group>
                  <Stack gap="md">
                    {stock.locations.map((location: any) => (
                      <Box key={location.id} p="sm" bg="gray.0" style={{ borderRadius: '4px' }}>
                        <Stack gap="xs">
                          <Group justify="space-between">
                            <Text size="sm" fw={600}>
                              {location.store.name}
                            </Text>
                            {location.aisle && (
                              <Badge size="sm" color="blue" variant="light">
                                Aisle: {location.aisle}
                              </Badge>
                            )}
                          </Group>
                          {location.store.address && (
                            <Text size="xs" c="dimmed">
                              {location.store.address}
                            </Text>
                          )}
                          <Text size="sm" fw={500}>
                            {location.quantity} units
                          </Text>
                        </Stack>
                      </Box>
                    ))}
                  </Stack>
                </Card>
              )}
            </Stack>
          </Grid.Col>
        </Grid>
      </Stack>

      {/* Issue Stock Modal */}
      <Modal opened={issueOpened} onClose={closeIssue} title="Issue Stock">
        <Stack gap="md">
          <NumberInput
            label="Quantity to Issue"
            value={issueQuantity}
            onChange={(value) => setIssueQuantity(Number(value) || 1)}
            min={1}
            max={stock.available_for_sale}
          />
          <Textarea
            label="Notes (Optional)"
            placeholder="Add any notes about this issue..."
            value={issueNote}
            onChange={(event) => setIssueNote(event.currentTarget.value)}
            rows={3}
          />
          <Group justify="right">
            <Button variant="light" onClick={closeIssue}>
              Cancel
            </Button>
            <Button
              onClick={handleIssueStock}
              loading={issueMutation.isPending}
              color="orange"
            >
              Issue Stock
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Receive Stock Modal */}
      <Modal opened={receiveOpened} onClose={closeReceive} title="Receive Stock">
        <Stack gap="md">
          <NumberInput
            label="Quantity to Receive"
            value={receiveQuantity}
            onChange={(value) => setReceiveQuantity(Number(value) || 1)}
            min={1}
          />
          <TextInput
            label="Aisle (Optional)"
            placeholder="e.g., A1, B2, C3..."
            value={receiveAisle}
            onChange={(event) => setReceiveAisle(event.currentTarget.value)}
            description="Specify the aisle location for this stock"
          />
          <Textarea
            label="Notes (Optional)"
            placeholder="Add any notes about this receipt..."
            value={receiveNote}
            onChange={(event) => setReceiveNote(event.currentTarget.value)}
            rows={3}
          />
          <Group justify="right">
            <Button variant="light" onClick={closeReceive}>
              Cancel
            </Button>
            <Button
              onClick={handleReceiveStock}
              loading={receiveMutation.isPending}
              color="green"
            >
              Receive Stock
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Reserve Stock Modal */}
      <Modal opened={reserveOpened} onClose={closeReserve} title="Reserve Stock" size="md">
        <Stack gap="md">
          <NumberInput
            label="Quantity to Reserve"
            value={reserveQuantity}
            onChange={(value) => setReserveQuantity(Number(value) || 1)}
            min={1}
            max={stock.available_for_sale}
            required
          />

          <Select
            label="Reservation Type"
            value={reservationType}
            onChange={(value) => setReservationType(value || 'hold')}
            data={[
              { value: 'quote', label: 'Quote' },
              { value: 'hold', label: 'Hold' },
              { value: 'inspection', label: 'Inspection' },
              { value: 'transfer_prep', label: 'Transfer Prep' },
              { value: 'maintenance', label: 'Maintenance' },
              { value: 'other', label: 'Other' },
            ]}
            required
          />

          <TextInput
            label="Customer Name"
            value={customerName}
            onChange={(event) => setCustomerName(event.currentTarget.value)}
            required
          />

          <TextInput
            label="Customer Phone"
            value={customerPhone}
            onChange={(event) => setCustomerPhone(event.currentTarget.value)}
            placeholder="Optional"
          />

          <TextInput
            label="Customer Email"
            value={customerEmail}
            onChange={(event) => setCustomerEmail(event.currentTarget.value)}
            placeholder="Optional"
          />

          <TextInput
            label="Expires At"
            type="datetime-local"
            value={expiresAt}
            onChange={(event) => setExpiresAt(event.currentTarget.value)}
            required
          />

          <Textarea
            label="Reason"
            value={reserveReason}
            onChange={(event) => setReserveReason(event.currentTarget.value)}
            placeholder="Reason for reservation..."
            rows={3}
            required
          />

          <Group justify="right">
            <Button variant="light" onClick={closeReserve}>
              Cancel
            </Button>
            <Button
              onClick={handleReserveStock}
              loading={reserveMutation.isPending}
              color="blue"
            >
              Reserve Stock
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Commit Stock Modal */}
      <Modal opened={commitOpened} onClose={closeCommit} title="Commit Stock" size="md">
        <Stack gap="md">
          <NumberInput
            label="Quantity to Commit"
            value={commitQuantity}
            onChange={(value) => setCommitQuantity(Number(value) || 1)}
            min={1}
            max={stock.available_for_sale}
            required
          />

          <TextInput
            label="Customer Order Number"
            value={orderNumber}
            onChange={(event) => setOrderNumber(event.currentTarget.value)}
            required
          />

          <NumberInput
            label="Deposit Amount"
            value={depositAmount}
            onChange={(value) => setDepositAmount(Number(value) || 0)}
            min={0}
            prefix="$"
            decimalScale={2}
            fixedDecimalScale
          />

          <TextInput
            label="Customer Name"
            value={commitCustomerName}
            onChange={(event) => setCommitCustomerName(event.currentTarget.value)}
            required
          />

          <TextInput
            label="Customer Phone"
            value={commitCustomerPhone}
            onChange={(event) => setCommitCustomerPhone(event.currentTarget.value)}
            placeholder="Optional"
          />

          <TextInput
            label="Customer Email"
            value={commitCustomerEmail}
            onChange={(event) => setCommitCustomerEmail(event.currentTarget.value)}
            placeholder="Optional"
          />

          <Textarea
            label="Notes"
            value={commitNotes}
            onChange={(event) => setCommitNotes(event.currentTarget.value)}
            placeholder="Additional notes..."
            rows={3}
          />

          <Group justify="right">
            <Button variant="light" onClick={closeCommit}>
              Cancel
            </Button>
            <Button
              onClick={handleCommitStock}
              loading={commitMutation.isPending}
              color="purple"
            >
              Commit Stock
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Container>
  );
};

export default StockDetail;