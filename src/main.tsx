import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { App } from './App'
import { AuthProvider } from './contexts/AuthContext'
import './style.css'

const container = document.querySelector<HTMLDivElement>('#app')

if (container) {
  const root = ReactDOM.createRoot(container)
  root.render(
    <React.StrictMode>
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </React.StrictMode>,
  )
}

