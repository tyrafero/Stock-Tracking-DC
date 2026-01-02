// @ts-nocheck
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Container,
  Title,
  Text,
  Paper,
  Group,
  Button,
  Stack,
  Table,
  ActionIcon,
  TextInput,
  Modal,
  Badge,
  Loader,
  Alert,
} from '@mantine/core';
import {
  IconPlus,
  IconEdit,
  IconTrash,
  IconSearch,
  IconAlertCircle,
} from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { stockAPI } from '@/api/stock';
import { useAuth, useHasPermission } from '@/states/authState';
import { ManufacturerForm } from './ManufacturerForm';
import type { Manufacturer } from '@/types/stock';

const ManufacturersList: React.FC = () => {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const hasPermission = useHasPermission();

  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingManufacturer, setEditingManufacturer] = useState<Manufacturer | null>(null);

  // Fetch manufacturers
  const { data, isLoading, error } = useQuery({
    queryKey: ['manufacturers', page, search],
    queryFn: () => stockAPI.getManufacturers({
      page,
      page_size: 20,
      search,
    }),
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => {
      // Assuming delete endpoint exists
      return fetch(`/api/v1/manufacturers/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
    },
    onSuccess: () => {
      notifications.show({
        title: 'Manufacturer Deleted',
        message: 'Manufacturer has been deleted successfully',
        color: 'green',
      });
      queryClient.invalidateQueries({ queryKey: ['manufacturers'] });
    },
    onError: () => {
      notifications.show({
        title: 'Error',
        message: 'Failed to delete manufacturer',
        color: 'red',
      });
    },
  });

  const handleCreate = () => {
    setEditingManufacturer(null);
    setModalOpen(true);
  };

  const handleEdit = (manufacturer: Manufacturer) => {
    setEditingManufacturer(manufacturer);
    setModalOpen(true);
  };

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Are you sure you want to delete ${name}?`)) {
      deleteMutation.mutate(id);
    }
  };

  const handleModalClose = () => {
    setModalOpen(false);
    setEditingManufacturer(null);
  };

  const handleSuccess = () => {
    handleModalClose();
    queryClient.invalidateQueries({ queryKey: ['manufacturers'] });
  };

  const canManage = hasPermission('add_manufacturer') || hasPermission('change_manufacturer');

  if (error) {
    return (
      <Container fluid>
        <Alert icon={<IconAlertCircle size={16} />} color="red">
          Failed to load manufacturers. Please try again.
        </Alert>
      </Container>
    );
  }

  return (
    <>
      <Container fluid>
        <Stack gap="md">
          <Group justify="space-between">
            <div>
              <Title order={1}>Manufacturers</Title>
              <Text c="dimmed">Manage suppliers and manufacturers</Text>
            </div>
            {canManage && (
              <Button
                leftSection={<IconPlus size={16} />}
                onClick={handleCreate}
              >
                Add Manufacturer
              </Button>
            )}
          </Group>

          <Paper shadow="xs" p="lg">
            <Stack gap="md">
              <TextInput
                placeholder="Search manufacturers..."
                leftSection={<IconSearch size={16} />}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />

              {isLoading ? (
                <Group justify="center" p="xl">
                  <Loader />
                </Group>
              ) : (
                <Table withTableBorder striped highlightOnHover>
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Company Name</Table.Th>
                      <Table.Th>Email</Table.Th>
                      <Table.Th>Phone</Table.Th>
                      <Table.Th>City</Table.Th>
                      <Table.Th>Country</Table.Th>
                      {canManage && <Table.Th style={{ width: 100 }}>Actions</Table.Th>}
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {data?.results?.length === 0 ? (
                      <Table.Tr>
                        <Table.Td colSpan={canManage ? 6 : 5} style={{ textAlign: 'center' }}>
                          <Text c="dimmed" p="xl">
                            No manufacturers found. {canManage && 'Click "Add Manufacturer" to create one.'}
                          </Text>
                        </Table.Td>
                      </Table.Tr>
                    ) : (
                      data?.results?.map((manufacturer) => (
                        <Table.Tr key={manufacturer.id}>
                          <Table.Td>
                            <Text fw={500}>{manufacturer.company_name}</Text>
                          </Table.Td>
                          <Table.Td>{manufacturer.company_email}</Table.Td>
                          <Table.Td>{manufacturer.company_telephone}</Table.Td>
                          <Table.Td>{manufacturer.city}</Table.Td>
                          <Table.Td>{manufacturer.country}</Table.Td>
                          {canManage && (
                            <Table.Td>
                              <Group gap="xs">
                                <ActionIcon
                                  variant="light"
                                  color="blue"
                                  onClick={() => handleEdit(manufacturer)}
                                >
                                  <IconEdit size={16} />
                                </ActionIcon>
                                <ActionIcon
                                  variant="light"
                                  color="red"
                                  onClick={() => handleDelete(manufacturer.id, manufacturer.company_name)}
                                  loading={deleteMutation.isPending}
                                >
                                  <IconTrash size={16} />
                                </ActionIcon>
                              </Group>
                            </Table.Td>
                          )}
                        </Table.Tr>
                      ))
                    )}
                  </Table.Tbody>
                </Table>
              )}

              {data && data.total_pages > 1 && (
                <Group justify="center">
                  <Button
                    variant="light"
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Previous
                  </Button>
                  <Text size="sm">
                    Page {page} of {data.total_pages}
                  </Text>
                  <Button
                    variant="light"
                    onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
                    disabled={page === data.total_pages}
                  >
                    Next
                  </Button>
                </Group>
              )}
            </Stack>
          </Paper>
        </Stack>
      </Container>

      <Modal
        opened={modalOpen}
        onClose={handleModalClose}
        title={editingManufacturer ? 'Edit Manufacturer' : 'Add Manufacturer'}
        size="lg"
        centered
        zIndex={1000}
        overlayProps={{ backgroundOpacity: 0.55, blur: 3 }}
      >
        <ManufacturerForm
          manufacturer={editingManufacturer}
          onSuccess={handleSuccess}
          onCancel={handleModalClose}
        />
      </Modal>
    </>
  );
};

export default ManufacturersList;
