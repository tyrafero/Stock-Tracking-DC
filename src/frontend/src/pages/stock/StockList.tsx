import React, { useState, useMemo } from 'react';
import {
  Title,
  Box,
  Container,
  Group,
  Button,
  LoadingOverlay,
  Alert,
  Stack,
  Paper
} from '@mantine/core';
import { IconPlus, IconAlertCircle } from '@tabler/icons-react';
import { useMediaQuery } from '@mantine/hooks';
import { useQuery } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { useNavigate } from 'react-router-dom';

import { stockAPI } from '@/api/stock';
import { Stock, StockFilters } from '@/types/stock';
import { useAuthStore, useHasPermission } from '@/states/authState';
import StockTable from '@/components/stock/StockTable';
import StockFiltersComponent from '@/components/stock/StockFilters';

const StockList: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const hasPermission = useHasPermission();
  const isMobile = useMediaQuery('(max-width: 768px)');

  const [filters, setFilters] = useState<StockFilters>({});
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 25;

  // Fetch stock data with React Query
  const {
    data: stockData,
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['stocks', filters, currentPage],
    queryFn: () => stockAPI.getStocks({
      ...filters,
      page: currentPage,
      page_size: pageSize,
      ordering: '-last_updated'
    }),
    staleTime: 30000, // Consider data fresh for 30 seconds
  });

  const stocks = useMemo(() => stockData?.results || [], [stockData]);
  const totalCount = stockData?.count || 0;
  const totalPages = stockData?.total_pages || 1;

  const handleFiltersChange = (newFilters: StockFilters) => {
    setFilters(newFilters);
    setCurrentPage(1); // Reset to first page when filters change
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleCreateStock = () => {
    if (!hasPermission('stock.add_stock')) {
      notifications.show({
        title: 'Permission denied',
        message: 'You do not have permission to create stock items',
        color: 'red',
      });
      return;
    }
    navigate('/stock/create');
  };

  const handleRefresh = () => {
    refetch();
    notifications.show({
      title: 'Refreshed',
      message: 'Stock list has been refreshed',
      color: 'blue',
    });
  };

  return (
    <Container fluid px={isMobile ? "sm" : "md"}>
      <Box pos="relative">
        <LoadingOverlay visible={isLoading} />

        <Stack gap="md">
          {/* Header */}
          <Stack gap="sm">
            <Title order={isMobile ? 2 : 1}>Stock Management</Title>
            {isMobile ? (
              <Stack gap="xs">
                <Button
                  variant="light"
                  onClick={handleRefresh}
                  loading={isLoading}
                  fullWidth
                >
                  Refresh
                </Button>
                {hasPermission('stock.add_stock') && (
                  <Button
                    leftSection={<IconPlus size="1rem" />}
                    onClick={handleCreateStock}
                    fullWidth
                  >
                    Add Stock
                  </Button>
                )}
              </Stack>
            ) : (
              <Group justify="space-between" align="center">
                <div /> {/* Spacer */}
                <Group>
                  <Button
                    variant="light"
                    onClick={handleRefresh}
                    loading={isLoading}
                  >
                    Refresh
                  </Button>
                  {hasPermission('stock.add_stock') && (
                    <Button
                      leftSection={<IconPlus size="1rem" />}
                      onClick={handleCreateStock}
                    >
                      Add Stock
                    </Button>
                  )}
                </Group>
              </Group>
            )}
          </Stack>

          {/* Error Alert */}
          {isError && (
            <Alert
              icon={<IconAlertCircle size="1rem" />}
              title="Error loading stock data"
              color="red"
              variant="light"
            >
              {(error as any)?.response?.data?.detail || 'An unexpected error occurred. Please try again.'}
            </Alert>
          )}

          {/* Filters */}
          <Paper p="md" shadow="sm">
            <StockFiltersComponent
              filters={filters}
              onFiltersChange={handleFiltersChange}
            />
          </Paper>

          {/* Stock Table */}
          <Paper shadow="sm">
            <StockTable
              stocks={stocks}
              totalCount={totalCount}
              currentPage={currentPage}
              totalPages={totalPages}
              pageSize={pageSize}
              onPageChange={handlePageChange}
              isLoading={isLoading}
            />
          </Paper>
        </Stack>
      </Box>
    </Container>
  );
};

export default StockList;