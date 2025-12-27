import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
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
  Select,
  MultiSelect,
  ActionIcon,
  Alert,
  LoadingOverlay,
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
import type { StocktakeForm, Store, Stock } from '@/types/stock';

const CreateStocktake: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const hasPermission = useHasPermission();

  const form = useForm<StocktakeForm>({
    initialValues: {
      name: '',
      description: '',
      location_id: undefined,
      stock_ids: [],
    },
    validate: {
      name: (value) => (!value ? 'Name is required' : null),
    },
  });

  const { data: storesData, isLoading: isLoadingStores } = useQuery({
    queryKey: ['stores'],
    queryFn: () => stockAPI.getStores(),
  });

  const { data: stocksData, isLoading: isLoadingStocks } = useQuery({
    queryKey: ['stocks-for-stocktake'],
    queryFn: () => stockAPI.getStocks({
      page_size: 1000,
      ordering: 'item_name',
    }),
  });

  const createMutation = useMutation({
    mutationFn: (data: StocktakeForm) => stockAPI.createStocktake(data),
    onSuccess: (stocktake) => {
      notifications.show({
        title: 'Stocktake Created',
        message: 'Stocktake has been created successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['stocktakes'] });
      navigate(`/stocktake/${stocktake.id}`);
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error?.response?.data?.detail || 'Failed to create stocktake',
        color: 'red',
      });
    },
  });

  const handleSubmit = (values: StocktakeForm) => {
    createMutation.mutate(values);
  };

  const canCreateStocktake = hasPermission('create_stocktake');

  if (!canCreateStocktake) {
    return (
      <Container fluid>
        <Alert icon={<IconAlertCircle size={16} />} color="red">
          You don't have permission to create stocktakes.
        </Alert>
      </Container>
    );
  }

  const storeOptions = storesData?.results.map((store: Store) => ({
    value: store.id.toString(),
    label: store.name,
  })) || [];

  const stockOptions = stocksData?.results.map((stock: Stock) => ({
    value: stock.id.toString(),
    label: `${stock.item_name} (${stock.sku || 'No SKU'})`,
  })) || [];

  return (
    <Container fluid>
      <Stack gap="md">
        <Group justify="space-between">
          <Group>
            <ActionIcon variant="light" onClick={() => navigate('/stocktake')}>
              <IconArrowLeft size={16} />
            </ActionIcon>
            <div>
              <Title order={1}>Create Stocktake</Title>
              <Text c="dimmed">Create a new stock counting session</Text>
            </div>
          </Group>
        </Group>

        <Paper shadow="xs" p="lg">
          <form onSubmit={form.onSubmit(handleSubmit)}>
            <Stack gap="md">
              <TextInput
                label="Stocktake Name"
                placeholder="Enter stocktake name"
                required
                {...form.getInputProps('name')}
              />

              <Textarea
                label="Description"
                placeholder="Optional description of this stocktake"
                rows={3}
                {...form.getInputProps('description')}
              />

              <Select
                label="Location"
                placeholder="Select location (optional - leave empty for all locations)"
                data={storeOptions}
                value={form.values.location_id?.toString() || ''}
                onChange={(value) => form.setFieldValue('location_id', value ? parseInt(value) : undefined)}
                clearable
                searchable
                disabled={isLoadingStores}
              />

              <MultiSelect
                label="Stock Items"
                placeholder="Select specific items (optional - leave empty to include all items)"
                data={stockOptions}
                value={form.values.stock_ids?.map(id => id.toString()) || []}
                onChange={(values) => form.setFieldValue('stock_ids', values.map(v => parseInt(v)))}
                searchable
                disabled={isLoadingStocks}
                maxDropdownHeight={200}
              />

              <Alert color="blue" variant="light">
                <Text size="sm">
                  <strong>Note:</strong> If no location is selected, the stocktake will include items from all locations.
                  If no specific items are selected, all items in the chosen location(s) will be included.
                </Text>
              </Alert>

              <Group justify="right">
                <Button
                  variant="light"
                  onClick={() => navigate('/stocktake')}
                  disabled={createMutation.isPending}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  leftSection={<IconDeviceFloppy size={16} />}
                  loading={createMutation.isPending}
                >
                  Create Stocktake
                </Button>
              </Group>
            </Stack>
          </form>
        </Paper>
      </Stack>

      {(isLoadingStores || isLoadingStocks) && <LoadingOverlay visible />}
    </Container>
  );
};

export default CreateStocktake;