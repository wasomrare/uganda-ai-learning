import { create } from 'zustand';
import Cookies from 'js-cookie';
import type { User } from '@/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  setAuth: (user: User, access: string, refresh: string) => void;
  clearAuth: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: typeof window !== 'undefined' ? Cookies.get('access_token') ?? null : null,
  refreshToken: typeof window !== 'undefined' ? Cookies.get('refresh_token') ?? null : null,
  isLoading: false,

  setAuth: (user, access, refresh) => {
    Cookies.set('access_token', access, { expires: 1, sameSite: 'lax' });
    Cookies.set('refresh_token', refresh, { expires: 30, sameSite: 'lax' });
    set({ user, accessToken: access, refreshToken: refresh });
  },

  clearAuth: () => {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    set({ user: null, accessToken: null, refreshToken: null });
  },

  setLoading: (loading) => set({ isLoading: loading }),
}));
