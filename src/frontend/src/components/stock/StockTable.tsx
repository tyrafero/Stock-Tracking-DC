import React from 'react';
import {
  ActionIcon,
  Badge,
  Group,
  Text,
  Box,
  Tooltip,
  Stack,
  Avatar,
  Progress,
  Anchor,
  Card,
  Grid,
  Paper,
  ScrollArea
} from '@mantine/core';
import {
  IconEye,
  IconEdit,
  IconTrash,
  IconShoppingCart,
  IconPackage,
  IconAlertTriangle,
  IconReservedLine
} from '@tabler/icons-react';
import { useMediaQuery } from '@mantine/hooks';
import { DataTable, type DataTableColumn } from 'mantine-datatable';
import { useNavigate } from 'react-router-dom';
import { notifications } from '@mantine/notifications';

import type { Stock } from '@/types/stock';
import { useAuthStore, useHasPermission } from '@/states/authState';

interface StockTableProps {
  stocks: Stock[];
  totalCount: number;
  currentPage: number;
  totalPages: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  isLoading: boolean;
}

const StockTable: React.FC<StockTableProps> = ({
  stocks,
  totalCount,
  currentPage,
  totalPages,
  pageSize,
  onPageChange,
  isLoading
}) => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const hasPermission = useHasPermission();
  const isMobile = useMediaQuery('(max-width: 768px)');

  const handleView = (stock: Stock) => {
    navigate(`/stock/${stock.id}`);
  };

  const handleEdit = (stock: Stock) => {
    if (!hasPermission('stock.change_stock')) {
      notifications.show({
        title: 'Permission denied',
        message: 'You do not have permission to edit stock items',
        color: 'red',
      });
      return;
    }
    navigate(`/stock/${stock.id}/edit`);
  };

  const handleDelete = (stock: Stock) => {
    if (!hasPermission('stock.delete_stock')) {
      notifications.show({
        title: 'Permission denied',
        message: 'You do not have permission to delete stock items',
        color: 'red',
      });
      return;
    }
    // TODO: Implement delete confirmation modal
    console.log('Delete stock:', stock.id);
  };

  const getConditionColor = (condition: string) => {
    switch (condition) {
      case 'new':
        return 'green';
      case 'demo_unit':
        return 'blue';
      case 'bstock':
        return 'yellow';
      case 'open_box':
        return 'orange';
      case 'refurbished':
        return 'gray';
      default:
        return 'gray';
    }
  };

  const getStockLevelColor = (stock: Stock) => {
    if (stock.is_low_stock) return 'red';
    if (stock.available_for_sale === 0) return 'gray';
    if (stock.available_for_sale < stock.re_order) return 'yellow';
    return 'green';
  };

  const renderStockLevel = (stock: Stock) => {
    const totalStock = stock.total_across_locations || stock.total_stock || 0;
    const percentage = stock.re_order > 0
      ? Math.min((stock.available_for_sale / stock.re_order) * 100, 100)
      : stock.available_for_sale > 0 ? 100 : 0;

    return (
      <Stack gap={2}>
        <Group gap="xs" justify="space-between">
          <Text size="sm" fw={500}>
            {stock.available_for_sale} / {totalStock}
          </Text>
          {stock.is_low_stock && (
            <Tooltip label="Low stock warning">
              <IconAlertTriangle size="1rem" color="red" />
            </Tooltip>
          )}
        </Group>
        <Progress
          value={percentage}
          color={getStockLevelColor(stock)}
          size="sm"
        />
        {(stock.committed_quantity > 0 || stock.reserved_quantity > 0) && (
          <Group gap="xs">
            {stock.committed_quantity > 0 && (
              <Badge size="xs" variant="light" color="blue" leftSection={<IconShoppingCart size="0.8rem" />}>
                {stock.committed_quantity} committed
              </Badge>
            )}
            {stock.reserved_quantity > 0 && (
              <Badge size="xs" variant="light" color="orange" leftSection={<IconReservedLine size="0.8rem" />}>
                {stock.reserved_quantity} reserved
              </Badge>
            )}
          </Group>
        )}
      </Stack>
    );
  };

  // Mobile card layout component
  const MobileStockCard: React.FC<{ stock: Stock }> = ({ stock }) => (
    <Card shadow="sm" padding="md" mb="sm">
      <Group justify="space-between" mb="sm">
        <Group gap="sm">
          <Avatar
            src={stock.image_url}
            alt={stock.item_name}
            size="md"
            radius="sm"
          >
            <IconPackage size="1.2rem" />
          </Avatar>
          <Stack gap={2}>
            <Anchor
              component="button"
              onClick={() => handleView(stock)}
              fw={500}
              size="sm"
            >
              {stock.item_name}
            </Anchor>
            {stock.sku && (
              <Text size="xs" c="dimmed">
                SKU: {stock.sku}
              </Text>
            )}
          </Stack>
        </Group>
        <Group gap="xs">
          <ActionIcon
            size="sm"
            variant="light"
            color="blue"
            onClick={() => handleView(stock)}
          >
            <IconEye size="1rem" />
          </ActionIcon>
          {hasPermission('stock.change_stock') && (
            <ActionIcon
              size="sm"
              variant="light"
              color="yellow"
              onClick={() => handleEdit(stock)}
            >
              <IconEdit size="1rem" />
            </ActionIcon>
          )}
        </Group>
      </Group>

      <Grid gutter="xs">
        <Grid.Col span={6}>
          <Text size="xs" c="dimmed">Category</Text>
          <Text size="sm">{stock.category?.group || 'N/A'}</Text>
        </Grid.Col>
        <Grid.Col span={6}>
          <Text size="xs" c="dimmed">Condition</Text>
          <Badge
            color={getConditionColor(stock.condition)}
            variant="light"
            size="xs"
          >
            {stock.condition_display}
          </Badge>
        </Grid.Col>
        <Grid.Col span={12}>
          <Text size="xs" c="dimmed">Stock Level</Text>
          {renderStockLevel(stock)}
        </Grid.Col>
        {stock.locations && stock.locations.length > 0 && (
          <Grid.Col span={12}>
            <Text size="xs" c="dimmed">Locations</Text>
            <Stack gap={2}>
              {stock.locations.map((loc) => (
                <Text key={loc.id} size="xs">
                  {loc.store.name}: {loc.quantity} {loc.aisle && `(${loc.aisle})`}
                </Text>
              ))}
            </Stack>
          </Grid.Col>
        )}
      </Grid>
    </Card>
  );

  const columns: DataTableColumn<Stock>[] = [
    {
      accessor: 'image_url',
      title: '',
      width: 60,
      hidden: isMobile,
      render: (stock: Stock) => (
        <Avatar
          src={stock.image_url}
          alt={stock.item_name}
          size="sm"
          radius="sm"
        >
          <IconPackage size="1rem" />
        </Avatar>
      ),
    },
    {
      accessor: 'item_name',
      title: 'Item Name',
      width: 250,
      textAlign: 'left',
      render: (stock: Stock) => (
        <Stack gap={2} style={{ textAlign: 'left' }}>
          <Anchor
            component="button"
            onClick={() => handleView(stock)}
            fw={500}
            truncate
            style={{ textAlign: 'left', display: 'block' }}
          >
            {stock.item_name}
          </Anchor>
          {stock.sku && (
            <Text size="xs" color="dimmed" truncate style={{ textAlign: 'left' }}>
              SKU: {stock.sku}
            </Text>
          )}
        </Stack>
      ),
    },
    {
      accessor: 'category.group',
      title: 'Category',
      width: 120,
      hidden: isMobile,
      textAlign: 'left',
      render: (stock: Stock) => (
        <Text size="sm" truncate style={{ textAlign: 'left' }}>
          {stock.category?.group || 'N/A'}
        </Text>
      ),
    },
    {
      accessor: 'condition',
      title: 'Condition',
      width: 100,
      hidden: isMobile,
      render: (stock: Stock) => (
        <Badge
          color={getConditionColor(stock.condition)}
          variant="light"
          size="sm"
        >
          {stock.condition_display}
        </Badge>
      ),
    },
    {
      accessor: 'location.name',
      title: 'Location',
      width: 180,
      hidden: isMobile,
      textAlign: 'left',
      render: (stock: Stock) => (
        <Stack gap={4} style={{ textAlign: 'left' }}>
          {stock.locations && stock.locations.length > 0 ? (
            stock.locations.map((loc) => (
              <div key={loc.id}>
                <Text size="sm" fw={500} style={{ textAlign: 'left' }}>
                  {loc.store.name}: {loc.quantity}
                </Text>
                {loc.aisle && (
                  <Text size="xs" c="dimmed" style={{ textAlign: 'left' }}>
                    Aisle: {loc.aisle}
                  </Text>
                )}
              </div>
            ))
          ) : (
            <Text size="sm" c="dimmed" style={{ textAlign: 'left' }}>
              N/A
            </Text>
          )}
        </Stack>
      ),
    },
    {
      accessor: 'available_for_sale',
      title: 'Stock Level',
      width: 150,
      render: renderStockLevel,
    },
    {
      accessor: 'last_updated',
      title: 'Last Updated',
      width: 120,
      hidden: isMobile,
      render: (stock: Stock) => (
        <Text size="sm">
          {new Date(stock.last_updated).toLocaleDateString()}
        </Text>
      ),
    },
    {
      accessor: 'actions',
      title: 'Actions',
      width: 120,
textAlign: 'center',
      render: (stock: Stock) => (
        <Group gap="xs" justify="center">
          <ActionIcon
            size="sm"
            variant="light"
            color="blue"
            onClick={() => handleView(stock)}
          >
            <IconEye size="1rem" />
          </ActionIcon>
          {hasPermission('stock.change_stock') && (
            <ActionIcon
              size="sm"
              variant="light"
              color="yellow"
              onClick={() => handleEdit(stock)}
            >
              <IconEdit size="1rem" />
            </ActionIcon>
          )}
          {hasPermission('stock.delete_stock') && (
            <ActionIcon
              size="sm"
              variant="light"
              color="red"
              onClick={() => handleDelete(stock)}
            >
              <IconTrash size="1rem" />
            </ActionIcon>
          )}
        </Group>
      ),
    },
  ];

  return (
    <Box>
      {isMobile ? (
        // Mobile Card Layout
        <Box>
          {isLoading ? (
            <Text ta="center" py="xl">Loading stock data...</Text>
          ) : stocks.length === 0 ? (
            <Text ta="center" py="xl" c="dimmed">No stock items found</Text>
          ) : (
            stocks.map((stock) => (
              <MobileStockCard key={stock.id} stock={stock} />
            ))
          )}

          {/* Mobile Pagination */}
          {totalCount > pageSize && (
            <Group justify="center" mt="md">
              <Text size="sm" c="dimmed">
                Page {currentPage} of {Math.ceil(totalCount / pageSize)}
              </Text>
              <Group gap="xs">
                <ActionIcon
                  size="sm"
                  disabled={currentPage === 1}
                  onClick={() => onPageChange(currentPage - 1)}
                >
                  ←
                </ActionIcon>
                <ActionIcon
                  size="sm"
                  disabled={currentPage === Math.ceil(totalCount / pageSize)}
                  onClick={() => onPageChange(currentPage + 1)}
                >
                  →
                </ActionIcon>
              </Group>
            </Group>
          )}
        </Box>
      ) : (
        // Desktop Table Layout
        <ScrollArea>
          <DataTable
            columns={columns}
            records={stocks}
            fetching={isLoading}
            totalRecords={totalCount}
            recordsPerPage={pageSize}
            page={currentPage}
            onPageChange={onPageChange}
            paginationActiveBackgroundColor={{ light: 'blue', dark: 'blue' }}
            loadingText="Loading stock data..."
            noRecordsText={!isLoading && stocks.length === 0 ? "No stock items found" : ""}
            noRecordsIcon={stocks.length > 0 ? <></> : undefined}
            minHeight={400}
            striped
            highlightOnHover
            withTableBorder={false}
            borderRadius="sm"
            shadow="sm"
            verticalSpacing="sm"
            horizontalSpacing="md"
            // Custom styling for better appearance
            styles={{
              header: {
                backgroundColor: 'var(--mantine-color-gray-1)',
                fontWeight: 600,
              },
            }}
          />
        </ScrollArea>
      )}
    </Box>
  );
};

export default StockTable;