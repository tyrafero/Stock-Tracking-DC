// @ts-nocheck
import React, { useMemo } from 'react';
import { NumberInput, TextInput, ActionIcon, Table } from '@mantine/core';
import { IconTrash } from '@tabler/icons-react';
import { ProductAutocomplete } from './ProductAutocomplete';

export interface POItem {
  id?: string; // Temporary ID for React key
  product: string;
  associated_order_number?: string;
  price_inc: number;
  quantity: number;
  discount_percent: number;
}

interface POItemRowProps {
  item: POItem;
  index: number;
  onChange: (index: number, field: keyof POItem, value: any) => void;
  onRemove: (index: number) => void;
  canRemove: boolean;
  error?: { [key: string]: string };
}

export const POItemRow: React.FC<POItemRowProps> = ({
  item,
  index,
  onChange,
  onRemove,
  canRemove,
  error = {},
}) => {
  // Calculate derived values
  const calculations = useMemo(() => {
    const priceExc = item.price_inc * 0.9; // Remove 10% GST
    const lineTotalExc = priceExc * item.quantity;
    const discountAmount = (lineTotalExc * item.discount_percent) / 100;
    const subtotalExc = lineTotalExc - discountAmount;

    return {
      priceExc,
      subtotalExc,
    };
  }, [item.price_inc, item.quantity, item.discount_percent]);

  const formatCurrency = (amount: number) => {
    return `$${amount.toFixed(2)}`;
  };

  const handleProductSelect = (stock) => {
    // When a product is selected, auto-fill the product name
    if (stock) {
      onChange(index, 'product', stock.item_name);
      // Note: Price auto-fill is intentionally not implemented here
      // as purchase prices may differ from current stock prices
    }
  };

  return (
    <Table.Tr>
      {/* Product Name with Autocomplete */}
      <Table.Td style={{ minWidth: 200 }}>
        <ProductAutocomplete
          value={item.product}
          onChange={(value) => onChange(index, 'product', value)}
          onSelect={handleProductSelect}
          placeholder="Product name"
          error={error.product}
        />
      </Table.Td>

      {/* Associated Order Number */}
      <Table.Td style={{ minWidth: 120 }}>
        <TextInput
          value={item.associated_order_number || ''}
          onChange={(e) => onChange(index, 'associated_order_number', e.target.value)}
          placeholder="Order #"
          size="sm"
        />
      </Table.Td>

      {/* Price Inc GST */}
      <Table.Td style={{ minWidth: 110 }}>
        <NumberInput
          value={item.price_inc}
          onChange={(value) => onChange(index, 'price_inc', value || 0)}
          min={0}
          decimalScale={2}
          prefix="$"
          placeholder="0.00"
          error={error.price_inc}
          size="sm"
          hideControls
        />
      </Table.Td>

      {/* Price Exc GST (Calculated, Read-only) */}
      <Table.Td style={{ minWidth: 110 }}>
        <TextInput
          value={formatCurrency(calculations.priceExc)}
          readOnly
          size="sm"
          styles={{ input: { backgroundColor: '#f8f9fa' } }}
        />
      </Table.Td>

      {/* Quantity */}
      <Table.Td style={{ minWidth: 90 }}>
        <NumberInput
          value={item.quantity}
          onChange={(value) => onChange(index, 'quantity', value || 1)}
          min={1}
          decimalScale={0}
          placeholder="1"
          error={error.quantity}
          size="sm"
          hideControls
        />
      </Table.Td>

      {/* Discount % */}
      <Table.Td style={{ minWidth: 100 }}>
        <NumberInput
          value={item.discount_percent}
          onChange={(value) => onChange(index, 'discount_percent', value || 0)}
          min={0}
          max={100}
          decimalScale={2}
          suffix="%"
          placeholder="0.00"
          size="sm"
          hideControls
        />
      </Table.Td>

      {/* Subtotal Exc GST (Calculated, Read-only) */}
      <Table.Td style={{ minWidth: 120 }}>
        <TextInput
          value={formatCurrency(calculations.subtotalExc)}
          readOnly
          size="sm"
          styles={{ input: { backgroundColor: '#f8f9fa', fontWeight: 500 } }}
        />
      </Table.Td>

      {/* Remove Button */}
      <Table.Td style={{ width: 60 }}>
        <ActionIcon
          color="red"
          variant="light"
          onClick={() => onRemove(index)}
          disabled={!canRemove}
          size="sm"
        >
          <IconTrash size={16} />
        </ActionIcon>
      </Table.Td>
    </Table.Tr>
  );
};
