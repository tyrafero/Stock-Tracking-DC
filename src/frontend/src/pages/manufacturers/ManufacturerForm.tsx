// @ts-nocheck
import React from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  Stack,
  TextInput,
  Textarea,
  Button,
  Group,
  Grid,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import type { Manufacturer } from '@/types/stock';

interface ManufacturerFormProps {
  manufacturer?: Manufacturer | null;
  onSuccess: () => void;
  onCancel: () => void;
}

interface ManufacturerFormValues {
  company_name: string;
  company_email: string;
  additional_email: string;
  street_address: string;
  city: string;
  country: string;
  region: string;
  postal_code: string;
  company_telephone: string;
  abn: string;
}

export const ManufacturerForm: React.FC<ManufacturerFormProps> = ({
  manufacturer,
  onSuccess,
  onCancel,
}) => {
  const form = useForm<ManufacturerFormValues>({
    initialValues: {
      company_name: manufacturer?.company_name || '',
      company_email: manufacturer?.company_email || '',
      additional_email: manufacturer?.additional_email || '',
      street_address: manufacturer?.street_address || '',
      city: manufacturer?.city || '',
      country: manufacturer?.country || 'Australia',
      region: manufacturer?.region || '',
      postal_code: manufacturer?.postal_code || '',
      company_telephone: manufacturer?.company_telephone || '',
      abn: manufacturer?.abn || '',
    },
    validate: {
      company_name: (value) => (!value ? 'Company name is required' : null),
      company_email: (value) => {
        if (!value) return 'Email is required';
        if (!/^\S+@\S+$/.test(value)) return 'Invalid email';
        return null;
      },
      street_address: (value) => (!value ? 'Street address is required' : null),
      city: (value) => (!value ? 'City is required' : null),
      country: (value) => (!value ? 'Country is required' : null),
      region: (value) => (!value ? 'Region/State is required' : null),
      postal_code: (value) => (!value ? 'Postal code is required' : null),
      company_telephone: (value) => (!value ? 'Phone number is required' : null),
    },
  });

  const saveMutation = useMutation({
    mutationFn: async (data: ManufacturerFormValues) => {
      const url = manufacturer
        ? `/api/v1/manufacturers/${manufacturer.id}/`
        : `/api/v1/manufacturers/`;

      const method = manufacturer ? 'PATCH' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to save manufacturer');
      }

      return response.json();
    },
    onSuccess: () => {
      notifications.show({
        title: 'Success',
        message: `Manufacturer ${manufacturer ? 'updated' : 'created'} successfully`,
        color: 'green',
      });
      onSuccess();
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error.message || 'Failed to save manufacturer',
        color: 'red',
      });
    },
  });

  const handleSubmit = (values: ManufacturerFormValues) => {
    saveMutation.mutate(values);
  };

  return (
    <form onSubmit={form.onSubmit(handleSubmit)}>
      <Stack gap="md">
        <TextInput
          label="Company Name"
          placeholder="Enter company name"
          required
          {...form.getInputProps('company_name')}
        />

        <Grid>
          <Grid.Col span={6}>
            <TextInput
              label="Email"
              placeholder="company@example.com"
              type="email"
              required
              {...form.getInputProps('company_email')}
            />
          </Grid.Col>
          <Grid.Col span={6}>
            <TextInput
              label="Additional Email"
              placeholder="orders@example.com"
              type="email"
              {...form.getInputProps('additional_email')}
            />
          </Grid.Col>
        </Grid>

        <Textarea
          label="Street Address"
          placeholder="123 Business St"
          required
          rows={2}
          {...form.getInputProps('street_address')}
        />

        <Grid>
          <Grid.Col span={6}>
            <TextInput
              label="City"
              placeholder="Sydney"
              required
              {...form.getInputProps('city')}
            />
          </Grid.Col>
          <Grid.Col span={6}>
            <TextInput
              label="Region/State"
              placeholder="NSW"
              required
              {...form.getInputProps('region')}
            />
          </Grid.Col>
        </Grid>

        <Grid>
          <Grid.Col span={6}>
            <TextInput
              label="Country"
              placeholder="Australia"
              required
              {...form.getInputProps('country')}
            />
          </Grid.Col>
          <Grid.Col span={6}>
            <TextInput
              label="Postal Code"
              placeholder="2000"
              required
              {...form.getInputProps('postal_code')}
            />
          </Grid.Col>
        </Grid>

        <Grid>
          <Grid.Col span={6}>
            <TextInput
              label="Phone Number"
              placeholder="(02) 9876 5432"
              required
              {...form.getInputProps('company_telephone')}
            />
          </Grid.Col>
          <Grid.Col span={6}>
            <TextInput
              label="ABN (Optional)"
              placeholder="12 345 678 901"
              {...form.getInputProps('abn')}
            />
          </Grid.Col>
        </Grid>

        <Group justify="flex-end" mt="md">
          <Button variant="light" onClick={onCancel} disabled={saveMutation.isPending}>
            Cancel
          </Button>
          <Button type="submit" loading={saveMutation.isPending}>
            {manufacturer ? 'Update' : 'Create'} Manufacturer
          </Button>
        </Group>
      </Stack>
    </form>
  );
};
