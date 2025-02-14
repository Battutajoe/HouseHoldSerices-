import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import jwt_decode from 'jwt-decode';

const UserDashboard = () => {
  const [services, setServices] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const validateToken = useCallback(() => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      console.error("No token found in localStorage");
      return false;
    }

    try {
      const decoded = jwt_decode(token);
      if (!decoded || !decoded.exp) {
        throw new Error("Invalid token format");
      }

      if (Date.now() >= decoded.exp * 1000) {
        throw new Error("Token expired");
      }

      return token; // Return the token if valid
    } catch (error) {
      console.error('Session expired or invalid token:', error.message);
      localStorage.removeItem('access_token');
      navigate('/login');
      return false;
    }
  }, [navigate]);

  const fetchDashboardData = useCallback(async () => {
    const token = validateToken();
    if (!token) return;

    console.log("Token before request:", token);  // Debugging line

    setLoading(true);
    setError(null);

    try {
        const headers = { Authorization: `Bearer ${token}` };

        const [servicesResponse, ordersResponse] = await Promise.all([
            axios.get('http://127.0.0.1:5000/api/services', { headers }),
            axios.get('http://127.0.0.1:5000/api/orders/my', { headers }),
        ]);

        console.log("Services response:", servicesResponse.data);  // Debugging line
        console.log("Orders response:", ordersResponse.data);  // Debugging line

        setServices(servicesResponse.data);
        setOrders(ordersResponse.data);
    } catch (err) {
        console.error('Error fetching data:', err.response?.data || err.message);
        setError('Failed to load data.');
    } finally {
        setLoading(false);
    }
}, [validateToken]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return (
    <div>
      <h1>User Dashboard</h1>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <h2>Services</h2>
      <ul>
        {services.map(service => (
          <li key={service.id}>{service.name} - KES {service.price}</li>
        ))}
      </ul>

      <h2>Orders</h2>
      <ul>
        {orders.map(order => (
          <li key={order.order_id}>
            <strong>Order ID:</strong> {order.order_id}<br />
            <strong>Service:</strong> {order.service_id}<br />
            <strong>Quantity:</strong> {order.quantity}<br />
            <strong>Total Price:</strong> KES {order.total_price}<br />
            <strong>Status:</strong> {order.status}<br />
            <strong>Created At:</strong> {new Date(order.created_at).toLocaleString()}<br />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UserDashboard;