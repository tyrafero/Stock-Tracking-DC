import React, { useState } from 'react';
import {
  Container,
  Title,
  Text,
  Paper,
  Group,
  Button,
  Stack,
  TextInput,
  NumberInput,
  Textarea,
  Select,
  Grid,
  ActionIcon,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { IconArrowLeft, IconDeviceFloppy } from '@tabler/icons-react';

import { stockAPI } from '@/api/stock';
import type { StockCreate } from '@/types/stock';

const CreateStock: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch categories
  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: () => stockAPI.getCategories(),
  });

  // Fetch stores
  const { data: storesData } = useQuery({
    queryKey: ['stores'],
    queryFn: () => stockAPI.getStores(),
  });

  const categories = categoriesData?.results || [];
  const stores = storesData?.results || [];

  const form = useForm<StockCreate>({
    initialValues: {
      item_name: '',
      sku: '',
      category_id: undefined,
      condition: 'new',
      location_id: undefined,
      aisle: '',
      quantity: 0,
      re_order: 0,
      note: '',
      image_url: '',
    },
    validate: {
      item_name: (value) => (!value ? 'Item name is required' : null),
      quantity: (value) => (value === undefined || value < 0 ? 'Quantity must be 0 or greater' : null),
      re_order: (value) => (value === undefined || value < 0 ? 'Re-order level must be 0 or greater' : null),
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: StockCreate) => stockAPI.createStock(data),
    onSuccess: (data) => {
      notifications.show({
        title: 'Stock Created',
        message: 'Stock item has been created successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stocks'] });
      navigate(`/stock/${data.id}`);
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to create stock item',
        color: 'red',
      });
    },
  });

  const handleSubmit = (values: StockCreate) => {
    createMutation.mutate(values);
  };

  return (
    <Container fluid>
      <Group justify="space-between" mb="xl">
        <Group>
          <ActionIcon
            variant="light"
            size="lg"
            onClick={() => navigate('/stock')}
          >
            <IconArrowLeft size={18} />
          </ActionIcon>
          <div>
            <Title order={1}>Add New Stock</Title>
            <Text c="dimmed">Create a new stock item in the system</Text>
          </div>
        </Group>
      </Group>

      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Grid>
          <Grid.Col span={{ base: 12, md: 8 }}>
            <Paper shadow="xs" p="md" mb="md">
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
                  placeholder="Enter SKU (Stock Keeping Unit)"
                  description="Unique identifier for this item"
                  {...form.getInputProps('sku')}
                />

                <Select
                  label="Category"
                  placeholder="Select category"
                  data={categories.map((cat) => ({
                    value: cat.id.toString(),
                    label: cat.group,
                  }))}
                  searchable
                  clearable
                  {...form.getInputProps('category_id')}
                  onChange={(value) => form.setFieldValue('category_id', value ? Number(value) : undefined)}
                />

                <Select
                  label="Condition"
                  placeholder="Select condition"
                  required
                  data={[
                    { value: 'new', label: 'New' },
                    { value: 'demo_unit', label: 'Demo Unit' },
                    { value: 'bstock', label: 'B-Stock' },
                    { value: 'open_box', label: 'Open Box' },
                    { value: 'refurbished', label: 'Refurbished' },
                  ]}
                  {...form.getInputProps('condition')}
                />

                <TextInput
                  label="Image URL"
                  placeholder="Enter image URL (optional)"
                  description="URL to display an image of the item"
                  {...form.getInputProps('image_url')}
                />

                <Textarea
                  label="Notes"
                  placeholder="Enter any additional notes about this item"
                  autosize
                  minRows={3}
                  maxRows={6}
                  {...form.getInputProps('note')}
                />
              </Stack>
            </Paper>
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 4 }}>
            <Paper shadow="xs" p="md" mb="md">
              <Title order={4} mb="md">Location & Quantity</Title>
              <Stack gap="md">
                <Select
                  label="Store Location"
                  placeholder="Select store"
                  description="Primary store location for this item"
                  data={stores.map((store) => ({
                    value: store.id.toString(),
                    label: store.name,
                  }))}
                  searchable
                  clearable
                  {...form.getInputProps('location_id')}
                  onChange={(value) => form.setFieldValue('location_id', value ? Number(value) : undefined)}
                />

                <TextInput
                  label="Aisle"
                  placeholder="e.g., A1, B2, C3"
                  description="Specific aisle or section within the store"
                  {...form.getInputProps('aisle')}
                />

                <NumberInput
                  label="Initial Quantity"
                  placeholder="Enter quantity"
                  min={0}
                  required
                  {...form.getInputProps('quantity')}
                />

                <NumberInput
                  label="Re-order Level"
                  placeholder="Enter re-order level"
                  description="Alert when stock falls below this level"
                  min={0}
                  {...form.getInputProps('re_order')}
                />
              </Stack>
            </Paper>

            <Paper shadow="xs" p="md">
              <Stack gap="md">
                <Button
                  type="submit"
                  fullWidth
                  leftSection={<IconDeviceFloppy size="1rem" />}
                  loading={createMutation.isPending}
                >
                  Create Stock Item
                </Button>
                <Button
                  variant="light"
                  fullWidth
                  onClick={() => navigate('/stock')}
                  disabled={createMutation.isPending}
                >
                  Cancel
                </Button>
              </Stack>
            </Paper>
          </Grid.Col>
        </Grid>
      </form>
    </Container>
  );
};

export default CreateStock;
