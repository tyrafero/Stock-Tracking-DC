import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Container,
  Title,
  Text,
  Paper,
  Group,
  Button,
  Stack,
  TextInput,
  Textarea,
  NumberInput,
  ActionIcon,
  Alert,
  Table,
  Grid,
  Divider,
  Card,
} from '@mantine/core';
import {
  IconArrowLeft,
  IconDeviceFloppy,
  IconAlertCircle,
  IconPlus,
  IconTrash,
} from '@tabler/icons-react';
import { useForm, useFieldArray } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth, useHasPermission } from '@/states/authState';
import type { PurchaseOrderForm } from '@/types/stock';

const CreatePurchaseOrder: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const hasPermission = useHasPermission();

  const form = useForm<PurchaseOrderForm>({
    initialValues: {
      supplier_name: '',
      supplier_email: '',
      supplier_phone: '',
      supplier_address: '',
      expected_delivery_date: '',
      notes: '',
      items: [
        {
          item_name: '',
          description: '',
          quantity: 1,
          unit_price: 0,
          notes: '',
        },
      ],
    },
    validate: {
      supplier_name: (value) => (!value ? 'Supplier name is required' : null),
      items: {
        item_name: (value) => (!value ? 'Item name is required' : null),
        quantity: (value) => (!value || value <= 0 ? 'Quantity must be greater than 0' : null),
        unit_price: (value) => (value < 0 ? 'Unit price cannot be negative' : null),
      },
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: PurchaseOrderForm) => stockAPI.createPurchaseOrder(data),
    onSuccess: (purchaseOrder) => {
      notifications.show({
        title: 'Purchase Order Created',
        message: 'Purchase order has been created successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      navigate(`/purchase-orders/${purchaseOrder.id}`);
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to create purchase order',
        color: 'red',
      });
    },
  });

  const handleSubmit = (values: PurchaseOrderForm) => {
    createMutation.mutate(values);
  };

  const addItem = () => {
    form.insertListItem('items', {
      item_name: '',
      description: '',
      quantity: 1,
      unit_price: 0,
      notes: '',
    });
  };

  const removeItem = (index: number) => {
    if (form.values.items.length > 1) {
      form.removeListItem('items', index);
    }
  };

  const calculateSubtotal = () => {
    return form.values.items.reduce((sum, item) => {
      return sum + (item.quantity * item.unit_price);
    }, 0);
  };

  const calculateTax = (subtotal: number) => {
    return subtotal * 0.1; // 10% tax rate
  };

  const calculateTotal = () => {
    const subtotal = calculateSubtotal();
    const tax = calculateTax(subtotal);
    return subtotal + tax;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const canCreatePO = hasPermission('create_purchase_order');

  if (!canCreatePO) {
    return (
      <Container fluid>
        <Alert icon={<IconAlertCircle size={16} />} color="red">
          You don't have permission to create purchase orders.
        </Alert>
      </Container>
    );
  }

  const subtotal = calculateSubtotal();
  const tax = calculateTax(subtotal);
  const total = calculateTotal();

  return (
    <Container fluid>
      <Stack gap="md">
        <Group justify="space-between">
          <Group>
            <ActionIcon variant="light" onClick={() => navigate('/purchase-orders')}>
              <IconArrowLeft size={16} />
            </ActionIcon>
            <div>
              <Title order={1}>Create Purchase Order</Title>
              <Text c="dimmed">Create a new purchase order for suppliers</Text>
            </div>
          </Group>
        </Group>

        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Grid>
            <Grid.Col span={8}>
              <Stack gap="md">
                <Paper shadow="xs" p="lg">
                  <Stack gap="md">
                    <Title order={3}>Supplier Information</Title>

                    <TextInput
                      label="Supplier Name"
                      placeholder="Enter supplier name"
                      required
                      {...form.getInputProps('supplier_name')}
                    />

                    <Grid>
                      <Grid.Col span={6}>
                        <TextInput
                          label="Email"
                          placeholder="supplier@example.com"
                          type="email"
                          {...form.getInputProps('supplier_email')}
                        />
                      </Grid.Col>
                      <Grid.Col span={6}>
                        <TextInput
                          label="Phone"
                          placeholder="(555) 123-4567"
                          {...form.getInputProps('supplier_phone')}
                        />
                      </Grid.Col>
                    </Grid>

                    <Textarea
                      label="Address"
                      placeholder="Enter supplier address"
                      rows={3}
                      {...form.getInputProps('supplier_address')}
                    />

                    <TextInput
                      label="Expected Delivery Date"
                      type="date"
                      {...form.getInputProps('expected_delivery_date')}
                    />

                    <Textarea
                      label="Notes"
                      placeholder="Additional notes about this order"
                      rows={3}
                      {...form.getInputProps('notes')}
                    />
                  </Stack>
                </Paper>

                <Paper shadow="xs" p="lg">
                  <Stack gap="md">
                    <Group justify="space-between">
                      <Title order={3}>Order Items</Title>
                      <Button
                        leftSection={<IconPlus size={16} />}
                        variant="light"
                        onClick={addItem}
                      >
                        Add Item
                      </Button>
                    </Group>

                    <Table>
                      <Table.Thead>
                        <Table.Tr>
                          <Table.Th>Item Name</Table.Th>
                          <Table.Th>Description</Table.Th>
                          <Table.Th>Qty</Table.Th>
                          <Table.Th>Unit Price</Table.Th>
                          <Table.Th>Total</Table.Th>
                          <Table.Th></Table.Th>
                        </Table.Tr>
                      </Table.Thead>
                      <Table.Tbody>
                        {form.values.items.map((item, index) => (
                          <Table.Tr key={index}>
                            <Table.Td>
                              <TextInput
                                placeholder="Item name"
                                {...form.getInputProps(`items.${index}.item_name`)}
                                size="sm"
                              />
                            </Table.Td>
                            <Table.Td>
                              <TextInput
                                placeholder="Description"
                                {...form.getInputProps(`items.${index}.description`)}
                                size="sm"
                              />
                            </Table.Td>
                            <Table.Td>
                              <NumberInput
                                min={1}
                                {...form.getInputProps(`items.${index}.quantity`)}
                                size="sm"
                                w={80}
                              />
                            </Table.Td>
                            <Table.Td>
                              <NumberInput
                                min={0}
                                precision={2}
                                {...form.getInputProps(`items.${index}.unit_price`)}
                                size="sm"
                                w={120}
                              />
                            </Table.Td>
                            <Table.Td>
                              <Text size="sm" fw={500}>
                                {formatCurrency(item.quantity * item.unit_price)}
                              </Text>
                            </Table.Td>
                            <Table.Td>
                              <ActionIcon
                                color="red"
                                variant="light"
                                size="sm"
                                onClick={() => removeItem(index)}
                                disabled={form.values.items.length === 1}
                              >
                                <IconTrash size={14} />
                              </ActionIcon>
                            </Table.Td>
                          </Table.Tr>
                        ))}
                      </Table.Tbody>
                    </Table>
                  </Stack>
                </Paper>
              </Stack>
            </Grid.Col>

            <Grid.Col span={4}>
              <Card shadow="xs" padding="lg" withBorder>
                <Stack gap="md">
                  <Title order={4}>Order Summary</Title>

                  <Stack gap="xs">
                    <Group justify="space-between">
                      <Text size="sm">Subtotal</Text>
                      <Text size="sm">{formatCurrency(subtotal)}</Text>
                    </Group>
                    <Group justify="space-between">
                      <Text size="sm">Tax (10%)</Text>
                      <Text size="sm">{formatCurrency(tax)}</Text>
                    </Group>
                    <Divider />
                    <Group justify="space-between">
                      <Text fw={500}>Total</Text>
                      <Text fw={500} size="lg">{formatCurrency(total)}</Text>
                    </Group>
                  </Stack>

                  <Divider />

                  <Stack gap="sm">
                    <Button
                      variant="light"
                      fullWidth
                      onClick={() => navigate('/purchase-orders')}
                      disabled={createMutation.isPending}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      leftSection={<IconDeviceFloppy size={16} />}
                      fullWidth
                      loading={createMutation.isPending}
                    >
                      Create Purchase Order
                    </Button>
                  </Stack>
                </Stack>
              </Card>
            </Grid.Col>
          </Grid>
        </form>
      </Stack>
    </Container>
  );
};

export default CreatePurchaseOrder;