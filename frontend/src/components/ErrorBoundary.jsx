import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error: error };
  }

  componentDidCatch(error, errorInfo) {
    // You can also log the error to an error reporting service
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div className="d-flex align-items-center justify-content-center vh-100 bg-light">
            <div className="text-center p-4">
                <h1 className="display-1 fw-bold">Errore</h1>
                <p className="fs-3"> <span className="text-danger">Oops!</span> Qualcosa è andato storto.</p>
                <p className="lead">Si è verificato un errore inatteso nell'applicazione.</p>
                <button className="btn btn-primary" onClick={() => window.location.reload()}>Ricarica la Pagina</button>
            </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;