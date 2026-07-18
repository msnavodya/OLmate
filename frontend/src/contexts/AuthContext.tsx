import { useState, useCallback, useEffect, ReactNode } from 'react';
import { authService } from '../services/authService';
import { AuthContext, User } from './AuthContextValue';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(authService.getStoredUser());
  const [isLoading, setIsLoading] = useState(false);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await authService.login({ email, password });
      authService.setStoredAuth(response);
      setUser(response.user);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (name: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await authService.register({ name, email, password });
      authService.setStoredAuth(response);
      setUser(response.user);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshUser = useCallback(async () => {
    if (!authService.getStoredToken()) {
      setUser(null);
      return;
    }

    setIsLoading(true);
    try {
      const currentUser = await authService.getCurrentUser();
      authService.setStoredUser(currentUser);
      setUser(currentUser);
    } catch {
      authService.logout();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateProfile = useCallback(async (name: string, email: string) => {
    setIsLoading(true);
    try {
      const updatedUser = await authService.updateProfile({ name, email });
      authService.setStoredUser(updatedUser);
      setUser(updatedUser);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const changePassword = useCallback(async (currentPassword: string, newPassword: string) => {
    setIsLoading(true);
    try {
      await authService.changePassword(currentPassword, newPassword);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        refreshUser,
        updateProfile,
        changePassword,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
