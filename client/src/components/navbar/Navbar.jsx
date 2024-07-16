import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import logo from './../../assets/logofont.svg';
import './navbar.css';

const NavLinks = ({ handleLogout, isAuthenticated, fullName }) => {
    return (
        <React.Fragment>
            <p>
                <a href="/">Blog</a>
            </p>
            <p>
                <a href="/">Product</a>
            </p>
            <p>
                <a href="/">Community</a>
            </p>
            <p>
                <a href="/">Contact Us</a>
            </p>
            {isAuthenticated ? (
                <React.Fragment>
                    <p>
                        <span>Welcome, {fullName}</span>
                    </p>
                    <p>
                        <a href="/dashboard">Dashboard</a>
                    </p>
                    <p>
                        <a href="/" onClick={handleLogout}>Logout</a>
                    </p>
                </React.Fragment>
            ) : (
                <p>
                    <a href="/login">Login</a>
                </p>
            )}
        </React.Fragment>
    );
};

const Navbar = () => {  

    const navigate = useNavigate();
    const isAuthenticated = !!localStorage.getItem('token');
    const fullName = localStorage.getItem('fullName');

    const handleLogout = () => {
        // Clear the authentication data
        localStorage.removeItem('token');
        localStorage.removeItem('email');
        localStorage.removeItem('fullName');
        // Redirect to login page
        navigate('/login');
    };

    const handleLogoClick = () => {
        navigate('/');
    };

    return (
        <div className="landing-navbar">
            <div className="landing-navbar-logo" onClick={handleLogoClick} style={{ cursor: 'pointer' }}>
                <img src={logo} alt="aankh-logo" />
            </div>
            <div className="landing-navbar-links">
                <NavLinks handleLogout={handleLogout} isAuthenticated={isAuthenticated} fullName={fullName} />
            </div>
        </div>
    );
};

export default Navbar;
