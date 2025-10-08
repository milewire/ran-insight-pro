"use client"

import { createContext, useContext, useEffect, useState, ReactNode } from "react"

interface User {
  user_id: string
  username: string
  email: string
  role: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (userData: {
    username: string
    email: string
    password: string
    full_name?: string
  }) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem("auth_token")
    const storedUser = localStorage.getItem("auth_user")

    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }
    setIsLoading(false)
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Login failed")
      }

      const data = await response.json()
      
      setToken(data.access_token)
      setUser(data.user_info)
      
      // Store in localStorage
      localStorage.setItem("auth_token", data.access_token)
      localStorage.setItem("auth_user", JSON.stringify(data.user_info))
    } catch (error) {
      throw error
    }
  }

  const register = async (userData: {
    username: string
    email: string
    password: string
    full_name?: string
  }) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Registration failed")
      }

      // After successful registration, automatically log in
      await login(userData.username, userData.password)
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem("auth_token")
    localStorage.removeItem("auth_user")
  }

  const refreshToken = async () => {
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error("Token refresh failed")
      }

      const data = await response.json()
      setToken(data.access_token)
      localStorage.setItem("auth_token", data.access_token)
    } catch (error) {
      // If refresh fails, logout user
      logout()
      throw error
    }
  }

  const value = {
    user,
    token,
    isLoading,
    login,
    register,
    logout,
    refreshToken,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

// Helper function to make authenticated API calls
export async function authenticatedFetch(url: string, options: RequestInit = {}, token?: string) {
  const authToken = token || localStorage.getItem("auth_token")
  
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  }

  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (response.status === 401) {
    // Token expired or invalid, clear auth state
    localStorage.removeItem("auth_token")
    localStorage.removeItem("auth_user")
    window.location.href = "/login"
  }

  return response
}
