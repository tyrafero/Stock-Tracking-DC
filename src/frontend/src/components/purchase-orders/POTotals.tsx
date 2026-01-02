// @ts-nocheck
import React, { useMemo } from 'react';
import { Stack, Group, Text, Divider, Title } from '@mantine/core';
import type { POItem } from './POItemRow';

interface POTotalsProps {
  items: POItem[];
  shipping?: number;
}

export const POTotals: React.FC<POTotalsProps> = ({ items, shipping = 0 }) => {
  const totals = useMemo(() => {
    let subtotalExc = 0;
    let totalDiscount = 0;

    items.forEach((item) => {
      const priceExc = item.price_inc * 0.9; // Remove 10% GST
      const lineTotalExc = priceExc * item.quantity;
      const discountAmount = (lineTotalExc * item.discount_percent) / 100;
      const lineSubtotal = lineTotalExc - discountAmount;

      subtotalExc += lineTotalExc;
      totalDiscount += discountAmount;
    });

    const afterDiscount = subtotalExc - totalDiscount;
    const gst = afterDiscount * 0.10; // 10% GST
    const grandTotal = afterDiscount + gst + shipping;

    return {
      subtotalExc,
      totalDiscount,
      afterDiscount,
      gst,
      grandTotal,
    };
  }, [items, shipping]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
    }).format(amount);
  };

  return (
    <Stack gap="md">
      <Title order={5}>Purchase Order Totals</Title>

      <Stack gap="xs">
        <Group justify="space-between">
          <Text size="sm">Subtotal (Exc GST):</Text>
          <Text size="sm" fw={500}>{formatCurrency(totals.subtotalExc)}</Text>
        </Group>

        <Group justify="space-between">
          <Text size="sm">Total Discount:</Text>
          <Text size="sm" fw={500} c="red">{formatCurrency(totals.totalDiscount)}</Text>
        </Group>

        <Group justify="space-between">
          <Text size="sm">After Discount:</Text>
          <Text size="sm" fw={500}>{formatCurrency(totals.afterDiscount)}</Text>
        </Group>

        <Group justify="space-between">
          <Text size="sm">GST (10%):</Text>
          <Text size="sm" fw={500}>{formatCurrency(totals.gst)}</Text>
        </Group>

        {shipping > 0 && (
          <Group justify="space-between">
            <Text size="sm">Shipping:</Text>
            <Text size="sm" fw={500}>{formatCurrency(shipping)}</Text>
          </Group>
        )}

        <Divider my="xs" />

        <Group justify="space-between">
          <Text fw={700}>GRAND TOTAL:</Text>
          <Text fw={700} size="lg">{formatCurrency(totals.grandTotal)}</Text>
        </Group>
      </Stack>
    </Stack>
  );
};
