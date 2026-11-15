import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './routes/LandingPage';
import Dashboard from './routes/Dashboard';
import Login from './routes/Login';
import Register from './routes/Register';
import { AuthProvider, useAuth } from './context/AuthContext';

// Public Route Wrapper (Redirects to dashboard if already logged in)
const PublicRoute = ({ children }) => {
  const { token } = useAuth();
  if (token) return <Navigate to="/dashboard" replace />;
  return children;
};

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { token } = useAuth();
  if (!token) return <Navigate to="/" replace />;
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<PublicRoute><LandingPage /></PublicRoute>} />
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
