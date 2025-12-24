import { Grid, Card, Text, Title, Group, Badge, Stack } from '@mantine/core';
import { useAuth, useUserRole } from '@/states/authState';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const userRole = useUserRole();

  const getRoleColor = (role: string) => {
    const colors: Record<string, string> = {
      admin: 'red',
      owner: 'violet',
      logistics: 'blue',
      warehouse: 'green',
      stocktake_manager: 'orange',
      sales: 'cyan',
      accountant: 'yellow',
      warehouse_boy: 'gray',
      pending: 'gray',
    };
    return colors[role] || 'gray';
  };

  return (
    <div>
      <Group justify="space-between" mb="xl">
        <div>
          <Title order={1}>Dashboard</Title>
          <Text c="dimmed" size="lg">
            Welcome back, {user?.first_name || user?.username}!
          </Text>
        </div>
        {userRole && (
          <Badge size="lg" color={getRoleColor(userRole)} variant="light">
            {userRole.charAt(0).toUpperCase() + userRole.slice(1).replace('_', ' ')}
          </Badge>
        )}
      </Group>

      <Grid>
        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Stack gap="xs">
              <Text size="sm" c="dimmed">
                Total Stock Items
              </Text>
              <Text size="xl" fw={700}>
                --
              </Text>
              <Text size="xs" c="dimmed">
                API integration coming soon
              </Text>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Stack gap="xs">
              <Text size="sm" c="dimmed">
                Low Stock Items
              </Text>
              <Text size="xl" fw={700} c="orange">
                --
              </Text>
              <Text size="xs" c="dimmed">
                Items below reorder level
              </Text>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Stack gap="xs">
              <Text size="sm" c="dimmed">
                Active Reservations
              </Text>
              <Text size="xl" fw={700} c="blue">
                --
              </Text>
              <Text size="xs" c="dimmed">
                Stock reserved for customers
              </Text>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Stack gap="xs">
              <Text size="sm" c="dimmed">
                Pending Transfers
              </Text>
              <Text size="xl" fw={700} c="yellow">
                --
              </Text>
              <Text size="xs" c="dimmed">
                Transfers awaiting approval
              </Text>
            </Stack>
          </Card>
        </Grid.Col>
      </Grid>

      <Grid mt="xl">
        <Grid.Col span={12}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={3} mb="md">
              Quick Actions
            </Title>
            <Text c="dimmed">
              Stock management interface is being built. You can now:
            </Text>
            <ul>
              <li>Navigate using the sidebar</li>
              <li>Access stock management pages (coming soon)</li>
              <li>View your role and permissions</li>
              <li>Use the logout functionality</li>
            </ul>
          </Card>
        </Grid.Col>
      </Grid>
    </div>
  );
};

export default Dashboard;