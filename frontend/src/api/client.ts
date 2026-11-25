import axios, {
  AxiosHeaders,
  type AxiosError,
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios";
import type { RefreshTokenRequest, TokenResponse } from "../types/api";

const ACCESS_TOKEN_STORAGE_KEY = "edu_auto_grader_access_token";
const REFRESH_TOKEN_STORAGE_KEY = "edu_auto_grader_refresh_token";
const REQUEST_TIMEOUT_MS = 15000;

export interface RetryableAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

export type AuthFailureListener = () => void;

const authFailureListeners = new Set<AuthFailureListener>();
let refreshPromise: Promise<string> | null = null;
let authSessionGeneration = 0;

export function getAccessToken(): string | null {
  return window.localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
}

export function setAccessToken(token: string): void {
  window.localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, token);
}

export function getRefreshToken(): string | null {
  return window.localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);
}

export function setRefreshToken(token: string): void {
  window.localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, token);
}

export function clearAuthTokens(): void {
  authSessionGeneration += 1;
  window.localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
}

export function subscribeToAuthFailure(
  listener: AuthFailureListener
): () => void {
  authFailureListeners.add(listener);
  return () => {
    authFailureListeners.delete(listener);
  };
}

function notifyAuthFailure(): void {
  for (const listener of authFailureListeners) {
    listener();
  }
}

function isAuthRefreshExcludedUrl(url: string | undefined): boolean {
  if (url === undefined || url.length === 0) {
    return false;
  }
  const normalizedPath = (url.split(/[?#]/, 1)[0] ?? "").replace(/\/+$/, "");
  return (
    normalizedPath === "/auth/login" ||
    normalizedPath === "auth/login" ||
    normalizedPath.endsWith("/auth/login") ||
    normalizedPath === "/auth/refresh" ||
    normalizedPath === "auth/refresh" ||
    normalizedPath.endsWith("/auth/refresh")
  );
}

function setAuthorizationHeader(
  config: RetryableAxiosRequestConfig,
  accessToken: string
): void {
  const headers = AxiosHeaders.from(config.headers);
  headers.set("Authorization", `Bearer ${accessToken}`);
  config.headers = headers;
}

export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

function startSingleFlightRefresh(refreshToken: string): Promise<string> {
  if (refreshPromise !== null) {
    return refreshPromise;
  }

  const requestGeneration = authSessionGeneration;
  const payload: RefreshTokenRequest = { refresh_token: refreshToken };
  const refreshUrl = `${API_BASE_URL.replace(/\/+$/, "")}/auth/refresh`;

  refreshPromise = axios
    .post<TokenResponse>(refreshUrl, payload, {
      headers: {
        "Content-Type": "application/json",
      },
      timeout: REQUEST_TIMEOUT_MS,
    })
    .then((response): string => {
      if (requestGeneration !== authSessionGeneration) {
        throw new Error("Сесію користувача було завершено під час оновлення токена.");
      }

      const nextAccessToken = response.data.access_token;
      const nextRefreshToken = response.data.refresh_token;

      if (typeof nextAccessToken !== "string" || nextAccessToken.length === 0) {
        throw new Error("Сервер не повернув дійсний access_token.");
      }

      setAccessToken(nextAccessToken);
      if (
        typeof nextRefreshToken === "string" &&
        nextRefreshToken.length > 0
      ) {
        setRefreshToken(nextRefreshToken);
      }

      return nextAccessToken;
    })
    .catch((refreshError: unknown): never => {
      if (requestGeneration === authSessionGeneration) {
        clearAuthTokens();
        notifyAuthFailure();
      }
      throw refreshError;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}

export function refreshAccessToken(): Promise<string> {
  if (refreshPromise !== null) {
    return refreshPromise;
  }

  const refreshToken = getRefreshToken();
  if (refreshToken === null || refreshToken.length === 0) {
    clearAuthTokens();
    notifyAuthFailure();
    return Promise.reject(new Error("Refresh token відсутній."));
  }

  return startSingleFlightRefresh(refreshToken);
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: REQUEST_TIMEOUT_MS,
});

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
    const token = getAccessToken();
    if (token !== null && token.length > 0) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError): Promise<never> => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => response,
  async (error: AxiosError): Promise<AxiosResponse> => {
    const status = error.response?.status;
    const originalRequest = error.config as
      | RetryableAxiosRequestConfig
      | undefined;

    if (status !== 401 || originalRequest === undefined) {
      return Promise.reject(error);
    }

    if (isAuthRefreshExcludedUrl(originalRequest.url)) {
      return Promise.reject(error);
    }

    if (originalRequest._retry === true) {
      clearAuthTokens();
      notifyAuthFailure();
      return Promise.reject(error);
    }

    if (refreshPromise === null) {
      const refreshToken = getRefreshToken();
      if (refreshToken === null || refreshToken.length === 0) {
        clearAuthTokens();
        notifyAuthFailure();
        return Promise.reject(error);
      }
    }

    originalRequest._retry = true;

    const nextAccessToken = await refreshAccessToken();
    setAuthorizationHeader(originalRequest, nextAccessToken);
    return apiClient(originalRequest);
  }
);

export default apiClient;
