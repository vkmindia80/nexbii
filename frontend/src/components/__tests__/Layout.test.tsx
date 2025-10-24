/**
 * Tests for Layout component
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Layout from '../Layout';
import { authService } from '../../services/authService';

// Mock authService
jest.mock('../../services/authService');
const mockedAuthService = authService as jest.Mocked<typeof authService>;

// Mock WebSocket hook
jest.mock('../../hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    isConnected: false,
    onlineUsers: [],
    joinRoom: jest.fn(),
    leaveRoom: jest.fn()
  })
}));

describe('Layout Component', () => {
  const mockUser = {
    id: '1',
    email: 'test@example.com',
    full_name: 'Test User',
    role: 'admin' as const
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderLayout = () => {
    return render(
      <BrowserRouter>
        <Layout user={mockUser} onLogout={jest.fn()}>
          <div>Test Content</div>
        </Layout>
      </BrowserRouter>
    );
  };

  it('should render layout with user info', () => {
    renderLayout();

    expect(screen.getByText('NexBII')).toBeInTheDocument();
    expect(screen.getByText('Test User')).toBeInTheDocument();
  });

  it('should render navigation links', () => {
    renderLayout();

    expect(screen.getByText('Data Sources')).toBeInTheDocument();
    expect(screen.getByText('Queries')).toBeInTheDocument();
    expect(screen.getByText('Dashboards')).toBeInTheDocument();
    expect(screen.getByText('Analytics')).toBeInTheDocument();
  });

  it('should render children content', () => {
    renderLayout();

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('should show admin links for admin users', () => {
    renderLayout();

    expect(screen.getByText('Integrations')).toBeInTheDocument();
  });

  it('should call onLogout when logout is clicked', () => {
    const mockLogout = jest.fn();
    
    render(
      <BrowserRouter>
        <Layout user={mockUser} onLogout={mockLogout}>
          <div>Test Content</div>
        </Layout>
      </BrowserRouter>
    );

    // Find and click logout button
    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);

    expect(mockLogout).toHaveBeenCalled();
  });
});
