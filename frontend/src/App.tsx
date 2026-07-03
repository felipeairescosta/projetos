import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/Layout'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { ColaboradoresPage } from './pages/ColaboradoresPage'
import { ZonasPage } from './pages/ZonasPage'
import { EscalasPage } from './pages/EscalasPage'
import { AfastamentosPage } from './pages/AfastamentosPage'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<DashboardPage />} />
            <Route path="/colaboradores" element={<ColaboradoresPage />} />
            <Route path="/zonas" element={<ZonasPage />} />
            <Route path="/escalas" element={<EscalasPage />} />
            <Route path="/afastamentos" element={<AfastamentosPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
