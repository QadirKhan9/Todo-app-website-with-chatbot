// frontend/src/hooks/useAuth.ts
import { useState, useEffect } from 'react';
import { authService } from '../lib/auth';
import { User } from '../lib/types';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isLoading: true,
    error: null,
    isAuthenticated: false,
  });

  useEffect(() => {
    // Check authentication status on mount
    const checkAuthStatus = async () => {
      try {
        if (authService.isAuthenticated()) {
          const user = authService.getCurrentUser();
          setAuthState({
            user,
            isLoading: false,
            error: null,
            isAuthenticated: true,
          });
        } else {
          setAuthState({
            user: null,
            isLoading: false,
            error: null,
            isAuthenticated: false,
          });
        }
      } catch (error: any) {
        setAuthState({
          user: null,
          isLoading: false,
          error: error.message || 'Error checking authentication status',
          isAuthenticated: false,
        });
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (email: string, password: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const result = await authService.login({ email, password });
      if (result.success) {
        setAuthState({
          user: result.user || null,
          isLoading: false,
          error: null,
          isAuthenticated: !!result.user,
        });
        return { success: true, user: result.user, token: result.token };
      } else {
        setAuthState(prev => ({
          ...prev,
          isLoading: false,
          error: result.error || 'Login failed',
        }));
        return { success: false, error: result.error || 'Login failed' };
      }
    } catch (error: any) {
      // Since we're now returning errors instead of throwing them in AuthService,
      // this catch block might not be reached, but keeping it for safety
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error.message || 'Login failed',
      }));
      return { success: false, error: error.message || 'Login failed' };
    }
  };

  const signup = async (username: string, email: string, password: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const result = await authService.signup({ username, email, password });
      if (result.success && result.user) {
        setAuthState({
          user: result.user,
          isLoading: false,
          error: null,
          isAuthenticated: true,
        });
        return { success: true, user: result.user, token: result.token };
      } else {
        setAuthState(prev => ({
          ...prev,
          isLoading: false,
          error: result.error || 'Signup failed',
        }));
        return { success: false, error: result.error || 'Signup failed' };
      }
    } catch (error: any) {
      // Since we're now returning errors instead of throwing them in AuthService,
      // this catch block might not be reached, but keeping it for safety
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error.message || 'Signup failed',
      }));
      return { success: false, error: error.message || 'Signup failed' };
    }
  };

  const logout = () => {
    authService.logout();
    setAuthState({
      user: null,
      isLoading: false,
      error: null,
      isAuthenticated: false,
    });
  };

  return {
    ...authState,
    login,
    signup,
    logout,
  };
};