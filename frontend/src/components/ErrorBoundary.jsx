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
                <h1 className="display-1 fw-bold">Error</h1>
                <p className="fs-3"> <span className="text-danger">Oops!</span> Something went wrong.</p>
                <p className="lead">An unexpected error occurred in the application.</p>
                <button className="btn btn-primary" onClick={() => window.location.reload()}>Reload Page</button>
            </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;