import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactElement,
  type ReactNode,
} from "react";
import axios from "axios";
import apiClient, {
  clearAuthTokens,
  getAccessToken,
  getRefreshToken,
  refreshAccessToken,
  setAccessToken,
  setRefreshToken,
  subscribeToAuthFailure,
} from "../api/client";
import type {
  ErrorResponse,
  LoginRequest,
  TokenResponse,
  UserRead,
  UserRole,
} from "../types/api";

export interface AuthContextValue {
  user: UserRead | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<UserRead>;
  logout: () => void;
  refreshUser: () => Promise<UserRead | null>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const ROLE_DEFAULT_PATHS: Record<UserRole, string> = {
  student: "/student/courses",
  teacher: "/teacher/courses",
  admin: "/admin/users",
};

// eslint-disable-next-line react-refresh/only-export-components
export function getDefaultHomePath(role: UserRole): string {
  return ROLE_DEFAULT_PATHS[role];
}

// eslint-disable-next-line react-refresh/only-export-components
export function extractApiErrorMessage(
  error: unknown,
  fallbackMessage: string
): string {
  if (axios.isAxiosError<ErrorResponse>(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string" && detail.trim().length > 0) {
      return detail;
    }
  }
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }
  return fallbackMessage;
}

async function fetchCurrentUserProfile(): Promise<UserRead> {
  const response = await apiClient.get<UserRead>("/auth/me");
  return response.data;
}

export interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps): ReactElement {
  const [user, setUser] = useState<UserRead | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    return subscribeToAuthFailure(() => {
      setUser(null);
    });
  }, []);

  const refreshUser = useCallback(async (): Promise<UserRead | null> => {
    const accessToken = getAccessToken();
    const refreshToken = getRefreshToken();

    if (accessToken === null && refreshToken === null) {
      setUser(null);
      return null;
    }

    if (accessToken !== null) {
      try {
        const currentUser = await fetchCurrentUserProfile();
        setUser(currentUser);
        return currentUser;
      } catch {
        // Якщо access-токен був прострочений, apiClient вже виконав спробу silent refresh
        clearAuthTokens();
        setUser(null);
        return null;
      }
    }

    if (refreshToken !== null) {
      try {
        await refreshAccessToken();
        const currentUser = await fetchCurrentUserProfile();
        setUser(currentUser);
        return currentUser;
      } catch {
        clearAuthTokens();
        setUser(null);
        return null;
      }
    }

    clearAuthTokens();
    setUser(null);
    return null;
  }, []);

  useEffect(() => {
    let isMounted = true;

    const initializeAuth = async (): Promise<void> => {
      try {
        await refreshUser();
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    void initializeAuth();

    return () => {
      isMounted = false;
    };
  }, [refreshUser]);

  const login = useCallback(async (credentials: LoginRequest): Promise<UserRead> => {
    const tokenResponse = await apiClient.post<TokenResponse>(
      "/auth/login",
      credentials
    );
    setAccessToken(tokenResponse.data.access_token);
    setRefreshToken(tokenResponse.data.refresh_token);

    try {
      const currentUser = await fetchCurrentUserProfile();
      setUser(currentUser);
      return currentUser;
    } catch (error: unknown) {
      clearAuthTokens();
      setUser(null);
      throw error;
    }
  }, []);

  const logout = useCallback((): void => {
    clearAuthTokens();
    setUser(null);
  }, []);

  const contextValue = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      login,
      logout,
      refreshUser,
    }),
    [user, isLoading, login, logout, refreshUser]
  );

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth повинен викликатися всередині AuthProvider");
  }
  return context;
}
