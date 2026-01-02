import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Title,
  Paper,
  TextInput,
  Textarea,
  Select,
  Button,
  Group,
  Stack,
  NumberInput,
  Box,
  Text,
  Table,
  ActionIcon,
  LoadingOverlay,
  Divider,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { IconDeviceFloppy, IconArrowLeft, IconEdit } from '@tabler/icons-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { stockAPI } from '@/api/stock';
import type { Stock, StockUpdate, Category, StockLocation } from '@/types/stock';

const EditStock: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [editingAisleId, setEditingAisleId] = useState<number | null>(null);
  const [aisleValues, setAisleValues] = useState<Record<number, string>>({});

  // Fetch stock data
  const { data: stock, isLoading: isLoadingStock, error: stockError } = useQuery<Stock>({
    queryKey: ['stock', id],
    queryFn: () => stockAPI.getStock(parseInt(id!)),
    enabled: !!id,
  });

  // Fetch categories
  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: () => stockAPI.getCategories(),
  });

  const categories = categoriesData?.results || [];

  // Initialize form
  const form = useForm<StockUpdate>({
    initialValues: {
      item_name: '',
      sku: '',
      condition: 'new',
      re_order: 0,
      note: '',
      category_id: undefined,
    },
  });

  // Populate form when stock data is loaded
  useEffect(() => {
    if (stock) {
      form.setValues({
        item_name: stock.item_name || '',
        sku: stock.sku || '',
        condition: stock.condition || 'new',
        re_order: stock.re_order || 0,
        note: stock.note || '',
        category_id: stock.category?.id,
      });

      // Initialize aisle values
      const aisles: Record<number, string> = {};
      stock.locations?.forEach((loc) => {
        aisles[loc.id] = loc.aisle || '';
      });
      setAisleValues(aisles);
    }
  }, [stock]);

  // Update stock mutation
  const updateStockMutation = useMutation({
    mutationFn: (data: StockUpdate) => stockAPI.updateStock(parseInt(id!), data),
    onSuccess: () => {
      notifications.show({
        title: 'Success',
        message: 'Stock updated successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stock', id] });
      queryClient.invalidateQueries({ queryKey: ['stocks'] });
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to update stock',
        color: 'red',
      });
    },
  });

  // Update stock location mutation
  const updateLocationMutation = useMutation({
    mutationFn: ({ locationId, aisle }: { locationId: number; aisle: string }) =>
      stockAPI.updateStockLocation(locationId, { aisle }),
    onSuccess: () => {
      notifications.show({
        title: 'Success',
        message: 'Aisle updated successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stock', id] });
      setEditingAisleId(null);
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to update aisle',
        color: 'red',
      });
    },
  });

  const handleSubmit = (values: StockUpdate) => {
    updateStockMutation.mutate(values);
  };

  const handleUpdateAisle = (locationId: number) => {
    const aisle = aisleValues[locationId] || '';
    updateLocationMutation.mutate({ locationId, aisle });
  };

  const conditionOptions = [
    { value: 'new', label: 'New' },
    { value: 'demo_unit', label: 'Demo Unit' },
    { value: 'bstock', label: 'B-Stock' },
    { value: 'open_box', label: 'Open Box' },
    { value: 'refurbished', label: 'Refurbished' },
  ];

  if (isLoadingStock) {
    return (
      <Box pos="relative" mih={400}>
        <LoadingOverlay visible />
      </Box>
    );
  }

  if (stockError) {
    return (
      <Box>
        <Group mb="md">
          <ActionIcon
            variant="subtle"
            onClick={() => navigate('/stock')}
            size="lg"
          >
            <IconArrowLeft size={20} />
          </ActionIcon>
          <Title order={1}>Error Loading Stock</Title>
        </Group>
        <Text c="red">
          {(stockError as any)?.message || 'Failed to load stock details'}
        </Text>
      </Box>
    );
  }

  if (!stock) {
    return (
      <Box>
        <Group mb="md">
          <ActionIcon
            variant="subtle"
            onClick={() => navigate('/stock')}
            size="lg"
          >
            <IconArrowLeft size={20} />
          </ActionIcon>
          <Title order={1}>Stock Not Found</Title>
        </Group>
        <Text>The requested stock item could not be found.</Text>
      </Box>
    );
  }

  return (
    <Box>
      <Group justify="space-between" mb="md">
        <Group>
          <ActionIcon
            variant="subtle"
            onClick={() => navigate(`/stock/${id}`)}
            size="lg"
          >
            <IconArrowLeft size={20} />
          </ActionIcon>
          <Title order={1}>Edit Stock</Title>
        </Group>
      </Group>

      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack gap="lg">
          {/* Basic Information */}
          <Paper p="md" shadow="sm" withBorder>
            <Title order={3} mb="md">Basic Information</Title>
            <Stack gap="md">
              <TextInput
                label="Item Name"
                placeholder="Enter item name"
                required
                {...form.getInputProps('item_name')}
              />

              <TextInput
                label="SKU"
                placeholder="Enter SKU"
                {...form.getInputProps('sku')}
              />

              <Select
                label="Category"
                placeholder="Select category"
                data={categories.map((cat: Category) => ({
                  value: cat.id.toString(),
                  label: cat.group,
                }))}
                value={form.values.category_id?.toString()}
                onChange={(value) =>
                  form.setFieldValue('category_id', value ? parseInt(value) : undefined)
                }
                clearable
              />

              <Select
                label="Condition"
                placeholder="Select condition"
                data={conditionOptions}
                {...form.getInputProps('condition')}
              />

              <NumberInput
                label="Re-order Level"
                placeholder="Enter re-order level"
                min={0}
                {...form.getInputProps('re_order')}
              />

              <Textarea
                label="Notes"
                placeholder="Enter any notes"
                minRows={3}
                {...form.getInputProps('note')}
              />
            </Stack>
          </Paper>

          {/* Stock Locations */}
          <Paper p="md" shadow="sm" withBorder>
            <Title order={3} mb="md">Stock Locations</Title>
            <Text size="sm" c="dimmed" mb="md">
              View stock quantities across locations and update aisle information
            </Text>

            {stock.locations && stock.locations.length > 0 ? (
              <Table striped highlightOnHover>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Store</Table.Th>
                    <Table.Th>Quantity</Table.Th>
                    <Table.Th>Aisle</Table.Th>
                    <Table.Th>Actions</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {stock.locations.map((location: StockLocation) => (
                    <Table.Tr key={location.id}>
                      <Table.Td>
                        <Text fw={500}>{location.store.name}</Text>
                      </Table.Td>
                      <Table.Td>
                        <Text>{location.quantity}</Text>
                      </Table.Td>
                      <Table.Td>
                        {editingAisleId === location.id ? (
                          <TextInput
                            size="xs"
                            placeholder="e.g., A1, B2, C3"
                            value={aisleValues[location.id] || ''}
                            onChange={(e) =>
                              setAisleValues({
                                ...aisleValues,
                                [location.id]: e.target.value,
                              })
                            }
                            style={{ maxWidth: 150 }}
                          />
                        ) : (
                          <Text size="sm">
                            {location.aisle || <Text c="dimmed">Not set</Text>}
                          </Text>
                        )}
                      </Table.Td>
                      <Table.Td>
                        {editingAisleId === location.id ? (
                          <Group gap="xs">
                            <Button
                              size="xs"
                              onClick={() => handleUpdateAisle(location.id)}
                              loading={updateLocationMutation.isPending}
                            >
                              Save
                            </Button>
                            <Button
                              size="xs"
                              variant="subtle"
                              onClick={() => {
                                setEditingAisleId(null);
                                setAisleValues({
                                  ...aisleValues,
                                  [location.id]: location.aisle || '',
                                });
                              }}
                            >
                              Cancel
                            </Button>
                          </Group>
                        ) : (
                          <ActionIcon
                            size="sm"
                            variant="subtle"
                            onClick={() => setEditingAisleId(location.id)}
                          >
                            <IconEdit size={16} />
                          </ActionIcon>
                        )}
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            ) : (
              <Text c="dimmed">No stock locations found</Text>
            )}
          </Paper>

          <Divider />

          {/* Action Buttons */}
          <Group justify="flex-end">
            <Button
              variant="subtle"
              onClick={() => navigate(`/stock/${id}`)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              leftSection={<IconDeviceFloppy size={16} />}
              loading={updateStockMutation.isPending}
            >
              Save Changes
            </Button>
          </Group>
        </Stack>
      </form>
    </Box>
  );
};

export default EditStock;
