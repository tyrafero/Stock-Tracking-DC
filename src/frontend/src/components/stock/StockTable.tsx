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
  Anchor
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
    const percentage = stock.re_order > 0
      ? Math.min((stock.available_for_sale / stock.re_order) * 100, 100)
      : stock.available_for_sale > 0 ? 100 : 0;

    return (
      <Stack gap={2}>
        <Group gap="xs" justify="space-between">
          <Text size="sm" fw={500}>
            {stock.available_for_sale} / {stock.total_stock}
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

  const columns: DataTableColumn<Stock>[] = [
    {
      accessor: 'image_url',
      title: '',
      width: 60,
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
      render: (stock: Stock) => (
        <Stack gap={2}>
          <Anchor
            component="button"
            onClick={() => handleView(stock)}
            fw={500}
            truncate
          >
            {stock.item_name}
          </Anchor>
          {stock.sku && (
            <Text size="xs" color="dimmed" truncate>
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
      render: (stock: Stock) => (
        <Text size="sm" truncate>
          {stock.category?.group || 'N/A'}
        </Text>
      ),
    },
    {
      accessor: 'condition',
      title: 'Condition',
      width: 100,
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
      width: 120,
      render: (stock: Stock) => (
        <Stack gap={2}>
          <Text size="sm" truncate>
            {stock.location?.name || 'N/A'}
          </Text>
          {stock.aisle && (
            <Text size="xs" color="dimmed" truncate>
              Aisle: {stock.aisle}
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
        noRecordsText="No stock items found"
        minHeight={400}
        striped
        highlightOnHover
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
    </Box>
  );
};

export default StockTable;