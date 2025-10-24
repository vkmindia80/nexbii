/**
 * Tests for authService
 */
import { authService } from '../authService';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('authService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('login', () => {
    it('should login successfully and store token', async () => {
      const mockResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
          user: {
            id: '1',
            email: 'test@example.com',
            full_name: 'Test User',
            role: 'admin'
          }
        }
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const result = await authService.login('test@example.com', 'password123');

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/auth/login', {
        email: 'test@example.com',
        password: 'password123'
      });
      expect(result).toEqual(mockResponse.data);
      expect(localStorage.getItem('token')).toBe('test-token');
    });

    it('should handle login failure', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Invalid credentials'));

      await expect(
        authService.login('test@example.com', 'wrong')
      ).rejects.toThrow('Invalid credentials');
    });
  });

  describe('register', () => {
    it('should register successfully', async () => {
      const mockResponse = {
        data: {
          id: '1',
          email: 'new@example.com',
          full_name: 'New User',
          role: 'viewer'
        }
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const result = await authService.register(
        'new@example.com',
        'password123',
        'New User'
      );

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/auth/register', {
        email: 'new@example.com',
        password: 'password123',
        full_name: 'New User'
      });
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('getCurrentUser', () => {
    it('should get current user', async () => {
      const mockUser = {
        data: {
          id: '1',
          email: 'test@example.com',
          full_name: 'Test User',
          role: 'admin'
        }
      };

      mockedAxios.get.mockResolvedValueOnce(mockUser);

      const result = await authService.getCurrentUser();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/auth/me');
      expect(result).toEqual(mockUser.data);
    });
  });

  describe('logout', () => {
    it('should clear token on logout', () => {
      localStorage.setItem('token', 'test-token');
      
      authService.logout();

      expect(localStorage.getItem('token')).toBeNull();
    });
  });

  describe('getToken', () => {
    it('should return token from localStorage', () => {
      localStorage.setItem('token', 'test-token');

      const token = authService.getToken();

      expect(token).toBe('test-token');
    });

    it('should return null if no token', () => {
      const token = authService.getToken();

      expect(token).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true if token exists', () => {
      localStorage.setItem('token', 'test-token');

      expect(authService.isAuthenticated()).toBe(true);
    });

    it('should return false if no token', () => {
      expect(authService.isAuthenticated()).toBe(false);
    });
  });
});
