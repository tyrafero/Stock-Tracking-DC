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
  IconSend,
  IconCheck,
  IconX,
  IconTrash,
  IconClipboard,
  IconAlertCircle,
  IconCalendar,
  IconUser,
  IconBuilding,
  IconPackage,
} from '@tabler/icons-react';
import { modals } from '@mantine/modals';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth, useHasPermission } from '@/states/authState';
import type { PurchaseOrder, PaginatedResponse } from '@/types/stock';

const PurchaseOrdersList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const hasPermission = useHasPermission();

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);

  const { data: purchaseOrdersData, isLoading, error } = useQuery({
    queryKey: ['purchase-orders', searchQuery, statusFilter, currentPage],
    queryFn: () => stockAPI.getPurchaseOrders({
      search: searchQuery,
      status: statusFilter || undefined,
      page: currentPage,
      page_size: 20,
    }),
  });

  const sendMutation = useMutation({
    mutationFn: (id: number) => stockAPI.sendPurchaseOrder(id),
    onSuccess: () => {
      notifications.show({
        title: 'Purchase Order Sent',
        message: 'Purchase order has been sent to supplier successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to send purchase order',
        color: 'red',
      });
    },
  });

  const approveMutation = useMutation({
    mutationFn: (id: number) => stockAPI.approvePurchaseOrder(id),
    onSuccess: () => {
      notifications.show({
        title: 'Purchase Order Approved',
        message: 'Purchase order has been approved successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to approve purchase order',
        color: 'red',
      });
    },
  });

  const cancelMutation = useMutation({
    mutationFn: (id: number) => stockAPI.cancelPurchaseOrder(id),
    onSuccess: () => {
      notifications.show({
        title: 'Purchase Order Cancelled',
        message: 'Purchase order has been cancelled successfully',
        color: 'orange',
      });
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to cancel purchase order',
        color: 'red',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => stockAPI.deletePurchaseOrder(id),
    onSuccess: () => {
      notifications.show({
        title: 'Purchase Order Deleted',
        message: 'Purchase order has been deleted successfully',
        color: 'red',
      });
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to delete purchase order',
        color: 'red',
      });
    },
  });

  const handleSend = (purchaseOrder: PurchaseOrder) => {
    modals.openConfirmModal({
      title: 'Send Purchase Order',
      children: (
        <Text>
          Are you sure you want to send "{purchaseOrder.reference_number}" to {purchaseOrder.manufacturer}?
        </Text>
      ),
      labels: { confirm: 'Send', cancel: 'Cancel' },
      confirmProps: { color: 'blue' },
      onConfirm: () => sendMutation.mutate(purchaseOrder.id),
    });
  };

  const handleApprove = (purchaseOrder: PurchaseOrder) => {
    modals.openConfirmModal({
      title: 'Approve Purchase Order',
      children: (
        <Text>
          Are you sure you want to approve "{purchaseOrder.reference_number}"? This will confirm the order.
        </Text>
      ),
      labels: { confirm: 'Approve', cancel: 'Cancel' },
      confirmProps: { color: 'green' },
      onConfirm: () => approveMutation.mutate(purchaseOrder.id),
    });
  };

  const handleCancel = (purchaseOrder: PurchaseOrder) => {
    modals.openConfirmModal({
      title: 'Cancel Purchase Order',
      children: (
        <Text>
          Are you sure you want to cancel "{purchaseOrder.reference_number}"? This action cannot be undone.
        </Text>
      ),
      labels: { confirm: 'Cancel Order', cancel: 'Keep' },
      confirmProps: { color: 'red' },
      onConfirm: () => cancelMutation.mutate(purchaseOrder.id),
    });
  };

  const handleDelete = (purchaseOrder: PurchaseOrder) => {
    modals.openConfirmModal({
      title: 'Delete Purchase Order',
      children: (
        <Text>
          Are you sure you want to delete "{purchaseOrder.reference_number}"? This action cannot be undone.
        </Text>
      ),
      labels: { confirm: 'Delete', cancel: 'Cancel' },
      confirmProps: { color: 'red' },
      onConfirm: () => deleteMutation.mutate(purchaseOrder.id),
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'gray',
      sent: 'blue',
      confirmed: 'green',
      partially_received: 'orange',
      completed: 'teal',
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

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const canCreatePO = hasPermission('create_purchase_order');
  const canSendPO = hasPermission('send_purchase_order');
  const canApprovePO = hasPermission('approve_purchase_order');
  const canCancelPO = hasPermission('cancel_purchase_order');
  const canDeletePO = hasPermission('delete_purchase_order');

  return (
    <Container fluid>
      <Group justify="space-between" mb="xl">
        <div>
          <Title order={1}>Purchase Orders</Title>
          <Text c="dimmed">Manage supplier orders and deliveries</Text>
        </div>
        {canCreatePO && (
          <Button
            leftSection={<IconPlus size={16} />}
            onClick={() => navigate('/purchase-orders/create')}
          >
            Create Purchase Order
          </Button>
        )}
      </Group>

      <Paper shadow="xs" p="md" mb="md">
        <Group>
          <TextInput
            placeholder="Search purchase orders..."
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
              { value: 'draft', label: 'Draft' },
              { value: 'sent', label: 'Sent' },
              { value: 'confirmed', label: 'Confirmed' },
              { value: 'partially_received', label: 'Partially Received' },
              { value: 'completed', label: 'Completed' },
              { value: 'cancelled', label: 'Cancelled' },
            ]}
            value={statusFilter}
            onChange={(value) => setStatusFilter(value || '')}
            clearable
            w={200}
          />
        </Group>
      </Paper>

      <Paper shadow="xs" p="md">
        {isLoading ? (
          <LoadingOverlay visible />
        ) : error ? (
          <Alert icon={<IconAlertCircle size={16} />} color="red">
            Failed to load purchase orders. Please try again.
          </Alert>
        ) : purchaseOrdersData?.results.length === 0 ? (
          <Stack align="center" py="xl">
            <IconClipboard size={48} stroke={1.5} color="gray" />
            <Text size="lg" fw={500}>No purchase orders found</Text>
            <Text c="dimmed" ta="center">
              {searchQuery || statusFilter
                ? 'Try adjusting your search filters'
                : 'Create your first purchase order to start ordering from suppliers'
              }
            </Text>
            {canCreatePO && !searchQuery && !statusFilter && (
              <Button
                leftSection={<IconPlus size={16} />}
                onClick={() => navigate('/purchase-orders/create')}
              >
                Create Purchase Order
              </Button>
            )}
          </Stack>
        ) : (
          <>
            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>PO Number</Table.Th>
                  <Table.Th>Supplier</Table.Th>
                  <Table.Th>Status</Table.Th>
                  <Table.Th>Items</Table.Th>
                  <Table.Th>Total Amount</Table.Th>
                  <Table.Th>Order Date</Table.Th>
                  <Table.Th>Created By</Table.Th>
                  <Table.Th>Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {purchaseOrdersData?.results.map((purchaseOrder: PurchaseOrder) => (
                  <Table.Tr key={purchaseOrder.id}>
                    <Table.Td>
                      <div>
                        <Text fw={500}>{purchaseOrder.reference_number}</Text>
                        {purchaseOrder.expected_delivery_date && (
                          <Text size="sm" c="dimmed">
                            Expected: {formatDate(purchaseOrder.expected_delivery_date)}
                          </Text>
                        )}
                      </div>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <IconBuilding size={14} />
                        <Text size="sm">{purchaseOrder.manufacturer}</Text>
                      </Group>
                    </Table.Td>
                    <Table.Td>
                      <Badge color={getStatusColor(purchaseOrder.status)} variant="light">
                        {purchaseOrder.status.charAt(0).toUpperCase() +
                         purchaseOrder.status.slice(1).replace('_', ' ')}
                      </Badge>
                    </Table.Td>
                    <Table.Td>
                      <div>
                        <Text size="sm" mb="xs">
                          {purchaseOrder.items?.length || 0} items
                        </Text>
                      </div>
                    </Table.Td>
                    <Table.Td>
                      <Text size="sm" fw={500}>
                        {purchaseOrder.items && purchaseOrder.items.length > 0 ?
                          formatCurrency(purchaseOrder.items.reduce((sum, item) => sum + (item.price_inc * item.quantity), 0)) :
                          '$0.00'
                        }
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <IconCalendar size={14} />
                        <Text size="sm">{formatDate(purchaseOrder.created_at)}</Text>
                      </Group>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <IconUser size={14} />
                        <Text size="sm">
                          {purchaseOrder.created_by?.full_name ||
                           `${purchaseOrder.created_by?.first_name || ''} ${purchaseOrder.created_by?.last_name || ''}`.trim() ||
                           purchaseOrder.created_by?.username ||
                           'Unknown'
                          }
                        </Text>
                      </Group>
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <ActionIcon
                          variant="light"
                          size="sm"
                          onClick={() => navigate(`/purchase-orders/${purchaseOrder.id}`)}
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
                              onClick={() => navigate(`/purchase-orders/${purchaseOrder.id}`)}
                            >
                              View Details
                            </Menu.Item>

                            {purchaseOrder.status === 'draft' && (
                              <Menu.Item
                                leftSection={<IconEdit size={14} />}
                                onClick={() => navigate(`/purchase-orders/${purchaseOrder.id}/edit`)}
                              >
                                Edit
                              </Menu.Item>
                            )}

                            {purchaseOrder.status === 'draft' && canSendPO && (
                              <Menu.Item
                                leftSection={<IconSend size={14} />}
                                onClick={() => handleSend(purchaseOrder)}
                                color="blue"
                              >
                                Send to Supplier
                              </Menu.Item>
                            )}

                            {['sent', 'confirmed', 'partially_received'].includes(purchaseOrder.status) && (
                              <Menu.Item
                                leftSection={<IconPackage size={14} />}
                                onClick={() => navigate(`/purchase-orders/${purchaseOrder.id}`)}
                                color="orange"
                              >
                                Receive Items
                              </Menu.Item>
                            )}

                            {['draft', 'sent'].includes(purchaseOrder.status) && canCancelPO && (
                              <Menu.Item
                                leftSection={<IconX size={14} />}
                                onClick={() => handleCancel(purchaseOrder)}
                                color="orange"
                              >
                                Cancel
                              </Menu.Item>
                            )}

                            {purchaseOrder.status === 'draft' && canDeletePO && (
                              <Menu.Item
                                leftSection={<IconTrash size={14} />}
                                onClick={() => handleDelete(purchaseOrder)}
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

            {purchaseOrdersData && purchaseOrdersData.count > 20 && (
              <Group justify="center" mt="md">
                <Pagination
                  value={currentPage}
                  onChange={setCurrentPage}
                  total={Math.ceil(purchaseOrdersData.count / 20)}
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

export default PurchaseOrdersList;