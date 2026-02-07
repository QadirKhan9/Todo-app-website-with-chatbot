import axios from 'axios';
import { getStorageItem, setStorageItem, removeStorageItem } from '../utils/storage';

// Get the API base URL from environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  public client;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000, // 30 seconds timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include JWT token for non-auth endpoints
    this.client.interceptors.request.use(
      (config) => {
        // Don't add token for auth endpoints (signup, login)
        const isAuthEndpoint = config.url?.includes('/auth/') || config.url?.includes('/login') || config.url?.includes('/signup');

        // Try to get token from localStorage first, then from cookie
        let token = getStorageItem('token');

        if (!token && typeof document !== 'undefined') {
          // Extract token from cookies if not in localStorage (only in browser)
          const cookieToken = document.cookie
            .split(';')
            .find(cookie => cookie.trim().startsWith('token='));

          if (cookieToken) {
            token = cookieToken.split('=')[1];
          }
        }

        if (token && config.headers && !isAuthEndpoint) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error: any) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor to handle 401 responses (token expiration) and 409 conflicts
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      (error: any) => {
        if (error.response?.status === 401) {
          // Token might be expired, remove it from both localStorage and cookies and redirect to login
          removeStorageItem('token');

          // Remove token from cookies as well (only in browser)
          if (typeof document !== 'undefined') {
            document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
          }

          // Only redirect if we're in the browser (not during SSR)
          if (typeof window !== 'undefined') {
            // Dispatch a custom event to notify the app about the 401 error
            window.dispatchEvent(new CustomEvent('unauthorized'));

            // Redirect to login page
            window.location.href = '/login';
          }
        }

        if (error.response?.status === 403) {
          // Forbidden error - clear auth state and redirect to login
          removeStorageItem('token');

          // Remove token from cookies as well (only in browser)
          if (typeof document !== 'undefined') {
            document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
          }

          // Only redirect if we're in the browser (not during SSR)
          if (typeof window !== 'undefined') {
            // Dispatch a custom event to notify the app about the 403 error
            window.dispatchEvent(new CustomEvent('forbidden'));

            // Redirect to login page
            window.location.href = '/login';
          }
        }

        // For 409 Conflict errors, we don't want to log them in production
        if (error.response?.status === 409) {
          // Don't log 409 errors in production to avoid console spam
          if (process.env.NODE_ENV !== 'production') {
            console.error('Axios 409 error:', error);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Authentication endpoints
  async login(email: string, password: string) {
    return this.client.post('/api/v1/auth/login', { email, password }, {
      timeout: 30000 // 30 seconds for login
    });
  }

  async signup(username: string, email: string, password: string) {
    // Use a longer timeout for signup since it might involve email verification, etc.
    return this.client.post('/api/v1/auth/signup', { username, email, password }, {
      timeout: 60000 // 60 seconds for signup
    });
  }

  async logout() {
    return this.client.post('/api/v1/auth/logout', {}, {
      timeout: 15000 // 15 seconds for logout
    });
  }

  // Token management methods
  getToken() {
    // Try to get token from localStorage first, then from cookie
    let token = getStorageItem('token');

    if (!token && typeof document !== 'undefined') {
      // Extract token from cookies if not in localStorage (only in browser)
      const cookieToken = document.cookie
        .split(';')
        .find(cookie => cookie.trim().startsWith('token='));

      if (cookieToken) {
        token = cookieToken.split('=')[1];
      }
    }

    return token;
  }

  setToken(token: string) {
    // Store token in localStorage
    setStorageItem('token', token);

    // Also store in cookies for server-side access if needed (only in browser)
    if (typeof document !== 'undefined') {
      const expiryDate = new Date();
      expiryDate.setDate(expiryDate.getDate() + 7); // Token expires in 7 days

      document.cookie = `token=${token}; path=/; expires=${expiryDate.toUTCString()}; SameSite=Strict`;
    }
  }

  removeToken() {
    // Remove token from localStorage
    removeStorageItem('token');

    // Remove token from cookies as well (only in browser)
    if (typeof document !== 'undefined') {
      document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
    }
  }


  // User endpoints
  async getUserProfile() {
    return this.client.get('/api/v1/users/me', {
      timeout: 15000 // 15 seconds for getting user profile
    });
  }

  private getUserIdFromToken(): string | null {
    const token = getStorageItem('token');
    if (!token) return null;

    try {
      // Simple JWT token decoding to extract user ID
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );

      const payload = JSON.parse(jsonPayload);
      return payload.user_id || payload.sub;
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  }
}

export const apiClient = new ApiClient();

// Export the client instance for use in other services
export { ApiClient };