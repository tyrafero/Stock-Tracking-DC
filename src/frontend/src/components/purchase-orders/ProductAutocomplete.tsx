// @ts-nocheck
import React, { useState, useEffect, useRef } from 'react';
import { Autocomplete, Loader } from '@mantine/core';
import { useDebouncedValue } from '@mantine/hooks';
import { stockAPI } from '@/api/stock';
import type { Stock } from '@/types/stock';

interface ProductAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect?: (stock: Stock | null) => void;
  placeholder?: string;
  error?: string;
  disabled?: boolean;
}

export const ProductAutocomplete: React.FC<ProductAutocompleteProps> = ({
  value,
  onChange,
  onSelect,
  placeholder = 'Search for product...',
  error,
  disabled = false,
}) => {
  const [loading, setLoading] = useState(false);
  const [options, setOptions] = useState<Array<{ value: string; label: string; stock?: Stock }>>([]);
  const [debounced] = useDebouncedValue(value, 200);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const searchProducts = async () => {
      if (!debounced || debounced.length < 1) {
        setOptions([]);
        return;
      }

      // Abort previous request if still pending
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();
      setLoading(true);

      try {
        const response = await stockAPI.getStocks({
          search: debounced,
          page_size: 10,
        });

        // Group stocks by item_name to handle duplicates
        const stockGroups = response.results.reduce((groups, stock) => {
          const key = stock.item_name;
          if (!groups[key]) {
            groups[key] = [];
          }
          groups[key].push(stock);
          return groups;
        }, {} as Record<string, Stock[]>);

        // Create options with unique values and descriptive labels
        const stockOptions = Object.entries(stockGroups).flatMap(([itemName, stocks]) => {
          if (stocks.length === 1) {
            // Single stock item - use simple label
            return [{
              value: itemName,
              label: itemName,
              stock: stocks[0],
            }];
          } else {
            // Multiple stocks with same name - add distinguishing info
            return stocks.map((stock, index) => {
              const locationInfo = stock.location_name ? ` (${stock.location_name})` : '';
              const qtyInfo = stock.quantity ? ` - Qty: ${stock.quantity}` : '';
              const uniqueValue = `${itemName}_${stock.id}`;

              return {
                value: uniqueValue,
                label: `${itemName}${locationInfo}${qtyInfo}`,
                stock,
                originalName: itemName,
              };
            });
          }
        });

        setOptions(stockOptions);
      } catch (error: any) {
        if (error.name !== 'AbortError') {
          console.error('Error searching products:', error);
          setOptions([]);
        }
      } finally {
        setLoading(false);
      }
    };

    searchProducts();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [debounced]);

  const handleSelect = (selectedValue: string) => {
    // Find the stock item that was selected
    const selectedOption = options.find((opt) => opt.value === selectedValue);

    // Use original item name for duplicate entries, otherwise use the selected value
    const displayName = (selectedOption as any)?.originalName || selectedValue;
    onChange(displayName);

    if (onSelect) {
      onSelect(selectedOption?.stock || null);
    }
  };

  return (
    <Autocomplete
      value={value}
      onChange={onChange}
      onOptionSubmit={handleSelect}
      data={options}
      placeholder={placeholder}
      error={error}
      disabled={disabled}
      rightSection={loading ? <Loader size="xs" /> : null}
      limit={10}
      size="sm"
      comboboxProps={{ withinPortal: true }}
    />
  );
};
