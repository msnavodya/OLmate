import apiClient from './apiClient';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  name: string;
  email: string;
  password: string;
  role?: string;
}

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

interface ProfileUpdate {
  name?: string;
  email?: string;
}

const REMEMBERED_EMAIL_KEY = 'remembered_login_email';

export const authService = {
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await apiClient.post('/auth/register', {
      ...data,
      name: data.name.trim(),
      email: data.email.trim().toLowerCase(),
    });
    return response.data;
  },

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post('/auth/login', {
      email: credentials.email.trim().toLowerCase(),
      password: credentials.password,
    });
    return response.data;
  },

  async getCurrentUser(): Promise<AuthUser> {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  async updateProfile(data: ProfileUpdate): Promise<AuthUser> {
    const response = await apiClient.patch('/auth/me', {
      ...data,
      ...(data.name !== undefined ? { name: data.name.trim() } : {}),
      ...(data.email !== undefined ? { email: data.email.trim().toLowerCase() } : {}),
    });
    return response.data;
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/me/password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  getStoredToken(): string | null {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    try {
      const parts = token.split('.');
      if (parts.length !== 3) return token;
      const payload = JSON.parse(atob(parts[1]));
      if (payload.exp && typeof payload.exp === 'number') {
        const now = Math.floor(Date.now() / 1000);
        if (payload.exp < now) {
          // Token expired — clear stored auth
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          return null;
        }
      }
    } catch {
      // If parsing fails, return the raw token and let server validate it
      return token;
    }

    return token;
  },

  getStoredUser() {
    const user = localStorage.getItem('user');
    if (!user) return null;

    try {
      return JSON.parse(user);
    } catch {
      localStorage.removeItem('user');
      return null;
    }
  },

  setStoredAuth(response: AuthResponse): void {
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('user', JSON.stringify(response.user));
  },

  setStoredUser(user: AuthUser): void {
    localStorage.setItem('user', JSON.stringify(user));
  },

  getRememberedEmail(): string {
    return localStorage.getItem(REMEMBERED_EMAIL_KEY) || '';
  },

  setRememberedEmail(email: string): void {
    localStorage.setItem(REMEMBERED_EMAIL_KEY, email.trim().toLowerCase());
  },

  clearRememberedEmail(): void {
    localStorage.removeItem(REMEMBERED_EMAIL_KEY);
  },
};
