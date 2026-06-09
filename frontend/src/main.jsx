import React from 'react'
import ReactDOM from 'react-dom/client'
import '@ant-design/v5-patch-for-react-19'
import App from './App.jsx'
import { AuthProvider, NotificationProvider } from './context'
import ErrorBoundary from './components/ErrorBoundary.jsx';
import './i18n.js';
import 'bootstrap/dist/css/bootstrap.min.css' // Importa Bootstrap CSS

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <AuthProvider>
        <NotificationProvider>
          <App />
        </NotificationProvider>
      </AuthProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)