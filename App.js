import React, { useState, useEffect } from 'react';
import { Route, Routes, useNavigate } from 'react-router-dom';
import jwt_decode from 'jwt-decode';
import Login from './Login';
import UserDashboard from './UserDashboard';
import AdminDashboard from './AdminDashboard';

const App = () => {
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const checkToken = () => {
      const token = localStorage.getItem('access_token');

      if (!token) {
        navigate('/login');
        setLoading(false);
        return;
      }

      try {
        const decoded = jwt_decode(token);
        if (Date.now() >= decoded.exp * 1000) {
          throw new Error("Session expired");
        }
        setRole(decoded.sub.role);
      } catch (error) {
        console.error("Session expired. Please log in again.");
        localStorage.removeItem("access_token");
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    checkToken();
  }, [navigate]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={role === 'admin' ? <AdminDashboard /> : <UserDashboard />} />
    </Routes>
  );
};

export default App;