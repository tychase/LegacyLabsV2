import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useEffect, useState } from 'react'
import { Loader2 } from 'lucide-react'

export default function ProtectedRoute() {
  const { isAuthenticated, checkAuth, token } = useAuthStore()
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    const verifyAuth = async () => {
      if (token) {
        await checkAuth()
      }
      setIsChecking(false)
    }
    verifyAuth()
  }, [token, checkAuth])

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />
}
