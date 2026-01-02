// @ts-nocheck
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Container,
  Title,
  Text,
  Paper,
  Group,
  Button,
  Stack,
  Select,
  Textarea,
  TextInput,
  ActionIcon,
  Alert,
  Grid,
  Card,
} from '@mantine/core';
import {
  IconArrowLeft,
  IconDeviceFloppy,
  IconAlertCircle,
} from '@tabler/icons-react';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth, useHasPermission } from '@/states/authState';
import { POItemTable } from '@/components/purchase-orders/POItemTable';
import { POTotals } from '@/components/purchase-orders/POTotals';
import type { POItem } from '@/components/purchase-orders/POItemRow';

interface PurchaseOrderFormValues {
  manufacturer_id: string;
  delivery_person_id: string;
  delivery_type: string;
  store_id: string;
  creating_store_id: string;
  note_for_manufacturer: string;
  customer_name?: string;
  customer_phone?: string;
  customer_email?: string;
  customer_address?: string;
  items: POItem[];
}

const CreatePurchaseOrder: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const hasPermission = useHasPermission();
  const isEditMode = !!id;

  // Fetch existing PO if editing
  const { data: existingPO, isLoading: loadingPO } = useQuery({
    queryKey: ['purchase-order', id],
    queryFn: () => stockAPI.getPurchaseOrder(Number(id)),
    enabled: isEditMode,
  });

  // Fetch manufacturers
  const { data: manufacturersData, isLoading: loadingManufacturers } = useQuery({
    queryKey: ['manufacturers'],
    queryFn: () => stockAPI.getManufacturers({ page_size: 100 }),
  });

  // Fetch delivery persons
  const { data: deliveryPersonsData, isLoading: loadingDeliveryPersons } = useQuery({
    queryKey: ['delivery-persons'],
    queryFn: () => stockAPI.getDeliveryPersons({ page_size: 100 }),
  });

  // Fetch stores
  const { data: storesData, isLoading: loadingStores } = useQuery({
    queryKey: ['stores'],
    queryFn: () => stockAPI.getStores(),
  });

  const form = useForm<PurchaseOrderFormValues>({
    initialValues: {
      manufacturer_id: '',
      delivery_person_id: '',
      delivery_type: 'store',
      store_id: '',
      creating_store_id: '',
      note_for_manufacturer: '',
      customer_name: '',
      customer_phone: '',
      customer_email: '',
      customer_address: '',
      items: [
        {
          id: 'initial',
          product: '',
          associated_order_number: '',
          price_inc: 0,
          quantity: 1,
          discount_percent: 0,
        },
      ],
    },
    validate: {
      manufacturer_id: (value) => (!value ? 'Manufacturer is required' : null),
      delivery_person_id: (value) => (!value ? 'Delivery person is required' : null),
      store_id: (value, values) => {
        if (values.delivery_type === 'store' && !value) {
          return 'Delivery location is required for store deliveries';
        }
        return null;
      },
      customer_name: (value, values) => {
        if (values.delivery_type === 'dropship' && !value) {
          return 'Customer name is required for dropship orders';
        }
        return null;
      },
      customer_address: (value, values) => {
        if (values.delivery_type === 'dropship' && !value) {
          return 'Customer address is required for dropship orders';
        }
        return null;
      },
      items: (value) => {
        if (!value || value.length === 0) {
          return 'At least one item is required';
        }
        // Validate each item
        for (let i = 0; i < value.length; i++) {
          const item = value[i];
          if (!item.product) {
            return `Item ${i + 1}: Product name is required`;
          }
          if (!item.quantity || item.quantity <= 0) {
            return `Item ${i + 1}: Quantity must be greater than 0`;
          }
          if (item.price_inc < 0) {
            return `Item ${i + 1}: Price cannot be negative`;
          }
        }
        return null;
      },
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => stockAPI.createPurchaseOrder(data),
    onSuccess: (purchaseOrder) => {
      notifications.show({
        title: 'Purchase Order Created',
        message: `PO ${purchaseOrder.reference_number} has been created successfully`,
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

  const updateMutation = useMutation({
    mutationFn: (data: any) => stockAPI.updatePurchaseOrder(Number(id), data),
    onSuccess: (purchaseOrder) => {
      notifications.show({
        title: 'Purchase Order Updated',
        message: `PO ${purchaseOrder.reference_number} has been updated successfully`,
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      queryClient.invalidateQueries({ queryKey: ['purchase-order', id] });
      navigate(`/purchase-orders/${id}`);
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to update purchase order',
        color: 'red',
      });
    },
  });

  // Populate form when editing
  useEffect(() => {
    if (existingPO && isEditMode) {
      form.setValues({
        manufacturer_id: existingPO.manufacturer_id?.toString() || '',
        delivery_person_id: existingPO.delivery_person_id?.toString() || '',
        delivery_type: existingPO.delivery_type || 'store',
        store_id: existingPO.store_id?.toString() || '',
        creating_store_id: existingPO.creating_store_id?.toString() || '',
        note_for_manufacturer: existingPO.note_for_manufacturer || '',
        customer_name: existingPO.customer_name || '',
        customer_phone: existingPO.customer_phone || '',
        customer_email: existingPO.customer_email || '',
        customer_address: existingPO.customer_address || '',
        items: existingPO.items.map((item: any) => ({
          id: item.id.toString(),
          product: item.product,
          associated_order_number: item.associated_order_number || '',
          price_inc: item.price_inc,
          quantity: item.quantity,
          discount_percent: item.discount_percent,
        })),
      });
    }
  }, [existingPO, isEditMode]);

  const handleSubmit = (values: PurchaseOrderFormValues) => {
    // Transform items to match backend expected format
    const items = values.items.map((item) => ({
      product: item.product,
      associated_order_number: item.associated_order_number || '',
      price_inc: item.price_inc,
      quantity: item.quantity,
      discount_percent: item.discount_percent,
    }));

    const payload = {
      manufacturer_id: parseInt(values.manufacturer_id),
      delivery_person_id: parseInt(values.delivery_person_id),
      delivery_type: values.delivery_type,
      store_id: values.delivery_type === 'store' && values.store_id ? parseInt(values.store_id) : null,
      creating_store_id: values.creating_store_id ? parseInt(values.creating_store_id) : null,
      note_for_manufacturer: values.note_for_manufacturer,
      customer_name: values.delivery_type === 'dropship' ? values.customer_name : null,
      customer_phone: values.delivery_type === 'dropship' ? values.customer_phone : null,
      customer_email: values.delivery_type === 'dropship' ? values.customer_email : null,
      customer_address: values.delivery_type === 'dropship' ? values.customer_address : null,
      items,
    };

    if (isEditMode) {
      updateMutation.mutate(payload);
    } else {
      createMutation.mutate(payload);
    }
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

  const manufacturers = manufacturersData?.results.map((m) => ({
    value: m.id.toString(),
    label: m.company_name,
  })) || [];

  const deliveryPersons = deliveryPersonsData?.results.map((dp) => ({
    value: dp.id.toString(),
    label: `${dp.name} (${dp.phone_number})`,
  })) || [];

  const stores = storesData?.results.map((s) => ({
    value: s.id.toString(),
    label: `${s.name} - ${s.location}`,
  })) || [];

  return (
    <Container fluid>
      <Stack gap="md">
        <Group justify="space-between">
          <Group>
            <ActionIcon variant="light" onClick={() => navigate('/purchase-orders')}>
              <IconArrowLeft size={16} />
            </ActionIcon>
            <div>
              <Title order={1}>{isEditMode ? 'Edit Purchase Order' : 'Create Purchase Order'}</Title>
              <Text c="dimmed">
                {isEditMode ? 'Update purchase order details' : 'Create a new purchase order for suppliers'}
              </Text>
            </div>
          </Group>
        </Group>

        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Grid>
            <Grid.Col span={8}>
              <Stack gap="md">
                <Paper shadow="xs" p="lg">
                  <Stack gap="md">
                    <Title order={3}>Purchase Order Information</Title>

                    <Select
                      label="Manufacturer / Supplier"
                      placeholder="Select manufacturer"
                      data={manufacturers}
                      required
                      searchable
                      {...form.getInputProps('manufacturer_id')}
                      disabled={loadingManufacturers}
                    />

                    <Grid>
                      <Grid.Col span={6}>
                        <Select
                          label="Delivery Person"
                          placeholder="Select delivery person"
                          data={deliveryPersons}
                          required
                          searchable
                          {...form.getInputProps('delivery_person_id')}
                          disabled={loadingDeliveryPersons}
                        />
                      </Grid.Col>
                      <Grid.Col span={6}>
                        <Select
                          label="Delivery Type"
                          placeholder="Select delivery type"
                          data={[
                            { value: 'store', label: 'Store' },
                            { value: 'dropship', label: 'Dropship' },
                          ]}
                          {...form.getInputProps('delivery_type')}
                        />
                      </Grid.Col>
                    </Grid>

                    {form.values.delivery_type === 'store' ? (
                      <Grid>
                        <Grid.Col span={6}>
                          <Select
                            label="Delivery Location (Receiving Store)"
                            placeholder="Select store"
                            data={stores}
                            required
                            searchable
                            {...form.getInputProps('store_id')}
                            disabled={loadingStores}
                          />
                        </Grid.Col>
                        <Grid.Col span={6}>
                          <Select
                            label="Creating Store (Optional)"
                            placeholder="Select creating store"
                            data={stores}
                            searchable
                            clearable
                            {...form.getInputProps('creating_store_id')}
                            disabled={loadingStores}
                          />
                        </Grid.Col>
                      </Grid>
                    ) : (
                      <Select
                        label="Creating Store (Optional)"
                        placeholder="Select creating store"
                        data={stores}
                        searchable
                        clearable
                        {...form.getInputProps('creating_store_id')}
                        disabled={loadingStores}
                      />
                    )}

                    {form.values.delivery_type === 'dropship' && (
                      <>
                        <Title order={4} mt="md">Customer Details</Title>
                        <Grid>
                          <Grid.Col span={6}>
                            <TextInput
                              label="Customer Name"
                              placeholder="Enter customer name"
                              required
                              {...form.getInputProps('customer_name')}
                            />
                          </Grid.Col>
                          <Grid.Col span={6}>
                            <TextInput
                              label="Customer Order Number"
                              placeholder="Order #"
                              {...form.getInputProps('items.0.associated_order_number')}
                            />
                          </Grid.Col>
                        </Grid>
                        <Grid>
                          <Grid.Col span={6}>
                            <TextInput
                              label="Customer Phone"
                              placeholder="Enter phone number"
                              {...form.getInputProps('customer_phone')}
                            />
                          </Grid.Col>
                          <Grid.Col span={6}>
                            <TextInput
                              label="Customer Email"
                              placeholder="customer@example.com"
                              type="email"
                              {...form.getInputProps('customer_email')}
                            />
                          </Grid.Col>
                        </Grid>
                        <Textarea
                          label="Customer Delivery Address"
                          placeholder="Enter full delivery address"
                          rows={2}
                          required
                          {...form.getInputProps('customer_address')}
                        />
                      </>
                    )}

                    <Textarea
                      label="Note for Manufacturer"
                      placeholder="Add any special instructions or notes for the manufacturer"
                      rows={3}
                      {...form.getInputProps('note_for_manufacturer')}
                    />
                  </Stack>
                </Paper>

                <Paper shadow="xs" p="lg">
                  <Stack gap="md">
                    <Title order={3}>Order Items</Title>
                    <POItemTable
                      items={form.values.items}
                      onChange={(items) => form.setFieldValue('items', items)}
                    />
                    {form.errors.items && (
                      <Text size="sm" c="red">{form.errors.items}</Text>
                    )}
                  </Stack>
                </Paper>
              </Stack>
            </Grid.Col>

            <Grid.Col span={4}>
              <Card shadow="xs" padding="lg" withBorder>
                <Stack gap="md">
                  <POTotals items={form.values.items} />

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
                      loading={createMutation.isPending || updateMutation.isPending}
                    >
                      {isEditMode ? 'Update Purchase Order' : 'Create Purchase Order'}
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
