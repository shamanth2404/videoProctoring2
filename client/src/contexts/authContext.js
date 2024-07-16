import React, { createContext, useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [auth, setAuth] = useState({
        isAuthenticated: !!localStorage.getItem('token'),
        token: localStorage.getItem('token'),
        email: localStorage.getItem('email'),
        fullName: localStorage.getItem('fullName'),
    });
    
    const navigate = useNavigate();

    const login = (token, email, fullName) => {
        localStorage.setItem('token', token);
        localStorage.setItem('email', email);
        localStorage.setItem('fullName', fullName);
        setAuth({
            isAuthenticated: true,
            token,
            email,
            fullName,
        });
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('email');
        localStorage.removeItem('fullName');
        setAuth({
            isAuthenticated: false,
            token: null,
            email: null,
            fullName: null,
        });
        navigate('/login');
    };

    return (
        <AuthContext.Provider value={{ auth, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
