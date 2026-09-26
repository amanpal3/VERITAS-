import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { ToastProvider } from './context/ToastContext'
import AppSidebar from './components/layout/AppSidebar'
import AppHeader from './components/layout/AppHeader'
import Footer from './components/layout/Footer'

import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import NetworkAnalysis from './pages/NetworkAnalysis'
import EntityDetails from './pages/EntityDetails'
import Analytics from './pages/Analytics'
import { getHealth } from './api/graphApi'

export default function App() {
  const [stats, setStats] = useState({ nodes: 29, edges: 33 })
  const [isRefreshing, setIsRefreshing] = useState(false)

  const fetchStats = () => {
    setIsRefreshing(true)
    getHealth()
      .then(res => {
        setStats({
          nodes: res.data.total_nodes || 29,
          edges: res.data.total_edges || 33,
        })
      })
      .catch(() => {
        // Fallback default
      })
      .finally(() => {
        setTimeout(() => setIsRefreshing(false), 500)
      })
  }

  useEffect(() => {
    fetchStats()
  }, [])

  return (
    <ThemeProvider>
      <ToastProvider>
        <BrowserRouter>
          <div className="min-h-screen flex bg-canvas text-primary transition-colors">
            {/* Left Persistent Navigation Sidebar */}
            <AppSidebar stats={stats} />

            {/* Right Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
              <AppHeader onRefresh={fetchStats} isRefreshing={isRefreshing} />

              {/* Scrollable Container with Content and Footer */}
              <main className="flex-1 p-6 md:p-8 overflow-y-auto">
                <div className="min-h-[calc(100vh-14rem)]">
                  <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/network" element={<NetworkAnalysis />} />
                    <Route path="/entities" element={<EntityDetails />} />
                    <Route path="/analytics" element={<Analytics />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </div>

                {/* Footer Section on Every Dashboard View */}
                <Footer />
              </main>
            </div>
          </div>
        </BrowserRouter>
      </ToastProvider>
    </ThemeProvider>
  )
}
