import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Landing from './pages/Landing';
import Login from './pages/Login';
import UserDashboard from './pages/UserDashboard';
import AgentDashboard from './pages/AgentDashboard';
import ClaimDetails from './pages/ClaimDetails';
import Register from './pages/Register.jsx';
import FraudGraph from './FraudGraph';
import ShapExplainer from './ShapExplainer';
import './App.css';

const ProtectedRoute = ({ children, role }) => {
  const { user } = useAuth();
  
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to="/" replace />;
  
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* User Routes */}
          <Route 
            path="/user/dashboard" 
            element={
              <ProtectedRoute role="user">
                <UserDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Agent Routes */}
          <Route 
            path="/agent/dashboard" 
            element={
              <ProtectedRoute role="agent">
                <AgentDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Shared Routes */}
          <Route 
            path="/claim/:id" 
            element={
              <ProtectedRoute>
                <ClaimDetails />
              </ProtectedRoute>
            } 
          />
          
          {/* Agent-only Features */}
          <Route 
            path="/fraud-graph" 
            element={
              <ProtectedRoute role="agent">
                <FraudGraph />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/shap/:claimId" 
            element={
              <ProtectedRoute>
                <ShapExplainer />
              </ProtectedRoute>
            } 
          />
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

