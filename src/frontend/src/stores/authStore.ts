import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import axios from 'axios'

interface User {
  id: number
  email: string
  full_name?: string
  role: string
  subscription_tier: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
  setUser: (user: User | null) => void
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// Configure axios defaults
axios.defaults.baseURL = API_URL

// Add token to requests if it exists
axios.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await axios.post('/auth/login', {
            username: email,
            password,
          })
          
          const { access_token, user } = response.data
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      signup: async (email: string, password: string, fullName?: string) => {
        set({ isLoading: true })
        try {
          const response = await axios.post('/auth/signup', {
            email,
            password,
            full_name: fullName,
          })
          
          const { access_token, user } = response.data
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },

      checkAuth: async () => {
        const token = get().token
        if (!token) {
          set({ isAuthenticated: false })
          return
        }

        try {
          const response = await axios.get('/auth/me')
          set({
            user: response.data,
            isAuthenticated: true,
          })
        } catch (error) {
          // Token is invalid
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          })
        }
      },

      setUser: (user: User | null) => {
        set({ user })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
