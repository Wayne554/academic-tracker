import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useStore } from './store'
import Login from './pages/Login'
import Home from './pages/Home'
import Starred from './pages/Starred'
import Admin from './pages/Admin'

function App() {
  const { token, fetchMe, user } = useStore()

  useEffect(() => {
    if (token) {
      fetchMe()
    }
  }, [token])

  if (token && !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!token) {
    return <Login />
  }

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/starred" element={<Starred />} />
      {user?.is_admin && <Route path="/admin" element={<Admin />} />}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
