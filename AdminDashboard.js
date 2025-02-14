import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AdminDashboard = () => {
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    axios.get('http://127.0.0.1:5000/api/orders', {
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    })
    .then(response => setOrders(response.data.orders))
    .catch(error => setError('Error fetching orders'));
  }, []);

  return (
    <div>
      <h1>Admin Dashboard</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <ul>
        {orders.map(order => (
          <li key={order.order_id}>
            <strong>Order ID:</strong> {order.order_id}<br />
            <strong>User:</strong> {order.user}<br />
            <strong>Service:</strong> {order.service}<br />
            <strong>Status:</strong> {order.status}<br />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AdminDashboard;