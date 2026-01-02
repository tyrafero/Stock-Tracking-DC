import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Paper,
  TextInput,
  PasswordInput,
  Button,
  Title,
  Text,
  Container,
  Alert,
  Box,
  Center,
} from '@mantine/core';
import { IconAlertCircle, IconUser, IconLock } from '@tabler/icons-react';
import { useAuth } from '@/states/authState';
import { useNotify } from '@/states/notificationState';

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

const Login: React.FC = () => {
  const { login, isAuthenticated, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const notify = useNotify();

  const from = (location.state as any)?.from?.pathname || '/dashboard';

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  useEffect(() => {
    // Clear any existing errors when component mounts
    clearError();
  }, [clearError]);

  const onSubmit = async (data: LoginFormData) => {
    try {
      clearError();
      await login(data);
      notify.success('Welcome back!', 'You have successfully logged in.');
      navigate(from, { replace: true });
    } catch (error: any) {
      notify.error('Login Failed', error.message || 'Please check your credentials and try again.');
      reset({ password: '' }); // Clear password on error
    }
  };

  return (
    <Container size={420} my={40}>
      <Center>
        <Box w="100%">
          <Title ta="center" mb={5}>
            Stock Tracking DC
          </Title>
          <Text c="dimmed" size="sm" ta="center" mb={30}>
            Welcome back! Please sign in to your account
          </Text>

          <Paper withBorder shadow="md" p={30} mt={30} radius="md">
            {error && (
              <Alert
                icon={<IconAlertCircle size="1rem" />}
                title="Login Error"
                color="red"
                mb="md"
                variant="filled"
              >
                {error}
              </Alert>
            )}

            <form onSubmit={handleSubmit(onSubmit)}>
              <TextInput
                label="Username"
                placeholder="Enter your username"
                leftSection={<IconUser size="1rem" />}
                error={errors.username?.message}
                disabled={isSubmitting || isLoading}
                {...register('username')}
                mb="md"
              />

              <PasswordInput
                label="Password"
                placeholder="Enter your password"
                leftSection={<IconLock size="1rem" />}
                error={errors.password?.message}
                disabled={isSubmitting || isLoading}
                {...register('password')}
                mb="xl"
              />

              <Button
                type="submit"
                fullWidth
                loading={isSubmitting || isLoading}
                size="md"
              >
                Sign In
              </Button>
            </form>

            <Text c="dimmed" size="sm" ta="center" mt="xl">
              Need access? Contact your system administrator
            </Text>
          </Paper>
        </Box>
      </Center>
    </Container>
  );
};

export default Login;