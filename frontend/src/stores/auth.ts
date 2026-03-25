import { create } from "zustand";
import { api } from "../api/client";

export interface AuthState {
  user: any | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    companyName: string
  ) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  loading: true,

  login: async (email, password) => {
    const resp = await api.login(email, password);
    api.setToken(resp.access_token);
    const user = await api.getMe();
    set({ user });
  },

  register: async (email, password, companyName) => {
    const resp = await api.register(email, password, companyName);
    api.setToken(resp.access_token);
    const user = await api.getMe();
    set({ user });
  },

  logout: () => {
    api.setToken(null);
    set({ user: null });
  },

  loadUser: async () => {
    try {
      if (api.getToken()) {
        const user = await api.getMe();
        set({ user, loading: false });
      } else {
        set({ loading: false });
      }
    } catch {
      set({ user: null, loading: false });
    }
  },
}));
