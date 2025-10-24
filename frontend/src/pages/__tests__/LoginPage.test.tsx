/**
 * Tests for LoginPage component
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../LoginPage';
import { authService } from '../../services/authService';

// Mock authService
jest.mock('../../services/authService');
const mockedAuthService = authService as jest.Mocked<typeof authService>;

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

describe('LoginPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render login form', () => {
    render(
      <BrowserRouter>
        <LoginPage onLogin={jest.fn()} />
      </BrowserRouter>
    );

    expect(screen.getByText(/sign in to your account/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('should handle successful login', async () => {
    const mockOnLogin = jest.fn();
    const mockLoginResponse = {
      access_token: 'test-token',
      token_type: 'bearer',
      user: {
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'admin'
      }
    };

    mockedAuthService.login.mockResolvedValueOnce(mockLoginResponse);

    render(
      <BrowserRouter>
        <LoginPage onLogin={mockOnLogin} />
      </BrowserRouter>
    );

    // Fill in form
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockedAuthService.login).toHaveBeenCalledWith(
        'test@example.com',
        'password123'
      );
      expect(mockOnLogin).toHaveBeenCalledWith(mockLoginResponse.user);
    });
  });

  it('should display error on failed login', async () => {
    mockedAuthService.login.mockRejectedValueOnce(
      new Error('Invalid credentials')
    );

    render(
      <BrowserRouter>
        <LoginPage onLogin={jest.fn()} />
      </BrowserRouter>
    );

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'wrong' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });

  it('should have link to register page', () => {
    render(
      <BrowserRouter>
        <LoginPage onLogin={jest.fn()} />
      </BrowserRouter>
    );

    const registerLink = screen.getByText(/create an account/i);
    expect(registerLink).toBeInTheDocument();
  });

  it('should have link to forgot password', () => {
    render(
      <BrowserRouter>
        <LoginPage onLogin={jest.fn()} />
      </BrowserRouter>
    );

    const forgotLink = screen.getByText(/forgot password/i);
    expect(forgotLink).toBeInTheDocument();
  });

  it('should validate required fields', async () => {
    render(
      <BrowserRouter>
        <LoginPage onLogin={jest.fn()} />
      </BrowserRouter>
    );

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockedAuthService.login).not.toHaveBeenCalled();
    });
  });
});
