// @ts-nocheck
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
import { DateInput } from '@mantine/dates';
import {
  IconArrowLeft,
  IconDeviceFloppy,
  IconAlertCircle,
} from '@tabler/icons-react';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth, useHasPermission } from '@/states/authState';
import type { StocktakeForm, Store } from '@/types/stock';

const CreateStocktake: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const hasPermission = useHasPermission();

  const form = useForm<StocktakeForm>({
    initialValues: {
      title: '',
      description: '',
      audit_type: 'full',
      planned_start_date: new Date().toISOString().split('T')[0],
      planned_end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 7 days from now
      audit_location_ids: [],
      audit_category_ids: [],
    },
    validate: {
      title: (value) => (!value ? 'Title is required' : null),
      planned_start_date: (value) => (!value ? 'Start date is required' : null),
      planned_end_date: (value) => (!value ? 'End date is required' : null),
    },
  });

  const { data: storesData, isLoading: isLoadingStores } = useQuery({
    queryKey: ['stores'],
    queryFn: () => stockAPI.getStores(),
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
                label="Stocktake Title"
                placeholder="Enter stocktake title"
                required
                {...form.getInputProps('title')}
              />

              <Textarea
                label="Description"
                placeholder="Optional description of this stocktake"
                rows={3}
                {...form.getInputProps('description')}
              />

              <Select
                label="Audit Type"
                placeholder="Select audit type"
                data={[
                  { value: 'full', label: 'Full Stock Audit' },
                  { value: 'partial', label: 'Partial Audit' },
                  { value: 'cycle', label: 'Cycle Count' },
                  { value: 'location', label: 'Location Audit' },
                  { value: 'category', label: 'Category Audit' },
                  { value: 'spot_check', label: 'Spot Check' },
                ]}
                {...form.getInputProps('audit_type')}
              />

              <DateInput
                label="Planned Start Date"
                placeholder="Select start date"
                required
                valueFormat="YYYY-MM-DD"
                value={form.values.planned_start_date ? new Date(form.values.planned_start_date) : null}
                onChange={(date) => {
                  if (date instanceof Date) {
                    form.setFieldValue('planned_start_date', date.toISOString().split('T')[0]);
                  } else {
                    form.setFieldValue('planned_start_date', '');
                  }
                }}
              />

              <DateInput
                label="Planned End Date"
                placeholder="Select end date"
                required
                valueFormat="YYYY-MM-DD"
                value={form.values.planned_end_date ? new Date(form.values.planned_end_date) : null}
                onChange={(date) => {
                  if (date instanceof Date) {
                    form.setFieldValue('planned_end_date', date.toISOString().split('T')[0]);
                  } else {
                    form.setFieldValue('planned_end_date', '');
                  }
                }}
              />

              <MultiSelect
                label="Locations"
                placeholder="Select locations (optional - leave empty for all locations)"
                data={storeOptions}
                value={form.values.audit_location_ids?.map(id => id.toString()) || []}
                onChange={(values) => form.setFieldValue('audit_location_ids', values.map(v => parseInt(v)))}
                clearable
                searchable
                disabled={isLoadingStores}
              />

              <Alert color="blue" variant="light">
                <Text size="sm">
                  <strong>Note:</strong> If no locations are selected, the stocktake will include items from all locations.
                  Stock items will be automatically added when you start the audit.
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

      {isLoadingStores && <LoadingOverlay visible />}
    </Container>
  );
};

export default CreateStocktake;