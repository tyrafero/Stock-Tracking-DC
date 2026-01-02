import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
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
  ActionIcon,
  TextInput,
  NumberInput,
  Textarea,
  Select,
  Table,
  Badge,
  Pagination,
  LoadingOverlay,
  Alert,
} from '@mantine/core';
import {
  IconArrowLeft,
  IconSearch,
  IconPlus,
  IconAlertCircle,
  IconPackage,
  IconBuilding,
  IconArrowRight,
} from '@tabler/icons-react';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth } from '@/states/authState';

interface CreateTransferForm {
  stock_id: string;
  from_location: string;
  quantity: number;
  to_location: string;
  transfer_type: string;
  transfer_reason: string;
  customer_name?: string;
  customer_phone?: string;
  notes: string;
}

const CreateTransfer: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const stockIdFromUrl = searchParams.get('stock_id');
  const [selectedStock, setSelectedStock] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const form = useForm<CreateTransferForm>({
    initialValues: {
      stock_id: '',
      from_location: '',
      quantity: 1,
      to_location: '',
      transfer_type: 'general',
      transfer_reason: '',
      customer_name: '',
      customer_phone: '',
      notes: '',
    },
    validate: {
      stock_id: (value) => (!value ? 'Please select a stock item' : null),
      from_location: (value) => (!value ? 'Please select a source store' : null),
      quantity: (value) => (value <= 0 ? 'Quantity must be greater than 0' : null),
      to_location: (value) => (!value ? 'Please select a destination store' : null),
      transfer_type: (value) => (!value ? 'Please select a transfer type' : null),
      transfer_reason: (value) => (!value ? 'Please enter a transfer reason' : null),
      customer_name: (value, values) =>
        values.transfer_type === 'customer_collection' && !value ? 'Customer name is required for customer collections' : null,
      customer_phone: (value, values) =>
        values.transfer_type === 'customer_collection' && !value ? 'Customer phone is required for customer collections' : null,
    },
  });

  const { data: stockData, isLoading: stockLoading } = useQuery({
    queryKey: ['stock-list', searchQuery, currentPage],
    queryFn: () => stockAPI.getStockList({
      search: searchQuery,
      page: currentPage,
      page_size: 10,
    }),
  });

  const { data: storesData } = useQuery({
    queryKey: ['stores'],
    queryFn: () => stockAPI.getStores(),
  });

  // Fetch stock from URL parameter if provided
  const { data: preSelectedStock } = useQuery({
    queryKey: ['stock', stockIdFromUrl],
    queryFn: () => stockAPI.getStock(Number(stockIdFromUrl)),
    enabled: !!stockIdFromUrl,
  });

  // Auto-select stock from URL parameter
  useEffect(() => {
    if (preSelectedStock && !selectedStock) {
      handleStockSelect(preSelectedStock);
    }
  }, [preSelectedStock]);

  const createMutation = useMutation({
    mutationFn: (data: CreateTransferForm) => stockAPI.createTransfer({
      stock_id: Number(data.stock_id),
      from_location_id: Number(data.from_location),
      to_location_id: Number(data.to_location),
      quantity: data.quantity,
      transfer_type: data.transfer_type,
      transfer_reason: data.transfer_reason,
      customer_name: data.customer_name || undefined,
      customer_phone: data.customer_phone || undefined,
      notes: data.notes,
    }),
    onSuccess: (data) => {
      notifications.show({
        title: 'Transfer Created',
        message: 'Transfer has been created successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['transfers'] });
      navigate(`/transfers/${data.id}`);
    },
    onError: (error) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to create transfer',
        color: 'red',
      });
    },
  });

  const handleStockSelect = (stock: any) => {
    setSelectedStock(stock);
    form.setFieldValue('stock_id', stock.id.toString());

    // Auto-suggest quantity based on available stock
    const maxQuantity = Math.min(stock.available_for_sale, 10);
    if (maxQuantity > 0) {
      form.setFieldValue('quantity', maxQuantity);
    }
  };

  const handleSubmit = (values: CreateTransferForm) => {
    if (!selectedStock) {
      notifications.show({
        title: 'Error',
        message: 'Please select a stock item',
        color: 'red',
      });
      return;
    }

    if (values.quantity > selectedStock.available_for_sale) {
      notifications.show({
        title: 'Error',
        message: `Quantity cannot exceed available stock (${selectedStock.available_for_sale})`,
        color: 'red',
      });
      return;
    }

    if (values.to_location === selectedStock.location?.name) {
      notifications.show({
        title: 'Error',
        message: 'Destination location cannot be the same as current location',
        color: 'red',
      });
      return;
    }

    createMutation.mutate(values);
  };

  const getAvailabilityColor = (available: number, total: number) => {
    const ratio = available / total;
    if (ratio > 0.5) return 'green';
    if (ratio > 0.2) return 'yellow';
    return 'red';
  };

  const getSourceStoreOptions = () => {
    if (!selectedStock || !selectedStock.locations) return [];

    // Only show stores where stock actually exists with quantity > 0
    return selectedStock.locations
      .filter((loc: any) => loc.quantity > 0)
      .map((loc: any) => ({
        value: loc.store.id.toString(),
        label: `${loc.store.name} (${loc.quantity} units)`,
      }));
  };

  const getDestinationStoreOptions = () => {
    if (!storesData || !selectedStock || !form.values.from_location) return [];

    // Get stores from the paginated response
    const stores = storesData.results || [];

    // Filter out the selected source store
    return stores
      .filter((store: any) => store.id.toString() !== form.values.from_location)
      .map((store: any) => ({
        value: store.id.toString(),
        label: store.name,
      }));
  };

  return (
    <Container fluid>
      <Group justify="space-between" mb="xl">
        <Group>
          <ActionIcon
            variant="light"
            size="lg"
            onClick={() => navigate('/transfers')}
          >
            <IconArrowLeft size={18} />
          </ActionIcon>
          <div>
            <Title order={1}>Create New Transfer</Title>
            <Text c="dimmed">Transfer stock between locations</Text>
          </div>
        </Group>
      </Group>

      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Grid>
          <Grid.Col span={{ base: 12, md: 8 }}>
            <Paper shadow="xs" p="md" mb="md">
              <Title order={3} mb="md">Select Stock Item</Title>

              <TextInput
                placeholder="Search stock items..."
                leftSection={<IconSearch size={16} />}
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setCurrentPage(1);
                }}
                mb="md"
              />

              {stockLoading ? (
                <LoadingOverlay visible />
              ) : stockData?.results.length === 0 ? (
                <Alert icon={<IconAlertCircle size={16} />} color="blue">
                  No stock items found. Try adjusting your search.
                </Alert>
              ) : (
                <>
                  <Table striped highlightOnHover>
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>Item</Table.Th>
                        <Table.Th>Location</Table.Th>
                        <Table.Th>Available</Table.Th>
                        <Table.Th>Total</Table.Th>
                        <Table.Th>Action</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {stockData?.results.map((stock: any) => (
                        <Table.Tr
                          key={stock.id}
                          style={{
                            backgroundColor: selectedStock?.id === stock.id ? '#e3f2fd' : undefined,
                            cursor: 'pointer'
                          }}
                          onClick={() => handleStockSelect(stock)}
                        >
                          <Table.Td>
                            <Group>
                              <IconPackage size={16} />
                              <div>
                                <Text fw={500}>{stock.item_name}</Text>
                                {stock.sku && (
                                  <Text size="sm" c="dimmed">SKU: {stock.sku}</Text>
                                )}
                              </div>
                            </Group>
                          </Table.Td>
                          <Table.Td>
                            <Group gap="xs">
                              <IconBuilding size={14} />
                              <Text size="sm">{stock.location?.name || 'N/A'}</Text>
                            </Group>
                          </Table.Td>
                          <Table.Td>
                            <Badge
                              color={getAvailabilityColor(stock.available_for_sale, stock.quantity)}
                              variant="light"
                            >
                              {stock.available_for_sale}
                            </Badge>
                          </Table.Td>
                          <Table.Td>{stock.quantity}</Table.Td>
                          <Table.Td>
                            <Button
                              size="xs"
                              variant={selectedStock?.id === stock.id ? "filled" : "light"}
                              leftSection={<IconPlus size={12} />}
                              disabled={stock.available_for_sale === 0}
                              onClick={(e) => {
                                e.stopPropagation();
                                handleStockSelect(stock);
                              }}
                            >
                              {selectedStock?.id === stock.id ? 'Selected' : 'Select'}
                            </Button>
                          </Table.Td>
                        </Table.Tr>
                      ))}
                    </Table.Tbody>
                  </Table>

                  {stockData && stockData.count > 10 && (
                    <Group justify="center" mt="md">
                      <Pagination
                        value={currentPage}
                        onChange={setCurrentPage}
                        total={Math.ceil(stockData.count / 10)}
                        size="sm"
                      />
                    </Group>
                  )}
                </>
              )}
            </Paper>

            {selectedStock && (
              <Paper shadow="xs" p="md">
                <Title order={4} mb="md">Selected Item Details</Title>
                <Grid>
                  <Grid.Col span={6}>
                    <Text size="sm" c="dimmed">Item Name</Text>
                    <Text fw={500}>{selectedStock.item_name}</Text>
                  </Grid.Col>
                  <Grid.Col span={6}>
                    <Text size="sm" c="dimmed">Current Location</Text>
                    <Text fw={500}>{selectedStock.location?.name || 'N/A'}</Text>
                  </Grid.Col>
                  <Grid.Col span={6}>
                    <Text size="sm" c="dimmed">Available Quantity</Text>
                    <Text fw={500} c="green">{selectedStock.available_for_sale}</Text>
                  </Grid.Col>
                  <Grid.Col span={6}>
                    <Text size="sm" c="dimmed">Total Stock</Text>
                    <Text fw={500}>{selectedStock.quantity}</Text>
                  </Grid.Col>
                </Grid>
              </Paper>
            )}
          </Grid.Col>

          <Grid.Col span={{ base: 12, md: 4 }}>
            <Paper shadow="xs" p="md" mb="md">
              <Title order={4} mb="md">Transfer Details</Title>
              <Stack gap="md">
                <Select
                  label="From Store (Source)"
                  placeholder="Select source store"
                  data={getSourceStoreOptions()}
                  searchable
                  leftSection={<IconBuilding size={16} />}
                  {...form.getInputProps('from_location')}
                  disabled={!selectedStock}
                />

                <Select
                  label="To Store (Destination)"
                  placeholder="Select destination store"
                  data={getDestinationStoreOptions()}
                  searchable
                  leftSection={<IconBuilding size={16} />}
                  {...form.getInputProps('to_location')}
                  disabled={!selectedStock || !form.values.from_location}
                />

                <NumberInput
                  label="Quantity to Transfer"
                  placeholder="Enter quantity"
                  min={1}
                  max={selectedStock?.available_for_sale || undefined}
                  {...form.getInputProps('quantity')}
                  disabled={!selectedStock || !form.values.from_location}
                />

                <Select
                  label="Transfer Type"
                  placeholder="Select transfer type"
                  required
                  data={[
                    { value: 'general', label: 'General Transfer' },
                    { value: 'restock', label: 'Restock' },
                    { value: 'customer_collection', label: 'Customer Collection' },
                  ]}
                  {...form.getInputProps('transfer_type')}
                  description="Type of transfer operation"
                />

                <TextInput
                  label="Transfer Reason"
                  placeholder="e.g., Customer collection, Restock, Store transfer..."
                  required
                  {...form.getInputProps('transfer_reason')}
                  description="Reason for this transfer"
                />

                {form.values.transfer_type === 'customer_collection' && (
                  <>
                    <TextInput
                      label="Customer Name"
                      placeholder="Enter customer name"
                      required
                      {...form.getInputProps('customer_name')}
                    />

                    <TextInput
                      label="Customer Phone"
                      placeholder="Enter customer phone number"
                      required
                      {...form.getInputProps('customer_phone')}
                    />
                  </>
                )}

                <Textarea
                  label="Notes (Optional)"
                  placeholder="Add any additional notes about this transfer..."
                  autosize
                  minRows={3}
                  maxRows={5}
                  {...form.getInputProps('notes')}
                />
              </Stack>
            </Paper>

            {selectedStock && form.values.to_location && (
              <Paper shadow="xs" p="md" mb="md">
                <Title order={5} mb="md">Transfer Summary</Title>
                <Stack gap="xs">
                  <Group justify="space-between">
                    <Text size="sm">Item:</Text>
                    <Text size="sm" fw={500}>{selectedStock.item_name}</Text>
                  </Group>
                  <Group justify="space-between">
                    <Text size="sm">Quantity:</Text>
                    <Text size="sm" fw={500}>{form.values.quantity}</Text>
                  </Group>
                  <Group justify="space-between" align="flex-start">
                    <Text size="sm">Route:</Text>
                    <div style={{ textAlign: 'right' }}>
                      <Group gap="xs" justify="flex-end">
                        <Text size="sm" fw={500}>{selectedStock.location?.name || 'N/A'}</Text>
                        <IconArrowRight size={14} />
                        <Text size="sm" fw={500}>{form.values.to_location}</Text>
                      </Group>
                    </div>
                  </Group>
                  <Group justify="space-between">
                    <Text size="sm">Remaining at Source:</Text>
                    <Text
                      size="sm"
                      fw={500}
                      c={selectedStock.available_for_sale - form.values.quantity >= 0 ? 'green' : 'red'}
                    >
                      {selectedStock.available_for_sale - form.values.quantity}
                    </Text>
                  </Group>
                </Stack>
              </Paper>
            )}

            <Group>
              <Button
                type="submit"
                fullWidth
                loading={createMutation.isPending}
                disabled={!selectedStock || !form.values.from_location || !form.values.to_location || !form.values.transfer_reason || form.values.quantity === 0}
              >
                Create Transfer
              </Button>
            </Group>
          </Grid.Col>
        </Grid>
      </form>
    </Container>
  );
};

export default CreateTransfer;