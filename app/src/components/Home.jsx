// components/Home.js
import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import LandingPage from './LandingPage';
import AuthenticatedHome from './AuthenticatedHome';
import './../css/Home.css';

const Home = () => {
    const { isAuthenticated } = useAuth();

    return isAuthenticated ? <AuthenticatedHome /> : <LandingPage />;
}

export default Home;
