'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService } from '@/lib/auth';
import { User } from '@/lib/types';
import { removeStorageItem } from '@/utils/storage';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<any>;
  signup: (username: string, email: string, password: string) => Promise<any>;
  logout: () => void;
  checkAuthStatus: () => Promise<void>;
  refreshAuthStatus: () => Promise<any>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // Check authentication status on initial load (only in browser)
  useEffect(() => {
    // Only run in browser environment
    if (typeof window === 'undefined') {
      setIsLoading(false);
      return;
    }

    const checkStoredAuth = async () => {
      setIsLoading(true);
      try {
        const isAuth = authService.isAuthenticated();

        if (isAuth) {
          const currentUser = authService.getCurrentUser();

          // Even if the user doesn't have a valid ID, we can still authenticate them
          // The ID might be retrieved later or the backend might provide it in a different format
          if (currentUser) {
            setUser(currentUser);
            const token = authService.getToken();
            setToken(token);
            setIsAuthenticated(true);
          } else {
            // If there's no user object at all, treat as not authenticated
            setUser(null);
            setToken(null);
            setIsAuthenticated(false);
            authService.logout(); // Clean up any invalid token
          }
        } else {
          // No valid token found, user remains unauthenticated
        }
      } catch (err) {
        console.error('Error checking auth status:', err);
        // Clear invalid token from both localStorage and cookies if there's an error
        removeStorageItem('token');
        if (typeof document !== 'undefined') {
          document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkStoredAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.login({ email, password });

      if (result.success) {
        // Wait a moment to ensure the token is properly stored in both localStorage and cookies
        await new Promise(resolve => setTimeout(resolve, 100));

        // Get the token to verify it's properly stored
        const token = authService.getToken();

        // Get the current user which should extract info from the JWT
        const currentUser = authService.getCurrentUser();

        // Even if the user doesn't have a valid ID, we can still authenticate them
        // The ID might be retrieved later or the backend might provide it in a different format
        if (currentUser) {
          setUser(currentUser);
          setToken(token);
          setIsAuthenticated(true);
        } else {
          // If there's no user object at all, treat as authentication failure
          setError('Invalid user data received from server');
          authService.logout(); // Clean up any invalid token
        }
      } else {
        setError(result.error || 'Login failed');
      }
      return result;
    } catch (err: any) {
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (username: string, email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.signup({ username, email, password });
      if (result.success) {
        // Automatically log the user in after successful signup
        await login(email, password);
      } else {
        setError(result.error || 'Signup failed');
      }
      return result;
    } catch (err: any) {
      // Don't set error here since the component will handle it
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
  };

  const checkAuthStatus = async () => {
    if (authService.isAuthenticated()) {
      const currentUser = authService.getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
        setToken(authService.getToken());
        setIsAuthenticated(true);
      } else {
        // If there's no user object at all, treat as not authenticated
        setUser(null);
        setToken(null);
        setIsAuthenticated(false);
        authService.logout(); // Clean up any invalid token
      }
    } else {
      setUser(null);
      setToken(null);
      setIsAuthenticated(false);
    }
  };

  const refreshAuthStatus = async () => {
    // Force a refresh of the auth status by rechecking the token
    const isAuth = authService.isAuthenticated();
    if (isAuth) {
      const currentUser = authService.getCurrentUser();
      if (currentUser) {
        // Only update state if the user data has actually changed
        setUser(prevUser => {
          if (!prevUser || prevUser.id !== currentUser.id || prevUser.email !== currentUser.email) {
            return currentUser;
          }
          return prevUser; // Don't update if nothing has changed
        });

        const token = authService.getToken();
        setToken(prevToken => {
          if (prevToken !== token) {
            return token;
          }
          return prevToken; // Don't update if token hasn't changed
        });

        setIsAuthenticated(prevAuth => {
          if (!prevAuth) {
            return true;
          }
          return prevAuth; // Don't update if already authenticated
        });

        return { success: true, user: currentUser };
      } else {
        // If there's no user object at all, treat as not authenticated
        setUser(null);
        setToken(null);
        setIsAuthenticated(false);
        authService.logout(); // Clean up any invalid token
        return { success: false, error: 'Could not retrieve user data' };
      }
    } else {
      setUser(null);
      setToken(null);
      setIsAuthenticated(false);
      return { success: false, error: 'Not authenticated' };
    }
  };

  const value = {
    user,
    token,
    isLoading,
    error,
    isAuthenticated,
    login,
    signup,
    logout,
    checkAuthStatus,
    refreshAuthStatus,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};