import React from 'react';
import { Link } from 'react-router-dom';
import '../css/LandingPage.css';

const LandingPage = () => {
    return (
        <div className="landing-page">
            {/* Hero Section */}
            <section className="hero-section">
                <div className="hero-content">
                    <div className="hero-text">
                        <h1 className="hero-title">
                            <span className="company-name">Hands on Labor</span>
                            <span className="tagline">Professional Staffing Solutions</span>
                        </h1>
                        <p className="hero-subtitle">
                            San Diego's premier labor staffing agency connecting skilled workers 
                            with quality employment opportunities across Southern California.
                        </p>
                        <div className="hero-stats">
                            <div className="stat-item">
                                <span className="stat-number">500+</span>
                                <span className="stat-label">Active Workers</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-number">100+</span>
                                <span className="stat-label">Partner Companies</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-number">24/7</span>
                                <span className="stat-label">Support</span>
                            </div>
                        </div>
                    </div>
                    <div className="hero-image">
                        <img src="/worker.png" alt="Professional Worker" className="worker-image" />
                    </div>
                </div>
            </section>

            {/* Services Section */}
            <section className="services-section">
                <div className="container">
                    <h2 className="section-title">Our Services</h2>
                    <div className="services-grid">
                        <div className="service-card">
                            <div className="service-icon">🏗️</div>
                            <h3>Construction & Industrial</h3>
                            <p>Skilled tradespeople for construction, manufacturing, and industrial projects</p>
                        </div>
                        <div className="service-card">
                            <div className="service-icon">📦</div>
                            <h3>Warehouse & Logistics</h3>
                            <p>Reliable workers for warehousing, shipping, and distribution operations</p>
                        </div>
                        <div className="service-card">
                            <div className="service-icon">🔧</div>
                            <h3>General Labor</h3>
                            <p>Versatile workers for various manual labor and support roles</p>
                        </div>
                        <div className="service-card">
                            <div className="service-icon">⚡</div>
                            <h3>Emergency Staffing</h3>
                            <p>Quick response team for urgent staffing needs and last-minute requests</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta-section">
                <div className="container">
                    <h2 className="cta-title">Get Started with EasyShifts</h2>
                    <p className="cta-subtitle">
                        Join our platform to streamline your workforce management
                    </p>
                    <div className="cta-buttons">
                        <div className="user-type-card">
                            <div className="card-icon">👔</div>
                            <h3>For Managers</h3>
                            <p>Manage schedules, track timesheets, and coordinate your workforce</p>
                            <Link to="/signupManager" className="cta-button manager-btn">
                                Manager Sign Up
                            </Link>
                        </div>
                        <div className="user-type-card">
                            <div className="card-icon">👷</div>
                            <h3>For Workers</h3>
                            <p>Find shifts, manage your schedule, and track your hours</p>
                            <Link to="/signupEmployee" className="cta-button employee-btn">
                                Worker Sign Up
                            </Link>
                        </div>
                        <div className="user-type-card">
                            <div className="card-icon">🏢</div>
                            <h3>For Companies</h3>
                            <p>Access skilled workers and manage your staffing needs</p>
                            <Link to="/signupClient" className="cta-button client-btn">
                                Company Sign Up
                            </Link>
                        </div>
                    </div>
                    <div className="existing-user">
                        <p>Already have an account?</p>
                        <Link to="/login" className="login-link">Sign In</Link>
                    </div>
                </div>
            </section>

            {/* About Section */}
            <section className="about-section">
                <div className="container">
                    <div className="about-content">
                        <div className="about-text">
                            <h2>About Hands on Labor</h2>
                            <p>
                                Based in San Diego, California, Hands on Labor has been connecting 
                                skilled workers with quality employment opportunities throughout 
                                Southern California for over a decade.
                            </p>
                            <p>
                                Our EasyShifts platform revolutionizes workforce management by 
                                providing real-time scheduling, automated timesheet tracking, 
                                and seamless communication between workers, managers, and clients.
                            </p>
                            <div className="contact-info">
                                <div className="contact-item">
                                    <span className="contact-icon">🌐</span>
                                    <a href="https://handsonlabor.com" target="_blank" rel="noopener noreferrer">
                                        handsonlabor.com
                                    </a>
                                </div>
                                <div className="contact-item">
                                    <span className="contact-icon">📍</span>
                                    <span>San Diego, CA</span>
                                </div>
                            </div>
                        </div>
                        <div className="about-image">
                            <img src="/businessman.png" alt="Business Professional" className="business-image" />
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="landing-footer">
                <div className="container">
                    <div className="footer-content">
                        <div className="footer-brand">
                            <h3>Hands on Labor</h3>
                            <p>Professional Staffing Solutions</p>
                        </div>
                        <div className="footer-links">
                            <div className="footer-section">
                                <h4>Platform</h4>
                                <Link to="/login">Sign In</Link>
                                <Link to="/signup">Sign Up</Link>
                            </div>
                            <div className="footer-section">
                                <h4>Services</h4>
                                <span>Construction</span>
                                <span>Warehouse</span>
                                <span>General Labor</span>
                            </div>
                            <div className="footer-section">
                                <h4>Contact</h4>
                                <a href="https://handsonlabor.com" target="_blank" rel="noopener noreferrer">
                                    Website
                                </a>
                                <span>San Diego, CA</span>
                            </div>
                        </div>
                    </div>
                    <div className="footer-bottom">
                        <p>&copy; 2024 Hands on Labor. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
