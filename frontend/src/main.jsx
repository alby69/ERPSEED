import React from 'react'
import ReactDOM from 'react-dom/client'
import '@ant-design/v5-patch-for-react-19'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App.jsx'
import { AuthProvider, NotificationProvider } from './context'
import ErrorBoundary from './components/ErrorBoundary.jsx';
import './i18n.js';
import 'bootstrap/dist/css/bootstrap.min.css' // Importa Bootstrap CSS

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <NotificationProvider>
            <App />
          </NotificationProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)