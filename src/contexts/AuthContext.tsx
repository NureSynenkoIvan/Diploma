import { createContext, useContext, useEffect, useMemo, useState } from 'react'

type AuthContextValue = {
  isAuthenticated: boolean
  login: () => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const stored = window.localStorage.getItem('trading-app:auth')
    if (stored === 'true') {
      setIsAuthenticated(true)
    }
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated,
      login: () => {
        window.localStorage.setItem('trading-app:auth', 'true')
        setIsAuthenticated(true)
      },
      logout: () => {
        window.localStorage.removeItem('trading-app:auth')
        setIsAuthenticated(false)
      },
    }),
    [isAuthenticated],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

