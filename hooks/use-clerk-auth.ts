"use client"

import { useUser, useAuth as useClerkAuth, useClerk } from "@clerk/nextjs"
import { useRouter } from "next/navigation"

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

// Helper function to make authenticated API calls with Clerk token
export async function authenticatedFetch(url: string, options: RequestInit = {}, token?: string) {
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (response.status === 401) {
    // Token expired or invalid, redirect to sign-in
    window.location.href = "/sign-in"
  }

  return response
}

// Custom hook that provides a similar interface to the original useAuth
export function useAuth(): AuthContextType {
  const { user: clerkUser, isLoaded } = useUser()
  const { getToken } = useClerkAuth()
  const { signOut } = useClerk()
  const router = useRouter()

  // Transform Clerk user to our expected format
  const user: User | null = clerkUser ? {
    user_id: clerkUser.id,
    username: clerkUser.username || clerkUser.emailAddresses[0]?.emailAddress || '',
    email: clerkUser.emailAddresses[0]?.emailAddress || '',
    role: clerkUser.publicMetadata?.role as string || 'user'
  } : null

  const login = async (username: string, password: string) => {
    // Clerk handles login through their components, so this is mainly for compatibility
    // In practice, you'd use Clerk's SignIn component
    throw new Error("Use Clerk's SignIn component for authentication")
  }

  const register = async (userData: {
    username: string
    email: string
    password: string
    full_name?: string
  }) => {
    // Clerk handles registration through their components, so this is mainly for compatibility
    // In practice, you'd use Clerk's SignUp component
    throw new Error("Use Clerk's SignUp component for registration")
  }

  const logout = async () => {
    await signOut()
    router.push("/")
  }

  const refreshToken = async () => {
    // Clerk handles token refresh automatically
    // This is mainly for compatibility with existing code
    return Promise.resolve()
  }

  return {
    user,
    token: null, // Clerk handles tokens internally
    isLoading: !isLoaded,
    login,
    register,
    logout,
    refreshToken,
  }
}

// Hook to get Clerk token for API calls
export function useClerkToken() {
  const { getToken } = useClerkAuth()
  
  const getAuthToken = async () => {
    try {
      return await getToken()
    } catch (error) {
      console.error("Failed to get Clerk token:", error)
      return null
    }
  }

  return { getAuthToken }
}
