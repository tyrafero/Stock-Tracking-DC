import { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import {
  AppShell,
  Burger,
  Group,
  Text,
  NavLink,
  Avatar,
  Menu,
  UnstyledButton,
  Flex,
  Badge,
  Box,
} from '@mantine/core';
import { useDisclosure, useMediaQuery } from '@mantine/hooks';
import {
  IconDashboard,
  IconPackage,
  IconHistory,
  IconReservedLine,
  IconArrowsExchange,
  IconHandStop,
  IconLogout,
  IconUser,
  IconSettings,
  IconChevronDown,
  IconClipboardList,
  IconShoppingCart,
  IconUsersGroup,
} from '@tabler/icons-react';
import { useAuth, useUserRole } from '@/states/authState';

const Layout: React.FC = () => {
  const [opened, { toggle, close }] = useDisclosure();
  const { user, logout } = useAuth();
  const userRole = useUserRole();
  const navigate = useNavigate();
  const isMobile = useMediaQuery('(max-width: 768px)');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleNavigate = (path: string) => {
    navigate(path);
    if (isMobile) {
      close();
    }
  };

  const navItems = [
    {
      label: 'Dashboard',
      icon: IconDashboard,
      path: '/dashboard',
    },
    {
      label: 'Stock Management',
      icon: IconPackage,
      path: '/stock',
      children: [
        { label: 'Add New Stock', path: '/stock/create' },
        { label: 'Stock History', path: '/stock/history' },
        { label: 'Committed Stock', path: '/stock/committed' },
      ],
    },
    {
      label: 'Reservations',
      icon: IconReservedLine,
      path: '/reservations',
      children: [
        { label: 'Create Reservation', path: '/reservations/create' },
      ],
    },
    {
      label: 'Transfers',
      icon: IconArrowsExchange,
      path: '/transfers',
      children: [
        { label: 'Create Transfer', path: '/transfers/create' },
      ],
    },
    {
      label: 'Stocktake',
      icon: IconClipboardList,
      path: '/stocktake',
    },
    {
      label: 'Purchase Orders',
      icon: IconShoppingCart,
      path: '/purchase-orders',
    },
    {
      label: 'Manufacturers',
      icon: IconUsersGroup,
      path: '/manufacturers',
    },
  ];

  const getRoleBadgeColor = (role: string) => {
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
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { mobile: !opened, desktop: false }
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group gap="sm">
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <Text size="lg" fw={700} c="blue" truncate>
              Stock Tracking DC
            </Text>
          </Group>

          <Group gap="xs">
            <Menu shadow="md" width={200}>
              <Menu.Target>
                <UnstyledButton>
                  <Flex align="center" gap="xs">
                    <Avatar size="sm" radius="xl">
                      {user?.first_name?.[0] || user?.username?.[0] || 'U'}
                    </Avatar>
                    <Box style={{ textAlign: 'left' }} visibleFrom="sm">
                      <Text size="sm" fw={500} truncate>
                        {user?.first_name && user?.last_name
                          ? `${user.first_name} ${user.last_name}`
                          : user?.username || 'User'}
                      </Text>
                      {userRole && (
                        <Badge size="xs" color={getRoleBadgeColor(userRole)} variant="light">
                          {userRole.charAt(0).toUpperCase() + userRole.slice(1).replace('_', ' ')}
                        </Badge>
                      )}
                    </Box>
                    <Box visibleFrom="sm">
                      <IconChevronDown size={14} />
                    </Box>
                  </Flex>
                </UnstyledButton>
              </Menu.Target>

              <Menu.Dropdown>
                <Menu.Label>Account</Menu.Label>
                <Menu.Item leftSection={<IconUser size={14} />}>
                  Profile
                </Menu.Item>
                <Menu.Item leftSection={<IconSettings size={14} />}>
                  Settings
                </Menu.Item>

                <Menu.Divider />

                <Menu.Item
                  leftSection={<IconLogout size={14} />}
                  onClick={handleLogout}
                  c="red"
                >
                  Logout
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Text size="sm" c="dimmed" mb="md">
          Navigation
        </Text>

        {navItems.map((item) => (
          <NavLink
            key={item.path}
            label={item.label}
            leftSection={<item.icon size="1rem" />}
            onClick={() => handleNavigate(item.path)}
            childrenOffset={28}
          >
            {item.children?.map((child) => (
              <NavLink
                key={child.path}
                label={child.label}
                onClick={() => handleNavigate(child.path)}
              />
            ))}
          </NavLink>
        ))}
      </AppShell.Navbar>

      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
};

export default Layout;