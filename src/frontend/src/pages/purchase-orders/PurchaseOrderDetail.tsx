import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Container,
  Title,
  Text,
  Paper,
  Group,
  Button,
  Stack,
  Grid,
  Badge,
  ActionIcon,
  Table,
  NumberInput,
  Textarea,
  Modal,
  Alert,
  LoadingOverlay,
  Divider,
  Card,
  Progress,
} from '@mantine/core';
import {
  IconArrowLeft,
  IconEdit,
  IconSend,
  IconCheck,
  IconX,
  IconTrash,
  IconPackage,
  IconAlertCircle,
  IconCalendar,
  IconUser,
  IconBuilding,
  IconCurrency,
  IconClipboard,
  IconPhone,
  IconMail,
  IconMapPin,
  IconNotes,
} from '@tabler/icons-react';
import { useForm } from '@mantine/form';
import { useDisclosure } from '@mantine/hooks';
import { modals } from '@mantine/modals';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth, useHasPermission } from '@/states/authState';
import type { PurchaseOrder, PurchaseOrderItem } from '@/types/stock';

const PurchaseOrderDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const hasPermission = useHasPermission();

  const [showReceiveModal, setShowReceiveModal] = useState(false);
  const [isReceiving, setIsReceiving] = useState(false);

  const { data: purchaseOrder, isLoading, error } = useQuery({
    queryKey: ['purchase-order', id],
    queryFn: () => stockAPI.getPurchaseOrder(Number(id)),
    enabled: !!id,
  });

  const receiveForm = useForm({
    initialValues: {
      items: [] as Array<{ id: number; received_quantity: number }>,
      delivery_date: new Date().toISOString().split('T')[0],
      notes: '',
    },
  });

  React.useEffect(() => {
    if (purchaseOrder) {
      receiveForm.setValues({
        items: purchaseOrder.items.map(item => ({
          id: item.id,
          received_quantity: item.quantity - item.received_quantity,
        })),
        delivery_date: new Date().toISOString().split('T')[0],
        notes: '',
      });
    }
  }, [purchaseOrder]);

  const sendMutation = useMutation({
    mutationFn: (id: number) => stockAPI.sendPurchaseOrder(id),
    onSuccess: () => {
      notifications.show({
        title: 'Purchase Order Sent',
        message: 'Purchase order has been sent to supplier successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['purchase-order', id] });
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
      queryClient.invalidateQueries({ queryKey: ['purchase-order', id] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to approve purchase order',
        color: 'red',
      });
    },
  });

  const receiveMutation = useMutation({
    mutationFn: (data: any) => stockAPI.receivePurchaseOrder(Number(id), data),
    onSuccess: () => {
      notifications.show({
        title: 'Items Received',
        message: 'Purchase order items have been received successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['purchase-order', id] });
      setShowReceiveModal(false);
      setIsReceiving(false);
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to receive items',
        color: 'red',
      });
      setIsReceiving(false);
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
      queryClient.invalidateQueries({ queryKey: ['purchase-order', id] });
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to cancel purchase order',
        color: 'red',
      });
    },
  });

  const handleSend = () => {
    modals.openConfirmModal({
      title: 'Send Purchase Order',
      children: (
        <Text>
          Are you sure you want to send this purchase order to {purchaseOrder?.supplier_name}?
        </Text>
      ),
      labels: { confirm: 'Send', cancel: 'Cancel' },
      confirmProps: { color: 'blue' },
      onConfirm: () => sendMutation.mutate(Number(id)),
    });
  };

  const handleApprove = () => {
    modals.openConfirmModal({
      title: 'Approve Purchase Order',
      children: (
        <Text>
          Are you sure you want to approve this purchase order? This will confirm the order.
        </Text>
      ),
      labels: { confirm: 'Approve', cancel: 'Cancel' },
      confirmProps: { color: 'green' },
      onConfirm: () => approveMutation.mutate(Number(id)),
    });
  };

  const handleCancel = () => {
    modals.openConfirmModal({
      title: 'Cancel Purchase Order',
      children: (
        <Text>
          Are you sure you want to cancel this purchase order? This action cannot be undone.
        </Text>
      ),
      labels: { confirm: 'Cancel Order', cancel: 'Keep' },
      confirmProps: { color: 'red' },
      onConfirm: () => cancelMutation.mutate(Number(id)),
    });
  };

  const handleReceive = () => {
    setIsReceiving(true);
    const validItems = receiveForm.values.items.filter(item => item.received_quantity > 0);

    if (validItems.length === 0) {
      notifications.show({
        title: 'No Items to Receive',
        message: 'Please specify quantities for items to receive',
        color: 'orange',
      });
      setIsReceiving(false);
      return;
    }

    receiveMutation.mutate({
      items: validItems,
      delivery_date: receiveForm.values.delivery_date,
      notes: receiveForm.values.notes,
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'gray',
      sent: 'blue',
      confirmed: 'green',
      partially_received: 'orange',
      received: 'teal',
      cancelled: 'red',
    };
    return colors[status] || 'gray';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  if (isLoading) return <LoadingOverlay visible />;
  if (error || !purchaseOrder) {
    return (
      <Container fluid>
        <Alert icon={<IconAlertCircle size={16} />} color="red">
          Failed to load purchase order. Please try again.
        </Alert>
      </Container>
    );
  }

  const canSendPO = hasPermission('send_purchase_order');
  const canApprovePO = hasPermission('approve_purchase_order');
  const canReceivePO = hasPermission('receive_purchase_order');
  const canCancelPO = hasPermission('cancel_purchase_order');

  return (
    <Container fluid>
      <Stack gap="md">
        <Group justify="space-between">
          <Group>
            <ActionIcon variant="light" onClick={() => navigate('/purchase-orders')}>
              <IconArrowLeft size={16} />
            </ActionIcon>
            <div>
              <Title order={1}>{purchaseOrder.po_number}</Title>
              <Text c="dimmed">Purchase Order Details</Text>
            </div>
          </Group>

          <Group>
            {purchaseOrder.status === 'draft' && (
              <Button
                leftSection={<IconEdit size={16} />}
                variant="light"
                onClick={() => navigate(`/purchase-orders/${id}/edit`)}
              >
                Edit
              </Button>
            )}

            {purchaseOrder.status === 'draft' && canSendPO && (
              <Button
                leftSection={<IconSend size={16} />}
                color="blue"
                onClick={handleSend}
                loading={sendMutation.isPending}
              >
                Send to Supplier
              </Button>
            )}

            {purchaseOrder.status === 'sent' && canApprovePO && (
              <Button
                leftSection={<IconCheck size={16} />}
                color="green"
                onClick={handleApprove}
                loading={approveMutation.isPending}
              >
                Approve
              </Button>
            )}

            {!purchaseOrder.is_fully_received && canReceivePO && (
              <Button
                leftSection={<IconPackage size={16} />}
                color="orange"
                onClick={() => setShowReceiveModal(true)}
              >
                Receive Items
              </Button>
            )}

            {['draft', 'sent'].includes(purchaseOrder.status) && canCancelPO && (
              <Button
                leftSection={<IconX size={16} />}
                color="red"
                variant="outline"
                onClick={handleCancel}
                loading={cancelMutation.isPending}
              >
                Cancel
              </Button>
            )}
          </Group>
        </Group>

        <Grid>
          <Grid.Col span={8}>
            <Paper shadow="xs" p="lg">
              <Stack gap="md">
                <Group justify="space-between">
                  <Title order={3}>Order Information</Title>
                  <Badge size="lg" color={getStatusColor(purchaseOrder.status)} variant="light">
                    {purchaseOrder.status.charAt(0).toUpperCase() +
                     purchaseOrder.status.slice(1).replace('_', ' ')}
                  </Badge>
                </Group>

                <Grid>
                  <Grid.Col span={6}>
                    <Stack gap="xs">
                      <Group gap="xs">
                        <IconBuilding size={16} />
                        <Text size="sm" fw={500}>Supplier</Text>
                      </Group>
                      <Text>{purchaseOrder.supplier_name}</Text>
                      {purchaseOrder.supplier_email && (
                        <Group gap="xs">
                          <IconMail size={14} />
                          <Text size="sm" c="dimmed">{purchaseOrder.supplier_email}</Text>
                        </Group>
                      )}
                      {purchaseOrder.supplier_phone && (
                        <Group gap="xs">
                          <IconPhone size={14} />
                          <Text size="sm" c="dimmed">{purchaseOrder.supplier_phone}</Text>
                        </Group>
                      )}
                    </Stack>
                  </Grid.Col>

                  <Grid.Col span={6}>
                    <Stack gap="xs">
                      <Group gap="xs">
                        <IconCalendar size={16} />
                        <Text size="sm" fw={500}>Order Date</Text>
                      </Group>
                      <Text>{formatDate(purchaseOrder.order_date)}</Text>

                      {purchaseOrder.expected_delivery_date && (
                        <>
                          <Text size="sm" fw={500} mt="md">Expected Delivery</Text>
                          <Text>{formatDate(purchaseOrder.expected_delivery_date)}</Text>
                        </>
                      )}
                    </Stack>
                  </Grid.Col>
                </Grid>

                {purchaseOrder.supplier_address && (
                  <div>
                    <Group gap="xs" mb="xs">
                      <IconMapPin size={16} />
                      <Text size="sm" fw={500}>Supplier Address</Text>
                    </Group>
                    <Text size="sm" c="dimmed">{purchaseOrder.supplier_address}</Text>
                  </div>
                )}

                {purchaseOrder.notes && (
                  <div>
                    <Group gap="xs" mb="xs">
                      <IconNotes size={16} />
                      <Text size="sm" fw={500}>Notes</Text>
                    </Group>
                    <Text size="sm">{purchaseOrder.notes}</Text>
                  </div>
                )}

                <Divider />

                <Group justify="space-between">
                  <Title order={4}>Items</Title>
                  <Text size="sm" c="dimmed">
                    {purchaseOrder.items_received}/{purchaseOrder.total_items} items received
                  </Text>
                </Group>

                {purchaseOrder.status === 'partially_received' && (
                  <Progress
                    value={(purchaseOrder.items_received / purchaseOrder.total_items) * 100}
                    size="md"
                    color="orange"
                    mb="md"
                  />
                )}

                <Table>
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Item</Table.Th>
                      <Table.Th>Quantity</Table.Th>
                      <Table.Th>Received</Table.Th>
                      <Table.Th>Unit Price</Table.Th>
                      <Table.Th>Total</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {purchaseOrder.items.map((item: PurchaseOrderItem) => (
                      <Table.Tr key={item.id}>
                        <Table.Td>
                          <div>
                            <Text fw={500}>{item.item_name}</Text>
                            {item.description && (
                              <Text size="sm" c="dimmed">{item.description}</Text>
                            )}
                          </div>
                        </Table.Td>
                        <Table.Td>{item.quantity}</Table.Td>
                        <Table.Td>
                          <Badge
                            color={item.received_quantity === item.quantity ? 'green' :
                                  item.received_quantity > 0 ? 'orange' : 'gray'}
                            variant="light"
                          >
                            {item.received_quantity}
                          </Badge>
                        </Table.Td>
                        <Table.Td>{formatCurrency(item.unit_price)}</Table.Td>
                        <Table.Td>{formatCurrency(item.total_price)}</Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              </Stack>
            </Paper>
          </Grid.Col>

          <Grid.Col span={4}>
            <Stack gap="md">
              <Card shadow="xs" padding="lg" withBorder>
                <Stack gap="md">
                  <Group justify="space-between">
                    <Text fw={500}>Order Summary</Text>
                    <IconCurrency size={20} />
                  </Group>

                  <Stack gap="xs">
                    <Group justify="space-between">
                      <Text size="sm">Subtotal</Text>
                      <Text size="sm">{formatCurrency(purchaseOrder.subtotal)}</Text>
                    </Group>
                    <Group justify="space-between">
                      <Text size="sm">Tax</Text>
                      <Text size="sm">{formatCurrency(purchaseOrder.tax_amount)}</Text>
                    </Group>
                    <Divider />
                    <Group justify="space-between">
                      <Text fw={500}>Total</Text>
                      <Text fw={500} size="lg">{formatCurrency(purchaseOrder.total_amount)}</Text>
                    </Group>
                  </Stack>
                </Stack>
              </Card>

              <Card shadow="xs" padding="lg" withBorder>
                <Stack gap="md">
                  <Group justify="space-between">
                    <Text fw={500}>Order History</Text>
                    <IconClipboard size={20} />
                  </Group>

                  <Stack gap="sm">
                    <div>
                      <Group gap="xs">
                        <IconUser size={14} />
                        <Text size="sm" fw={500}>Created</Text>
                      </Group>
                      <Text size="sm" c="dimmed">
                        {formatDate(purchaseOrder.created_at)} by{' '}
                        {purchaseOrder.created_by.first_name} {purchaseOrder.created_by.last_name}
                      </Text>
                    </div>

                    {purchaseOrder.sent_at && (
                      <div>
                        <Text size="sm" fw={500}>Sent</Text>
                        <Text size="sm" c="dimmed">{formatDate(purchaseOrder.sent_at)}</Text>
                      </div>
                    )}

                    {purchaseOrder.approved_at && purchaseOrder.approved_by && (
                      <div>
                        <Text size="sm" fw={500}>Approved</Text>
                        <Text size="sm" c="dimmed">
                          {formatDate(purchaseOrder.approved_at)} by{' '}
                          {purchaseOrder.approved_by.first_name} {purchaseOrder.approved_by.last_name}
                        </Text>
                      </div>
                    )}

                    {purchaseOrder.received_at && purchaseOrder.received_by && (
                      <div>
                        <Text size="sm" fw={500}>Received</Text>
                        <Text size="sm" c="dimmed">
                          {formatDate(purchaseOrder.received_at)} by{' '}
                          {purchaseOrder.received_by.first_name} {purchaseOrder.received_by.last_name}
                        </Text>
                      </div>
                    )}
                  </Stack>
                </Stack>
              </Card>
            </Stack>
          </Grid.Col>
        </Grid>
      </Stack>

      <Modal
        opened={showReceiveModal}
        onClose={() => setShowReceiveModal(false)}
        title="Receive Purchase Order Items"
        size="lg"
      >
        <Stack gap="md">
          <Alert icon={<IconPackage size={16} />} color="blue">
            Specify the quantities received for each item. Only items with quantities greater than 0 will be processed.
          </Alert>

          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Item</Table.Th>
                <Table.Th>Ordered</Table.Th>
                <Table.Th>Already Received</Table.Th>
                <Table.Th>Receive Now</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {purchaseOrder.items.map((item, index) => (
                <Table.Tr key={item.id}>
                  <Table.Td>
                    <div>
                      <Text fw={500}>{item.item_name}</Text>
                      {item.description && (
                        <Text size="sm" c="dimmed">{item.description}</Text>
                      )}
                    </div>
                  </Table.Td>
                  <Table.Td>{item.quantity}</Table.Td>
                  <Table.Td>{item.received_quantity}</Table.Td>
                  <Table.Td>
                    <NumberInput
                      min={0}
                      max={item.quantity - item.received_quantity}
                      value={receiveForm.values.items[index]?.received_quantity || 0}
                      onChange={(value) => {
                        const items = [...receiveForm.values.items];
                        items[index] = {
                          id: item.id,
                          received_quantity: Number(value) || 0,
                        };
                        receiveForm.setFieldValue('items', items);
                      }}
                      w={100}
                    />
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>

          <Textarea
            label="Delivery Notes"
            placeholder="Add any notes about the delivery..."
            value={receiveForm.values.notes}
            onChange={(e) => receiveForm.setFieldValue('notes', e.target.value)}
          />

          <Group justify="right">
            <Button variant="light" onClick={() => setShowReceiveModal(false)}>
              Cancel
            </Button>
            <Button
              color="orange"
              onClick={handleReceive}
              loading={isReceiving || receiveMutation.isPending}
            >
              Receive Items
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Container>
  );
};

export default PurchaseOrderDetail;