// @ts-nocheck
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
  Select,
  TextInput,
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
  IconFileInvoice,
  IconCash,
  IconPlus,
  IconDownload,
} from '@tabler/icons-react';
import { useForm } from '@mantine/form';
import { useDisclosure } from '@mantine/hooks';
import { modals } from '@mantine/modals';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth, useHasPermission } from '@/states/authState';
import type { PurchaseOrder, PurchaseOrderItem, Invoice, InvoiceForm, Payment, PaymentForm } from '@/types/stock';

const PurchaseOrderDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const hasPermission = useHasPermission();

  const [showReceiveModal, setShowReceiveModal] = useState(false);
  const [isReceiving, setIsReceiving] = useState(false);
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);

  const { data: purchaseOrder, isLoading, error } = useQuery({
    queryKey: ['purchase-order', id],
    queryFn: () => stockAPI.getPurchaseOrder(Number(id)),
    enabled: !!id,
  });

  const { data: storesData, isLoading: loadingStores } = useQuery({
    queryKey: ['stores'],
    queryFn: () => stockAPI.getStores(),
  });

  // Use invoices from purchase order response
  const invoices = purchaseOrder?.invoices || [];
  const loadingInvoices = isLoading;

  const receiveForm = useForm({
    initialValues: {
      items: [] as Array<{ id: number; received_quantity: number }>,
      receiving_store_id: '',
      delivery_date: new Date().toISOString().split('T')[0],
      notes: '',
      aisle: '',
    },
  });

  React.useEffect(() => {
    if (purchaseOrder) {
      receiveForm.setValues({
        items: purchaseOrder.items.map(item => ({
          id: item.id,
          received_quantity: item.quantity - item.received_quantity,
        })),
        receiving_store_id: purchaseOrder.store?.id ? purchaseOrder.store.id.toString() : '',
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

  const createInvoiceMutation = useMutation({
    mutationFn: (data: InvoiceForm) => stockAPI.createInvoice(Number(id), data),
    onSuccess: () => {
      notifications.show({
        title: 'Invoice Created',
        message: 'Invoice has been created successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['purchase-order', id] });
      setShowInvoiceModal(false);
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.error || 'Failed to create invoice',
        color: 'red',
      });
    },
  });

  const recordPaymentMutation = useMutation({
    mutationFn: ({ invoiceId, data }: { invoiceId: number; data: PaymentForm }) =>
      stockAPI.recordPayment(invoiceId, data),
    onSuccess: () => {
      notifications.show({
        title: 'Payment Recorded',
        message: 'Payment has been recorded successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['purchase-order', id] });
      setShowPaymentModal(false);
      setSelectedInvoice(null);
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.error || 'Failed to record payment',
        color: 'red',
      });
    },
  });

  const handleSend = () => {
    modals.openConfirmModal({
      title: 'Send Purchase Order',
      children: (
        <Text>
          Are you sure you want to send this purchase order to {purchaseOrder?.manufacturer}?
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

    if (!receiveForm.values.receiving_store_id) {
      notifications.show({
        title: 'Store Required',
        message: 'Please select a store where items will be received',
        color: 'orange',
      });
      setIsReceiving(false);
      return;
    }

    receiveMutation.mutate({
      items: validItems,
      receiving_store_id: parseInt(receiveForm.values.receiving_store_id),
      delivery_date: receiveForm.values.delivery_date,
      notes: receiveForm.values.notes,
      aisle: receiveForm.values.aisle || undefined,
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

  const getInvoiceStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'yellow',
      partially_paid: 'orange',
      fully_paid: 'green',
      overdue: 'red',
      disputed: 'grape',
      cancelled: 'gray',
    };
    return colors[status] || 'gray';
  };

  // Calculate totals from items
  const calculateTotals = (items: PurchaseOrderItem[]) => {
    const subtotalExc = items.reduce((sum, item) => {
      const priceExc = item.price_inc * 0.9; // Remove 10% GST
      const lineTotalExc = priceExc * item.quantity;
      const discountAmount = (lineTotalExc * item.discount_percent) / 100;
      return sum + (lineTotalExc - discountAmount);
    }, 0);

    const taxAmount = subtotalExc * 0.1; // 10% GST
    const totalAmount = subtotalExc + taxAmount;

    return { subtotalExc, taxAmount, totalAmount };
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

  // Calculate order totals
  const { subtotalExc, taxAmount, totalAmount } = calculateTotals(purchaseOrder.items);

  // Calculate received items
  const totalItems = purchaseOrder.items.length;
  const itemsReceived = purchaseOrder.items.filter(item => item.received_quantity >= item.quantity).length;
  const hasItemsToReceive = purchaseOrder.items.some(item => item.received_quantity < item.quantity);
  const hasAnyItems = purchaseOrder.items.length > 0;

  return (
    <Container fluid>
      <Stack gap="md">
        <Group justify="space-between">
          <Group>
            <ActionIcon variant="light" onClick={() => navigate('/purchase-orders')}>
              <IconArrowLeft size={16} />
            </ActionIcon>
            <div>
              <Title order={1}>{purchaseOrder.reference_number}</Title>
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

            {['sent', 'confirmed', 'partially_received'].includes(purchaseOrder.status) && canReceivePO && hasAnyItems && hasItemsToReceive && (
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
                        <Text size="sm" fw={500}>Manufacturer</Text>
                      </Group>
                      <Text>{purchaseOrder.manufacturer || 'N/A'}</Text>

                      <Text size="sm" fw={500} mt="md">Delivery Type</Text>
                      <Badge color={purchaseOrder.delivery_type === 'dropship' ? 'blue' : 'green'}>
                        {purchaseOrder.delivery_type === 'dropship' ? 'Dropship' : 'Store Delivery'}
                      </Badge>

                      {purchaseOrder.delivery_person && (
                        <>
                          <Text size="sm" fw={500} mt="md">Delivery Person</Text>
                          <Text size="sm">{purchaseOrder.delivery_person}</Text>
                        </>
                      )}
                    </Stack>
                  </Grid.Col>

                  <Grid.Col span={6}>
                    <Stack gap="xs">
                      <Group gap="xs">
                        <IconCalendar size={16} />
                        <Text size="sm" fw={500}>Order Date</Text>
                      </Group>
                      <Text>{formatDate(purchaseOrder.created_at)}</Text>

                      {purchaseOrder.sent_at && (
                        <>
                          <Text size="sm" fw={500} mt="md">Sent Date</Text>
                          <Text size="sm">{formatDate(purchaseOrder.sent_at)}</Text>
                        </>
                      )}
                    </Stack>
                  </Grid.Col>
                </Grid>

                {purchaseOrder.delivery_type === 'dropship' && purchaseOrder.customer_name && (
                  <div>
                    <Group gap="xs" mb="xs">
                      <IconUser size={16} />
                      <Text size="sm" fw={500}>Customer Details</Text>
                    </Group>
                    <Text size="sm" fw={500}>{purchaseOrder.customer_name}</Text>
                    {purchaseOrder.customer_phone && (
                      <Text size="sm" c="dimmed">{purchaseOrder.customer_phone}</Text>
                    )}
                    {purchaseOrder.customer_email && (
                      <Text size="sm" c="dimmed">{purchaseOrder.customer_email}</Text>
                    )}
                    {purchaseOrder.customer_address && (
                      <>
                        <Text size="sm" fw={500} mt="xs">Delivery Address</Text>
                        <Text size="sm" c="dimmed" style={{ whiteSpace: 'pre-wrap' }}>
                          {purchaseOrder.customer_address}
                        </Text>
                      </>
                    )}
                  </div>
                )}

                {purchaseOrder.store && (
                  <div>
                    <Group gap="xs" mb="xs">
                      <IconMapPin size={16} />
                      <Text size="sm" fw={500}>
                        {purchaseOrder.delivery_type === 'dropship' ? 'Creating Store' : 'Delivery Location'}
                      </Text>
                    </Group>
                    <Text size="sm">{purchaseOrder.store}</Text>
                  </div>
                )}

                {purchaseOrder.note_for_manufacturer && (
                  <div>
                    <Group gap="xs" mb="xs">
                      <IconNotes size={16} />
                      <Text size="sm" fw={500}>Notes for Manufacturer</Text>
                    </Group>
                    <Text size="sm">{purchaseOrder.note_for_manufacturer}</Text>
                  </div>
                )}

                <Divider />

                <Group justify="space-between">
                  <Title order={4}>Items</Title>
                  <Text size="sm" c="dimmed">
                    {itemsReceived}/{totalItems} items received
                  </Text>
                </Group>

                {itemsReceived > 0 && itemsReceived < totalItems && (
                  <Progress
                    value={(itemsReceived / totalItems) * 100}
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
                    {purchaseOrder.items.map((item: PurchaseOrderItem) => {
                      const priceExc = item.price_inc * 0.9;
                      const lineTotalExc = priceExc * item.quantity;
                      const discountAmount = (lineTotalExc * item.discount_percent) / 100;
                      const subtotalExc = lineTotalExc - discountAmount;

                      return (
                        <Table.Tr key={item.id}>
                          <Table.Td>
                            <div>
                              <Text fw={500}>{item.product}</Text>
                              {item.associated_order_number && (
                                <Text size="sm" c="dimmed">Order #{item.associated_order_number}</Text>
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
                          <Table.Td>{formatCurrency(item.price_inc)}</Table.Td>
                          <Table.Td>{formatCurrency(subtotalExc)}</Table.Td>
                        </Table.Tr>
                      );
                    })}
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
                      <Text size="sm">Subtotal (Exc GST)</Text>
                      <Text size="sm">{formatCurrency(subtotalExc)}</Text>
                    </Group>
                    <Group justify="space-between">
                      <Text size="sm">GST (10%)</Text>
                      <Text size="sm">{formatCurrency(taxAmount)}</Text>
                    </Group>
                    <Divider />
                    <Group justify="space-between">
                      <Text fw={500}>Total (Inc GST)</Text>
                      <Text fw={500} size="lg">{formatCurrency(totalAmount)}</Text>
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

                  {purchaseOrder.history && purchaseOrder.history.length > 0 ? (
                    <Stack gap="sm">
                      {purchaseOrder.history.slice(0, 10).map((historyItem: any, index: number) => (
                        <Paper key={index} p="xs" withBorder>
                          <Stack gap={4}>
                            <Group gap="xs">
                              <Badge size="sm" variant="light">
                                {historyItem.action}
                              </Badge>
                              <Text size="xs" c="dimmed">
                                {formatDate(historyItem.created_at)}
                              </Text>
                            </Group>
                            {historyItem.notes && (
                              <Text size="xs" c="dimmed">{historyItem.notes}</Text>
                            )}
                            <Text size="xs" c="dimmed">
                              by {historyItem.created_by?.first_name} {historyItem.created_by?.last_name}
                            </Text>
                          </Stack>
                        </Paper>
                      ))}
                    </Stack>
                  ) : (
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
                    </Stack>
                  )}
                </Stack>
              </Card>

              {/* Invoices & Payments */}
              <Card shadow="xs" padding="lg" withBorder>
                <Stack gap="md">
                  <Group justify="space-between">
                    <Group gap="xs">
                      <IconFileInvoice size={20} />
                      <Text fw={500}>Invoices & Payments</Text>
                    </Group>
                    {['sent', 'confirmed', 'partially_received', 'completed'].includes(purchaseOrder.status) && (
                      <Button
                        size="xs"
                        leftSection={<IconPlus size={14} />}
                        onClick={() => setShowInvoiceModal(true)}
                      >
                        Add Invoice
                      </Button>
                    )}
                  </Group>

                  {loadingInvoices ? (
                    <Text size="sm" c="dimmed">Loading invoices...</Text>
                  ) : invoices && invoices.length > 0 ? (
                    <Stack gap="sm">
                      {invoices.map((invoice: Invoice) => (
                        <Paper key={invoice.id} p="sm" withBorder>
                          <Stack gap="xs">
                            <Group justify="space-between">
                              <Text size="sm" fw={600}>{invoice.invoice_number}</Text>
                              <Badge size="sm" color={getInvoiceStatusColor(invoice.status)}>
                                {invoice.status.replace('_', ' ')}
                              </Badge>
                            </Group>
                            <Group gap="md">
                              <div>
                                <Text size="xs" c="dimmed">Total</Text>
                                <Text size="sm" fw={500}>{formatCurrency(invoice.invoice_total)}</Text>
                              </div>
                              <div>
                                <Text size="xs" c="dimmed">Paid</Text>
                                <Text size="sm" c="green">{formatCurrency(invoice.total_paid)}</Text>
                              </div>
                              <div>
                                <Text size="xs" c="dimmed">Outstanding</Text>
                                <Text size="sm" c="red">{formatCurrency(invoice.outstanding_amount)}</Text>
                              </div>
                            </Group>
                            {invoice.outstanding_amount > 0 && (
                              <Progress
                                value={invoice.payment_percentage}
                                size="sm"
                                color={invoice.payment_percentage >= 100 ? 'green' : 'orange'}
                              />
                            )}
                            <Group gap="xs">
                              <Text size="xs" c="dimmed">Date: {formatDate(invoice.invoice_date)}</Text>
                              <Text size="xs" c="dimmed">•</Text>
                              <Text size="xs" c="dimmed">Due: {formatDate(invoice.due_date)}</Text>
                              {invoice.is_overdue && (
                                <Badge size="xs" color="red">{invoice.days_overdue} days overdue</Badge>
                              )}
                            </Group>
                            {invoice.invoice_file && (
                              <Button
                                size="xs"
                                variant="subtle"
                                component="a"
                                href={invoice.invoice_file}
                                target="_blank"
                                leftSection={<IconFileInvoice size={14} />}
                              >
                                View Invoice PDF
                              </Button>
                            )}
                            {invoice.outstanding_amount > 0 && (
                              <Button
                                size="xs"
                                variant="light"
                                leftSection={<IconCash size={14} />}
                                onClick={() => {
                                  setSelectedInvoice(invoice);
                                  setShowPaymentModal(true);
                                }}
                              >
                                Record Payment
                              </Button>
                            )}
                          </Stack>
                        </Paper>
                      ))}
                    </Stack>
                  ) : (
                    <Text size="sm" c="dimmed">No invoices yet</Text>
                  )}
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
                      <Text fw={500}>{item.product}</Text>
                      {item.associated_order_number && (
                        <Text size="sm" c="dimmed">Order #{item.associated_order_number}</Text>
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

          <Select
            label="Receiving Location"
            placeholder="Select store where items will be received"
            data={storesData?.results.map((s) => ({
              value: s.id.toString(),
              label: `${s.name} - ${s.location}`,
            })) || []}
            value={receiveForm.values.receiving_store_id}
            onChange={(value) => receiveForm.setFieldValue('receiving_store_id', value)}
            searchable
            required
            disabled={loadingStores}
          />

          <TextInput
            label="Aisle (Optional)"
            placeholder="e.g., A1, B2, C3..."
            value={receiveForm.values.aisle}
            onChange={(e) => receiveForm.setFieldValue('aisle', e.target.value)}
            description="Specify the aisle location at the selected receiving store"
          />

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

      {/* Add Invoice Modal */}
      <Modal
        opened={showInvoiceModal}
        onClose={() => setShowInvoiceModal(false)}
        title="Add Invoice"
        size="lg"
      >
        <form onSubmit={(e) => {
          e.preventDefault();
          const formData = new FormData(e.currentTarget);
          const invoiceFile = formData.get('invoice_file') as File;
          const data: InvoiceForm = {
            invoice_number: formData.get('invoice_number') as string,
            invoice_date: formData.get('invoice_date') as string,
            due_date: formData.get('due_date') as string,
            invoice_amount_exc: parseFloat(formData.get('invoice_amount_exc') as string),
            gst_amount: parseFloat(formData.get('gst_amount') as string),
            invoice_total: parseFloat(formData.get('invoice_total') as string),
            notes: formData.get('notes') as string || undefined,
            invoice_file: invoiceFile?.size > 0 ? invoiceFile : undefined,
          };
          createInvoiceMutation.mutate(data);
        }}>
          <Stack gap="md">
            <TextInput
              name="invoice_number"
              label="Invoice Number"
              placeholder="INV-001"
              required
            />
            <Grid>
              <Grid.Col span={6}>
                <TextInput
                  name="invoice_date"
                  label="Invoice Date"
                  type="date"
                  required
                />
              </Grid.Col>
              <Grid.Col span={6}>
                <TextInput
                  name="due_date"
                  label="Due Date"
                  type="date"
                  required
                />
              </Grid.Col>
            </Grid>
            <Grid>
              <Grid.Col span={4}>
                <NumberInput
                  name="invoice_amount_exc"
                  label="Amount (Exc GST)"
                  defaultValue={purchaseOrder?.items ? calculateTotals(purchaseOrder.items).subtotalExc : 0}
                  min={0}
                  decimalScale={2}
                  required
                />
              </Grid.Col>
              <Grid.Col span={4}>
                <NumberInput
                  name="gst_amount"
                  label="GST Amount"
                  defaultValue={purchaseOrder?.items ? calculateTotals(purchaseOrder.items).taxAmount : 0}
                  min={0}
                  decimalScale={2}
                  required
                />
              </Grid.Col>
              <Grid.Col span={4}>
                <NumberInput
                  name="invoice_total"
                  label="Total (Inc GST)"
                  defaultValue={purchaseOrder?.items ? calculateTotals(purchaseOrder.items).totalAmount : 0}
                  min={0}
                  decimalScale={2}
                  required
                />
              </Grid.Col>
            </Grid>
            <Textarea
              name="notes"
              label="Notes"
              placeholder="Add any notes about this invoice..."
              rows={3}
            />
            <div>
              <Text size="sm" fw={500} mb="xs">Invoice PDF (from manufacturer)</Text>
              <input
                type="file"
                name="invoice_file"
                accept=".pdf"
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #dee2e6',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              />
              <Text size="xs" c="dimmed" mt="xs">Upload the invoice PDF received from the manufacturer</Text>
            </div>
            <Group justify="right">
              <Button variant="light" onClick={() => setShowInvoiceModal(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={createInvoiceMutation.isPending}>
                Create Invoice
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>

      {/* Record Payment Modal */}
      <Modal
        opened={showPaymentModal}
        onClose={() => {
          setShowPaymentModal(false);
          setSelectedInvoice(null);
        }}
        title={`Record Payment - ${selectedInvoice?.invoice_number}`}
        size="md"
      >
        <form onSubmit={(e) => {
          e.preventDefault();
          if (!selectedInvoice) return;
          const formData = new FormData(e.currentTarget);
          const data: PaymentForm = {
            payment_reference: formData.get('payment_reference') as string,
            payment_date: formData.get('payment_date') as string,
            payment_amount: parseFloat(formData.get('payment_amount') as string),
            payment_method: formData.get('payment_method') as string,
            notes: formData.get('notes') as string || undefined,
          };
          recordPaymentMutation.mutate({ invoiceId: selectedInvoice.id, data });
        }}>
          <Stack gap="md">
            {selectedInvoice && (
              <Alert color="blue">
                <Stack gap="xs">
                  <Text size="sm">Invoice Total: {formatCurrency(selectedInvoice.invoice_total)}</Text>
                  <Text size="sm">Already Paid: {formatCurrency(selectedInvoice.total_paid)}</Text>
                  <Text size="sm" fw={600}>Outstanding: {formatCurrency(selectedInvoice.outstanding_amount)}</Text>
                </Stack>
              </Alert>
            )}
            <TextInput
              name="payment_reference"
              label="Payment Reference"
              placeholder="Check number, transfer ID, etc."
              required
            />
            <TextInput
              name="payment_date"
              label="Payment Date"
              type="date"
              defaultValue={new Date().toISOString().split('T')[0]}
              required
            />
            <NumberInput
              name="payment_amount"
              label="Payment Amount"
              defaultValue={selectedInvoice?.outstanding_amount || 0}
              min={0}
              max={selectedInvoice?.outstanding_amount}
              decimalScale={2}
              required
            />
            <Select
              name="payment_method"
              label="Payment Method"
              data={[
                { value: 'bank_transfer', label: 'Bank Transfer' },
                { value: 'check', label: 'Check' },
                { value: 'cash', label: 'Cash' },
                { value: 'credit_card', label: 'Credit Card' },
                { value: 'other', label: 'Other' },
              ]}
              defaultValue="bank_transfer"
              required
            />
            <Textarea
              name="notes"
              label="Notes"
              placeholder="Add any notes about this payment..."
              rows={2}
            />
            <Group justify="right">
              <Button variant="light" onClick={() => {
                setShowPaymentModal(false);
                setSelectedInvoice(null);
              }}>
                Cancel
              </Button>
              <Button type="submit" loading={recordPaymentMutation.isPending}>
                Record Payment
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>
    </Container>
  );
};

export default PurchaseOrderDetail;