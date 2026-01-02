// @ts-nocheck
import React from 'react';
import { Table, Button, Stack, ScrollArea } from '@mantine/core';
import { IconPlus } from '@tabler/icons-react';
import { POItemRow, type POItem } from './POItemRow';

interface POItemTableProps {
  items: POItem[];
  onChange: (items: POItem[]) => void;
  errors?: { [index: number]: { [field: string]: string } };
}

export const POItemTable: React.FC<POItemTableProps> = ({
  items,
  onChange,
  errors = {},
}) => {
  const handleItemChange = (index: number, field: keyof POItem, value: any) => {
    const newItems = [...items];
    newItems[index] = {
      ...newItems[index],
      [field]: value,
    };
    onChange(newItems);
  };

  const handleAddItem = () => {
    const newItem: POItem = {
      id: `new-${Date.now()}`, // Temporary ID for React key
      product: '',
      associated_order_number: '',
      price_inc: 0,
      quantity: 1,
      discount_percent: 0,
    };
    onChange([...items, newItem]);
  };

  const handleRemoveItem = (index: number) => {
    if (items.length > 1) {
      const newItems = items.filter((_, i) => i !== index);
      onChange(newItems);
    }
  };

  return (
    <Stack gap="md">
      <ScrollArea>
        <Table withTableBorder striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th style={{ minWidth: 200 }}>Product</Table.Th>
              <Table.Th style={{ minWidth: 120 }}>Order #</Table.Th>
              <Table.Th style={{ minWidth: 110 }}>Price Inc</Table.Th>
              <Table.Th style={{ minWidth: 110 }}>Price Exc</Table.Th>
              <Table.Th style={{ minWidth: 90 }}>Quantity</Table.Th>
              <Table.Th style={{ minWidth: 100 }}>Discount %</Table.Th>
              <Table.Th style={{ minWidth: 120 }}>Subtotal Exc</Table.Th>
              <Table.Th style={{ width: 60 }}>Action</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {items.map((item, index) => (
              <POItemRow
                key={item.id || index}
                item={item}
                index={index}
                onChange={handleItemChange}
                onRemove={handleRemoveItem}
                canRemove={items.length > 1}
                error={errors[index]}
              />
            ))}
          </Table.Tbody>
        </Table>
      </ScrollArea>

      <Button
        leftSection={<IconPlus size={16} />}
        variant="light"
        onClick={handleAddItem}
      >
        Add Item
      </Button>
    </Stack>
  );
};
