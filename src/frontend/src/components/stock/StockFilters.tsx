import React, { useState, useEffect, useMemo } from 'react';
import {
  Grid,
  TextInput,
  Select,
  Group,
  Button,
  NumberInput,
  Switch,
  Collapse,
  Title,
  Box,
  Divider,
  ActionIcon,
  Tooltip,
  Stack
} from '@mantine/core';
import { useMediaQuery } from '@mantine/hooks';
import {
  IconSearch,
  IconFilter,
  IconX,
  IconChevronDown,
  IconChevronUp
} from '@tabler/icons-react';
import { useQuery } from '@tanstack/react-query';
import { useDebouncedValue } from '@mantine/hooks';

import { stockAPI } from '@/api/stock';
import { StockFilters as StockFiltersType, Category, Store } from '@/types/stock';

interface StockFiltersProps {
  filters: StockFiltersType;
  onFiltersChange: (filters: StockFiltersType) => void;
}

const conditionOptions = [
  { value: 'new', label: 'New' },
  { value: 'demo_unit', label: 'Demo Unit' },
  { value: 'bstock', label: 'B-Stock' },
  { value: 'open_box', label: 'Open Box' },
  { value: 'refurbished', label: 'Refurbished' },
];

const StockFilters: React.FC<StockFiltersProps> = ({
  filters,
  onFiltersChange
}) => {
  const [localFilters, setLocalFilters] = useState<StockFiltersType>(filters);
  const [searchTerm, setSearchTerm] = useState(filters.search || '');
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  const [debouncedSearch] = useDebouncedValue(searchTerm, 500);
  const isMobile = useMediaQuery('(max-width: 768px)');

  // Fetch categories for dropdown
  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: () => stockAPI.getCategories(),
    staleTime: 300000, // 5 minutes
  });

  // Fetch stores for dropdown
  const { data: storesData } = useQuery({
    queryKey: ['stores'],
    queryFn: () => stockAPI.getStores(),
    staleTime: 300000, // 5 minutes
  });

  const categories = categoriesData?.results || [];
  const stores = storesData?.results || [];

  // Convert categories to select options - memoized to prevent re-renders
  const categoryOptions = useMemo(() =>
    categories.map(cat => ({
      value: cat.id.toString(),
      label: cat.group
    })), [categories]
  );

  // Convert stores to select options - memoized to prevent re-renders
  const storeOptions = useMemo(() =>
    stores.map(store => ({
      value: store.id.toString(),
      label: store.name
    })), [stores]
  );

  // Update local filters when debounced search changes
  useEffect(() => {
    if (debouncedSearch !== localFilters.search) {
      const newFilters = { ...localFilters, search: debouncedSearch || undefined };
      setLocalFilters(newFilters);
      onFiltersChange(newFilters);
    }
  }, [debouncedSearch]);

  const handleFilterChange = (key: keyof StockFiltersType, value: any) => {
    const newFilters = {
      ...localFilters,
      [key]: value === '' || value === null ? undefined : value
    };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleClearFilters = () => {
    const clearedFilters: StockFiltersType = {};
    setLocalFilters(clearedFilters);
    setSearchTerm('');
    onFiltersChange(clearedFilters);
    setIsAdvancedOpen(false);
  };

  const hasActiveFilters = Object.keys(localFilters).some(
    key => localFilters[key as keyof StockFiltersType] !== undefined
  );

  const hasAdvancedFilters = Boolean(
    localFilters.category ||
    localFilters.location ||
    localFilters.condition ||
    localFilters.quantity_min ||
    localFilters.quantity_max ||
    localFilters.available_min ||
    localFilters.available_max ||
    localFilters.has_image !== undefined ||
    localFilters.warehouse_name
  );

  return (
    <Box>
      {/* Main Search and Filter Toggle */}
      {isMobile ? (
        <Stack gap="sm" mb="sm">
          <TextInput
            placeholder="Search stock items..."
            leftSection={<IconSearch size="1rem" />}
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.currentTarget.value)}
            rightSection={
              searchTerm ? (
                <ActionIcon onClick={() => setSearchTerm('')}>
                  <IconX size="1rem" />
                </ActionIcon>
              ) : null
            }
          />

          <Group>
            <Button
              variant={hasAdvancedFilters ? 'filled' : 'light'}
              leftSection={<IconFilter size="1rem" />}
              rightSection={
                isAdvancedOpen ? <IconChevronUp size="1rem" /> : <IconChevronDown size="1rem" />
              }
              onClick={() => setIsAdvancedOpen(!isAdvancedOpen)}
              style={{ flex: 1 }}
            >
              Filters {hasAdvancedFilters ? `(${Object.keys(localFilters).length})` : ''}
            </Button>

            {hasActiveFilters && (
              <Tooltip label="Clear all filters">
                <ActionIcon
                  color="red"
                  variant="light"
                  onClick={handleClearFilters}
                >
                  <IconX size="1rem" />
                </ActionIcon>
              </Tooltip>
            )}
          </Group>
        </Stack>
      ) : (
        <Group gap="md" mb="sm">
          <TextInput
            placeholder="Search stock items..."
            leftSection={<IconSearch size="1rem" />}
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.currentTarget.value)}
            style={{ flex: 1 }}
            rightSection={
              searchTerm ? (
                <ActionIcon onClick={() => setSearchTerm('')}>
                  <IconX size="1rem" />
                </ActionIcon>
              ) : null
            }
          />

          <Button
            variant={hasAdvancedFilters ? 'filled' : 'light'}
            leftSection={<IconFilter size="1rem" />}
            rightSection={
              isAdvancedOpen ? <IconChevronUp size="1rem" /> : <IconChevronDown size="1rem" />
            }
            onClick={() => setIsAdvancedOpen(!isAdvancedOpen)}
          >
            Filters {hasAdvancedFilters ? `(${Object.keys(localFilters).length})` : ''}
          </Button>

          {hasActiveFilters && (
            <Tooltip label="Clear all filters">
              <ActionIcon
                color="red"
                variant="light"
                onClick={handleClearFilters}
              >
                <IconX size="1rem" />
              </ActionIcon>
            </Tooltip>
          )}
        </Group>
      )}

      {/* Advanced Filters */}
      <Collapse in={isAdvancedOpen}>
        <Box pt="md">
          <Title order={4} mb="sm" size="h5">Advanced Filters</Title>

          <Grid gutter="md">
            {/* Row 1: Category, Location, Condition */}
            <Grid.Col span={{ base: 12, sm: 4 }}>
              <Select
                label="Category"
                placeholder="Select category"
                data={categoryOptions}
                value={localFilters.category?.toString() || null}
                onChange={(value) => handleFilterChange('category', value ? parseInt(value) : undefined)}
                searchable
                clearable
              />
            </Grid.Col>

            <Grid.Col span={{ base: 12, sm: 4 }}>
              <Select
                label="Location"
                placeholder="Select location"
                data={storeOptions}
                value={localFilters.location?.toString() || null}
                onChange={(value) => handleFilterChange('location', value ? parseInt(value) : undefined)}
                searchable
                clearable
              />
            </Grid.Col>

            <Grid.Col span={{ base: 12, sm: 4 }}>
              <Select
                label="Condition"
                placeholder="Select condition"
                data={conditionOptions}
                value={localFilters.condition || null}
                onChange={(value) => handleFilterChange('condition', value)}
                clearable
              />
            </Grid.Col>

            {/* Row 2: Quantity Range */}
            <Grid.Col span={{ base: 12, sm: 6 }}>
              {isMobile ? (
                <Stack gap="sm">
                  <NumberInput
                    label="Min Quantity"
                    placeholder="0"
                    min={0}
                    value={localFilters.quantity_min || ''}
                    onChange={(value) => handleFilterChange('quantity_min', value || undefined)}
                  />
                  <NumberInput
                    label="Max Quantity"
                    placeholder="1000"
                    min={0}
                    value={localFilters.quantity_max || ''}
                    onChange={(value) => handleFilterChange('quantity_max', value || undefined)}
                  />
                </Stack>
              ) : (
                <Group grow>
                  <NumberInput
                    label="Min Quantity"
                    placeholder="0"
                    min={0}
                    value={localFilters.quantity_min || ''}
                    onChange={(value) => handleFilterChange('quantity_min', value || undefined)}
                  />
                  <NumberInput
                    label="Max Quantity"
                    placeholder="1000"
                    min={0}
                    value={localFilters.quantity_max || ''}
                    onChange={(value) => handleFilterChange('quantity_max', value || undefined)}
                  />
                </Group>
              )}
            </Grid.Col>

            {/* Row 2: Available Range */}
            <Grid.Col span={{ base: 12, sm: 6 }}>
              {isMobile ? (
                <Stack gap="sm">
                  <NumberInput
                    label="Min Available"
                    placeholder="0"
                    min={0}
                    value={localFilters.available_min || ''}
                    onChange={(value) => handleFilterChange('available_min', value || undefined)}
                  />
                  <NumberInput
                    label="Max Available"
                    placeholder="1000"
                    min={0}
                    value={localFilters.available_max || ''}
                    onChange={(value) => handleFilterChange('available_max', value || undefined)}
                  />
                </Stack>
              ) : (
                <Group grow>
                  <NumberInput
                    label="Min Available"
                    placeholder="0"
                    min={0}
                    value={localFilters.available_min || ''}
                    onChange={(value) => handleFilterChange('available_min', value || undefined)}
                  />
                  <NumberInput
                    label="Max Available"
                    placeholder="1000"
                    min={0}
                    value={localFilters.available_max || ''}
                    onChange={(value) => handleFilterChange('available_max', value || undefined)}
                  />
                </Group>
              )}
            </Grid.Col>

            {/* Row 3: Additional Filters */}
            <Grid.Col span={{ base: 12, sm: 4 }}>
              <TextInput
                label="Warehouse Name"
                placeholder="Enter warehouse name"
                value={localFilters.warehouse_name || ''}
                onChange={(event) => handleFilterChange('warehouse_name', event.currentTarget.value)}
              />
            </Grid.Col>

            <Grid.Col span={{ base: 12, sm: 4 }}>
              <TextInput
                label="SKU"
                placeholder="Enter SKU"
                value={localFilters.sku || ''}
                onChange={(event) => handleFilterChange('sku', event.currentTarget.value)}
              />
            </Grid.Col>

            <Grid.Col span={{ base: 12, sm: 4 }}>
              <Box mt={isMobile ? 0 : "lg"}>
                <Switch
                  label="Has image"
                  checked={localFilters.has_image === true}
                  onChange={(event) =>
                    handleFilterChange('has_image', event.currentTarget.checked || undefined)
                  }
                />
              </Box>
            </Grid.Col>
          </Grid>

          <Divider my="md" />

          {/* Action Buttons */}
          {isMobile ? (
            <Stack gap="sm">
              <Button variant="light" onClick={handleClearFilters} fullWidth>
                Clear All
              </Button>
              <Button onClick={() => setIsAdvancedOpen(false)} fullWidth>
                Apply Filters
              </Button>
            </Stack>
          ) : (
            <Group justify="flex-end">
              <Button variant="light" onClick={handleClearFilters}>
                Clear All
              </Button>
              <Button onClick={() => setIsAdvancedOpen(false)}>
                Apply Filters
              </Button>
            </Group>
          )}
        </Box>
      </Collapse>
    </Box>
  );
};

export default StockFilters;