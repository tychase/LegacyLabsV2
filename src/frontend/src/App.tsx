import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import Layout from '@/components/Layout'
import HomePage from '@/pages/HomePage'
import DashboardPage from '@/pages/DashboardPage'
import ProjectPage from '@/pages/ProjectPage'
import LoginPage from '@/pages/LoginPage'
import SignupPage from '@/pages/SignupPage'
import PricingPage from '@/pages/PricingPage'
import AboutPage from '@/pages/AboutPage'
import ProtectedRoute from '@/components/ProtectedRoute'

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="pricing" element={<PricingPage />} />
          <Route path="about" element={<AboutPage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="signup" element={<SignupPage />} />
          
          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="project/:id" element={<ProjectPage />} />
          </Route>
        </Route>
      </Routes>
      <Toaster />
    </>
  )
}

export default App
