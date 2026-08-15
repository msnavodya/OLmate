import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';

// In development, use Vite's /api proxy. Deployments can set VITE_API_URL.
export const API_BASE_URL = (import.meta.env.VITE_API_URL as string) || '/api';
const LOCAL_API_FALLBACKS =
  import.meta.env.DEV && !import.meta.env.VITE_API_URL
    ? ['http://127.0.0.1:8001/api', 'http://127.0.0.1:8000/api']
    : [];

interface RetriableRequestConfig extends InternalAxiosRequestConfig {
  fallbackApiIndex?: number;
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to request if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const retryResponse = await retryWithLocalBackend(error);
    if (retryResponse) {
      return retryResponse;
    }

    const requestUrl = error.config?.url || '';
    const isAuthAttempt = requestUrl.includes('/auth/login') || requestUrl.includes('/auth/register');

    if (error.response?.status === 401 && !isAuthAttempt) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

async function retryWithLocalBackend(error: AxiosError) {
  if (error.response || LOCAL_API_FALLBACKS.length === 0 || !error.config) {
    return null;
  }

  const config = error.config as RetriableRequestConfig;
  const nextFallbackIndex = config.fallbackApiIndex ?? 0;
  const fallbackBaseUrl = LOCAL_API_FALLBACKS[nextFallbackIndex];

  if (!fallbackBaseUrl) {
    return null;
  }

  config.fallbackApiIndex = nextFallbackIndex + 1;
  config.baseURL = fallbackBaseUrl;
  return apiClient.request(config);
}

export default apiClient;
