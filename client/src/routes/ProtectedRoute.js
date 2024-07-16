import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/authContext';

const ProtectedRoute = () => {
    const { auth } = useAuth();
    console.log("ProtectedRoute - auth:", auth); // Debugging line

    return auth.isAuthenticated ? <Outlet /> : <Navigate to="/login" />;
};

export default ProtectedRoute;
